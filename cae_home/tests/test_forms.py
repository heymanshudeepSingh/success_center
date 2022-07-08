"""
Tests for CAE Home app Forms.
"""

# User Imports.
from .. import forms
from cae_home import models
from cae_home.tests.utils import IntegrationTestCase


class UserModelForm(IntegrationTestCase):
    """
    Tests to ensure valid User Model Form validation.
    """
    def test_valid_data(self):
        user = models.User.create_dummy_model()

        # Test form validity.
        form = forms.UserModelForm({
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }, instance=user)
        self.assertTrue(form.is_valid())

        # Test saved form values.
        saved_form = form.save()
        self.assertEqual(saved_form.username, user.username)
        self.assertEqual(saved_form.first_name, user.first_name)
        self.assertEqual(saved_form.last_name, user.last_name)

    def test_blank_data(self):
        form = forms.UserModelForm()
        self.assertFalse(form.is_valid())


class ProfileModelFormTests(IntegrationTestCase):
    """
    Tests to ensure valid Profile Model Form validation.
    """
    def test_valid_data_all(self):
        """
        Test form with all fields provided.
        """
        address = models.Address.create_dummy_model()
        site_theme = models.SiteTheme.create_dummy_model()
        phone_number = '2692763283'
        user_timezone = 'America/Detroit'
        font_size = 2
        color_black = '#000000'
        color_white = '#ffffff'

        # Test form validity.
        form = forms.ProfileModelForm({
            'address': address.pk,
            'phone_number': phone_number,
            'site_theme': site_theme.pk,
            'user_timezone': user_timezone,
            'desktop_font_size': font_size,
            'mobile_font_size': font_size,
            'fg_color': color_black,
            'bg_color': color_white,
        })
        self.assertTrue(form.is_valid())

        # Test saved form values.
        saved_form = form.save()
        self.assertEqual(saved_form.address, address)
        self.assertEqual(saved_form.site_theme, site_theme)
        self.assertEqual(saved_form.phone_number, phone_number)
        self.assertEqual(saved_form.user_timezone, user_timezone)
        self.assertEqual(saved_form.desktop_font_size, font_size)
        self.assertEqual(saved_form.mobile_font_size, font_size)
        self.assertEqual(saved_form.fg_color, color_black)
        self.assertEqual(saved_form.bg_color, color_white)

    def test_valid_data_min(self):
        """
        Test form with minimal fields provided.
        """
        site_theme = models.SiteTheme.create_dummy_model()
        user_timezone = 'America/Detroit'
        font_size = 2
        color_black = '#000000'
        color_white = '#ffffff'

        # Test form validity.
        form = forms.ProfileModelForm({
            'site_theme': site_theme.pk,
            'user_timezone': user_timezone,
            'desktop_font_size': font_size,
            'mobile_font_size': font_size,
            'fg_color': color_black,
            'bg_color': color_white,
        })
        self.assertTrue(form.is_valid())

        # Test saved form values.
        saved_form = form.save()
        self.assertEqual(saved_form.site_theme, site_theme)
        self.assertEqual(saved_form.user_timezone, user_timezone)
        self.assertEqual(saved_form.desktop_font_size, font_size)
        self.assertEqual(saved_form.mobile_font_size, font_size)
        self.assertEqual(saved_form.fg_color, color_black)
        self.assertEqual(saved_form.bg_color, color_white)

    def test_blank_data(self):
        form = forms.ProfileModelForm()
        self.assertFalse(form.is_valid())


class AddressModelFormTests(IntegrationTestCase):
    """
    Tests to ensure valid Address Model Form validation.
    """
    def test_valid_data(self):
        address = models.Address.create_dummy_model()

        # Test form validity.
        form = forms.AddressModelForm({
            'street': address.street,
            'city': address.city,
            'state': address.state,
            'zip': address.zip,
        })
        self.assertTrue(form.is_valid())

        # Test saved form values.
        saved_form = form.save()
        self.assertEqual(saved_form.street, address.street)
        self.assertEqual(saved_form.city, address.city)
        self.assertEqual(saved_form.state, address.state)
        self.assertEqual(saved_form.zip, address.zip)

    def test_blank_data(self):
        form = forms.AddressModelForm()
        self.assertFalse(form.is_valid())


class RoomModelFormTests(IntegrationTestCase):
    """
    Tests to ensure valid Room Model Form validation.
    """
    def test_valid_data(self):
        room = models.Room.create_dummy_model()
        department = room.department.first()

        # Test form validity.
        form = forms.RoomModelForm({
            'name': room.name,
            'department': [department.pk],
            'room_type': room.room_type.pk,
            'description': room.description,
            'capacity': room.capacity,
        }, instance=room)
        self.assertTrue(form.is_valid())

        # Test saved form values.
        saved_form = form.save()
        self.assertEqual(saved_form.name, room.name)
        self.assertEqual(saved_form.department.first(), department)
        self.assertEqual(saved_form.room_type, room.room_type)
        self.assertEqual(saved_form.description, room.description)
        self.assertEqual(saved_form.capacity, room.capacity)

    def test_blank_data(self):
        form = forms.RoomModelForm()
        self.assertFalse(form.is_valid())
