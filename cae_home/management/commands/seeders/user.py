"""
Seeder for "User" related Core Models.

Note that seeder methods will always call fixture methods first. Then attempt seeding afterwards.
"""

# System Imports.
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from faker import Faker
from faker_e164.providers import E164Provider
from phonenumber_field.phonenumber import PhoneNumber
from random import randint
from sys import stdout

# User Imports.
from cae_home import models
from cae_home.models.user import check_all_group_memberships
from cae_home.management.commands.fixtures import user as user_fixtures

default_password = settings.USER_SEED_PASSWORD


def generate_model_seeds(style, model_count):
    """
    Calls individual seeder methods.
    """
    stdout.write(style.HTTP_NOT_MODIFIED('SEEDING User Model Group.\n'))
    create_site_themes(style)
    create_groups(style, display_output=True)
    create_users(style, display_output=True)
    create_addresses(style, model_count)
    create_wmu_users(style, model_count)


def create_site_themes(style):
    """
    Creates profile theme models.
    """
    # Load preset fixtures.
    user_fixtures.create_site_themes(style)

    stdout.write('Populated ' + style.SQL_FIELD('Site Theme') + ' models.\n')


def create_groups(style=None, display_output=False):
    """
    Creates django "auth_group" models and allocates proper permissions.
    Should be identical to fixture version, so we simply use this as a reference to the function there.
    """
    return user_fixtures.create_groups(style, display_output=display_output)


def create_permission_groups():
    """
    Create main permission groups.
    Should be identical to fixture version, so we simply use this as a reference to the function there.
    :return: Array of permission groups.
    """
    return user_fixtures.create_permission_groups()


def get_cae_center_permissions(style=None):
    """
    Finds all permission models specific to the CAE Center.
    Should be identical to fixture version, so we simply use this as a reference to the function there.
    :return: A list of all permission models for the CAE Center.
    """
    return user_fixtures.get_cae_center_permissions()


def create_users(style=None, display_output=False):
    """
    Creates base user models.
    """
    # Create extra superusers for developers, using env.py settings.
    # Use the "SEED_USERS" list for usernames.
    for username in settings.SEED_USERS:
        # Create user account with given username and env password.
        user = models.User.get_or_create_superuser(username, '', default_password)

    # Create all default users for testing group logic.
    create_permission_group_users(password=default_password)

    # Loop through again, and set all "developer seed users" to have a default group of CAE Programmer.
    cae_programmer_group = Group.objects.get(name='CAE Programmer')
    for username in settings.SEED_USERS:
        user = models.User.get_or_create_superuser(username, '', default_password)
        user.groups.add(cae_programmer_group)
        user.save()

    if display_output and style is not None:
        stdout.write('Populated ' + style.SQL_FIELD('User') + ' models.\n')


def create_permission_group_users(password=default_password, with_names=True, as_dict=False):
    """
    Create specific users for each main group permission.
    :param password: Password to seed users with.
    :param with_names: Boolean indicating if names should be used. Should probably be set to False for UnitTesting.
    :param as_dict: Bool indicating if return value should be list or dict.
    :return: Array or dict of users.
    """
    # Create normal users for every CAE Center permission group.
    cae_director = models.User.get_or_create_user('cae_director', '', password)
    cae_director_inactive = models.User.get_or_create_user('cae_director_inactive', '', password, inactive=True)
    cae_building_coordinator = models.User.get_or_create_user('cae_building_coordinator', '', password)
    cae_building_coordinator_inactive = models.User.get_or_create_user('cae_building_coordinator_inactive', '', password, inactive=True)
    cae_admin_ga = models.User.get_or_create_user('cae_admin_ga', '', password)
    cae_admin_ga_inactive = models.User.get_or_create_user('cae_admin_ga_inactive', '', password, inactive=True)
    cae_programmer_ga = models.User.get_or_create_user('cae_programmer_ga', '', password)
    cae_programmer_ga_inactive = models.User.get_or_create_user('cae_programmer_ga_inactive', '', password, inactive=True)
    cae_admin = models.User.get_or_create_user('cae_admin', '', password)
    cae_admin_inactive = models.User.get_or_create_user('cae_admin_inactive', '', password, inactive=True)
    cae_programmer = models.User.get_or_create_user('cae_programmer', '', password)
    cae_programmer_inactive = models.User.get_or_create_user('cae_programmer_inactive', '', password, inactive=True)
    cae_attendant = models.User.get_or_create_user('cae_attendant', '', password)
    cae_attendant_inactive = models.User.get_or_create_user('cae_attendant_inactive', '', password, inactive=True)

    # Create normal users for every general basic WMU permission group.
    wmu_faculty = models.User.get_or_create_user('wmu_faculty', '', password)
    wmu_faculty_inactive = models.User.get_or_create_user('wmu_faculty_inactive', '', password, inactive=True)
    wmu_teacher = models.User.get_or_create_user('wmu_teacher', '', password)
    wmu_teacher_inactive = models.User.get_or_create_user('wmu_teacher_inactive', '', password, inactive=True)
    wmu_student = models.User.get_or_create_user('wmu_student', '', password)
    wmu_student_inactive = models.User.get_or_create_user('wmu_student_inactive', '', password, inactive=True)

    # Create normal users for every STEP (Success Center) permission group.
    step_admin = models.User.get_or_create_user('step_admin', '', password)
    step_admin_inactive = models.User.get_or_create_user('step_admin_inactive', '', password, inactive=True)
    step_employee = models.User.get_or_create_user('step_employee', '', password)
    step_employee_inactive = models.User.get_or_create_user('step_employee_inactive', '', password, inactive=True)

    # Create normal users for every GradApps permission group.
    grad_apps_admin = models.User.get_or_create_user('grad_apps_admin', '', password)
    grad_apps_admin_inactive = models.User.get_or_create_user('grad_apps_admin_inactive', '', password, inactive=True)
    grad_apps_committee_member = models.User.get_or_create_user('grad_apps_committee_member', '', password)
    grad_apps_committee_member_inactive = models.User.get_or_create_user(
        'grad_apps_committee_member_inactive',
        '',
        password,
        inactive=True,
    )

    # Set their names.
    if with_names:
        cae_admin.first_name = "Gumball"
        cae_admin.last_name = "Watterson"
        cae_admin.save()
        cae_admin_ga.first_name = "Homer"
        cae_admin_ga.last_name = "Simpson"
        cae_admin_ga.save()
        cae_attendant.first_name = "Darwin"
        cae_attendant.last_name = "Watterson"
        cae_attendant.save()
        cae_programmer.first_name = "Phillip"
        cae_programmer.last_name = "Fry"
        cae_programmer.save()
        cae_programmer_ga.first_name = "Chosen"
        cae_programmer_ga.last_name = "One"
        cae_programmer_ga.save()

    # Add permission groups to CAE Center users.
    cae_director.groups.add(Group.objects.get(name='CAE Director'))
    cae_director.save()
    cae_building_coordinator.groups.add(Group.objects.get(name='CAE Building Coordinator'))
    cae_building_coordinator.save()
    cae_admin_ga.groups.add(Group.objects.get(name='CAE Admin GA'), Group.objects.get(name='CAE Admin'))
    cae_admin_ga.save()
    cae_programmer_ga.groups.add(Group.objects.get(name='CAE Programmer GA'), Group.objects.get(name='CAE Programmer'))
    cae_programmer_ga.save()
    cae_admin.groups.add(Group.objects.get(name='CAE Admin'))
    cae_admin.save()
    cae_programmer.groups.add(Group.objects.get(name='CAE Programmer'))
    cae_programmer.save()
    cae_attendant.groups.add(Group.objects.get(name='CAE Attendant'))
    cae_attendant.save()

    # Add permission groups to general WMU users.
    wmu_faculty.groups.add(Group.objects.get(name='WMU Faculty'))
    wmu_faculty.save()
    wmu_teacher.groups.add(Group.objects.get(name='WMU Teacher'))
    wmu_teacher.save()
    wmu_student.groups.add(Group.objects.get(name='WMU Student'))
    wmu_student.save()

    # Add permission groups to STEP (Success Center) users.
    step_admin.groups.add(Group.objects.get(name='STEP Admin'))
    step_admin.save()
    step_employee.groups.add(Group.objects.get(name='STEP Employee'))
    step_employee.save()

    # Add permission groups to GradApps users.
    grad_apps_admin.groups.add(Group.objects.get(name='Grad Apps Admin'))
    grad_apps_admin.save()
    grad_apps_committee_member.groups.add(Group.objects.get(name='Grad Apps Committee Member'))
    grad_apps_committee_member.save()

    # Set all GroupMembership models for users.
    check_all_group_memberships()

    # Also set inactive user GroupMembership. For these, we just set from "two years ago" up through to today.
    today = timezone.localdate()
    two_years_ago = today - timezone.timedelta(days=730)

    # Set inactive GroupMembership for disabled users.
    # Required because the is_active bool is based on group membership, so we can't add directly.
    models.GroupMembership.objects.create(
        user=cae_director_inactive,
        group=Group.objects.get(name='CAE Director'),
        date_joined=two_years_ago,
        date_left=today,
    )
    models.GroupMembership.objects.create(
        user=cae_building_coordinator_inactive,
        group=Group.objects.get(name='CAE Building Coordinator'),
        date_joined=two_years_ago,
        date_left=today,
    )
    models.GroupMembership.objects.create(
        user=cae_admin_ga_inactive,
        group=Group.objects.get(name='CAE Admin GA'),
        date_joined=two_years_ago,
        date_left=today,
    )
    models.GroupMembership.objects.create(
        user=cae_admin_ga_inactive,
        group=Group.objects.get(name='CAE Admin'),
        date_joined=two_years_ago,
        date_left=today,
    )
    models.GroupMembership.objects.create(
        user=cae_programmer_ga_inactive,
        group=Group.objects.get(name='CAE Programmer GA'),
        date_joined=two_years_ago,
        date_left=today,
    )
    models.GroupMembership.objects.create(
        user=cae_programmer_ga_inactive,
        group=Group.objects.get(name='CAE Programmer'),
        date_joined=two_years_ago,
        date_left=today,
    )
    models.GroupMembership.objects.create(
        user=cae_admin_inactive,
        group=Group.objects.get(name='CAE Admin'),
        date_joined=two_years_ago,
        date_left=today,
    )
    models.GroupMembership.objects.create(
        user=cae_programmer_inactive,
        group=Group.objects.get(name='CAE Programmer'),
        date_joined=two_years_ago,
        date_left=today,
    )
    models.GroupMembership.objects.create(
        user=cae_attendant_inactive,
        group=Group.objects.get(name='CAE Attendant'),
        date_joined=two_years_ago,
        date_left=today,
    )

    # Set inactive GroupMembership for general WMU users.
    models.GroupMembership.objects.create(
        user=wmu_faculty_inactive,
        group=Group.objects.get(name='WMU Faculty'),
        date_joined=two_years_ago,
        date_left=today,
    )
    models.GroupMembership.objects.create(
        user=wmu_teacher_inactive,
        group=Group.objects.get(name='WMU Teacher'),
        date_joined=two_years_ago,
        date_left=today,
    )
    models.GroupMembership.objects.create(
        user=wmu_student_inactive,
        group=Group.objects.get(name='WMU Student'),
        date_joined=two_years_ago,
        date_left=today,
    )

    # Set inactive GroupMembership for STEP (Success Center) users.
    models.GroupMembership.objects.create(
        user=step_admin_inactive,
        group=Group.objects.get(name='STEP Admin'),
        date_joined=two_years_ago,
        date_left=today,
    )
    models.GroupMembership.objects.create(
        user=step_employee_inactive,
        group=Group.objects.get(name='STEP Employee'),
        date_joined=two_years_ago,
        date_left=today,
    )

    # Set inactive GroupMembership for GradApps users.
    models.GroupMembership.objects.create(
        user=grad_apps_admin_inactive,
        group=Group.objects.get(name='Grad Apps Admin'),
        date_joined=two_years_ago,
        date_left=today,
    )
    models.GroupMembership.objects.create(
        user=grad_apps_committee_member_inactive,
        group=Group.objects.get(name='Grad Apps Committee Member'),
        date_joined=two_years_ago,
        date_left=today,
    )

    if as_dict:
        # Populate dictionaries in case calling logic wants easy access to users.
        active_user_dict = {
            'cae_director': cae_director,
            'cae_building_coordinator': cae_building_coordinator,
            'cae_admin_ga': cae_admin_ga,
            'cae_programmer_ga': cae_programmer_ga,
            'cae_admin': cae_admin,
            'cae_programmer': cae_programmer,
            'cae_attendant': cae_attendant,
            'wmu_faculty': wmu_faculty,
            'wmu_teacher': wmu_teacher,
            'wmu_student': wmu_student,
            'step_admin': step_admin,
            'step_employee': step_employee,
            'grad_apps_admin': grad_apps_admin,
            'grad_apps_committee_member': grad_apps_committee_member,
        }
        inactive_user_dict = {
            'cae_director': cae_director_inactive,
            'cae_building_coordinator': cae_building_coordinator_inactive,
            'cae_admin_ga': cae_admin_ga_inactive,
            'cae_programmer_ga': cae_programmer_ga_inactive,
            'cae_admin': cae_admin_inactive,
            'cae_programmer': cae_programmer_inactive,
            'cae_attendant': cae_attendant_inactive,
            'wmu_faculty': wmu_faculty_inactive,
            'wmu_teacher': wmu_teacher_inactive,
            'wmu_student': wmu_student_inactive,
            'step_admin': step_admin_inactive,
            'step_employee': step_employee_inactive,
            'grad_apps_admin': grad_apps_admin_inactive,
            'grad_apps_committee_member': grad_apps_committee_member_inactive,
        }
        return (active_user_dict, inactive_user_dict)
    else:
        # Populate arrays in case calling logic wants easy access to users.
        active_user_array = [               # Index Num:
            cae_director,                   # 0
            cae_building_coordinator,       # 1
            cae_admin_ga,                   # 2
            cae_programmer_ga,              # 3
            cae_admin,                      # 4
            cae_programmer,                 # 5
            cae_attendant,                  # 6
            wmu_faculty,                    # 7
            wmu_teacher,                    # 8
            wmu_student,                    # 9
            step_admin,                     # 10
            step_employee,                  # 11
            grad_apps_admin,                # 12
            grad_apps_committee_member,     # 13
        ]
        inactive_user_array = [                     # Index Num:
            cae_director_inactive,                  # 0
            cae_building_coordinator_inactive,      # 1
            cae_admin_ga_inactive,                  # 2
            cae_programmer_ga_inactive,             # 3
            cae_admin_inactive,                     # 4
            cae_programmer_inactive,                # 5
            cae_attendant_inactive,                 # 6
            wmu_faculty_inactive,                   # 7
            wmu_teacher_inactive,                   # 8
            wmu_student_inactive,                   # 9
            step_admin_inactive,                    # 10
            step_employee_inactive,                 # 11
            grad_apps_admin_inactive,               # 12
            grad_apps_committee_member_inactive,    # 13
        ]
        return (active_user_array, inactive_user_array)


def create_wmu_users(style, model_count):
    """
    Create WMU User models.
    """
    # Load preset fixtures.
    user_fixtures.create_wmu_users(style)

    # Set associated profile data for fixtures.
    # (This is generated automatically. We can't really fixture this.
    cae_center_number = PhoneNumber.from_string('+12692763283')
    cae_center_profile = models.Profile.get_profile('ceas_cae')
    cae_center_profile.phone_number = cae_center_number
    cae_center_profile.save()

    # Create random data generator.
    faker_factory = Faker()
    faker_factory.add_provider(E164Provider)

    # Create a WmuUser model for each test user we created.
    # Note we intentionally use an "invalid" winno here,
    # so we can easily tell which are our seeded/testing users and which might be "real" users.
    winno = 100
    user_list = models.User.objects.all()
    for user in user_list:

        # Skip for generated users that have no groups.
        user_groups = user.groups.values_list('name', flat=True)
        if user_groups.count() == 0:
            continue

        # Initialize seed data.
        first_name = user.first_name or faker_factory.first_name()
        last_name = user.last_name or faker_factory.last_name()
        winno += 1

        # Set user type based on group.
        if (
            'CAE Admin GA' in user_groups
            or 'CAE Admin' in user_groups
            or 'CAE Programmer' in user_groups
            or 'CAE Programmer GA' in user_groups
            or 'CAE Attendant' in user_groups
            or 'WMU Student' in user_groups
            or 'STEP Employee' in user_groups
        ):
            user_type = 0
        elif (
            'WMU Teacher' in user_groups
            or 'Grad Apps Committee Member' in user_groups
        ):
            user_type = 1
        elif (
            'CAE Director' in user_groups
            or 'CAE Building Coordinator' in user_groups
            or 'WMU Faculty' in user_groups
            or 'STEP Admin' in user_groups
            or 'Grad Apps Admin' in user_groups
        ):
            user_type = 2
        else:
            # Assume student for all others.
            user_type = 0

        # Attempt to generate models.
        try:
            with transaction.atomic():
                models.WmuUser.objects.create(
                    bronco_net=user.username,
                    winno=winno,
                    first_name=first_name,
                    last_name=last_name,
                    user_type=user_type,
                    is_active=user.is_active,
                )
        except (ValidationError, IntegrityError):
            print('ERROR generating WmuUser model seed for {0}'.format(user))

    # Count number of models already created.
    pre_initialized_count = len(models.WmuUser.objects.all())

    # Get all related models.
    majors = models.Major.objects.all()
    addresses = models.Address.objects.all()

    # Generate models equal to model count.
    total_fail_count = 0
    for i in range(model_count - pre_initialized_count):
        fail_count = 0
        try_create_model = True

        # Loop attempt until 3 fails or model is created.
        # Model creation may fail due to randomness of bronco_net and unique requirement.
        while try_create_model:
            # Generate bronco net.
            bronco_net = '{0}{1}{2}{3}'.format(
                chr(randint(97, 122)),
                chr(randint(97, 122)),
                chr(randint(97, 122)),
                randint(1000, 9999)
            )

            # Generate win number.
            winno = '{0}{1}'.format(randint(1000, 9999), randint(10000, 99999))

            # Generate user type.
            user_type = randint(0, (len(models.WmuUser.USER_TYPE_CHOICES) - 1))

            # Get address.
            index = randint(0, len(addresses) - 1)
            address = addresses[index]

            # Generate phone number.
            phone_number = faker_factory.safe_e164(region_code="US")

            # Determine if active. 70% change of being true.
            if randint(0, 9) < 7:
                is_active = True
            else:
                is_active = False

            # Attempt to create model seed.
            try:
                with transaction.atomic():
                    wmu_user = models.WmuUser.objects.create(
                        bronco_net=bronco_net,
                        winno=winno,
                        first_name=faker_factory.first_name(),
                        last_name=faker_factory.last_name(),
                        user_type=user_type,
                        is_active=is_active,
                    )

                    # Add between one and three majors to student.
                    major_count = randint(1, 3)
                    for x in range(major_count):
                        # Get Major.
                        index = randint(0, len(majors) - 1)
                        major = majors[index]

                        if is_active:
                            models.WmuUserMajorRelationship.objects.create(
                                wmu_user=wmu_user,
                                major=major,
                                is_active=is_active,
                            )
                        else:
                            models.WmuUserMajorRelationship.objects.create(
                                wmu_user=wmu_user,
                                major=major,
                                is_active=is_active,
                                date_stopped=timezone.now(),
                            )
                    user_profile = models.Profile.get_profile(bronco_net)
                    user_profile.address = address
                    user_profile.phone_number = phone_number
                    user_profile.save()

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
        # Handle for all models failing to seed.
        if total_fail_count == model_count:
            raise ValidationError('Failed to generate any Wmu User seed instances.')

        if total_fail_count >= (model_count / 2):
            # Handle for a majority of models failing to seed (at least half).
            stdout.write(style.ERROR(
                'Failed to generate {0}/{1} Wmu User seed instances.\n'.format(total_fail_count, model_count)
            ))
        else:
            # Handle for some models failing to seed (less than half, more than 0).
            stdout.write(style.WARNING(
                'Failed to generate {0}/{1} Wmu User seed instances.\n'.format(total_fail_count, model_count)
            ))

    stdout.write('Populated ' + style.SQL_FIELD('Wmu User') + ' models.\n')


def create_addresses(style, model_count):
    """
    Creates address models.
    """
    # Load preset fixtures.
    user_fixtures.create_addresses(style)

    # Create random data generator.
    faker_factory = Faker()

    # Count number of models already created.
    pre_initialized_count = len(models.Address.objects.all())

    # Generate models equal to model count.
    total_fail_count = 0
    for index in range(model_count - pre_initialized_count):
        fail_count = 0
        try_create_model = True

        # Loop attempt until 3 fails or model is created.
        # Model creation may fail due to randomness of address info and unique requirement.
        while try_create_model:
            # Generate address info.
            street = faker_factory.building_number() + ' ' + faker_factory.street_address()
            city = faker_factory.city()
            state = randint(0, 49)
            zip = faker_factory.postalcode()
            if faker_factory.boolean():
                optional_street = faker_factory.secondary_address()
            else:
                optional_street = None

            # Attempt to create model seed.
            try:
                models.Address.objects.create(
                    street=street,
                    optional_street=optional_street,
                    city=city,
                    state=state,
                    zip=zip
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
        # Handle for all models failing to seed.
        if total_fail_count == model_count:
            raise ValidationError('Failed to generate any Address seed instances.')

        if total_fail_count >= (model_count / 2):
            # Handle for a majority of models failing to seed (at least half).
            stdout.write(style.ERROR(
                'Failed to generate {0}/{1} Address seed instances.\n'.format(total_fail_count, model_count)
            ))
        else:
            # Handle for some models failing to seed (less than half, more than 0).
            stdout.write(style.WARNING(
                'Failed to generate {0}/{1} Address seed instances.\n'.format(total_fail_count, model_count)
            ))

    stdout.write('Populated ' + style.SQL_FIELD('Address') + ' models.\n')
