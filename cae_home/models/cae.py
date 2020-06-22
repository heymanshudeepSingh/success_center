"""
Definitions of "CAE Center" related Core Models.
"""

# System Imports.
from django.db import models
from django.db.models import ObjectDoesNotExist


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
