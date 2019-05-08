"""
Definitions of "User" related Core Models.
"""

import pytz
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.management import call_command
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from os import devnull


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
    def get_or_create_user(username, email, password, inactive=False):
        """
        Attempts to either get or create user with given information.
        """
        new_user, created = User.objects.get_or_create(username=username, email=email)
        if isinstance(new_user, tuple):
            new_user = new_user[0]

        # If user was newly created, set new password.
        if created:
            new_user.set_password(password)
            if inactive:
                new_user.is_active = False
            new_user.save()

        return new_user

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.
        Used for testing.
        """
        return User.get_or_create_user('dummy_user', 'dummy@gmail.com', settings.USER_SEED_PASSWORD)


class UserIntermediary(models.Model):
    """
    Intermediary to connect (login) User models, user Profile models, and WmuUser models.
    """
    # Relationship Keys.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    wmu_user = models.OneToOneField('cae_home.WMUUser', on_delete=models.CASCADE, blank=True, null=True)
    profile = models.OneToOneField('Profile', on_delete=models.CASCADE, blank=True, null=True)

    # Model fields.
    bronco_net = models.CharField(max_length=MAX_LENGTH, blank=True, unique=True)

    # Self-setting/Non-user-editable fields.
    slug = models.SlugField(
        max_length=MAX_LENGTH,
        unique=True,
        help_text='Used for urls referencing this User and related models.',
    )
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

            # Set slug.
            self.slug = slugify(self.bronco_net)
        else:
            # Do not allow null profiles after initial creation.
            if self.profile is None:
                raise ValidationError('Must have associated user profile model.')

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.clean()    # Seems to error on validation without this line.
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
    site_theme = models.ForeignKey('SiteTheme', on_delete=models.CASCADE, blank=True)

    # Model fields.
    phone_number = PhoneNumberField(blank=True, null=True)
    user_timezone = models.CharField(
        choices=[(x, x) for x in pytz.common_timezones], blank=True, default="America/Detroit",
        max_length=255
    )
    desktop_font_size = models.PositiveSmallIntegerField(choices=FONT_SIZE_CHOICES, blank=True, default=2)
    mobile_font_size = models.PositiveSmallIntegerField(choices=FONT_SIZE_CHOICES, blank=True, default=2)
    fg_color = models.CharField(
        blank=True,
        help_text="Foreground css color for schedule. E.g. 'red' or '#FF0000'",
        max_length=30)
    bg_color = models.CharField(
        blank=True,
        help_text="Foreground css color for schedule. E.g. 'red' or '#FF0000'",
        max_length=30)

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
            site_theme = SiteTheme.objects.get(slug='wmu')
        except ObjectDoesNotExist:
            # Failed to get theme. Likely a unit test. Run site_theme fixtures and attempt again.
            with open(devnull, 'a') as null:
                call_command('loaddata', 'full_models/site_themes', stdout=null)
            site_theme = SiteTheme.objects.get(slug='wmu')

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
    # Preset field choices.
    STATE_CHOICES = (
        (0, 'AL - Alabama'),
        (1, 'AK - Alaska'),
        (2, 'AZ - Arizona'),
        (3, 'AR - Arkansas'),
        (4, 'CA - California'),
        (5, 'CO - Colorado'),
        (6, 'CT - Connecticut'),
        (7, 'DE - Delaware'),
        (8, 'FL - Florida'),
        (9, 'GA - Georgia'),
        (10, 'HI - Hawaii'),
        (11, 'ID - Idaho'),
        (12, 'IL - Illinois'),
        (13, 'IN - Indiana'),
        (14, 'IA - Iowa'),
        (15, 'KS - Kansas'),
        (16, 'KY - Kentucky'),
        (17, 'LA - Louisiana'),
        (18, 'ME - Maine'),
        (19, 'MD - Maryland'),
        (20, 'MA - Massachusetts'),
        (21, 'MI - Michigan'),
        (22, 'MN - Minnesota'),
        (23, 'MS - Mississippi'),
        (24, 'MO - Missouri'),
        (25, 'MT - Montana'),
        (26, 'NE - Nebraska'),
        (27, 'NV - Nevada'),
        (28, 'NH - New Hampshire'),
        (29, 'NJ - New Jersey'),
        (30, 'NM - New Mexico'),
        (31, 'NY - New York'),
        (32, 'NC - North Carolina'),
        (33, 'ND - North Dakota'),
        (34, 'OH - Ohio'),
        (35, 'OK - Oklahoma'),
        (36, 'OR - Oregon'),
        (37, 'PA - Pennsylvannia'),
        (38, 'RI - Rhode Island'),
        (39, 'SC - South Carolina'),
        (40, 'SD - South Dakota'),
        (41, 'TN - Tennessee'),
        (42, 'TX - Texas'),
        (43, 'UT - Utah'),
        (44, 'VT - Vermont'),
        (45, 'VA - Virginia'),
        (46, 'WA - Washington'),
        (47, 'WV - West Virginia'),
        (48, 'WI - Wisconsin'),
        (49, 'WY - Wyoming'),
    )

    # Model fields.
    street = models.CharField(max_length=MAX_LENGTH)
    optional_street = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    city = models.CharField(max_length=MAX_LENGTH)
    state = models.PositiveSmallIntegerField(choices=STATE_CHOICES, default=21)
    zip = models.CharField(max_length=7)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        unique_together = ('street', 'optional_street', 'city', 'state', 'zip')

    def __str__(self):
        if self.optional_street is not None:
            return '{0} {1} {2}, {3}, {4}'.format(
                self.street,
                self.optional_street,
                self.city,
                self.get_state_abbrev_as_string(),
                self.zip
            )
        else:
            return '{0} {1}, {2}, {3}'.format(
                self.street,
                self.city,
                self.get_state_abbrev_as_string(),
                self.zip
            )

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(Address, self).save(*args, **kwargs)

    def get_state_as_string(self, value=None):
        """
        Returns state name as string.
        :param value: Integer of value to get. If none, uses current model value.
        :return: State name.
        """
        if value is None:
            value = self.state
        state_string = self.STATE_CHOICES[value][1][5:]
        return state_string

    def get_state_abbrev_as_string(self, value=None):
        """
        Returns state abbreviation as string.
        :param value: Integer of value to get. If none, uses current model value.
        :return: State abbreviation.
        """
        if value is None:
            value = self.state
        state_string = self.STATE_CHOICES[value][1][:2]
        return state_string

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.
        Used for testing.
        """
        street = '1234 Dummy Lane'
        optional_street = 'Apt 1234'
        city = 'Kalamazoo'
        state = 21
        zip = '49008'
        try:
            return Address.objects.get(
                street=street,
                optional_street=optional_street,
                city=city,
                state=state,
                zip=zip
            )
        except ObjectDoesNotExist:
            return Address.objects.create(
                street=street,
                optional_street=optional_street,
                city=city,
                state=state,
                zip=zip
            )


class SiteTheme(models.Model):
    # Model fields.
    display_name = models.CharField(max_length=MAX_LENGTH, unique=True)     # The value displayed to users.
    file_name = models.CharField(max_length=MAX_LENGTH, unique=True)        # The value used in files and templating.
    gold_logo = models.BooleanField(default=True)
    ordering = models.PositiveSmallIntegerField(default=0)

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
        ordering = ('ordering', 'display_name')

    def __str__(self):
        return '{0}'.format(str(self.display_name))

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(SiteTheme, self).save(*args, **kwargs)

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.
        Used for testing.
        """
        name = 'Dummy Site Theme'
        slug = slugify(name)
        try:
            return SiteTheme.objects.get(
                display_name=name,
                file_name=slug,
                slug=slug,
            )
        except ObjectDoesNotExist:
            return SiteTheme.objects.create(
                display_name=name,
                file_name=slug,
                slug=slug,
            )
