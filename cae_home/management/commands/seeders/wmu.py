"""
Seeder for "WMU" related Core Models.

Note that seeder methods will always call fixture methods first. Then attempt seeding afterwards.
"""

# System Imports.
from faker import Faker
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from random import randint
from sys import stdout

# User Imports.
from cae_home.management.commands.fixtures import wmu as wmu_fixtures
from cae_home.models.wmu import Department, WmuClass


def generate_model_seeds(style, model_count):
    """
    Calls individual seeder methods.
    """
    stdout.write(style.HTTP_NOT_MODIFIED('SEEDING WMU Model Group.\n'))
    create_room_types(style)
    create_departments(style)
    create_rooms(style)
    create_majors(style)
    create_semesters(style)
    create_wmu_classes(style, model_count)


def create_wmu_classes(style, model_count):
    """
    Create WMU Class models.
    """
    wmu_fixtures.create_wmu_classes(style)
    # Create random data generator.
    faker_factory = Faker()

    # Count number of models already created.
    pre_initialized_count = len(WmuClass.objects.all())

    # Get all related models.
    departments = Department.objects.all()

    # Generate models equal to model count.
    total_fail_count = 0
    for i in range(model_count - pre_initialized_count):
        fail_count = 0
        try_create_model = True

        # Loop attempt until 3 fails or model is created.
        # Model creation may fail due to field unique requirement.
        while try_create_model:

            # Get Room.
            index = randint(0, len(departments) - 1)
            department = departments[index]

            # Generate classroom codes.
            code = faker_factory.bothify(text='???#####')

            # Attempt to create model seed.
            try:
                WmuClass.objects.create(
                    department=department,
                    code=code,
                    title=faker_factory.sentence(nb_words=5, variable_nb_words=True),
                    description=faker_factory.paragraph(),
                    slug=slugify(code)
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
            'Failed to generate {0}/{1} WmuClass seed instances.\n'.format(total_fail_count, model_count)
        ))

    stdout.write('Populated ' + style.SQL_FIELD('WmuClass') + ' models.\n')


def create_room_types(style):
    """
    Create Room Type models.
    """
    # Load preset fixtures.
    wmu_fixtures.create_room_types(style)

    stdout.write('Populated ' + style.SQL_FIELD('Room Type') + ' models.\n')


def create_departments(style):
    """
    Create Department models.
    """
    # Load preset fixtures.
    wmu_fixtures.create_departments(style)

    stdout.write('Populated ' + style.SQL_FIELD('Department') + ' models.\n')


def create_rooms(style):
    """
    Create Room models.
    """
    # Load preset fixtures.
    wmu_fixtures.create_rooms(style)

    stdout.write('Populated ' + style.SQL_FIELD('Room') + ' models.\n')


def create_majors(style):
    """
    Create Major models.
    """
    # Load preset fixtures.
    wmu_fixtures.create_majors(style)

    stdout.write('Populated ' + style.SQL_FIELD('Major') + ' models.\n')


def create_semesters(style):
    """
    Create Semester Date models.
    """
    # Load preset fixtures.
    wmu_fixtures.create_semester_dates(style)

    stdout.write('Populated ' + style.SQL_FIELD('Semester Date') + ' models.\n')
