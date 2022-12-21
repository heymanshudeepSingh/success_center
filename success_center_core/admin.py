"""
Admin views for Success Center Core app.
"""

# System Imports.
from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.html import mark_safe

# User Imports.
from . import models


class SuccessCtrProfileAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('get_bronco_net', 'get_winno', 'default_tutor_location')
    if settings.DEBUG:
        list_display = ('id',) + list_display

    # Default field ordering in admin list view.
    ordering = (
        '-profile__userintermediary__cae_is_active',
        '-profile__userintermediary__wmu_is_active',
        'profile__userintermediary__bronco_net',
    )

    # Fields to search in admin list view.
    search_fields = (
        'profile__userintermediary__bronco_net',
        'profile__userintermediary__wmu_user__winno',
        'profile__userintermediary__first_name',
        'profile__userintermediary__last_name',
    )

    # Read only fields for admin detail view.
    readonly_fields = ('id', 'date_created', 'date_modified', 'related_models')

    # Fieldset organization for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('related_models',),
        }),
        ('Location', {
            'fields': ('default_tutor_location',),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('id', 'date_created', 'date_modified'),
        }),
    )

    class Media:
        js = ['admin/js/list_filter_collapse.js']

    def get_bronco_net(self, obj):
        """
        Return associated BroncoNet from UserIntermediary model, if present.
        """
        try:
            return '{0}'.format(obj.profile.userintermediary.bronco_net)
        except AttributeError:
            return ''

    get_bronco_net.short_description = 'Winno'
    get_bronco_net.admin_order_field = 'profile__userintermediary__bronco_net'

    def get_winno(self, obj):
        """
        Return associated winno from WmuUser model, if present.
        """
        try:
            return '{0}'.format(obj.profile.userintermediary.wmu_user.winno)
        except AttributeError:
            return ''

    get_winno.short_description = 'Winno'
    get_winno.admin_order_field = 'profile__userintermediary__wmu_user__winno'

    def related_models(self, obj):
        """
        Creates string of related models, for ease of Admin navigation.
        """
        related_model_str = ''

        # Handle if related (login) User exists.
        if obj.profile.userintermediary.user is not None:
            # Get FK url.
            fk_link = reverse('admin:cae_home_user_change', args=[obj.profile.userintermediary.user.id])
            fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, '(Login) User Model'))

            # Add to string.
            related_model_str += fk_link

        # Handle if related WmuUser exists.
        if obj.profile.userintermediary.wmu_user is not None:
            # Get FK url.
            fk_link = reverse('admin:cae_home_wmuuser_change', args=[obj.profile.userintermediary.wmu_user.id])
            fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, 'WmuUser Model'))

            # Add to string.
            if related_model_str != '':
                related_model_str += '&nbsp; &nbsp; | &nbsp; &nbsp;'
            related_model_str += fk_link

        # Handle for related UserIntermediary.
        # Get FK url.
        fk_link = reverse('admin:cae_home_userintermediary_change', args=[obj.profile.userintermediary.id])
        fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, 'UserIntermediary Model'))

        # Add to string.
        if related_model_str != '':
            related_model_str += '&nbsp; &nbsp; | &nbsp; &nbsp;'
        related_model_str += fk_link

        # Handle if related Profile exists (it should, unconditionally. But check anyways to be safe).
        if obj.profile is not None:
            fk_link = reverse('admin:cae_home_profile_change', args=[obj.profile.id])
            fk_link = mark_safe('<a href="{0}">{1}</a>'.format(fk_link, 'Profile Model'))

            # Add to string.
            related_model_str += '&nbsp; &nbsp; | &nbsp; &nbsp;'
            related_model_str += fk_link

        # Return formatted string.
        return mark_safe(related_model_str)

    related_models.short_description = 'Related Models'


# Model Registration.
admin.site.register(models.StudentUsageLog)
admin.site.register(models.TutorLocations)
admin.site.register(models.SuccessCtrProfile, SuccessCtrProfileAdmin)
