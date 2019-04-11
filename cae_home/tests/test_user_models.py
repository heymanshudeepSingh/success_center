"""
Tests for CAE_Home User Models.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase
from phonenumber_field.phonenumber import PhoneNumber

from .. import models


class UserIntermediaryModelTests(TestCase):
    """
    Tests to ensure valid UserIntermediary Model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.department = models.Department.objects.create(name='Department', slug='department')
        cls.major = models.Major.objects.create(
            department=cls.department,
            code='Test Code',
            name='Test Name',
            undergrad=False,
            active=False,
            slug='test-code'
        )
        cls.user_type = models.WmuUser.PROFESSOR

        # Set up for User model instance.
        cls.user_bronco_net = 'user_temporary'
        cls.user = get_user_model().objects.create_user(
            cls.user_bronco_net,
            '{0}@wmich.edu'.format(cls.user_bronco_net),
            cls.user_bronco_net,
        )

        # Set up for WmuUser model instance.
        cls.wmu_user_bronco_net = 'wmu_temporary'
        cls.wmu_user = models.WmuUser.objects.create(
            department=cls.department,
            major=cls.major,
            bronco_net=cls.wmu_user_bronco_net,
            winno=cls.wmu_user_bronco_net,
            first_name='Test First',
            last_name='Test Last',
            user_type=cls.user_type,
        )

        # Set up for instance with both User and WmuUser. User model created first.
        cls.dual_bronco_net_1 = 'dual_1_temporary'
        cls.dual_user_1 = get_user_model().objects.create_user(
            cls.dual_bronco_net_1,
            '{0}@wmich.edu'.format(cls.dual_bronco_net_1),
            cls.dual_bronco_net_1,
        )
        cls.dual_wmu_user_1 = models.WmuUser.objects.create(
            department=cls.department,
            major=cls.major,
            bronco_net=cls.dual_bronco_net_1,
            winno=cls.dual_bronco_net_1,
            first_name='Test First',
            last_name='Test Last',
            user_type=cls.user_type,
        )

        # Set up for instance with both User and WmuUser. WmuUser model created first.
        cls.dual_bronco_net_2 = 'dual_2_temporary'
        cls.dual_wmu_user_2 = models.WmuUser.objects.create(
            department=cls.department,
            major=cls.major,
            bronco_net=cls.dual_bronco_net_2,
            winno=cls.dual_bronco_net_2,
            first_name='Test First',
            last_name='Test Last',
            user_type=cls.user_type,
        )
        cls.dual_user_2 = get_user_model().objects.create_user(
            cls.dual_bronco_net_2,
            '{0}@wmich.edu'.format(cls.dual_bronco_net_2),
            cls.dual_bronco_net_2,
        )

    def setUp(self):
        # Set up for User model instance.
        self.test_intermediary_with_user = models.UserIntermediary.objects.get(user=self.user)
        self.profile_with_user = self.test_intermediary_with_user.profile

        # Set up for WmuUser model instance.
        self.test_intermediary_with_wmuuser = models.UserIntermediary.objects.get(wmu_user=self.wmu_user)
        self.profile_with_wmuuser = self.test_intermediary_with_wmuuser.profile

        # Set up for instance with both User and WmuUser. User model created first.
        self.test_intermediary_with_dual_1 = models.UserIntermediary.objects.get(user=self.dual_user_1)
        self.profile_with_dual_1 = self.test_intermediary_with_dual_1.profile

        # Set up for instance with both User and WmuUser. WmuUser model created first.
        self.test_intermediary_with_dual_2 = models.UserIntermediary.objects.get(wmu_user=self.dual_wmu_user_2)
        self.profile_with_dual_2 = self.test_intermediary_with_dual_2.profile

    def test_model_creation_with_user(self):
        with self.subTest('Test User Intermediary with User model.'):
            # Test User Intermediary model.
            self.assertEqual(self.test_intermediary_with_user.user, self.user)
            self.assertEqual(self.test_intermediary_with_user.profile, self.profile_with_user)
            self.assertEqual(self.test_intermediary_with_user.bronco_net, self.user_bronco_net)

            # Test related bronco_net integrity.
            self.assertEqual(self.user.username, self.user_bronco_net)
            self.assertEqual(self.profile_with_user.userintermediary.bronco_net, self.user_bronco_net)

        with self.subTest('Test User Intermediary with WmuUser model.'):
            # Test User Intermediary model.
            self.assertEqual(self.test_intermediary_with_wmuuser.wmu_user, self.wmu_user)
            self.assertEqual(self.test_intermediary_with_wmuuser.profile, self.profile_with_wmuuser)
            self.assertEqual(self.test_intermediary_with_wmuuser.bronco_net, self.wmu_user_bronco_net)

            # Test related bronco_net integrity.
            self.assertEqual(self.wmu_user.bronco_net, self.wmu_user_bronco_net)
            self.assertEqual(self.profile_with_wmuuser.userintermediary.bronco_net, self.wmu_user_bronco_net)

        with self.subTest('Test User Intermediary with both User and WmuUser. User model created first.'):
            # Test User Intermediary model.
            self.assertEqual(self.test_intermediary_with_dual_1.user, self.dual_user_1)
            self.assertEqual(self.test_intermediary_with_dual_1.wmu_user, self.dual_wmu_user_1)
            self.assertEqual(self.test_intermediary_with_dual_1.profile, self.profile_with_dual_1)
            self.assertEqual(self.test_intermediary_with_dual_1.bronco_net, self.dual_bronco_net_1)

            # Test related bronco_net integrity.
            self.assertEqual(self.dual_user_1.username, self.dual_bronco_net_1)
            self.assertEqual(self.dual_wmu_user_1.bronco_net, self.dual_bronco_net_1)
            self.assertEqual(self.profile_with_dual_1.userintermediary.bronco_net, self.dual_bronco_net_1)

        with self.subTest('Test User Intermediary with both User and WmuUser. WmuUser model created first.'):
            # Test User Intermediary model.
            self.assertEqual(self.test_intermediary_with_dual_2.user, self.dual_user_2)
            self.assertEqual(self.test_intermediary_with_dual_2.wmu_user, self.dual_wmu_user_2)
            self.assertEqual(self.test_intermediary_with_dual_2.profile, self.profile_with_dual_2)
            self.assertEqual(self.test_intermediary_with_dual_2.bronco_net, self.dual_bronco_net_2)

            # Test related bronco_net integrity.
            self.assertEqual(self.dual_user_2.username, self.dual_bronco_net_2)
            self.assertEqual(self.dual_wmu_user_2.bronco_net, self.dual_bronco_net_2)
            self.assertEqual(self.profile_with_dual_2.userintermediary.bronco_net, self.dual_bronco_net_2)

    def test_string_representation_with_user(self):
        self.assertEqual(str(self.test_intermediary_with_user), str(self.test_intermediary_with_user.bronco_net))

    def test_plural_representation(self):
        self.assertEqual(str(self.test_intermediary_with_user._meta.verbose_name), 'User Intermediary')
        self.assertEqual(str(self.test_intermediary_with_user._meta.verbose_name_plural), 'User Intermediaries')

    def test_field_removal(self):
        # Test that removing profile field creates error.
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                self.test_intermediary_with_user.profile = None
                self.test_intermediary_with_user.save()

        # Test that removing bronco_net field creates error.
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                self.test_intermediary_with_user.bronco_net = None
                self.test_intermediary_with_user.save()

        # Test that cannot remove user field when it's the only relation.
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                self.test_intermediary_with_user.user = None
                self.test_intermediary_with_user.save()

        # Test that cannot remove wmu_user field when it's the only relation.
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                self.test_intermediary_with_wmuuser.wmu_user = None
                self.test_intermediary_with_wmuuser.save()


class ProfileModelTests(TestCase):
    """
    Tests to ensure valid Profile Model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.bronco_net = 'temporary'
        cls.user = get_user_model().objects.create_user(
            cls.bronco_net,
            '{0}@wmich.edu'.format(cls.bronco_net),
            cls.bronco_net
        )
        cls.user_intermediary = models.UserIntermediary.objects.get(user=cls.user)
        cls.address = models.Address.objects.create(
            street="1234 TestStreet",
            city="Test City",
            state="Test Region",
            zip="Test Zip",
        )
        cls.phone_number = '+12693211234'
        cls.site_theme = models.SiteTheme.objects.get(pk=1)
        cls.user_timezone = 'America/Detroit'
        cls.font_size = models.Profile.FONT_BASE

    def setUp(self):
        self.test_profile = self.user_intermediary.profile
        self.test_profile.address = self.address
        self.test_profile.phone_number = PhoneNumber.from_string(self.phone_number)
        self.test_profile.save()

    def test_model_creation(self):
        # Test related models.
        self.assertEqual(self.user_intermediary.user, self.user)
        self.assertEqual(self.user_intermediary.profile, self.test_profile)
        self.assertEqual(self.user_intermediary.bronco_net, self.bronco_net)

        # Test Profile model.
        self.assertEqual(self.test_profile.address, self.address)
        self.assertEqual(self.test_profile.phone_number, self.phone_number)
        self.assertEqual(self.test_profile.site_theme, self.site_theme)
        self.assertEqual(self.test_profile.user_timezone, self.user_timezone)
        self.assertEqual(self.test_profile.desktop_font_size, self.font_size)
        self.assertEqual(self.test_profile.mobile_font_size, self.font_size)

    def test_string_representation(self):
        self.assertEqual(str(self.test_profile), self.test_profile.userintermediary.bronco_net)

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


class SiteThemeModelTests(TestCase):
    """
    Tests to ensure valid Site Theme Model creation/logic.
    """
    def setUp(self):
        self.test_theme = models.SiteTheme.objects.create(
            name='Test Theme',
            gold_logo=False,
            slug='test-theme',
        )

    def test_model_creation(self):
        self.assertEqual(self.test_theme.name, 'Test Theme')
        self.assertEqual(self.test_theme.gold_logo, False)

    def test_string_representation(self):
        self.assertEqual(str(self.test_theme), self.test_theme.name.capitalize())

    def test_plural_representation(self):
        self.assertEqual(str(self.test_theme._meta.verbose_name), 'Site Theme')
        self.assertEqual(str(self.test_theme._meta.verbose_name_plural), 'Site Themes')
