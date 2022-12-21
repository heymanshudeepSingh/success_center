"""
Models for Success Center Core app.
"""

# System Imports.
from django.db import models

# User Imports.
from cae_home import models as cae_home_models
from django.utils import timezone

class StudentUsageLog(models.Model):
    """
    An instance of a student using the Success Center resources.
    """
    # Relationship keys.
    student = models.ForeignKey(cae_home_models.WmuUser, on_delete=models.CASCADE)
    location = models.ForeignKey('TutorLocations', on_delete=models.SET_NULL, blank=True, null=True)

    # Model fields.
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(blank=True, null=True)
    approved = models.BooleanField(default=False)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Student Usage Log'
        verbose_name_plural = 'Student Usage Logs'

    def __str__(self):
        return '{0} - {1} - {2} to {3} - {4}'.format(self.student, self.location, self.check_in, self.check_out, self.approved)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def getLocationName(self):
        return self.location.location_name

    # Nihal: Find time values that are greater then 10 hours: This method is needed for highlighting red text for the
    # students who forgot to clock out
    @property
    def if_data_greater_than_hours(self):
        if self.check_out is not None:
            try:
                time_threshold = self.check_out - self.check_in
                return time_threshold >= timezone.timedelta(hours=9)
            except TimeoutError:
                self.check_out = "In Progress"


class TutorLocations(models.Model):
    """
    Locations for tutoring centers.
    """
    # Model fields.
    location_name = models.CharField(blank=True, null=True, max_length=80)
    room_number = models.CharField(blank=True, null=True, max_length=10)
    is_active = models.BooleanField(default=True)
    is_event = models.BooleanField(default=False)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tutor Location'
        verbose_name_plural = 'Tutor Locations'

    def __str__(self):
        return '{0}'.format(self.location_name)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super().save(*args, **kwargs)


class SuccessCtrProfile(models.Model):
    """
    Settings for the current user, pertaining to SuccessCtr.
    Directly relates to the CaeHome User Profile model.
    """
    profile = models.OneToOneField(cae_home_models.Profile, on_delete=models.CASCADE)
    default_tutor_location = models.ForeignKey('TutorLocations', on_delete=models.CASCADE, blank=True, null=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'SuccessCenter User Profile'
        verbose_name_plural = 'SuccessCenter User Profiles'

    def __str__(self):
        return '{0}'.format(self.profile)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super().save(*args, **kwargs)
