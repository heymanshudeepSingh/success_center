"""
Seeder for "CAE Center" related Core Models.
"""

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from faker import Faker
from random import randint
from sys import stdout

from cae_home import models


def generate_model_seeds(style, model_count):
    """
    Calls individual seeder methods.
    """
    # stdout.write(style.HTTP_NOT_MODIFIED('SEEDING CAE Model Group.\n'))
    # create_assets(style, model_count)
    pass


def create_assets(style, model_count):
    """
    Create Asset models.
    """
    # Create random data generator.
    faker_factory = Faker()

    # Count number of models already created.
    pre_initialized_count = len(models.Asset.objects.all())

    # Get all related models.
    rooms = models.Room.objects.all()

    # Generate models equal to model count.
    total_fail_count = 0
    for i in range(model_count - pre_initialized_count):
        fail_count = 0
        try_create_model = True

        # Loop attempt until 3 fails or model is created.
        # Model creation may fail due to field unique requirement.
        while try_create_model:
            # Get Room.
            index = randint(0, len(rooms) - 1)
            room = rooms[index]

            # Generate Ip address. 50/50 chance of being ipv4 or ipv6
            if randint(0, 1) == 1:
                ip_address = faker_factory.ipv4()
            else:
                ip_address = faker_factory.ipv6()

            # Attempt to create model seed.
            try:
                models.Asset.objects.create(
                    room=room,
                    serial_number=faker_factory.isbn13(),
                    asset_tag=faker_factory.ean8(),
                    brand_name=faker_factory.domain_word(),
                    mac_address=faker_factory.mac_address(),
                    ip_address=ip_address,
                    device_name=faker_factory.last_name(),
                    description=faker_factory.sentence(),
                )
            except (ValidationError, IntegrityError):
                # Seed generation failed. Nothing can be done about this without removing the random generation aspect.
                # If we want that, we should use fixtures instead.
                fail_count += 1

                # If failed 3 times, give up model creation and move on to next model, to prevent infinite loops.
                if fail_count > 2:
                    try_create_model = False
                    total_fail_count += 1

    # Output if model instances failed to generate.
    if total_fail_count > 0:
        stdout.write(style.WARNING(
            'Failed to generate {0}/{1} Asset seed instances.\n'.format(total_fail_count, model_count)
        ))

    stdout.write('Populated ' + style.SQL_FIELD('Asset') + ' models.\n')
