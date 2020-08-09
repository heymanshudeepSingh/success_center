"""
Definitions of "CAE Center" related Core Models.
"""

# System Imports.
from django.db import models
from django.db.models import ObjectDoesNotExist
from django.utils import timezone
from django.utils.text import slugify

# User Imports.


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
        verbose_name_plural = "Assets"
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
        serial_number = "12345"
        asset_tag = "A12345"
        brand_name = "Popular Brand"
        mac_address = "FFFFFFFFFF"
        ip_address = "127.0.0.1"
        device_name = "Device"
        description = "It does something."

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
            return asset
        except ObjectDoesNotExist:
            asset = Asset.objects.create(
                serial_number=serial_number,
                asset_tag=asset_tag,
                brand_name=brand_name,
                mac_address=mac_address,
                ip_address=ip_address,
                device_name=device_name,
                description=description
            )
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
        verbose_name = "Software"
        verbose_name_plural = "Software"
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
        Used for testing.
        """
        name = 'Dummy Software'
        slug = slugify(name)
        try:
            return Software.objects.get(
                name=name,
                slug=slug,
            )
        except ObjectDoesNotExist:
            return Software.objects.create(
                name=name,
                slug=slug,
            )


class SoftwareDetail(models.Model):
    """
    Provides more detail about a piece of software.
    Includes things like version, expiration, etc.
    """
    # Relationship keys.
    software = models.ForeignKey('Software', on_delete=models.CASCADE)

    # Model fields
    version = models.CharField(max_length=MAX_LENGTH)
    expiration = models.DateField()

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Software Detail"
        verbose_name_plural = "Software Details"
        ordering = ('version', 'expiration')

    def __str__(self):
        return '{0} - {1}'.format(self.software.name, self.version)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(SoftwareDetail, self).save(*args, **kwargs)

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.
        Used for testing.
        """
        software = Software.create_dummy_model()
        version = 5
        expiration = timezone.datetime.strptime('2020-01-01', '%d-%m-%Y')
        try:
            return SoftwareDetail.objects.get(
                software=software,
                version=version,
                expiration=expiration,
            )
        except ObjectDoesNotExist:
            return SoftwareDetail.objects.create(
                software=software,
                version=version,
                expiration=expiration,
            )
