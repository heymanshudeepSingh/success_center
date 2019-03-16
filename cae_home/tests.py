"""
Tests for CAE_Home App.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from . import models


#region Model Tests

#region User Model Tests

class ProfileModelTests(TestCase):
    """
    Tests to ensure valid Profile Model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        cls.address = models.Address.objects.create(
            street="1234 TestStreet",
            city="Test City",
            state="Test Region",
            zip="Test Zip",
        )
        cls.phone_number = models.PhoneNumber.objects.create(phone_number='1234567890')
        cls.site_theme = models.SiteTheme.objects.get(pk=1)
        cls.user_timezone = 'America/Detroit'
        cls.font_size = models.Profile.FONT_BASE

    def setUp(self):
        self.test_profile = models.Profile.objects.get(user=self.user)
        self.test_profile.address = self.address
        self.test_profile.save()

    def test_model_creation(self):
        self.assertEqual(self.test_profile.user, self.user)
        self.assertEqual(self.test_profile.address, self.address)
        self.assertEqual(self.test_profile.site_theme, self.site_theme)
        self.assertEqual(self.test_profile.user_timezone, self.user_timezone)
        self.assertEqual(self.test_profile.desktop_font_size, self.font_size)
        self.assertEqual(self.test_profile.mobile_font_size, self.font_size)

    def test_string_representation(self):
        self.assertEqual(str(self.test_profile), str(self.test_profile.user))

    def test_plural_representation(self):
        self.assertEqual(str(self.test_profile._meta.verbose_name), 'Profile')
        self.assertEqual(str(self.test_profile._meta.verbose_name_plural), 'Profiles')


class AddressModelTests(TestCase):
    """
    Tests to ensure valid Address Model creation/logic.
    """
    def setUp(self):
        self.test_address = models.Address.objects.create(
            street="1234 TestStreet",
            optional_street="Test Apt",
            city="Test City",
            state="Test State",
            zip="Test Zip",
        )

    def test_model_creation(self):
        self.assertEqual(self.test_address.street, '1234 TestStreet')
        self.assertEqual(self.test_address.optional_street, 'Test Apt')
        self.assertEqual(self.test_address.city, 'Test City')
        self.assertEqual(self.test_address.state, 'Test State')
        self.assertEqual(self.test_address.zip, 'Test Zip')

    def test_string_representation(self):
        self.assertEqual(str(self.test_address),
                         (self.test_address.street + " " + self.test_address.optional_street +
                          " " + self.test_address.city + ", " + self.test_address.state +
                          ", " + self.test_address.zip))

    def test_plural_representation(self):
        self.assertEqual(str(self.test_address._meta.verbose_name), 'Address')
        self.assertEqual(str(self.test_address._meta.verbose_name_plural), 'Addresses')


class PhoneNumberModelTests(TestCase):
    """
    Tests to ensure valid Phone Number Model creation/logic.
    """
    def setUp(self):
        self.test_phone = models.PhoneNumber.objects.create(
            phone_number='1234567890',
        )

    def test_model_creation(self):
        self.assertEqual(self.test_phone.phone_number, '1234567890')

    def test_string_representation(self):
        self.assertEqual(str(self.test_phone), self.test_phone.phone_number)

    def test_plural_representation(self):
        self.assertEqual(str(self.test_phone._meta.verbose_name), 'Phone Number')
        self.assertEqual(str(self.test_phone._meta.verbose_name_plural), 'Phone Numbers')

    def test_invalid_numbers(self):
        with self.assertRaises(ValidationError):
            models.PhoneNumber.objects.create(phone_number='123456789')
        with self.assertRaises(ValidationError):
            models.PhoneNumber.objects.create(phone_number='9876543210987654')

class SiteThemeModelTests(TestCase):
    """
    Tests to ensure valid Site Theme Model creation/logic.
    """
    def setUp(self):
        self.test_theme = models.SiteTheme.objects.create(
            name='Test Theme',
            gold_logo=False,
        )

    def test_model_creation(self):
        self.assertEqual(self.test_theme.name, 'Test Theme')
        self.assertEqual(self.test_theme.gold_logo, False)

    def test_string_representation(self):
        self.assertEqual(str(self.test_theme), self.test_theme.name.capitalize())

    def test_plural_representation(self):
        self.assertEqual(str(self.test_theme._meta.verbose_name), 'Site Theme')
        self.assertEqual(str(self.test_theme._meta.verbose_name_plural), 'Site Themes')

#endregion User Model Tests


#region WMU Model Tests

class DepartmentModelTests(TestCase):
    """
    Tests to ensure valid Department model creation/logic.
    """
    def setUp(self):
        self.test_department = models.Department.objects.create(name='Test Department')

    def test_model_creation(self):
        self.assertEqual(self.test_department.name, 'Test Department')

    def test_string_representation(self):
        self.assertEqual(str(self.test_department), self.test_department.name)

    def test_plural_representation(self):
        self.assertEqual(str(self.test_department._meta.verbose_name), 'Department')
        self.assertEqual(str(self.test_department._meta.verbose_name_plural), 'Departments')


class RoomTypeModelTests(TestCase):
    """
    Tests to ensure valid Room Type model creation/logic.
    """
    def setUp(self):
        self.test_room_type = models.RoomType.objects.create(name="Test Room Type", slug='test-room-type')

    def test_model_creation(self):
        self.assertEqual(self.test_room_type.name, "Test Room Type")

    def test_string_representation(self):
        self.assertEqual(str(self.test_room_type), 'Test Room Type')

    def test_plural_representation(self):
        self.assertEqual(str(self.test_room_type._meta.verbose_name), 'Room Type')
        self.assertEqual(str(self.test_room_type._meta.verbose_name_plural), 'Room Types')


class RoomModelTests(TestCase):
    """
    Tests to ensure valid Room model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.room_type = models.RoomType.objects.create(name="Test Room Type", slug='test-room-type')
        cls.department = models.Department.objects.create(name='Department')

    def setUp(self):
        self.test_room = models.Room.objects.create(
            name='Test Room',
            room_type=self.room_type,
            department=self.department,
            capacity=30,
            description="Test Room Description",
        )

    def test_model_creation(self):
        self.assertEqual(self.test_room.name, 'Test Room')
        self.assertEqual(self.test_room.room_type, self.room_type)
        self.assertEqual(self.test_room.department, self.department)
        self.assertEqual(self.test_room.capacity, 30)

    def test_string_representation(self):
        self.assertEqual(str(self.test_room), self.test_room.name)

    def test_plural_representation(self):
        self.assertEqual(str(self.test_room._meta.verbose_name), 'Room')
        self.assertEqual(str(self.test_room._meta.verbose_name_plural), 'Rooms')


class MajorTests(TestCase):
    """
    Tests to ensure valid Major model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.department = models.Department.objects.create(name='Department')

    def setUp(self):
        self.test_major = models.Major.objects.create(
            department=self.department,
            code='Test Code',
            name='Test Name',
            undergrad=False,
            active=False,
        )

    def test_model_creation(self):
        self.assertEqual(self.test_major.department, self.department)
        self.assertEqual(self.test_major.code, 'Test Code')
        self.assertEqual(self.test_major.name, 'Test Name')
        self.assertEqual(self.test_major.undergrad, False)
        self.assertEqual(self.test_major.active, False)

    def test_string_representation(self):
        self.assertEqual(str(self.test_major), 'Test Code - Test Name')

    def test_plural_representation(self):
        self.assertEqual(str(self.test_major._meta.verbose_name), 'Major')
        self.assertEqual(str(self.test_major._meta.verbose_name_plural), 'Majors')


class SemesterDateModelTests(TestCase):
    """
    Tests to ensure valid Semester Date model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.end_date = timezone.now().date()
        cls.start_date = cls.end_date - timezone.timedelta(days=90)

    def setUp(self):
        self.test_semester_date = models.SemesterDate.objects.create(
            start_date=self.start_date,
            end_date=self.end_date,
        )

    def test_model_creation(self):
        self.assertEqual(self.test_semester_date.start_date, self.start_date)
        self.assertEqual(self.test_semester_date.end_date, self.end_date)

    def test_string_representation(self):
        self.assertEqual(str(self.test_semester_date), str(self.start_date) + ' - ' + str(self.end_date))

    def test_plural_representation(self):
        self.assertEqual(str(self.test_semester_date._meta.verbose_name), 'Semester Date')
        self.assertEqual(str(self.test_semester_date._meta.verbose_name_plural), 'Semester Dates')

    def test_name_generation(self):
        # Test Spring.
        semester_date = models.SemesterDate.objects.create(
            start_date=timezone.datetime(2017, 1, 1),
            end_date=timezone.datetime(2017, 1, 2)
        )
        self.assertEqual(semester_date.name, 'Spring_2017')

        # Test Summer 1.
        semester_date = models.SemesterDate.objects.create(
            start_date=timezone.datetime(2018, 4, 1),
            end_date=timezone.datetime(2018, 4, 2)
        )
        self.assertEqual(semester_date.name, 'Summer_I_2018')

        # Test Summer 2.
        semester_date = models.SemesterDate.objects.create(
            start_date=timezone.datetime(2019, 6, 1),
            end_date=timezone.datetime(2019, 6, 2)
        )
        self.assertEqual(semester_date.name, 'Summer_II_2019')

        # Test Fall.
        semester_date = models.SemesterDate.objects.create(
            start_date=timezone.datetime(2020, 8, 1),
            end_date=timezone.datetime(2020, 8, 2)
        )
        self.assertEqual(semester_date.name, 'Fall_2020')

    def test_start_date_before_end_date(self):
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.SemesterDate.objects.create(start_date=self.start_date, end_date=self.start_date)

        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.SemesterDate.objects.create(
                    start_date=self.start_date,
                    end_date=self.start_date - timezone.timedelta(days=1)
                )


class WmuUserTests(TestCase):
    """
    Tests to ensure valid WMU User model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.department = models.Department.objects.create(name='Test Department')
        cls.major = models.Major.objects.create(
            department=cls.department,
            code='Test Code',
            name='Test Name',
            undergrad=False,
            active=False,
        )
        cls.phone_number = models.PhoneNumber.objects.create(
            phone_number='1234567890',
        )
        cls.user_type = models.WmuUser.PROFESSOR

    def setUp(self):
        self.test_wmu_user = models.WmuUser.objects.create(
            department=self.department,
            major=self.major,
            phone_number=self.phone_number,
            bronco_net='abc1234',
            winno='123456789',
            first_name='Test First',
            last_name='Test Last',
            user_type=self.user_type,
        )

    def test_model_creation(self):
        self.assertEqual(self.test_wmu_user.department, self.department)
        self.assertEqual(self.test_wmu_user.major, self.major)
        self.assertEqual(self.test_wmu_user.phone_number, self.phone_number)
        self.assertEqual(self.test_wmu_user.bronco_net, 'abc1234')
        self.assertEqual(self.test_wmu_user.winno, '123456789')
        self.assertEqual(self.test_wmu_user.first_name, 'Test First')
        self.assertEqual(self.test_wmu_user.last_name, 'Test Last')
        self.assertEqual(self.test_wmu_user.user_type, self.user_type)

    def test_string_representation(self):
        self.assertEqual(str(self.test_wmu_user), 'abc1234: Test First Test Last')

    def test_plural_representation(self):
        self.assertEqual(str(self.test_wmu_user._meta.verbose_name), 'WMU User')
        self.assertEqual(str(self.test_wmu_user._meta.verbose_name_plural), 'WMU Users')

#endregion WMU Model Tests


#region CAE Model Tests

class AssetModelTests(TestCase):
    """
    Tests to ensure valid Room model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.room_type = models.RoomType.objects.create(name="Test Room Type", slug='test-room-type')
        cls.department = models.Department.objects.create(name='Department')
        cls.room = models.Room.objects.create(
            name='Test Room',
            room_type=cls.room_type,
            department=cls.department,
            capacity=30,
            description="Test Room Description",
        )

    def setUp(self):
        self.test_asset = models.Asset.objects.create(
            room=self.room,
            serial_number='Test Serial',
            asset_tag='Test Tag',
            brand_name='Test Brand',
            mac_address='F0:E1:D2:C3:B4:A5',
            ip_address='192.168.0.1',
            device_name='Test Name',
            description='Test Description',
        )

    def test_model_creation(self):
        self.assertEqual(self.test_asset.room, self.room)
        self.assertEqual(self.test_asset.serial_number, 'Test Serial')
        self.assertEqual(self.test_asset.asset_tag, 'Test Tag')
        self.assertEqual(self.test_asset.brand_name, 'Test Brand')
        self.assertEqual(self.test_asset.mac_address, 'F0:E1:D2:C3:B4:A5')
        self.assertEqual(self.test_asset.ip_address, '192.168.0.1')
        self.assertEqual(self.test_asset.device_name, 'Test Name')
        self.assertEqual(self.test_asset.description, 'Test Description')

    def test_string_representation(self):
        self.assertEqual(str(self.test_asset), 'Test Room Test Brand - Test Tag - Test Serial')

    def test_plural_representation(self):
        self.assertEqual(str(self.test_asset._meta.verbose_name), 'Asset')
        self.assertEqual(str(self.test_asset._meta.verbose_name_plural), 'Assets')

#endregion CAE Model Tests

#endregion Model Tests


#region View Tests

class HomeViewTests(TestCase):
    """
    Tests to ensure views load as expected.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site_theme = models.SiteTheme.objects.create(name='wmu')

    def test_index(self):
        """
        Tests the core index of the site.
        This should only be accessible in development environments.
        """
        # Page refers to dev-only urls. Thus only test in development environments.
        if settings.DEV_URLS:
            response = self.client.get(reverse('cae_home:index'))
            self.assertEqual(response.status_code, 200)

    def test_internal_dev_index(self):
        """
        Test the internal (cae_home) index page.
        This should only be accessible in development environments.
        """
        if settings.DEV_URLS:
            response = self.client.get(reverse('cae_home:internal_dev_index'))
            self.assertEqual(response.status_code, 200)

    def test_external_dev_index(self):
        """
        Test the external (wmu) index page.
        This should only be accessible in development environments.
        """
        if settings.DEV_URLS:
            response = self.client.get(reverse('cae_home:external_dev_index'))
            self.assertEqual(response.status_code, 200)

#endregion View Tests
