"""
Tests for CAE Home WMU app Models.
"""

# System Imports.
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

# User Class Imports.
from .. import models
from cae_home.tests.utils import IntegrationTestCase


class DepartmentModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Department model creation/logic.
    """
    def setUp(self):
        self.test_department = models.Department.objects.create(name='Test Department', slug='test-department')

    def test_model_creation(self):
        self.assertEqual(self.test_department.name, 'Test Department')

    def test_string_representation(self):
        self.assertEqual(str(self.test_department), self.test_department.name)

    def test_plural_representation(self):
        self.assertEqual(str(self.test_department._meta.verbose_name), 'Department')
        self.assertEqual(str(self.test_department._meta.verbose_name_plural), 'Departments')

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.Department.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.Department))

        # Test get.
        dummy_model_2 = models.Department.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.Department))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)


class RoomTypeModelTests(IntegrationTestCase):
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

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.RoomType.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.RoomType))

        # Test get.
        dummy_model_2 = models.RoomType.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.RoomType))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)


class RoomModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Room model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.room_type = models.RoomType.create_dummy_model()
        cls.department = models.Department.create_dummy_model()

    def setUp(self):
        self.test_room = models.Room.objects.create(
            name='Test Room',
            room_type=self.room_type,
            capacity=30,
            description='Test Room Description',
            slug='test-room',
        )
        self.test_room.department.add(self.department)
        self.test_room.save()

        self.departments_for_room = self.test_room.department.all()
        self.rooms_with_department = self.department.room_set.all()

    def test_model_creation(self):
        self.assertEqual(self.test_room.name, 'Test Room')
        self.assertEqual(self.test_room.room_type, self.room_type)
        self.assertEqual(self.departments_for_room[0], self.department)
        self.assertEqual(self.rooms_with_department[0], self.test_room)
        self.assertEqual(self.test_room.capacity, 30)
        self.assertEqual(self.test_room.description, 'Test Room Description')

    def test_string_representation(self):
        self.assertEqual(str(self.test_room), self.test_room.name)

    def test_plural_representation(self):
        self.assertEqual(str(self.test_room._meta.verbose_name), 'Room')
        self.assertEqual(str(self.test_room._meta.verbose_name_plural), 'Rooms')

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.Room.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.Room))

        # Test get.
        dummy_model_2 = models.Room.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.Room))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)


class MajorTests(IntegrationTestCase):
    """
    Tests to ensure valid Major model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.department = models.Department.create_dummy_model()

    def setUp(self):
        self.test_major = models.Major.objects.create(
            department=self.department,
            student_code='Test Student Code',
            program_code='Test Program Code',
            name='Test Name',
            degree_level=1,
            active=False,
            slug='test-code',
        )

    def test_model_creation(self):
        self.assertEqual(self.test_major.department, self.department)
        self.assertEqual(self.test_major.student_code, 'Test Student Code')
        self.assertEqual(self.test_major.program_code, 'Test Program Code')
        self.assertEqual(self.test_major.name, 'Test Name')
        self.assertEqual(self.test_major.degree_level, 1)
        self.assertEqual(self.test_major.active, False)

    def test_string_representation(self):
        self.assertEqual(str(self.test_major), 'Test Student Code - Test Name')

    def test_plural_representation(self):
        self.assertEqual(str(self.test_major._meta.verbose_name), 'Major')
        self.assertEqual(str(self.test_major._meta.verbose_name_plural), 'Majors')

    def test_get_degree_level_as_string(self):
        self.assertEqual(models.Major.get_degree_level_as_string(0), 'Unknown')
        self.assertEqual(models.Major.get_degree_level_as_string(1), 'Associates')
        self.assertEqual(models.Major.get_degree_level_as_string(2), 'Bachelors')
        self.assertEqual(models.Major.get_degree_level_as_string(3), 'Masters')
        self.assertEqual(models.Major.get_degree_level_as_string(4), 'Phd')

    def test_get_degree_level_as_int(self):
        self.assertEqual(models.Major.get_degree_level_as_int('Unknown'), 0)
        self.assertEqual(models.Major.get_degree_level_as_int('Associates'), 1)
        self.assertEqual(models.Major.get_degree_level_as_int('Bachelors'), 2)
        self.assertEqual(models.Major.get_degree_level_as_int('Masters'), 3)
        self.assertEqual(models.Major.get_degree_level_as_int('Phd'), 4)

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.Major.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.Major))

        # Test get.
        dummy_model_2 = models.Major.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.Major))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)


class SemesterDateModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Semester Date model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.end_date = timezone.localdate()
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
        self.assertEqual(
            str(self.test_semester_date),
            '{0}: {1} - {2}'.format(self.test_semester_date.name, self.start_date, self.end_date))

    def test_plural_representation(self):
        self.assertEqual(str(self.test_semester_date._meta.verbose_name), 'Semester Date')
        self.assertEqual(str(self.test_semester_date._meta.verbose_name_plural), 'Semester Dates')

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.SemesterDate.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.SemesterDate))

        # Test get.
        dummy_model_2 = models.SemesterDate.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.SemesterDate))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)

    def test_name_generation(self):
        # Test Spring.
        semester_date = models.SemesterDate.objects.create(
            start_date=timezone.datetime(2018, 1, 1),
            end_date=timezone.datetime(2018, 1, 2)
        )
        self.assertEqual(semester_date.name, 'Spring_2018')

        # Test Summer 1.
        semester_date = models.SemesterDate.objects.create(
            start_date=timezone.datetime(2018, 4, 1),
            end_date=timezone.datetime(2018, 4, 2)
        )
        self.assertEqual(semester_date.name, 'Summer_I_2018')

        # Test Summer 2.
        semester_date = models.SemesterDate.objects.create(
            start_date=timezone.datetime(2018, 6, 1),
            end_date=timezone.datetime(2018, 6, 2)
        )
        self.assertEqual(semester_date.name, 'Summer_II_2018')

        # Test Fall.
        semester_date = models.SemesterDate.objects.create(
            start_date=timezone.datetime(2018, 8, 1),
            end_date=timezone.datetime(2018, 8, 2)
        )
        self.assertEqual(semester_date.name, 'Fall_2018')

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
