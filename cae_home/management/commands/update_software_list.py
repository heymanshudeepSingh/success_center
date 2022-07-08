"""
Command that creates User models from a passed list of bronconet id's.
For security, these users always default to inactive, and must be manually activated.

For User model creation that is dynamically set to active or inactive (based on LDAP), please use Django's standard
website login logic.
"""

# System Imports.

import json, os, time, pathlib
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

# User Imports.
from cae_home.models import User
from django.db.models import ObjectDoesNotExist
from django.utils.text import slugify
from cae_home.models.cae import Software, SoftwareDetail
from workspace.ldap_backends.wmu_auth import cae_backend, wmu_backend
from workspace.settings import extra_settings


# logger = extra_settings.logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update software list database using cae_home models'

    def add_arguments(self, parser):
        """
        Parser for command.
        """
        # Optional arguments.
        parser.add_argument(
            'file_path',
            type=str,
            nargs='?',
            default='NetStore/Software',
            help='File path to process software. Defaults to alva directory root.',
        )

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        # Check if in development or production mode.
        homePath = '/alva/Software/'  # Remote location for scanning the folders for readmes
        # homePath = '/home/cae/projects/update-software/'

        softwaredetails = []  # List to store software details from readme.json
        softwarenames = []  # List to store software names taken from path that the readmes are found in
        # fileList = glob.glob(homePath, recursive=True)
        # currentPath = pathlib.Path('.').absolute()
        # print(currentPath)
        fileList = sorted(pathlib.Path(homePath).glob('*/readme.json'))
        # glob finds path names according to a pattern and returns a list of path names that match the pattern
        # https://docs.python.org/3/library/glob.html

        # print('File list: {0}'.format(fileList))

        for file_name in fileList:  # Loop to iterate through the directories with readme.jsons
            print(file_name)
            if self.checkLastModified(file_name):  # Check to see if the json has been modified in the past two weeks
                softFile = open(file_name, 'r')  # Open the json file
                softName = file_name.parent.name
                # print('  Software name: {0}'.format(softName))
                # Extract the directory name (which happens to be the name of the software)

                jsonfile = json.load(softFile)  # Parse json file
                softwarenames.append(softName)  # Add software names to the list
                softwaredetails.append(jsonfile)  # Add the software details to the list
                softFile.close()  # Close the opened json file

        # print('    Software names list: {0}'.format(softwarenames))
        # print('       Software details list: {0}'.format(softwarelist))
        softwarelist = zip(softwarenames, softwaredetails)
        print(list(softwarelist))
        for names, details in softwarelist:  # Loop to add the software names and details to the database

            # Next section is taken almost verbatim from the create_dummy_model from cae_home.models.cae.py
            name = names
            slug = slugify(name)
            version = details['version']
            expiration = details['expiration']
            rooms = details['rooms']

            try:
                currentModel = Software.objects.get(
                    name=name,
                    slug=slug,
                )
                Software.save(currentModel)
            except ObjectDoesNotExist:
                currentModel = Software.objects.create(
                    name=name,
                    slug=slug,
                )
                Software.save(currentModel)
            # print
            try:
                currentModel = SoftwareDetail.objects.get(
                    software=name,
                    version=version,
                    expiration=expiration,
                    # room detail ?
                )
                SoftwareDetail.save(currentModel)
            except ObjectDoesNotExist:
                return SoftwareDetail.objects.create(
                    software=name,
                    version=version,
                    expiration=expiration,
                    rooms=rooms
                )
                SoftwareDetail.save(self)

    def checkLastModified(self, readmefile):  # Function to check if the file was modified in the past two weeks
        # twoweeks = 1209600.00  # Value of two weeks in seconds
        # fileLM = os.path.getmtime(readmefile)  # Get the last modified time from the file
        # print('File last modified = {0}'.format(fileLM))
        # currentTime = time.time()  # Current time
        # print('Current time: {0}'.format(currentTime))
        # print('  Time since last update: {0}'.format(currentTime - fileLM))
        return True
        # if (currentTime - fileLM) > twoweeks:
        #     return True  # Return true if the file has been modified in more than two weeks
        # else:
        #     return False
        # #     # Return false if the file has been modified more recently than two weeks, so that it can be skipped
