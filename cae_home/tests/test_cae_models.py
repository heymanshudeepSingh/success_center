"""
Tests for CAE Home CAE app Models.
"""

# System Imports.
from django.utils import timezone

# User Imports.
from .. import models
from cae_home.tests.utils import IntegrationTestCase


class SoftwareModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Software model creation/logic.
    """
    def setUp(self):
        self.test_software = models.Software.objects.create(
            name='Test Software',
            slug='test-software',
        )

    def test_model_creation(self):
        self.assertEqual(self.test_software.name, 'Test Software')
        self.assertEqual(self.test_software.slug, 'test-software')

    def test_string_representation(self):
        self.assertEqual(str(self.test_software), 'Test Software')

    def test_plural_representation(self):
        self.assertEqual(str(self.test_software._meta.verbose_name), 'Software')
        self.assertEqual(str(self.test_software._meta.verbose_name_plural), 'Software')


class SoftwareDetailModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Software Detail model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.software = models.Software.create_dummy_model()
        cls.expiration=timezone.datetime.strptime('2020-01-01', '%Y-%m-%d').date()

    def setUp(self):
        self.test_software_detail = models.SoftwareDetail.objects.create(
            software=self.software,
            version=5,
            expiration=self.expiration,
        )

    def test_model_creation(self):
        self.assertEqual(self.test_software_detail.software, self.software)
        self.assertEqual(self.test_software_detail.version, '5')
        self.assertEqual(self.test_software_detail.expiration, self.expiration)

    def test_string_representation(self):
        self.assertEqual(str(self.test_software_detail), 'Dummy Software - 5')

    def test_plural_representation(self):
        self.assertEqual(str(self.test_software_detail._meta.verbose_name), 'Software Detail')
        self.assertEqual(str(self.test_software_detail._meta.verbose_name_plural), 'Software Details')
