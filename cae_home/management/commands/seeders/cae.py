"""
Seeder for "CAE Center" related Core Models.
"""

from django.core.exceptions import ValidationError
from faker import Faker
from random import randint

from cae_home import models


def generate_model_seeds(model_count):
    """
    Calls individual seeder methods.
    """
    print('SEEDING CAE Model Group.')
    create_assets(model_count)


def create_assets(model_count):
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
            except ValidationError:
                # Seed generation failed. Nothing can be done about this without removing the random generation aspect.
                # If we want that, we should use fixtures instead.
                fail_count += 1

                # If failed 3 times, give up model creation and move on to next model, to prevent infinite loops.
                if fail_count > 2:
                    try_create_model = False
                    print('Failed to generate asset seed instance.')

    print('Populated asset models.')
