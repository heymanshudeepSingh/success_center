"""
Admin view for CAE_Home App.
"""

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import forms, models


# Attempt to import RoomEvent Inline.
try:
    from apps.CAE_Web.cae_web_core.admin import RoomEventInline
except ImportError:
    # Assume that CAE_Web project isn't present.
    RoomEventInline = None


#region User Model Admin

class ProfileInline(admin.StackedInline):
    model = models.Profile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )

    # Fields to display in admin list view.
    BaseUserAdmin.list_display = ('username', 'first_name', 'last_name', 'user_type')

    # Remove individual permission list from admin detail view. Should only ever use groups.
    old_list = BaseUserAdmin.fieldsets[2][1]['fields']
    new_list = ()
    for item in old_list:
        if item is not 'user_permissions':
            new_list += (item,)
    BaseUserAdmin.fieldsets[2][1]['fields'] = new_list

    def user_type(self, obj):
        """
        Return list of user-associated group(s).
        """
        groups = []
        for group in obj.groups.all():
            groups.append(group.name)
        return ', '.join(groups)


class ProfileAdmin(admin.ModelAdmin):
    form = forms.ProfileAdminForm

    # Fields to display in admin list view.
    list_display = (
        'user', 'address', 'phone_number',
    )

    # Fields to search in admin list view.
    search_fields = [
        'user',
    ]

    # Read only fields for admin detail view.
    readonly_fields = (
        'user', 'date_created', 'date_modified',
    )

    # Fieldset organization for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('user', 'address', 'phone_number', 'user_timezone')
        }),
        ('Advanced', {
            'classes': ('collapse', ),
            'fields': ('date_created', 'date_modified', )
        }),
    )


class AddressAdmin(admin.ModelAdmin):
    form = forms.AddressAdminForm

    # Fields to display in admin list view.
    list_display = (
        'street', 'optional_street', 'city', 'state', 'zip',
    )

    # Fields to search in admin list view.
    search_fields = [
        'street', 'city', 'zip',
    ]

    # Fields to filter by in admin list view.
    list_filter = (
        'city', 'state',
    )

    # Read only fields for admin detail view.
    readonly_fields = (
        'date_created', 'date_modified',
    )

    # Fieldset organization for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('street', 'optional_street', 'city', 'state', 'zip', )
        }),
        ('Advanced', {
            'classes': ('collapse', ),
            'fields': ('date_created', 'date_modified', )
        }),
    )


class PhoneNumberAdmin(admin.ModelAdmin):
    form = forms.PhoneNumberAdminForm

    # Fields to display in admin list view.
    list_display = (
        'phone_number',
    )

    # Fields to search in admin list view.
    search_fields = [
        'phone_number',
    ]

    # Read only fields for admin detail view.
    readonly_fields = (
        'date_created', 'date_modified',
    )

    # Fieldset organization for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('phone_number', ),
        }),
        ('Advanced', {
            'classes': ('collapse', ),
            'fields': ('date_created', 'date_modified', )
        }),
    )

#endregion User Model Admin


#region WMU Model Admin

class DepartmentAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('name',)

    # Fields to search in admin list view.
    search_fields = ['name',]

    # Read only fields for admin detail view.
    readonly_fields = ('date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('date_created', 'date_modified',),
        }),
    )


class RoomTypeAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('name',)

    # Fields to search in admin list view.
    search_fields = ['name',]

    # Read only fields for admin detail view.
    readonly_fields = ('date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('date_created', 'date_modified',),
        }),
    )


class RoomAdmin(admin.ModelAdmin):
    # Check that the inline import succeeded.
    if RoomEventInline is not None:
        inlines = [RoomEventInline]

    # Fields to display in admin list view.
    list_display = ('name', 'capacity', 'room_type',)

    # Fields to filter by in admin list view.
    list_filter = ('room_type', 'department',)

    # Fields to search in admin list view.
    search_fields = ['name', 'capacity',]

    # Read only fields for admin detail view.
    readonly_fields = ('date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': (
                'name', 'room_type', 'department', 'capacity',
            )
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('date_created', 'date_modified',),
        }),
    )

#endregion WMU Model Admin


#region CAE Model Admin

class AssetAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('room', 'brand_name', 'asset_tag', 'serial_number', 'mac_address', 'ip_address')

    # Fields to filter by in admin list view.
    list_filter = ('room', 'brand_name',)

    # Fields to search in admin list view.
    search_fields = ['asset_tag', 'serial_number', 'mac_address', 'ip_address',]

    # Read only fields for admin detail view.
    readonly_fields = ('date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': (
                'room', 'brand_name', 'asset_tag', 'serial_number', 'mac_address', 'ip_address', 'device_name',
                'description',
            )
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('date_created', 'date_modified',),
        }),
    )

#endregion CAE Model Admin


# User Model Registration
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.Address, AddressAdmin)
admin.site.register(models.PhoneNumber, PhoneNumberAdmin)

# WMU Model Registration
admin.site.register(models.Department, DepartmentAdmin)
admin.site.register(models.RoomType, RoomTypeAdmin)
admin.site.register(models.Room, RoomAdmin)

# CAE Model Registration
admin.site.register(models.Asset, AssetAdmin)
