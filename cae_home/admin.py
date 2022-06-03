"""
Admin view for CAE Home app.
"""

# System Imports.
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Permission
from django.urls import reverse
from django.utils.html import mark_safe

# User Class Imports.
from . import models

# Attempt to import RoomEvent Inline.
try:
    from apps.CAE_Web.cae_web_core.admin import RoomEventInline
except ImportError:
    # Assume that CAE_Web project isn't present.
    RoomEventInline = None

CAE_CENTER_GROUPS = [
    'CAE Director', 'CAE Building Coordinator',
    'CAE Admin GA', 'CAE Admin',
    'CAE Programmer GA', 'CAE Programmer',
    'CAE Attendant',
    'CAE Director Inactive',
    'CAE Building Coordinator Inactive',
    'CAE Attendant Inactive',
    'CAE Admin Inactive',
    'CAE Programmer Inactive',
]


# region Model Inlines

class MajorInline(admin.TabularInline):
    model = models.WmuUser.major.through
    extra = 1


class GroupMembershipInline(admin.TabularInline):
    model = models.GroupMembership
    extra = 0


# endregion Model Inlines


# region Custom Filters

class UserToCAECenterEmployeeListFilter(admin.SimpleListFilter):
    """
    Filter for (login) User model Admin to show models associated with a CAE Center employee.
    """
    # Label to display for filter.
    title = 'Is CAE Employee'

    # This is the name used in the url for this filter.
    # Can be set to anything you want, as long as it's unique to other filters in this model.
    parameter_name = 'cae_user'

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
            return queryset.filter(groups__name__in=CAE_CENTER_GROUPS).distinct()
        if self.value() == 'no':
            return queryset.exclude(groups__name__in=CAE_CENTER_GROUPS).distinct()


class UserToWmuUserListFilter(admin.SimpleListFilter):
    """
    Filter for (login) User model Admin to show models associated with a valid WmuUser model.
    """
    # Label to display for filter.
    title = 'Associated with WMU User'

    # This is the name used in the url for this filter.
    # Can be set to anything you want, as long as it's unique to other filters in this model.
    parameter_name = 'wmu_user'

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
            return queryset.filter(userintermediary__wmu_user__isnull=False)
        if self.value() == 'no':
            return queryset.filter(userintermediary__wmu_user__isnull=True)


class UserIntermediaryToUserListFilter(admin.SimpleListFilter):
    """
    Filter for UserIntermediary model Admin to show models associated with a valid (login) User model.
    """
    # Label to display for filter.
    title = 'Associated with Login User'

    # This is the name used in the url for this filter.
    # Can be set to anything you want, as long as it's unique to other filters in this model.
    parameter_name = 'login_user'

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

    # This is the name used in the url for this filter.
    # Can be set to anything you want, as long as it's unique to other filters in this model.
    parameter_name = 'wmu_user'

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


class WmuUserToUserListFilter(admin.SimpleListFilter):
    """
    Filter for WmuUser model Admin to show models associated with a valid (login) User model.
    """
    # Label to display for filter.
    title = 'Associated with Login User'

    # This is the name used in the url for this filter.
    # Can be set to anything you want, as long as it's unique to other filters in this model.
    parameter_name = 'login_user'

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


class WmuUserToCaeUserListFilter(admin.SimpleListFilter):
    """
    Filter for WmuUser model Admin to show models associated with a (Login) User that is a CAE Center employee.
    """
    # Label to display for filter.
    title = 'CAE Employee'

    # This is the name used in the url for this filter.
    # Can be set to anything you want, as long as it's unique to other filters in this model.
    parameter_name = 'cae_employee'

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
        # First get all models that have an associated (login) User model.
        cae_user_list = queryset.filter(userintermediary__user__isnull=False)

        # Next, further filter to get only users associated with a CAE Center group.
        cae_user_list = cae_user_list.filter(userintermediary__user__groups__name__in=CAE_CENTER_GROUPS).distinct()

        if self.value() == 'yes':
            return cae_user_list
        if self.value() == 'no':
            # Get all Pk's of known CAE Users.
            cae_user_list = cae_user_list.values_list('id')

            # Get query by excluding any users where the pk matches a known CAE User.
            return queryset.exclude(id__in=cae_user_list)


class WmuUserToMajorListFilter(admin.SimpleListFilter):
    """
    Filter for WmuUser model Admin to show models associated with a Major model.
    """
    # Label to display for filter.
    title = 'Major'

    # This is the name used in the url for this filter.
    # Can be set to anything you want, as long as it's unique to other filters in this model.
    parameter_name = 'major'

    def lookups(self, request, model_admin):
        """
        This defines the filter options.
        """
        majors = models.Major.objects.all()
        major_list = []
        for major in majors:
            major_list.append((major.slug, major.name))
        return major_list

    def queryset(self, request, queryset):
        """
        This processes the filter option (defined above, in "lookups") when selected by a user.
        """
        major_filter = request.GET.get('major', '')
        if major_filter != '':
            return queryset.filter(major__slug=major_filter)


class ProfileToUserListFilter(admin.SimpleListFilter):
    """
    Filter for Profile model Admin to show models associated with a valid (login) User model.
    """
    # Label to display for filter.
    title = 'Associated with Login User'

    # This is the name used in the url for this filter.
    # Can be set to anything you want, as long as it's unique to other filters in this model.
    parameter_name = 'login_user'

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


class ProfileToWmuUserListFilter(admin.SimpleListFilter):
    """
    Filter for Profile model Admin to show models associated with a valid WmuUser model.
    """
    # Label to display for filter.
    title = 'Associated with WMU User'

    # This is the name used in the url for this filter.
    # Can be set to anything you want, as long as it's unique to other filters in this model.
    parameter_name = 'wmu_user'

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
            return queryset.filter(userintermediary__wmu_user__isnull=False)
        if self.value() == 'no':
            return queryset.filter(userintermediary__wmu_user__isnull=True)


class MajorToDepartmentListFilter(admin.SimpleListFilter):
    """
    Filter for Major model Admin to show models associated with Department.
    """
    # Label to display for filter.
    title = 'Department'

    # This is the name used in the url for this filter.
    # Can be set to anything you want, as long as it's unique to other filters in this model.
    parameter_name = 'department'

    def lookups(self, request, model_admin):
        """
        This defines the filter options.
        """
        departments = models.Department.objects.all()
        department_list = []
        for department in departments:
            department_list.append((department.slug, department.name))
        return department_list

    def queryset(self, request, queryset):
        """
        This processes the filter option (defined above, in "lookups") when selected by a user.
        """
        department_filter = request.GET.get('department', '')
        if department_filter != '':
            return queryset.filter(department__slug=department_filter)


class SemesterDateToYearListFilter(admin.SimpleListFilter):
    """
    Filter for Semester Date model Admin to show models associated with a given year.
    """
    # Label to display for filter.
    title = 'Year'

    # This is the name used in the url for this filter.
    # Can be set to anything you want, as long as it's unique to other filters in this model.
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        """
        This defines the filter options.
        """
        semester_dates = models.Semester.objects.all()
        year_list = []
        for semester_date in semester_dates:
            year = semester_date.start_date.year
            if (year, year) not in year_list:
                year_list.append((year, year))
        return year_list

    def queryset(self, request, queryset):
        """
        This processes the filter option (defined above, in "lookups") when selected by a user.
        """
        year_filter = request.GET.get('year', '')
        if year_filter != '':
            return queryset.filter(start_date__year=year_filter)


class SoftwareDetailToSoftwareListFilter(admin.SimpleListFilter):
    """
    Filter for SoftwareDetail model Admin to show models associated with Software.
    """
    # Label to display for filter.
    title = 'Software'

    # This is the name used in the url for this filter.
    # Can be set to anything you want, as long as it's unique to other filters in this model.
    parameter_name = 'software'

    def lookups(self, request, model_admin):
        """
        This defines the filter options.
        """
        software = models.Software.objects.all()
        software_list = []
        for item in software:
            software_list.append((item.slug, item.name))
        return software_list

    def queryset(self, request, queryset):
        """
        This processes the filter option (defined above, in "lookups") when selected by a user.
        """
        software_filter = request.GET.get('software', '')
        if software_filter != '':
            return queryset.filter(software__slug=software_filter)


class SoftwareExpiryToYearListFilter(admin.SimpleListFilter):
    """
    Filter for SoftwareDetail model Admin to show models associated with a given expiration year.
    """
    # Label to display for filter.
    title = 'Year'

    # This is the name used in the url for this filter.
    # Can be set to anything you want, as long as it's unique to other filters in this model.
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        """
        This defines the filter options.
        """
        software_details = models.SoftwareDetail.objects.all()
        year_list = []
        for software_detail in software_details:
            expiration = software_detail.expiration
            if expiration is not None:
                year = expiration.year
                if (year, year) not in year_list:
                    year_list.append((year, year))
            else:
                if ('None', 'None') not in year_list:
                    year_list = [('None', 'None')] + year_list
        return year_list

    def queryset(self, request, queryset):
        """
        This processes the filter option (defined above, in "lookups") when selected by a user.
        """
        year_filter = request.GET.get('year', '')
        if year_filter != '':
            if year_filter == 'None':
                return queryset.filter(expiration__year__isnull=True)
            else:
                return queryset.filter(expiration__year=year_filter)


# endregion Custom Filters


# region User Model Admin

class UserAdmin(BaseUserAdmin):
    inlines = (GroupMembershipInline,)

    # Fields to display in admin list view.
    list_display = ('username', 'get_winno', 'first_name', 'last_name', 'get_user_groups')
    if settings.DEBUG:
        list_display = ('id',) + list_display

    # Fields to filter by in admin list view.
    list_filter = (
        'is_active',
        UserToCAECenterEmployeeListFilter,
        'groups',
        UserToWmuUserListFilter,
        'is_staff',
        'is_superuser',
    )

    # Remove individual permission list from admin detail view. Should only ever use group permissions.
    old_list = BaseUserAdmin.fieldsets[2][1]['fields']
    new_list = ()
    for item in old_list:
        if item != 'user_permissions':
            new_list += (item,)
    BaseUserAdmin.fieldsets[2][1]['fields'] = new_list

    # # Hide Contact Info fields. These are redundant and should instead be managed in the WmuUser model.
    # new_list = ()
    # for item in BaseUserAdmin.fieldsets:
    #     if item[0] != 'Personal info':
    #         new_list += (item,)
    # BaseUserAdmin.fieldsets = new_list

    # Update fieldset default first row to have a title.
    updated_first_row = ('Login Info', BaseUserAdmin.fieldsets[0][1]),
    new_fieldsets = ()
    for index in range(len(BaseUserAdmin.fieldsets)):
        if index == 0:
            new_fieldsets += updated_first_row
        else:
            new_fieldsets += (BaseUserAdmin.fieldsets[index],)
    BaseUserAdmin.fieldsets = new_fieldsets

    # Add related model links to fieldsets.
    new_first_row = (None, {
        'fields': ('related_models',),
    }),
    updated_fieldsets = new_first_row + BaseUserAdmin.fieldsets
    BaseUserAdmin.fieldsets = updated_fieldsets

    # Update hidden fields.
    BaseUserAdmin.readonly_fields += ('related_models',)

    def get_winno(self, obj):
        """
        Return associated winno from WmuUser model, if present.
        """
        try:
            return '{0}'.format(obj.userintermediary.wmu_user.winno)
        except AttributeError:
            return ''

    get_winno.short_description = 'Winno'
    get_winno.admin_order_field = 'userintermediary__wmu_user__winno'

    def get_user_groups(self, obj):
        """
        Return list of user-associated group(s).
        """
        groups = []
        for group in obj.groups.all():
            groups.append(group.name)
        return ', '.join(groups)

    get_user_groups.short_description = 'User Groups'

    def related_models(self, obj):
        """
        Creates string of related models, for ease of Admin navigation.
        """
        related_model_str = ''

        # Handle if related WmuUser exists.
        if obj.userintermediary.wmu_user is not None:
            # Get FK url.
            fk_link = reverse('admin:cae_home_wmuuser_change', args=[obj.userintermediary.wmu_user.id])
            fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, 'WmuUser Model'))

            # Add to string.
            if related_model_str != '':
                related_model_str += '&nbsp; &nbsp; | &nbsp; &nbsp;'
            related_model_str += fk_link

        # Handle for related UserIntermediary.
        # Get FK url.
        fk_link = reverse('admin:cae_home_userintermediary_change', args=[obj.userintermediary.id])
        fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, 'UserIntermediary Model'))

        # Add to string.
        if related_model_str != '':
            related_model_str += '&nbsp; &nbsp; | &nbsp; &nbsp;'
        related_model_str += fk_link

        # Handle if related Profile exists (it should, unconditionally. But check anyways to be safe).
        if obj.userintermediary.profile is not None:
            fk_link = reverse('admin:cae_home_profile_change', args=[obj.userintermediary.profile.id])
            fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, 'Profile Model'))

            # Add to string.
            if related_model_str != '':
                related_model_str += '&nbsp; &nbsp; | &nbsp; &nbsp;'
            related_model_str += fk_link

        # Return formatted string.
        return mark_safe(related_model_str)

    related_models.short_description = 'Related Models'


class GroupMembershipAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('user', 'group', 'date_joined', 'date_left')
    if settings.DEBUG:
        list_display = ('id',) + list_display

    # Fields to filter by in admin list view.
    list_filter = ('user', 'group')

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified', 'related_models',)

    # Fieldset organization for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('related_models',),
        }),
        ('General', {
            'fields': ('user', 'group', 'date_joined', 'date_left'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'date_created', 'date_modified'),
        }),
    )

    def related_models(self, obj):
        """
        Creates string of related models, for ease of Admin navigation.
        """
        related_model_str = ''

        # Get FK url.
        fk_link = reverse('admin:cae_home_user_change', args=[obj.user.id])
        fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, 'Associated User Model'))

        # Add to string.
        related_model_str += fk_link

        # Return formatted string.
        return mark_safe(related_model_str)

    related_models.short_description = 'Related Models'


class UserIntermediaryAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('bronco_net', 'get_winno', 'first_name', 'last_name')
    if settings.DEBUG:
        list_display = ('id',) + list_display

    # list_display_links = ('(Login) User', 'WmuUser')

    # Default field ordering in admin list view.
    ordering = ('-cae_is_active', '-wmu_is_active', 'bronco_net')

    # Fields to filter by in admin list view.
    list_filter = (
        'cae_is_active',
        'wmu_is_active',
        UserIntermediaryToUserListFilter,
        UserIntermediaryToWmuUserListFilter,
    )

    # Fields to search in admin list view.
    search_fields = ('bronco_net', 'wmu_user__winno', 'first_name', 'last_name')

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified', 'related_models')

    # Fieldset organization for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('related_models',),
        }),
        ('General', {
            'fields': ('bronco_net', 'winno', 'first_name', 'last_name'),
        }),
        ('Relations', {
            'fields': ('user', 'wmu_user', 'profile'),
        }),
        ('User Active', {
            'fields': ('cae_is_active', 'wmu_is_active'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'last_ldap_check', 'slug', 'date_created', 'date_modified'),
        }),
    )

    # New object's slugs will be automatically set by bronco_net.
    prepopulated_fields = {'slug': ('bronco_net',)}

    def get_winno(self, obj):
        """
        Return associated winno from WmuUser model, if present.
        """
        try:
            return '{0}'.format(obj.wmu_user.winno)
        except AttributeError:
            return ''

    get_winno.short_description = 'Winno'
    get_winno.admin_order_field = 'wmu_user__winno'

    def related_models(self, obj):
        """
        Creates string of related models, for ease of Admin navigation.
        """
        related_model_str = ''

        # Handle if related (login) User exists.
        if obj.user is not None:
            # Get FK url.
            fk_link = reverse('admin:cae_home_user_change', args=[obj.user.id])
            fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, '(Login) User Model'))

            # Add to string.
            related_model_str += fk_link

        # Handle if related WmuUser exists.
        if obj.wmu_user is not None:
            # Get FK url.
            fk_link = reverse('admin:cae_home_wmuuser_change', args=[obj.wmu_user.id])
            fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, 'WmuUser Model'))

            # Add to string.
            if related_model_str != '':
                related_model_str += '&nbsp; &nbsp; | &nbsp; &nbsp;'
            related_model_str += fk_link

        # Handle if related Profile exists (it should, unconditionally. But check anyways to be safe).
        if obj.profile is not None:
            fk_link = reverse('admin:cae_home_profile_change', args=[obj.profile.id])
            fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, 'Profile Model'))

            # Add to string.
            if related_model_str != '':
                related_model_str += '&nbsp; &nbsp; | &nbsp; &nbsp;'
            related_model_str += fk_link

        # Return formatted string.
        return mark_safe(related_model_str)

    related_models.short_description = 'Related Models'


class WmuUserAdmin(admin.ModelAdmin):
    inlines = (MajorInline,)

    # Fields to display in admin list view.
    list_display = ('bronco_net', 'winno', 'first_name', 'last_name', 'get_majors', 'get_user_groups')
    if settings.DEBUG:
        list_display = ('id',) + list_display

    # Default field ordering in admin list view.
    ordering = ('-is_active', 'bronco_net')

    # Fields to filter by in admin list view.
    list_filter = ('is_active', WmuUserToUserListFilter, WmuUserToCaeUserListFilter, WmuUserToMajorListFilter)

    # Fields to search in admin list view.
    search_fields = ('bronco_net', 'winno', 'first_name', 'last_name')

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified', 'official_email', 'shorthand_email', 'related_models')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('related_models',),
        }),
        ('General', {
            'fields': ('user_type', 'bronco_net', 'winno', 'first_name', 'middle_name', 'last_name'),
        }),
        ('Contact Info', {
            'fields': ('official_email', 'shorthand_email'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'is_active', 'date_created', 'date_modified'),
        }),
    )

    def get_majors(self, obj):
        """
        Return list of user's majors.
        """
        return ' | '.join([major.student_code for major in obj.major.all()])

    get_majors.short_description = 'Majors'

    def get_user_groups(self, obj):
        """
        Return list of user-associated group(s).
        """
        try:
            groups = []
            for group in obj.userintermediary.user.groups.all():
                groups.append(group.name)
            return ', '.join(groups)
        except AttributeError:
            return ''

    get_user_groups.short_description = 'User Groups'

    def related_models(self, obj):
        """
        Creates string of related models, for ease of Admin navigation.
        """
        related_model_str = ''

        # Handle if related (login) User exists.
        if obj.userintermediary.user is not None:
            # Get FK url.
            fk_link = reverse('admin:cae_home_user_change', args=[obj.userintermediary.user.id])
            fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, '(Login) User Model'))

            # Add to string.
            related_model_str += fk_link

        # Handle for related UserIntermediary.
        # Get FK url.
        fk_link = reverse('admin:cae_home_userintermediary_change', args=[obj.userintermediary.id])
        fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, 'UserIntermediary Model'))

        # Add to string.
        if related_model_str != '':
            related_model_str += '&nbsp; &nbsp; | &nbsp; &nbsp;'
        related_model_str += fk_link

        # Handle if related Profile exists (it should, unconditionally. But check anyways to be safe).
        if obj.userintermediary.profile is not None:
            fk_link = reverse('admin:cae_home_profile_change', args=[obj.userintermediary.profile.id])
            fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, 'Profile Model'))

            # Add to string.
            if related_model_str != '':
                related_model_str += '&nbsp; &nbsp; | &nbsp; &nbsp;'
            related_model_str += fk_link

        # Return formatted string.
        return mark_safe(related_model_str)

    related_models.short_description = 'Related Models'


class ProfileAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('get_bronco_net', 'get_winno', 'get_first_name', 'get_last_name', 'phone_number', 'site_theme')
    if settings.DEBUG:
        list_display = ('id',) + list_display

    # Default field ordering in admin list view.
    ordering = ('-userintermediary__cae_is_active', '-userintermediary__wmu_is_active', 'userintermediary__bronco_net')

    # Fields to filter by in admin list view.
    list_filter = (ProfileToUserListFilter, ProfileToWmuUserListFilter)

    # Fields to search in admin list view.
    search_fields = (
        'userintermediary__bronco_net',
        'userintermediary__wmu_user__winno',
        'userintermediary__first_name',
        'userintermediary__last_name',
    )

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified', 'related_models')

    # Fieldset organization for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('related_models',),
        }),
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

    def get_bronco_net(self, obj):
        """
        Return associated BroncoNet.
        """
        return '{0}'.format(obj.userintermediary.bronco_net)

    get_bronco_net.short_description = 'Bronco Net'
    get_bronco_net.admin_order_field = 'userintermediary__bronco_net'

    def get_winno(self, obj):
        """
        Return associated winno from WmuUser model, if present.
        """
        try:
            return '{0}'.format(obj.userintermediary.wmu_user.winno)
        except AttributeError:
            return ''

    get_winno.short_description = 'Winno'
    get_winno.admin_order_field = 'userintermediary__wmu_user__winno'

    def get_first_name(self, obj):
        """
        Return associated First Name.
        """
        return '{0}'.format(obj.userintermediary.first_name)

    get_first_name.short_description = 'First Name'
    get_first_name.admin_order_field = 'userintermediary__first_name'

    def get_last_name(self, obj):
        """
        Return associated Last Name.
        """
        return '{0}'.format(obj.userintermediary.last_name)

    get_last_name.short_description = 'Last Name'
    get_last_name.admin_order_field = 'userintermediary__last_name'

    def related_models(self, obj):
        """
        Creates string of related models, for ease of Admin navigation.
        """
        related_model_str = ''

        # Handle if related (login) User exists.
        if obj.userintermediary.user is not None:
            # Get FK url.
            fk_link = reverse('admin:cae_home_user_change', args=[obj.userintermediary.user.id])
            fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, '(Login) User Model'))

            # Add to string.
            related_model_str += fk_link

        # Handle if related WmuUser exists.
        if obj.userintermediary.wmu_user is not None:
            # Get FK url.
            fk_link = reverse('admin:cae_home_wmuuser_change', args=[obj.userintermediary.wmu_user.id])
            fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, 'WmuUser Model'))

            # Add to string.
            if related_model_str != '':
                related_model_str += '&nbsp; &nbsp; | &nbsp; &nbsp;'
            related_model_str += fk_link

        # Handle for related UserIntermediary.
        # Get FK url.
        fk_link = reverse('admin:cae_home_userintermediary_change', args=[obj.userintermediary.id])
        fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, 'UserIntermediary Model'))

        # Add to string.
        if related_model_str != '':
            related_model_str += '&nbsp; &nbsp; | &nbsp; &nbsp;'
        related_model_str += fk_link

        # Return formatted string.
        return mark_safe(related_model_str)

    related_models.short_description = 'Related Models'


class AddressAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('street', 'optional_street', 'city', 'state', 'zip')
    if settings.DEBUG:
        list_display = ('id',) + list_display

    # Default field ordering in admin list view.
    ordering = ('state', 'city', 'street', 'optional_street')

    # Fields to filter by in admin list view.
    list_filter = ('city', 'state')

    # Fields to search in admin list view.
    search_fields = ('street', 'optional_street', 'city', 'zip')

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
    if settings.DEBUG:
        list_display = ('id',) + list_display

    # Default field ordering in admin list view.
    ordering = ('display_name',)

    # Fields to filter by in admin list view.
    list_filter = ()

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


# endregion User Model Admin


# region WMU Model Admin
class StudentHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'get_first_name', 'get_last_name', 'get_winno', "check_has_bachelors", "check_has_masters",)

    def get_first_name(self, obj):
        """
        Return associated first name.
        """
        return '{0}'.format(obj.wmu_user.first_name)

    get_first_name.short_description = 'First Name'
    get_first_name.admin_order_field = 'wmu_user__first_name'

    def get_last_name(self, obj):
        """
        Return associated last name.
        """
        return '{0}'.format(obj.wmu_user.last_name)

    get_last_name.short_description = 'Last Name'
    get_last_name.admin_order_field = 'wmu_user__last_name'

    def get_winno(self, obj):
        """
        Return associated last name.
        """
        return '{0}'.format(obj.wmu_user.winno)

    get_winno.short_description = 'Win Number'
    get_winno.admin_order_field = 'wmu_user__winno'

    def check_has_bachelors(self, obj):
        """
        check  if the student has bachelors
        """
        if obj.bachelors_gpa == 0:
            return False
        else:
            return True

    check_has_bachelors.short_description = 'Has Bachelors'
    check_has_bachelors.boolean = True

    def check_has_masters(self, obj):
        """
        check  if the student has masters
        """
        if obj.masters_gpa == 0:
            return False
        else:
            return True

    check_has_masters.short_description = 'Has Masters'
    check_has_masters.boolean = True


class DepartmentAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('name',)
    if settings.DEBUG:
        list_display = ('id',) + list_display

    # Default field ordering in admin list view.
    ordering = ('name',)

    # Fields to filter by in admin list view.
    list_filter = ()

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


class WmuClassAdmin(admin.ModelAdmin):
    """"""
    list_display = ('code', 'title', 'department')
    if settings.DEBUG:
        list_display = ('id',) + list_display

    # Default field ordering in admin list view.
    ordering = ('code', 'title', 'department')

    # Fields to search in admin list view.
    search_fields = ('code',)

    readonly_fields = ('id', 'date_created', 'date_modified')

    fieldsets = (
        (None, {
            'fields': ('code', 'title', 'description',),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'slug', 'date_created', 'date_modified'),
        }),
    )

    # New object's slugs will be automatically set by department.
    prepopulated_fields = {'slug': ('code',)}


class RoomTypeAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('name',)
    if settings.DEBUG:
        list_display = ('id',) + list_display

    # Default field ordering in admin list view.
    ordering = ('name',)

    # Fields to filter by in admin list view.
    list_filter = ()

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
    # Check that the inline import succeeded.
    if RoomEventInline is not None:
        inlines = (RoomEventInline,)

    # Fields to display in admin list view.
    list_display = ('name', 'room_type', 'get_departments')
    if settings.DEBUG:
        list_display = ('id',) + list_display

    # Fields to filter by in admin list view.
    list_filter = ('name',)

    # Fields to search in admin list view.
    search_fields = ('name',)

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

    def get_departments(self, obj):
        """
        Return associated Department.
        """
        dept_list = ''
        for department in obj.department.all():
            dept_list += '{0} | '.format(department.name)
        return dept_list[:-3]

    get_departments.short_description = 'Departments'


class MajorAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('student_code', 'program_code', 'name', 'degree_level', 'department', 'is_active')
    if settings.DEBUG:
        list_display = ('id',) + list_display

    # Default field ordering in admin list view.
    ordering = ('department', 'program_code')

    # Fields to filter by in admin list view.
    list_filter = ('is_active', 'degree_level', MajorToDepartmentListFilter)

    # Fields to search in admin list view.
    search_fields = ('student_code', 'program_code', 'name', 'department__name')

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('name', 'degree_level', 'department', 'is_active'),
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
    if settings.DEBUG:
        list_display = ('id',) + list_display

    # Default field ordering in admin list view.
    ordering = ('-start_date', '-end_date')

    # Fields to filter by in admin list view.
    list_filter = (SemesterDateToYearListFilter,)

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


# endregion WMU Model Admin


# region CAE Model Admin

class AssetAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('brand_name', 'asset_tag', 'serial_number', 'mac_address', 'ip_address')
    if settings.DEBUG:
        list_display = ('id',) + list_display

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


class SoftwareAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('name',)
    if settings.DEBUG:
        list_display = ('id',) + list_display

    # Fields to search in admin list view.
    search_fields = ['name', ]

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

    # New object's slugs will be automatically set by code.
    prepopulated_fields = {'slug': ('name',)}


class SoftwareDetailAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('software', 'version', 'expiration', 'software_type')
    if settings.DEBUG:
        list_display = ('id',) + list_display

    # Fields to filter by in admin list view.
    list_filter = (SoftwareDetailToSoftwareListFilter, SoftwareExpiryToYearListFilter)

    # Fields to search in admin list view.
    search_fields = ['version', 'expiration', 'software']

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('software', 'software_type', 'version', 'expiration', 'is_active')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'slug', 'date_created', 'date_modified',),
        }),
    )

    # New object's slugs will be automatically set by code.
    prepopulated_fields = {'slug': ('software', 'version')}


# endregion CAE Model Admin


# User Model Registration.
admin.site.register(models.User, UserAdmin)
admin.site.register(Permission)
admin.site.register(models.GroupMembership, GroupMembershipAdmin)
admin.site.register(models.UserIntermediary, UserIntermediaryAdmin)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.Address, AddressAdmin)
admin.site.register(models.SiteTheme, SiteThemeAdmin)

# WMU Model Registration.
admin.site.register(models.WmuUser, WmuUserAdmin)
admin.site.register(models.StudentHistory, StudentHistoryAdmin)
admin.site.register(models.Department, DepartmentAdmin)
admin.site.register(models.WmuClass, WmuClassAdmin)
admin.site.register(models.RoomType, RoomTypeAdmin)
admin.site.register(models.Room, RoomAdmin)
admin.site.register(models.Major, MajorAdmin)
admin.site.register(models.Semester, SemesterDateAdmin)

# CAE Model Registration.
admin.site.register(models.Asset, AssetAdmin)
admin.site.register(models.Software, SoftwareAdmin)
admin.site.register(models.SoftwareDetail, SoftwareDetailAdmin)
