"""
Definitions of "WMU" related Core Models.
"""

# System Imports.
import datetime
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.text import slugify


MAX_LENGTH = 255


class Department(models.Model):
    """
    A university department.
    """
    # Model fields.
    name = models.CharField(max_length=MAX_LENGTH, unique=True)

    # Self-setting/Non-user-editable fields.
    slug = models.SlugField(
        max_length=MAX_LENGTH,
        unique=True,
        help_text='Used for urls referencing this Department.',
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ('pk',)

    def __str__(self):
        return '{0}'.format(self.name)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(Department, self).save(*args, **kwargs)

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.

        Useful for when UnitTesting requires an instance of this model,
        but test does not care what values the model actually has.
        """
        # Define "dummy model" values.
        name = 'Dummy Department'
        slug = slugify(name)

        # Attempt to get corresponding model instance, if there is one.
        try:
            department = Department.objects.get(
                name=name,
                slug=slug,
            )
        except Department.DoesNotExist:
            # Instance not found. Create new model.
            department = Department.objects.create(
                name=name,
                slug=slug,
            )

        # Return "dummy model" instance.
        return department

class RoomType(models.Model):
    """
    University room types.
    """
    # Model fields.
    name = models.CharField(max_length=MAX_LENGTH, unique=True)

    # Self-setting/Non-user-editable fields.
    slug = models.SlugField(
        max_length=MAX_LENGTH,
        unique=True,
        help_text='Used for urls referencing this Room Type.',
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Room Type'
        verbose_name_plural = 'Room Types'
        ordering = ('pk',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(RoomType, self).save(*args, **kwargs)

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.

        Useful for when UnitTesting requires an instance of this model,
        but test does not care what values the model actually has.
        """
        # Define "dummy model" values.
        name = 'Dummy Room Type'
        slug = slugify(name)

        # Attempt to get corresponding model instance, if there is one.
        try:
            room_type = RoomType.objects.get(
                name=name,
                slug=slug,
            )
        except RoomType.DoesNotExist:
            # Instance not found. Create new model.
            room_type = RoomType.objects.create(
                name=name,
                slug=slug,
            )

        # Return "dummy model" instance.
        return room_type


# class RoomManager(models.Manager):
#     """
#     Room Model Manager used by models that have a room foreign key and need
#     to serialize the data to show foreign keys.
#     """
#     def get_by_natural_key(self, name):
#         return self.get(name=name)


class Room(models.Model):
    """
    A standard university room.
    """
    # objects = RoomManager()  # For serializing of foreign keys

    # Relationship keys.
    department = models.ManyToManyField('Department', blank=True)
    room_type = models.ForeignKey('RoomType', on_delete=models.CASCADE)

    # Model fields.
    name = models.CharField(max_length=MAX_LENGTH, unique=True)
    description = models.CharField(max_length=MAX_LENGTH, default='', blank=True)
    capacity = models.PositiveSmallIntegerField(default=0)
    is_row = models.BooleanField(null=True)

    # Self-setting/Non-user-editable fields.
    slug = models.SlugField(
        max_length=MAX_LENGTH,
        unique=True,
        help_text='Used for urls referencing this Room.',
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def natural_key(self):
        return self.name

    class Meta:
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        ordering = ('name',)

    def __str__(self):
        return '{0}'.format(self.name)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(Room, self).save(*args, **kwargs)

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.

        Useful for when UnitTesting requires an instance of this model,
        but test does not care what values the model actually has.
        """
        # Define "dummy model" values.
        name = 'Dummy Room'
        slug = slugify(name)
        department = Department.create_dummy_model()
        room_type = RoomType.create_dummy_model()

        # Attempt to get corresponding model instance, if there is one.
        try:
            room = Room.objects.get(
                name=name,
                slug=slug,
                department=department,
                room_type=room_type,
                is_row=False,
            )
        except Room.DoesNotExist:
            # Instance not found. Create new model.
            room = Room.objects.create(
                name=name,
                slug=slug,
                room_type=room_type,
                is_row=False,
            )

            # Add corresponding Department model relation.
            room.department.add(department)
            room.save()

        # Return "dummy model" instance.
        return room

    @staticmethod
    def get_cae_center_rooms():
        """
        Returns only computer labs/computer classrooms associated with the "CAE Center" department.
        :return: The list of CAE Center labs.
        """
        cae_lab_query = (
            (
                Q(room_type__slug='classroom') | Q(room_type__slug='computer-classroom') |
                Q(room_type__slug='department-office')
            )
            & Q(department__slug='cae-center')
        )
        return Room.objects.filter(cae_lab_query)


class Major(models.Model):
    """
    A major available at WMU.
    """
    # Preset field choices.
    UNKNOWN = 0
    ASSOCIATES = 1
    BACHELORS = 2
    MASTERS = 3
    PHD = 4
    DEGREE_LEVEL_CHOICES = (
        (UNKNOWN, 'Unknown'),
        (ASSOCIATES, 'Associates'),
        (BACHELORS, 'Bachelors'),
        (MASTERS, 'Masters'),
        (PHD, 'Phd'),
    )

    # Relationship keys.
    department = models.ForeignKey('Department', on_delete=models.CASCADE, default=1)

    # Model fields.
    student_code = models.CharField(max_length=MAX_LENGTH, unique=True)
    program_code = models.CharField(max_length=MAX_LENGTH, unique=True)
    name = models.CharField(max_length=MAX_LENGTH)
    degree_level = models.SmallIntegerField(choices=DEGREE_LEVEL_CHOICES, blank=True, default=0)
    is_active = models.BooleanField(default=True)

    # Self-setting/Non-user-editable fields.
    slug = models.SlugField(
        max_length=MAX_LENGTH,
        unique=True,
        help_text="Used for urls referencing this Major.",
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Major'
        verbose_name_plural = 'Majors'
        ordering = ('pk',)

    def __str__(self):
        return '{0} - {1}'.format(self.student_code, self.name)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(Major, self).save(*args, **kwargs)

    @staticmethod
    def get_degree_level_as_string(value):
        """
        Returns text description for degree level options.
        """
        if value == 1:
            return 'Associates'
        elif value == 2:
            return 'Bachelors'
        elif value == 3:
            return 'Masters'
        elif value == 4:
            return 'Phd'
        else:
            return 'Unknown'

    @staticmethod
    def get_degree_level_as_int(value):
        """
        Returns int value for degree level options.
        """
        value = str(value).capitalize()

        if value == 'Associates':
            return 1
        elif value == 'Bachelors':
            return 2
        elif value == 'Masters':
            return 3
        elif value == 'Phd':
            return 4
        else:
            return 0

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.

        Useful for when UnitTesting requires an instance of this model,
        but test does not care what values the model actually has.
        """
        # Define "dummy model" values.
        department = Department.create_dummy_model()
        code = 'dummy'
        slug = slugify(code)
        name = 'Dummy Major'

        # Attempt to get corresponding model instance, if there is one.
        try:
            major = Major.objects.get(
                student_code=code,
                program_code=code,
                slug=slug,
                name=name,
                department=department,
            )
        except Major.DoesNotExist:
            # Instance not found. Create new model.
            major = Major.objects.create(
                student_code=code,
                program_code=code,
                slug=slug,
                name=name,
                department=department,
            )

        # Return "dummy model" instance.
        return major


class SemesterDate(models.Model):
    """
    The start and end dates for a semester.
    """
    # Model fields.
    name = models.CharField(max_length=MAX_LENGTH, blank=True, null=True, unique=True)
    start_date = models.DateField(unique=True)
    end_date = models.DateField(unique=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Semester Date'
        verbose_name_plural = 'Semester Dates'

    def __str__(self):
        return '{0}: {1} - {2}'.format(self.name, self.start_date, self.end_date)

    def clean(self, *args, **kwargs):
        """
        Custom cleaning implementation. Includes validation, setting fields, etc.
        """
        # First check that dates exist at all.
        if self.start_date is not None and self.end_date is not None:

            # Calculate name based off of date fields.
            # Only set if model is new (in case of name calculation errors from abnormal semester dates).
            if self.pk is None:
                start_month = self.start_date.month
                if start_month < 4:
                    season = 'Spring_'
                elif start_month < 6:
                    season = 'Summer_I_'
                elif start_month < 8:
                    season = 'Summer_II_'
                else:
                    season = 'Fall_'

                self.name = '{0}{1}'.format(season, self.end_date.year)

            # Ensure that start date is not after end date.
            if self.start_date >= self.end_date:
                raise ValidationError('Start date must be before end date.')

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(SemesterDate, self).save(*args, **kwargs)

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.

        Useful for when UnitTesting requires an instance of this model,
        but test does not care what values the model actually has.
        """
        # Define "dummy model" values.
        start_date = datetime.datetime.strptime('2010 01 01', '%Y %m %d')
        end_date = datetime.datetime.strptime('2010 04 01', '%Y %m %d')

        # Attempt to get corresponding model instance, if there is one.
        try:
            semester_date = SemesterDate.objects.get(
                start_date=start_date,
                end_date=end_date,
            )
        except SemesterDate.DoesNotExist:
            # Instance not found. Create new model.
            semester_date = SemesterDate.objects.create(
                start_date=start_date,
                end_date=end_date,
            )

        # Return "dummy model" instance.
        return semester_date
