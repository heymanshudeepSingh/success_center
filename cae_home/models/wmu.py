"""
Definitions of "WMU" related Core Models.
"""

# System Imports.
import datetime, decimal
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
        super().save(*args, **kwargs)

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
        super().save(*args, **kwargs)

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
        super().save(*args, **kwargs)

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
                Q(room_type__slug='classroom')
                | Q(room_type__slug='computer-classroom')
                | Q(room_type__slug='department-office')
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
        help_text='Used for urls referencing this Major.',
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
        super().save(*args, **kwargs)

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


class WmuClass(models.Model):
    """
    A class to take at WMU.

    Note: We intentionally preface this with "Wmu" to prevent potential confusion with Python "class" namespacing.
    """
    # Relationship keys.
    department = models.ForeignKey('Department', on_delete=models.CASCADE)

    # Model fields.
    code = models.CharField(max_length=MAX_LENGTH, unique=True)
    title = models.CharField(max_length=MAX_LENGTH)
    description = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)

    # Self-setting/Non-user-editable fields.
    slug = models.SlugField(
        max_length=MAX_LENGTH,
        unique=True,
        help_text='Used for urls referencing this Class.',
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        ordering = ('pk',)

    def __str__(self):
        return '{0}'.format(self.code)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.

        Useful for when UnitTesting requires an instance of this model,
        but test does not care what values the model actually has.
        """
        # Define "dummy model" values.
        department = Department.create_dummy_model()
        code = 'D123'
        description = 'Dummy Description'

        # Attempt to get corresponding model instance, if there is one.
        try:
            wmu_class = WmuClass.objects.get(code=code)
        except WmuClass.DoesNotExist:
            # Instance not found. Create new model.
            wmu_class = WmuClass.objects.create(
                department=department,
                code=code,
                description=description,
                slug=slugify(code)
            )

        # Return "dummy model" instance.
        return wmu_class


class Semester(models.Model):
    """
    An instance of a semester for Wmu.
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
        super().save(*args, **kwargs)

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
            semester = Semester.objects.get(
                start_date=start_date,
                end_date=end_date,
            )
        except Semester.DoesNotExist:
            # Instance not found. Create new model.
            semester = Semester.objects.create(
                start_date=start_date,
                end_date=end_date,
            )

        # Return "dummy model" instance.
        return semester


class StudentHistory(models.Model):
    """
    A class to take at WMU.
    """
    # Relationship keys.
    wmu_user = models.ForeignKey('WmuUser', on_delete=models.CASCADE)

    # Model fields.
    bachelors_institution = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    bachelors_gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    masters_institution = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    masters_gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Student History'
        verbose_name_plural = 'Student History'
        ordering = ('pk',)

    def __str__(self):
        return '{0} Student History'.format(self.wmu_user)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.

        Useful for when UnitTesting requires an instance of this model,
        but test does not care what values the model actually has.
        """
        from cae_home.models import WmuUser

        # Define "dummy model" values.
        wmu_user = WmuUser.create_dummy_model()
        bachelors_institution = 'Dummy Bachelors Institution'
        masters_institution = 'Masters Bachelors Institution'
        bachelors_gpa = decimal.Decimal('3.33')
        masters_gpa = decimal.Decimal('0.00')

        # Attempt to get corresponding model instance, if there is one.
        try:
            student_history = StudentHistory.objects.get(wmu_user=wmu_user)
        except StudentHistory.DoesNotExist:
            # Instance not found. Create new model.
            student_history = StudentHistory.objects.create(
                wmu_user=wmu_user,
                bachelors_institution=bachelors_institution,
                masters_institution=masters_institution,
                bachelors_gpa=bachelors_gpa,
                masters_gpa=masters_gpa,
            )

        # Return "dummy model" instance.
        return student_history
