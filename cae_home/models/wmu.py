"""
General WMU models for CAE_Home App.
"""

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
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)

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

    def __str__(self):
        return '{0} - {1}'.format(self.code, self.name)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(Major, self).save(*args, **kwargs)


class Student(models.Model):
    """
    A student (or person with WMU ldap credentials) attending WMU.
    """
    # Relationship keys.
    major = models.ForeignKey(Major, on_delete=models.CASCADE)
    phone_number = models.ForeignKey('PhoneNumber', blank=True, null=True)

    # Model fields.
    winno = models.CharField(max_length=MAX_LENGTH)
    first_name = models.CharField(max_length=MAX_LENGTH)
    last_name = models.CharField(max_length=MAX_LENGTH)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(Student, self).save(*args, **kwargs)


class SemesterDate(models.Model):
    """
    The start and end dates for a semester.
    """
    # Model fields.
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

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(SemesterDate, self).save(*args, **kwargs)
