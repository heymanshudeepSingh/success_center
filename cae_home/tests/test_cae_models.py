"""
Tests for CAE Home CAE app Models.
"""

# System Imports.
from django.utils import timezone
from django.utils.text import slugify

# User Imports.
from .. import models
from cae_home.tests.utils import IntegrationTestCase


class SoftwareModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Software model creation/logic.
    """
    def setUp(self):
        """
        Logic to reset state before each individual test.
        """
        # Call parent logic.
        super().setUp()

        self.software_name = 'Test Software'
        self.test_software = models.Software.objects.create(
            name=self.software_name,
            slug=slugify(self.software_name),
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
        """
        Logic to initialize model/testing variable data.
        This is run exactly once, before any class tests are run.
        """
        # Call parent logic.
        super().setUpTestData()

        cls.software = models.Software.create_dummy_model()
        cls.expiration=timezone.datetime.strptime('2020-01-01', '%Y-%m-%d').date()

    def setUp(self):
        """
        Logic to reset state before each individual test.
        """
        # Call parent logic.
        super().setUp()

        self.software_version = 5
        self.test_software_detail = models.SoftwareDetail.objects.create(
            software=self.software,
            version=self.software_version,
            expiration=self.expiration,
            slug='{0}-{1}'.format(slugify(self.software.name), self.software_version)
        )

    def test_model_creation(self):
        self.assertEqual(self.test_software_detail.software, self.software)
        self.assertEqual(self.test_software_detail.version, str(self.software_version))
        self.assertEqual(self.test_software_detail.expiration, self.expiration)
        self.assertEqual(self.test_software_detail.slug, 'dummy-software-5')

    def test_string_representation(self):
        self.assertEqual(str(self.test_software_detail), 'Dummy Software - 5')

    def test_plural_representation(self):
        self.assertEqual(str(self.test_software_detail._meta.verbose_name), 'Software Detail')
        self.assertEqual(str(self.test_software_detail._meta.verbose_name_plural), 'Software Details')
