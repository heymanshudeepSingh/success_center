"""
Definitions of "User" related Core Models.
"""

import pytz
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.management import call_command
from django.core.validators import RegexValidator
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


MAX_LENGTH = 255


class User(AbstractUser):
    """
    An extension of Django's default user, allowing for additional functionality.
    Contains user authentication related information.
    """
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

    @staticmethod
    def get_or_create_user(username, email, password):
        """
        Attempts to either get or create user with given information.
        """
        new_user, created = User.objects.get_or_create(username=username, email=email)
        if isinstance(new_user, tuple):
            new_user = new_user[0]

        # If user was newly created, set new password.
        if created:
            new_user.set_password(password)
            new_user.save()

        return new_user


class UserIntermediary(models.Model):
    """
    Intermediary to connect (login) User models, user Profile models, and WmuUser models.
    """
    # Relationship Keys.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    wmu_user = models.OneToOneField('cae_home.WMUUser', on_delete=models.CASCADE, blank=True, null=True)
    profile = models.OneToOneField('Profile', on_delete=models.CASCADE, blank=True, null=True)

    # Model fields.
    bronco_net = models.CharField(max_length=MAX_LENGTH, blank=True, null=True, unique=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Intermediary'
        verbose_name_plural = 'User Intermediaries'

    def __str__(self):
        return '{0}'.format(self.bronco_net)

    def clean(self, *args, **kwargs):
        """
        Custom cleaning implementation. Includes validation, setting fields, etc.
        """
        # Check that at least one of either "User" or "WmuUser" is provided.
        if self.user is None and self.wmu_user is None:
            raise ValidationError('Must have relation to either "User" or "WmuUser" model.')

        # Set fields on model creation.
        if self.pk is None:
            # Attempt to pull bronco_net from login model. Otherwise, get from wmu_user model.
            if self.user is not None:
                self.bronco_net = self.user.username
            else:
                self.bronco_net = self.wmu_user.bronco_net
        else:
            # Do not allow null profiles after initial creation.
            if self.profile is None:
                raise ValidationError('Must have associated user profile model.')

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(UserIntermediary, self).save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_user_intermediary(sender, instance, created, **kwargs):
    if created:
        # Handle for new (login) User being created. Attempt to find existing Intermediary with bronco_net.
        # On failure, create new UserIntermediary instance.
        try:
            user_intermediary = UserIntermediary.objects.get(bronco_net=instance.username)

            # Check that User has not been provided to UserIntermediary.
            if user_intermediary.user is not None:
                raise ValidationError('User Intermediary model already has associated User model.')
            else:
                user_intermediary.user = instance
                user_intermediary.save()
        except ObjectDoesNotExist:
            UserIntermediary.objects.create(user=instance)
    else:
        # Just updating an existing UserIntermediary. Save.
        instance.userintermediary.save()


class Profile(models.Model):
    """
    A profile for a given user.
    Contains additional user information not regarding authentication.
    """
    # Preset field choices.
    FONT_XS = 0
    FONT_SM = 1
    FONT_BASE = 2
    FONT_MD = 3
    FONT_LG = 4
    FONT_XL = 5
    FONT_SIZE_CHOICES = (
        (FONT_XS, 'Extra Small'),
        (FONT_SM, 'Small'),
        (FONT_BASE, 'Default'),
        (FONT_MD, 'Medium'),
        (FONT_LG, 'Large'),
        (FONT_XL, 'Extra Large'),
    )

    # Relationship Keys.
    address = models.ForeignKey('Address', on_delete=models.CASCADE, blank=True, null=True)
    phone_number = models.ForeignKey('PhoneNumber', on_delete=models.CASCADE, blank=True, null=True)
    site_theme = models.ForeignKey('SiteTheme', on_delete=models.CASCADE, blank=True)

    # Model fields.
    user_timezone = models.CharField(
        choices=[(x, x) for x in pytz.common_timezones], blank=True, default="America/Detroit",
        max_length=255
    )
    desktop_font_size = models.PositiveSmallIntegerField(choices=FONT_SIZE_CHOICES, blank=True, default=2)
    mobile_font_size = models.PositiveSmallIntegerField(choices=FONT_SIZE_CHOICES, blank=True, default=2)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return '{0}'.format(self.userintermediary.bronco_net)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        self.full_clean()
        super(Profile, self).save(*args, **kwargs)

    def get_font_size(self, value):
        """
        Return text description for font size options.
        """
        if value is 0:
            return 'xs'
        elif value is 1:
            return 'sm'
        elif value is 3:
            return 'md'
        elif value is 4:
            return 'lg'
        elif value is 5:
            return 'xl'
        else:
            return 'base'

    def get_desktop_font_size(self, value=None):
        """
        Return text description for profile's desktop font size.
        """
        if value is None:
            value = self.desktop_font_size
        return self.get_font_size(value)

    def get_mobile_font_size(self, value=None):
        """
        Return text description for profile's mobile font size.
        """
        if value is None:
            value = self.mobile_font_size
        return self.get_font_size(value)

    def get_official_email(self):
        """
        Return official email for user profile.
        """
        return '{0}@wmich.edu'.format(self.userintermediary.bronco_net)

    @staticmethod
    def get_profile(bronco_net):
        """
        Given a valid bronco id, return the associated profile.
        """
        try:
            user_intermediary = UserIntermediary.objects.get(bronco_net=bronco_net)
            return user_intermediary.profile
        except ObjectDoesNotExist:
            return None


@receiver(post_save, sender=UserIntermediary)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Handle for new UserIntermediary being created. Create new profile as well.
        try:
            # Attempt to get default theme.
            site_theme = SiteTheme.objects.get(name='wmu')
        except ObjectDoesNotExist:
            # Failed to get theme. Likely a unit test. Run site_theme fixtures and attempt again.
            call_command('loaddata', 'full_models/site_themes')
            site_theme = SiteTheme.objects.get(name='wmu')

        # Create new profile object for new user.
        profile = Profile.objects.create(site_theme=site_theme)

        # Associate profile with UserIntermediary.
        instance.profile = profile
        instance.save()
    else:
        # Just updating an existing profile. Save.
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
        unique_together = ('street', 'optional_street', 'city', 'state', 'zip')

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
    phone_number = models.CharField(validators=[phone_regex], max_length=15, unique=True)

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

    def display(self):
        """
        Returns number in read-friendly format.
        Assumes US formatting of numbers.
        """
        if len(str(self.phone_number)) is 10:
            # Standard phone number with area code.
            return '({0}) {1}-{2}'.format(
                self.phone_number[0:3],
                self.phone_number[3:6],
                self.phone_number[6:10]
            )
        else:
            # Other format. Assume US formatting so last 10 digits are what we want.
            return '({0}) {1}-{2}'.format(
                self.phone_number[-10:-7],
                self.phone_number[-7:-4],
                self.phone_number[-4::]
            )

    def display_int(self):
        """
        Returns number in read-friendly format, plus country code.
        Assumes US formatting of numbers.
        """
        if len(str(self.phone_number)) is 10:
            # Standard phone number with area code.
            return '+1-{0}-{1}-{2}'.format(
                self.phone_number[0:3],
                self.phone_number[3:6],
                self.phone_number[6:10]
            )
        else:
            # Other format. Assume US formatting so last 10 digits are what we want.
            return '+1-{0}-{1}-{2}'.format(
                self.phone_number[-10:-7],
                self.phone_number[-7:-4],
                self.phone_number[-4::]
            )


class SiteTheme(models.Model):
    # Model fields.
    name = models.CharField(max_length=MAX_LENGTH, unique=True)
    gold_logo = models.BooleanField(default=True)

    # Self-setting/Non-user-editable fields.
    slug = models.SlugField(
        max_length=MAX_LENGTH,
        unique=True,
        help_text='Used for urls referencing this Site Theme.',
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Theme'
        verbose_name_plural = 'Site Themes'

    def __str__(self):
        return '{0}'.format(self.name.capitalize())

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(SiteTheme, self).save(*args, **kwargs)
