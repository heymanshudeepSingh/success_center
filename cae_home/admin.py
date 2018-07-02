"""
Admin view for CAE_Home App.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import forms, models


class ProfileInline(admin.StackedInline):
    model = models.Profile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )

    # Fields to display in admin list view.
    BaseUserAdmin.list_display = ('username', 'first_name', 'last_name', 'user_type')

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

    # Fields to filter by in admin list view.
    list_filter = (

    )

    # Read only fields for admin detail view.
    readonly_fields = (
        'user', 'date_created', 'date_modified',
    )

    # Fieldset organization for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('user', 'address', 'phone_number', )
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


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.Address, AddressAdmin)
admin.site.register(models.PhoneNumber, PhoneNumberAdmin)
