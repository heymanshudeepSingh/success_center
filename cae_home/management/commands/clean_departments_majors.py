"""
Command to clean/sanitize existing department and major model records.
"""

# System Imports.
import logging
from django.core.management.base import BaseCommand
from django.utils.text import slugify

# User Imports.
from cae_home import models
from workspace.ldap_backends.wmu_auth.adv_backend import AdvisingAuthBackend


# Initialize Logging.
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Cleans & sanitizes existing department and major model records.'

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        self.process_departments()
        self.process_majors()

    def process_departments(self):
        # Loop through all departments.
        department_list = models.Department.objects.all()
        for department in department_list:
            # Ensure model slug value matches model code.
            department.slug = slugify(department.code)
            department.save()

    def process_majors(self):
        # Define list of "known problem majors" that will fail the below checks, and we have *no* idea what type of
        # degree it's supposed to be (only add values to this sparingly. Having too many in this list will defeat
        # the entire purpose of this section of the manage.py script).
        known_problem_list = [
            # "Audiology" majors with the "AUD" type. No idea what to classify it as.
            'AUDD',
            'AUDZ',
            # Various majors with the "OTD" type. No idea what to classify it as.
            'OCTD',
            # Various majors with the "DPT" type. No idea what to classify it as.
            'PTHD',
            # Various majors with the "GCP" type. No idea what to classify it as.
            'ASTC',
            'HYDC',
            'PWEC',
            'SLTC',
            'YCDC',
            # Various majors with the "UCP" type. No idea what to classify it as.
            'SCPF',
            # "Unknown" majors that literally don't have a degree type.
            'CER',
            'UNC',
            'UND',
            'UNK',
            'UNV',
        ]

        # Loop through all majors.
        major_list = models.Major.objects.filter(
            degree_level=0,
        ).exclude(
            student_code__in=known_problem_list,
        ).order_by(
            'student_code',
        )
        unknown_major_list = []
        for major in major_list:
            # Ensure "degree level" field is properly populated (we want minimal to no unknown values).
            degree_level = AdvisingAuthBackend._get_degree_level_from_program_code('CAE', major.program_code)
            print('returned_level: {0}'.format(degree_level))
            if major.degree_level != degree_level:
                # Found a "better" degree level. Update and save.
                major.degree_level = degree_level
                major.save()

            # Check if degree level still returns as unknown.
            if major.degree_level == 0:
                unknown_major_list.append(str(major))
                print('Unknown Major: {0}'.format(major))
                print('    {0}'.format(major.program_code))

        # Notify programmers if any majors were unhandled.
        if len(unknown_major_list) > 0:
            logger.error(
                (
                    'Failed to associate degree levels with {0} majors. Please update ldap AdvAuth "major" logic. '
                    'Problem majors are are: {1}'
                ).format(
                    len(unknown_major_list),
                    unknown_major_list,
                )
            )
