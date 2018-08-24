"""
General WMU models for CAE_Home App.
"""

from django.core.exceptions import ValidationError
from django.db import models


MAX_LENGTH = 255


class Department(models.Model):
    """
    A university department.
    """
    # Model fields.
    name = models.CharField(max_length=MAX_LENGTH)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ('name',)

    def __str__(self):
        return '{0}'.format(self.name)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(Department, self).save(*args, **kwargs)


class RoomType(models.Model):
    """
    Room types.
    """
    # Model fields.
    name = models.CharField(
        max_length=MAX_LENGTH,
    )

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Room Type"
        verbose_name_plural = "Room Types"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(RoomType, self).save(*args, **kwargs)


class Room(models.Model):
    """
    A standard university room.
    """
    # Relationship keys.
    room_type = models.ForeignKey('RoomType', on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, blank=True, null=True)

    # Model fields.
    name = models.CharField(max_length=MAX_LENGTH)
    capacity = models.PositiveSmallIntegerField()

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
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


class Major(models.Model):
    """
    A major available at WMU.
    """
    # Model fields.
    code = models.CharField(max_length=MAX_LENGTH)
    name = models.CharField(max_length=MAX_LENGTH)
    undergrad = models.BooleanField(default=True)
    active = models.BooleanField(default=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Major"
        verbose_name_plural = "Majors"
        ordering = ('pk',)

    def __str__(self):
        return '{0} - {1}'.format(self.code, self.name)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(Major, self).save(*args, **kwargs)


class WmuUser(models.Model):
    """
    An entity with WMU ldap credentials. Generally will be a student, professor, or faculty.
    """
    # Preset field choices.
    STUDENT = 0
    PROFESSOR = 1
    FACULTY = 2
    USER_TYPE_CHOICES = (
        (STUDENT, 'Student'),
        (PROFESSOR, 'Professor'),
        (FACULTY, 'Faculty'),
    )

    # Relationship keys.
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    major = models.ForeignKey('Major', on_delete=models.CASCADE, blank=True)
    phone_number = models.ForeignKey('PhoneNumber', blank=True, null=True)

    # Model fields.
    bronco_net = models.CharField(max_length=MAX_LENGTH)
    winno = models.CharField(max_length=MAX_LENGTH)
    first_name = models.CharField(max_length=MAX_LENGTH)
    last_name = models.CharField(max_length=MAX_LENGTH)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=0)
    active = models.BooleanField(default=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "WMU User"
        verbose_name_plural = "WMU Users"

    def __str__(self):
        return '{0}: {1} {2}'.format(self.bronco_net, self.first_name, self.last_name)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(WmuUser, self).save(*args, **kwargs)

    def official_email(self):
        """
        Returns a string of student's official email.
        """
        return '{0}@wmich.edu'.format(self.bronco_net)


class SemesterDate(models.Model):
    """
    The start and end dates for a semester.
    """
    # Model fields.
    name = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Semester Date"
        verbose_name_plural = "Semester Dates"

    def __str__(self):
        return '{0} - {1}'.format(self.start_date, self.end_date)

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
