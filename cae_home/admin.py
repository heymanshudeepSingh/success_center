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
    # inlines = (ProfileInline, )

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


class UserIntermediaryToUserListFilter(admin.SimpleListFilter):
    """
    Filter for ProfileAdmin to show profiles associated to valid site login accounts.
    """
    title = ('Associated with Login User')
    parameter_name = 'login_user'

    def lookups(self, request, model_admin):
        return (
            ('Yes', ('Yes')),
            ('No', ('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(user__isnull=False)
        if self.value() == 'No':
            return queryset.filter(user__isnull=True)


class UserIntermediaryToWmuUserListFilter(admin.SimpleListFilter):
    """
    Filter for ProfileAdmin to show profiles associated to valid site login accounts.
    """
    title = ('Associated with WMU User')
    parameter_name = 'wmu_user'

    def lookups(self, request, model_admin):
        return (
            ('Yes', ('Yes')),
            ('No', ('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(wmu_user__isnull=False)
        if self.value() == 'No':
            return queryset.filter(wmu_user__isnull=True)


class UserIntermediaryAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = (
        'bronco_net',
    )

    # Fields to search in admin list view.
    search_fields = [
        'bronco_net',
    ]

    # Fields to filter by in admin list view.
    list_filter = (
        UserIntermediaryToUserListFilter, UserIntermediaryToWmuUserListFilter,
    )

    # Read only fields for admin detail view.
    readonly_fields = (
        'id', 'date_created', 'date_modified',
    )

    # Fieldset organization for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('bronco_net',)
        }),
        ('Relations', {
            'fields': ('user', 'wmu_user', 'profile',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'slug', 'date_created', 'date_modified',)
        }),
    )

    # New object's slugs will be automatically set by bronco_net.
    prepopulated_fields = {'slug': ('bronco_net',)}


class ProfileToUserListFilter(admin.SimpleListFilter):
    """
    Filter for ProfileAdmin to show profiles associated to valid site login accounts.
    """
    title = ('Associated with Login User')
    parameter_name = 'login_user'

    def lookups(self, request, model_admin):
        return (
            ('Yes', ('Yes')),
            ('No', ('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(userintermediary__user__isnull=False)
        if self.value() == 'No':
            return queryset.filter(userintermediary__user__isnull=True)


class ProfileAdmin(admin.ModelAdmin):

    # Needed for related field list display.
    def get_bronco_net(self, obj):
        return obj.userintermediary.bronco_net
    get_bronco_net.short_description = 'Bronco Net'
    get_bronco_net.admin_order_field = 'userintermediary__bronco_net'

    # Fields to display in admin list view.
    list_display = (
        'get_bronco_net', 'address', 'phone_number', 'site_theme',
    )

    # Fields to search in admin list view.
    search_fields = [
        'userintermediary__bronco_net',
    ]

    # Fields to filter by in admin list view.
    list_filter = (
        ProfileToUserListFilter,
    )

    # Read only fields for admin detail view.
    readonly_fields = (
        'id', 'date_created', 'date_modified',
    )

    # Fieldset organization for admin detail view.
    fieldsets = (
        ('User Info', {
            'fields': ('address', 'phone_number',)
        }),
        ('Site Options', {
            'fields': ('user_timezone', 'site_theme', 'desktop_font_size', 'mobile_font_size',)
        }),
        ('Schedule Colors', {
            'fields': ('fg_color', 'bg_color')
        }),
        ('Advanced', {
            'classes': ('collapse', ),
            'fields': ('id', 'date_created', 'date_modified', )
        }),
    )


class AddressAdmin(admin.ModelAdmin):
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
        'id', 'date_created', 'date_modified',
    )

    # Fieldset organization for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('street', 'optional_street', 'city', 'state', 'zip', )
        }),
        ('Advanced', {
            'classes': ('collapse', ),
            'fields': ('id', 'date_created', 'date_modified', )
        }),
    )


class SiteThemeAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = (
        'name', 'gold_logo',
    )

    # Fields to search in admin list view.
    search_fields = [
        'name',
    ]

    # Read only fields for admin detail view.
    readonly_fields = (
        'id', 'date_created', 'date_modified',
    )

    # Fieldset organization for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('slug', 'name', 'gold_logo',)
        }),
        ('Advanced', {
            'classes': ('collapse', ),
            'fields': ('id', 'date_created', 'date_modified', )
        }),
    )

    # New object's slugs will be automatically set by name.
    prepopulated_fields = {'slug': ('name',)}

#endregion User Model Admin


#region WMU Model Admin

class DepartmentAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('name',)

    # Fields to search in admin list view.
    search_fields = ['name',]

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'slug', 'date_created', 'date_modified',),
        }),
    )

    # New object's slugs will be automatically set by name.
    prepopulated_fields = {'slug': ('name',)}


class RoomTypeAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('name',)

    # Fields to search in admin list view.
    search_fields = ['name',]

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'slug', 'date_created', 'date_modified',),
        }),
    )

    # New object's slugs will be automatically set by name.
    prepopulated_fields = {'slug': ('name',)}


class RoomAdmin(admin.ModelAdmin):

    def get_departments(self, obj):
        dept_list = ''
        for department in obj.department.all():
            dept_list += '{0} | '.format(department.name)
        return dept_list[:-3]

    # Check that the inline import succeeded.
    if RoomEventInline is not None:
        inlines = [RoomEventInline]

    # Fields to display in admin list view.
    list_display = ('name', 'room_type', 'get_departments')

    # Fields to filter by in admin list view.
    list_filter = ('room_type', 'department',)

    # Fields to search in admin list view.
    search_fields = ['name', 'capacity',]

    # Select2 search fields for admin detail view.
    autocomplete_fields = ['department',]

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': (
                'name', 'room_type', 'department', 'description', 'capacity',
            )
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'slug', 'date_created', 'date_modified',),
        }),
    )

    # New object's slugs will be automatically set by name.
    prepopulated_fields = {'slug': ('name',)}


class MajorAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('code', 'name', 'department', 'undergrad', 'active',)

    # Fields to filter by in admin list view.
    list_filter = ('undergrad', 'active',)

    # Fields to search in admin list view.
    search_fields = ['department', 'code', 'name',]

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': (
                'code', 'name', 'department', 'undergrad', 'active',
            )
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'slug', 'date_created', 'date_modified',),
        }),
    )

    # New object's slugs will be automatically set by code.
    prepopulated_fields = {'slug': ('code',)}


class SemesterDateAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('name', 'start_date', 'end_date',)

    # Fields to search in admin list view.
    search_fields = ['name', 'start_date', 'end_date',]

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': (
                'name', 'start_date', 'end_date',
            )
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'date_created', 'date_modified',),
        }),
    )


class WmuUserAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('bronco_net', 'winno', 'first_name', 'last_name', 'department',)

    # Fields to filter by in admin list view.
    list_filter = ('active', 'major',)

    # Fields to search in admin list view.
    search_fields = ['bronco_net', 'winno', 'first_name', 'last_name',]

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified', 'official_email')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': (
                'user_type', 'bronco_net', 'winno', 'first_name', 'last_name', 'major', 'department',
            )}),
        ('Contact Info', {
            'fields': ('official_email',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'active', 'date_created', 'date_modified',),
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
    readonly_fields = ('id', 'date_created', 'date_modified')

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
            'fields': ('id', 'date_created', 'date_modified',),
        }),
    )

#endregion CAE Model Admin


# User Model Registration
admin.site.register(models.User, UserAdmin)
admin.site.register(models.UserIntermediary, UserIntermediaryAdmin)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.Address, AddressAdmin)
admin.site.register(models.SiteTheme, SiteThemeAdmin)

# WMU Model Registration
admin.site.register(models.Department, DepartmentAdmin)
admin.site.register(models.RoomType, RoomTypeAdmin)
admin.site.register(models.Room, RoomAdmin)
admin.site.register(models.Major, MajorAdmin)
admin.site.register(models.SemesterDate, SemesterDateAdmin)
admin.site.register(models.WmuUser, WmuUserAdmin)

# CAE Model Registration
# admin.site.register(models.Asset, AssetAdmin)
