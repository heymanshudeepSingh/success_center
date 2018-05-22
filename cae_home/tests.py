"""
Tests for CAE_Home App.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from . import models


#region Model Tests

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

    def setUp(self):
        self.test_profile = models.Profile.objects.get(user=self.user)
        self.test_profile.address = self.address
        self.test_profile.save()

    def test_model_creation(self):
        self.assertEqual(self.test_profile.user, self.user)
        self.assertEqual(self.test_profile.address, self.address)

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

#endregion Model Tests


#region View Tests

class HomeViewTests(TestCase):
    """
    Tests to ensure views load as expected.
    """
    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

#endregion View Tests