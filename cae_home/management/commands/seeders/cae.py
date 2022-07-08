"""
Seeder for "CAE Center" related Core Models.
"""

# System Imports
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.text import slugify
from faker import Faker
from random import randint
from sys import stdout

# User Imports.
from cae_home import models
from cae_home.management.commands.fixtures import cae as cae_fixtures


def generate_model_seeds(style, model_count):
    """
    Calls individual seeder methods.
    """
    stdout.write(style.HTTP_NOT_MODIFIED('SEEDING CAE Model Group.\n'))
    create_assets(style, model_count)
    create_software(style, model_count)
    create_software_detail(style, model_count)


def create_assets(style, model_count):
    """
    Create Asset models.
    """
    # Load preset fixtures.
    cae_fixtures.create_assets(style)

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
            # room = rooms[index]

            # Generate Ip address. 50/50 chance of being ipv4 or ipv6
            if randint(0, 1) == 1:
                ip_address = faker_factory.ipv4()
            else:
                ip_address = faker_factory.ipv6()

            # Attempt to create model seed.
            try:
                models.Asset.objects.create(
                    # room=room,
                    serial_number=faker_factory.isbn13(),
                    asset_tag=faker_factory.ean8(),
                    brand_name=faker_factory.domain_word(),
                    mac_address=faker_factory.mac_address(),
                    ip_address=ip_address,
                    device_name=faker_factory.last_name(),
                    description=faker_factory.sentence(),
                )

                try_create_model = False
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


def create_software(style, model_count):
    """
    Create Software models.
    """
    # Load preset fixtures.
    cae_fixtures.create_software(style)

    # Generate random data.
    faker_factory = Faker()

    # Count number of models already created.
    pre_initialized_count = len(models.Software.objects.all())

    # Generate models equal to model count.
    total_fail_count = 0
    for i in range(model_count - pre_initialized_count):
        fail_count = 0
        try_create_model = True

        # Loop attempt until 3 fails or model is created.
        # Model creation may fail due to randomness of name value and overlapping slugs being invalid.
        while try_create_model:

            name = faker_factory.job()
            slug = slugify(name)

            # Attempt to create model seed.
            try:
                models.Software.objects.create(
                    name=name,
                    slug=slug
                )
                try_create_model = False
            except (ValidationError, IntegrityError):
                # Seed generation failed. Nothing can be done about this without removing the random generation
                # aspect. If we want that, we should use fixtures instead.
                fail_count += 1

                # If failed 3 times, give up model creation and move on to next model, to prevent infinite loops.
                if fail_count > 2:
                    try_create_model = False
                    total_fail_count += 1

    # Output if model instances failed to generate.
    if total_fail_count > 0:
        stdout.write(style.WARNING(
            'Failed to generate {0}/{1} Software seed instances.\n'.format(total_fail_count, model_count)
        ))

    stdout.write('Populated ' + style.SQL_FIELD('Software') + ' models.\n')


def create_software_detail(style, model_count):
    """
    Create Software Detail models
    """
    # Load preset fixtures.
    cae_fixtures.create_software_detail(style)

    # Generate random data.
    faker_factory = Faker()

    softwares = models.Software.objects.all()

    # Count number of models already created.
    pre_initialized_count = len(models.SoftwareDetail.objects.all())

    # Generate models equal to model count.
    total_fail_count = 0
    for i in range(model_count - pre_initialized_count):
        fail_count = 0
        try_create_model = True

        # Loop attempt until 3 fails or model is created.
        # Model creation may fail due to randomness of name value and overlapping slugs being invalid.
        while try_create_model:

            # Get software.
            index = randint(0, len(softwares) - 1)
            software = softwares[index]

            software_type = randint(1, 3)
            version = faker_factory.job()
            is_active = faker_factory.boolean()
            slug = slugify('{0} - {1}'.format(software.name, version))

            # Attempt to create model seed.
            try:
                models.SoftwareDetail.objects.create(
                    software=software,
                    software_type=software_type,
                    version=faker_factory.random_int(min=1, max=500),
                    expiration=faker_factory.date_between(start_date="-1y", end_date="+2y"),
                    is_active=is_active,
                    slug=slug,
                )
                try_create_model = False
            except (ValidationError, IntegrityError):
                # Seed generation failed. Nothing can be done about this without removing the random generation
                # aspect. If we want that, we should use fixtures instead.
                fail_count += 1

                # If failed 3 times, give up model creation and move on to next model, to prevent infinite loops.
                if fail_count > 2:
                    try_create_model = False
                    total_fail_count += 1

    # Output if model instances failed to generate.
    if total_fail_count > 0:
        stdout.write(style.WARNING(
            'Failed to generate {0}/{1} Software seed instances.\n'.format(total_fail_count, model_count)
        ))

    stdout.write('Populated ' + style.SQL_FIELD('Software Detail') + ' models.\n')
