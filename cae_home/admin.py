"""
Admin view for CAE Home app.
"""

# System Imports.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# User Class Imports.
from . import models


# Attempt to import RoomEvent Inline.
try:
    from apps.CAE_Web.cae_web_core.admin import RoomEventInline
except ImportError:
    # Assume that CAE_Web project isn't present.
    RoomEventInline = None


#region Model Inlines

class ProfileInline(admin.StackedInline):
    model = models.Profile
    can_delete = False


class MajorInline(admin.TabularInline):
    model = models.WmuUser.major.through
    extra = 1

#endregion Model Inlines


#region Custom Filters

class UserCAECenterEmployeeFilter(admin.SimpleListFilter):
    """
    Filter for (login) User model Admin to show models associated with a CAE Center employee.
    """
    # Label to display for filter.
    title = 'Is CAE Employee'

    # Doesn't seem to do anything if you define the "queryset" method. Still mandatory to define though.
    parameter_name = ''

    def lookups(self, request, model_admin):
        """
        This defines the filter options.
        """
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        """
        This processes the filter option (defined above, in "lookups") when selected by a user.
        """
        cae_center_groups = [
            'CAE Director', 'CAE Building Coordinator',
            'CAE Admin GA', 'CAE Admin',
            'CAE Programmer GA', 'CAE Programmer',
            'CAE Attendant',
        ]
        if self.value() == 'yes':
            return queryset.filter(groups__name__in=cae_center_groups)
        if self.value() == 'no':
            return queryset.exclude(groups__name__in=cae_center_groups)


class UserIntermediaryToUserListFilter(admin.SimpleListFilter):
    """
    Filter for UserIntermediary model Admin to show models associated with a valid (login) User model.
    """
    # Label to display for filter.
    title = 'Associated with Login User'

    # Doesn't seem to do anything if you define the "queryset" method. Still mandatory to define though.
    parameter_name = ''

    def lookups(self, request, model_admin):
        """
        This defines the filter options.
        """
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        """
        This processes the filter option (defined above, in "lookups") when selected by a user.
        """
        if self.value() == 'yes':
            return queryset.filter(user__isnull=False)
        if self.value() == 'no':
            return queryset.filter(user__isnull=True)


class UserIntermediaryToWmuUserListFilter(admin.SimpleListFilter):
    """
    Filter for UserIntermediary model Admin to show models associated with a valid WmuUser model.
    """
    # Label to display for filter.
    title = 'Associated with WMU User'

    # Doesn't seem to do anything if you define the "queryset" method. Still mandatory to define though.
    parameter_name = ''

    def lookups(self, request, model_admin):
        """
        This defines the filter options.
        """
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        """
        This processes the filter option (defined above, in "lookups") when selected by a user.
        """
        if self.value() == 'yes':
            return queryset.filter(wmu_user__isnull=False)
        if self.value() == 'no':
            return queryset.filter(wmu_user__isnull=True)


class ProfileToUserListFilter(admin.SimpleListFilter):
    """
    Filter for Profile model Admin to show models associated with a valid (login) User model.
    """
    # Label to display for filter.
    title = 'Associated with Login User'

    # Doesn't seem to do anything if you define the "queryset" method. Still mandatory to define though.
    parameter_name = ''

    def lookups(self, request, model_admin):
        """
        This defines the filter options.
        """
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        """
        This processes the filter option (defined above, in "lookups") when selected by a user.
        """
        if self.value() == 'yes':
            return queryset.filter(userintermediary__user__isnull=False)
        if self.value() == 'no':
            return queryset.filter(userintermediary__user__isnull=True)

#endregion Custom Filters


#region User Model Admin

class UserAdmin(BaseUserAdmin):
    # inlines = (ProfileInline, )

    # Fields to display in admin list view.
    list_display = ('username', 'first_name', 'last_name', 'user_type')

    # Fields to filter by in admin list view.
    list_filter = ('is_active', UserCAECenterEmployeeFilter, 'groups', 'is_staff', 'is_superuser')

    # Remove individual permission list from admin detail view. Should only ever use group permissions.
    old_list = BaseUserAdmin.fieldsets[2][1]['fields']
    new_list = ()
    for item in old_list:
        if item != 'user_permissions':
            new_list += (item,)
    BaseUserAdmin.fieldsets[2][1]['fields'] = new_list

    # Hide Contact Info fields. These are redundant and should instead be managed in the WmuUser model.
    new_list = ()
    for item in BaseUserAdmin.fieldsets:
        if item[0] != 'Personal info':
            new_list += (item,)
    BaseUserAdmin.fieldsets = new_list

    def user_type(self, obj):
        """
        Return list of user-associated group(s).
        """
        groups = []
        for group in obj.groups.all():
            groups.append(group.name)
        return ', '.join(groups)


class UserIntermediaryAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('bronco_net',)

    # Fields to search in admin list view.
    search_fields = ('bronco_net',)

    # Fields to filter by in admin list view.
    list_filter = (UserIntermediaryToUserListFilter, UserIntermediaryToWmuUserListFilter)

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Fieldset organization for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('bronco_net',),
        }),
        ('Relations', {
            'fields': ('user', 'wmu_user', 'profile'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'slug', 'date_created', 'date_modified'),
        }),
    )

    # New object's slugs will be automatically set by bronco_net.
    prepopulated_fields = {'slug': ('bronco_net',)}


class WmuUserAdmin(admin.ModelAdmin):
    inlines = (MajorInline,)

    def get_majors(self, obj):
        return ' | '.join([major.student_code for major in obj.major.all()])

    # Fields to display in admin list view.
    list_display = ('bronco_net', 'winno', 'first_name', 'last_name', 'get_majors')

    # Fields to filter by in admin list view.
    list_filter = ('active', 'wmuusermajorrelationship__major__name')

    # Fields to search in admin list view.
    search_fields = ('bronco_net', 'winno', 'first_name', 'last_name')

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified', 'official_email', 'shorthand_email')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('user_type', 'bronco_net', 'winno', 'first_name', 'middle_name', 'last_name'),
        }),
        ('Contact Info', {
            'fields': ('official_email', 'shorthand_email'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'active', 'date_created', 'date_modified'),
        }),
    )


class ProfileAdmin(admin.ModelAdmin):

    # Needed for related field list display.
    def get_bronco_net(self, obj):
        return obj.userintermediary.bronco_net
    get_bronco_net.short_description = 'Bronco Net'
    get_bronco_net.admin_order_field = 'userintermediary__bronco_net'

    # Fields to display in admin list view.
    list_display = ('get_bronco_net', 'address', 'phone_number', 'site_theme')

    # Fields to search in admin list view.
    search_fields = ('userintermediary__bronco_net',)

    # Fields to filter by in admin list view.
    list_filter = (ProfileToUserListFilter,)

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Fieldset organization for admin detail view.
    fieldsets = (
        ('User Info', {
            'fields': ('address', 'phone_number'),
        }),
        ('Site Options', {
            'fields': ('user_timezone', 'site_theme', 'desktop_font_size', 'mobile_font_size'),
        }),
        ('Schedule Colors', {
            'fields': ('fg_color', 'bg_color'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'date_created', 'date_modified'),
        }),
    )


class AddressAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('street', 'optional_street', 'city', 'state', 'zip')

    # Fields to search in admin list view.
    search_fields = ('street', 'city', 'zip')

    # Fields to filter by in admin list view.
    list_filter = ('city', 'state')

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Fieldset organization for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('street', 'optional_street', 'city', 'state', 'zip'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'date_created', 'date_modified'),
        }),
    )


class SiteThemeAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('display_name', 'file_name', 'gold_logo')

    # Fields to search in admin list view.
    search_fields = ('display_name', 'file_name')

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Fieldset organization for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('display_name', 'file_name', 'gold_logo'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'slug', 'date_created', 'date_modified'),
        }),
    )

    # New object's slugs will be automatically set by name.
    prepopulated_fields = {'slug': ('file_name',)}

#endregion User Model Admin


#region WMU Model Admin

class DepartmentAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('name',)

    # Fields to search in admin list view.
    search_fields = ('name',)

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('name',),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'slug', 'date_created', 'date_modified'),
        }),
    )

    # New object's slugs will be automatically set by name.
    prepopulated_fields = {'slug': ('name',)}


class RoomTypeAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('name',)

    # Fields to search in admin list view.
    search_fields = ('name',)

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'slug', 'date_created', 'date_modified'),
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
    list_filter = ('room_type', 'department')

    # Fields to search in admin list view.
    search_fields = ('name', 'capacity')

    # Select2 search fields for admin detail view.
    autocomplete_fields = ('department',)

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('name', 'room_type', 'department', 'description', 'capacity', 'is_row'),
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
    list_display = ('student_code', 'program_code', 'name', 'degree_level', 'department', 'active')

    # Fields to filter by in admin list view.
    list_filter = ('degree_level', 'active')

    # Fields to search in admin list view.
    search_fields = ('department', 'student_code', 'program_code', 'name')

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('name', 'degree_level', 'department', 'active'),
        }),
        ('Degree Codes', {
            'fields': ('student_code', 'program_code'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'slug', 'date_created', 'date_modified'),
        }),
    )

    # New object's slugs will be automatically set by code.
    prepopulated_fields = {'slug': ('student_code',)}


class SemesterDateAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('name', 'start_date', 'end_date')

    # Fields to search in admin list view.
    search_fields = ('name', 'start_date', 'end_date')

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('name', 'start_date', 'end_date'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'date_created', 'date_modified'),
        }),
    )


#endregion WMU Model Admin


#region CAE Model Admin

class AssetAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('brand_name', 'asset_tag', 'serial_number', 'mac_address', 'ip_address')

    # Fields to filter by in admin list view.
    list_filter = ('brand_name',)

    # Fields to search in admin list view.
    search_fields = ('asset_tag', 'serial_number', 'mac_address', 'ip_address')

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': (
                'brand_name', 'asset_tag', 'serial_number', 'mac_address', 'ip_address', 'device_name', 'description'
            ),
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
admin.site.register(models.Asset, AssetAdmin)
