"""
Definitions of "CAE Center" related Core Models.
"""

# System Imports.
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


MAX_LENGTH = 255


class Asset(models.Model):
    """
    An asset owned by the CAE Center (servers, computers, and other hardware).
    """
    # Relationship keys.
    # room = models.ForeignKey('Room', on_delete=models.CASCADE)

    # Model fields.
    serial_number = models.CharField(max_length=MAX_LENGTH, unique=True)
    asset_tag = models.CharField(max_length=MAX_LENGTH, unique=True)
    brand_name = models.CharField(max_length=MAX_LENGTH)
    mac_address = models.CharField(max_length=MAX_LENGTH, blank=True, null=True, unique=True)
    ip_address = models.CharField(max_length=MAX_LENGTH, blank=True, null=True, unique=True)
    device_name = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    description = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Assets'
        ordering = ('asset_tag',)

    def natural_key(self):
        values = []
        values.append(self.asset_tag)
        values.append(self.device_name)

        return values

    def __str__(self):
        return '{0} {1} - {2}'.format(self.brand_name, self.asset_tag, self.serial_number)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(Asset, self).save(*args, **kwargs)

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.

        Useful for when UnitTesting requires an instance of this model,
        but test does not care what values the model actually has.
        """
        # Define "dummy model" values.
        serial_number = '12345'
        asset_tag = 'A12345'
        brand_name = 'Popular Brand'
        mac_address = 'FFFFFFFFFF'
        ip_address = '127.0.0.1'
        device_name = 'Device'
        description = 'It does something.'

        # Attempt to get corresponding model instance, if there is one.
        try:
            asset = Asset.objects.get(
                serial_number=serial_number,
                asset_tag=asset_tag,
                brand_name=brand_name,
                mac_address=mac_address,
                ip_address=ip_address,
                device_name=device_name,
                description=description
            )
        except Asset.DoesNotExist:
            # Instance not found. Create new model.
            asset = Asset.objects.create(
                serial_number=serial_number,
                asset_tag=asset_tag,
                brand_name=brand_name,
                mac_address=mac_address,
                ip_address=ip_address,
                device_name=device_name,
                description=description
            )

        # Return "dummy model" instance.
        return asset


class Software(models.Model):
    """
    Software on a given computer.
    """
    # Model fields.
    name = models.CharField(max_length=MAX_LENGTH)

    # Self-setting/Non-user-editable fields.
    slug = models.SlugField(
        max_length=MAX_LENGTH,
        unique=True,
        help_text='Used for urls referencing this Software.',
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Software'
        verbose_name_plural = 'Software'
        ordering = ('name',)

    def natural_key(self):
        return self.name

    def __str__(self):
        return '{0}'.format(self.name)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(Software, self).save(*args, **kwargs)

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.

        Useful for when UnitTesting requires an instance of this model,
        but test does not care what values the model actually has.
        """
        # Define "dummy model" values.
        name = 'Dummy Software'
        slug = slugify(name)

        # Attempt to get corresponding model instance, if there is one.
        try:
            software = Software.objects.get(
                name=name,
                slug=slug,
            )
        except Software.DoesNotExist:
            # Instance not found. Create new model.
            software = Software.objects.create(
                name=name,
                slug=slug,
            )

        # Return "dummy model" instance.
        return software


class SoftwareDetail(models.Model):
    """
    Provides more detail about a piece of software.
    Includes things like version, expiration, etc.
    """
    # Preset field choices.
    SOFTWARE_TYPE_CHOICES = (
        (1, 'Public'),
        (2, 'University'),
        (3, 'Research'),
    )

    # Relationship keys.
    software = models.ForeignKey('Software', on_delete=models.CASCADE)

    # Model fields
    software_type = models.PositiveSmallIntegerField(choices=SOFTWARE_TYPE_CHOICES, default=2)
    version = models.CharField(max_length=MAX_LENGTH)
    expiration = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=False)

    # Self-setting/Non-user-editable fields.
    slug = models.SlugField(
        max_length=MAX_LENGTH,
        unique=True,
        help_text='Used for urls referencing this Software.',
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Software Detail'
        verbose_name_plural = 'Software Details'
        ordering = ('software__name', 'expiration', 'version')

    def __str__(self):
        return '{0} - {1}'.format(self.software.name, self.version)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(SoftwareDetail, self).save(*args, **kwargs)

    def get_software_type(self, value=None):
        """
        Returns software type as string.
        :param value: Integer of value to get. If None, then uses current model value.
        :return: Software Type.
        """
        if value is None:
            value = self.software_type
        return self.SOFTWARE_TYPE_CHOICES[value][1]

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.

        Useful for when UnitTesting requires an instance of this model,
        but test does not care what values the model actually has.
        """
        # Define "dummy model" values.
        software = Software.create_dummy_model()
        version = 5
        expiration = timezone.datetime.strptime('2020-01-01', '%Y-%m-%d')

        # Attempt to get corresponding model instance, if there is one.
        try:
            software_detail = SoftwareDetail.objects.get(
                software=software,
                version=version,
                expiration=expiration,
            )
        except SoftwareDetail.DoesNotExist:
            # Instance not found. Create new model.
            software_detail = SoftwareDetail.objects.create(
                software=software,
                version=version,
                expiration=expiration,
            )

        # Return "dummy model" instance.
        return software_detail
