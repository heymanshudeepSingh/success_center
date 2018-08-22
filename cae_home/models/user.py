"""
User models for CAE_Home App.
"""

import pytz
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


MAX_LENGTH = 255


class User(AbstractUser):
    """
    An extension of Django's default user, but allows for additional functionality.
    Contains user authentication related information.
    """
    # TODO: LDAP Authentication here. Likely need to change to AbstractBaseUser inheritance.

    @staticmethod
    def get_or_create_superuser(username, email, password):
        """
        Attempts to either get or create user with the given information.
        """
        try:
            new_user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            new_user = User.objects.create_superuser(username, email, password)
        return new_user


class Profile(models.Model):
    """
    A profile for a given user.
    Contains additional user information not regarding authentication.
    """
    # Relationship Keys.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.ForeignKey('Address', on_delete=models.CASCADE, blank=True, null=True)
    phone_number = models.ForeignKey('PhoneNumber', on_delete=models.CASCADE, blank=True, null=True)
    user_timezone = models.CharField(
        choices=[(x, x) for x in pytz.common_timezones], default="America/Detroit",
        max_length=255)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return '{0}'.format(self.user)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        self.full_clean()
        super(Profile, self).save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


class Address(models.Model):
    """
    Address for a user.
    """
    # Model fields.
    street = models.CharField(max_length=MAX_LENGTH)
    optional_street = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    city = models.CharField(max_length=MAX_LENGTH)
    state = models.CharField(max_length=MAX_LENGTH, default='MI')
    zip = models.CharField(max_length=MAX_LENGTH)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        if self.optional_street is not None:
            return '{0} {1} {2}, {3}, {4}'.format(self.street, self.optional_street, self.city, self.state,
                                                  self.zip)
        else:
            return '{0} {1}, {2}, {3}'.format(self.street, self.city, self.state, self.zip)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(Address, self).save(*args, **kwargs)


class PhoneNumber(models.Model):
    """
    Phone Number for a user.
    """
    # Model validators.
    phone_regex = RegexValidator(
        regex='^\+?1?\d{10,15}',
        message='Phone number must be entered in the format: "+999999999". Between 10 and 15 digits allowed.',
    )

    # Model fields.
    phone_number = models.CharField(validators=[phone_regex], max_length=15, blank=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Phone Number'
        verbose_name_plural = 'Phone Numbers'

    def __str__(self):
        return '{0}'.format(self.phone_number)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(PhoneNumber, self).save(*args, **kwargs)
