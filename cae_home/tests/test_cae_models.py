"""
Tests for CAE Home CAE app Models.
"""

# System Imports.

# User Imports.
from .. import models
from cae_home.tests.utils import IntegrationTestCase


class SoftwareModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Software model creation/logic.
    """
    def setUp(self):
        self.test_software = models.Software.objects.create(name='Test Software')

    def test_model_creation(self):
        self.assertEqual(self.test_software.name, 'Test Software')

    def test_string_representation(self):
        self.assertEqual(str(self.test_software), 'Test Software')

    def test_plural_representation(self):
        self.assertEqual(str(self.test_software._meta.verbose_name), 'Software')
        self.assertEqual(str(self.test_software._meta.verbose_name_plural), 'Software')
