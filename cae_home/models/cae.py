"""
CAE models for CAE_Home App.
"""

from django.db import models


MAX_LENGTH = 255


class Asset(models.Model):
    """
    An asset owned by the CAE Center (servers, computers, and other hardware).
    """
    # Relationship keys.
    room = models.ForeignKey('Room', on_delete=models.CASCADE)

    # Model fields.
    serial_number = models.CharField(max_length=MAX_LENGTH)
    asset_tag = models.CharField(max_length=MAX_LENGTH)
    brand_name = models.CharField(max_length=MAX_LENGTH)
    mac_address = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    ip_address = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    device_name = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    description = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Asset"
        verbose_name_plural = "Assets"

    def __str__(self):
        return '{0} {1} - {2} - {3}'.format(self.room, self.brand_name, self.asset_tag, self.serial_number)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(Asset, self).save(*args, **kwargs)
