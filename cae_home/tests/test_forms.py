"""
Tests for CAE Home Forms.
"""

from .. import forms
from cae_home.tests.utils import IntegrationTestCase


class AddressFormTests(IntegrationTestCase):
    """
    Tests to ensure valid Address Form validation.
    """
    def test_valid_data(self):
        form = forms.AddressForm({
            'street': '1234 Test Street',
            'city': 'Test City',
            'state': 3,
            'zip': 12345,
        })
        self.assertTrue(form.is_valid())

        address = form.save()
        self.assertEqual(address.street, '1234 Test Street')
        self.assertEqual(address.city, 'Test City')
        self.assertEqual(address.state, 3)
        self.assertEqual(address.zip, '12345')

    def test_blank_data(self):
        form = forms.AddressForm()
        self.assertFalse(form.is_valid())
