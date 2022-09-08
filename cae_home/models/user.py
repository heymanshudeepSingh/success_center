"""
Definitions of "User" related Core Models.
"""

# System Imports.
import pytz
from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField

# User Imports.
from ..models import Major


MAX_LENGTH = 255


# region Model Functions

def compare_user_and_wmuuser_models(uid):
    """
    Validates user info between login_user model and wmu_user model.
    :param uid: Id (BroncoNet) of user to validate.
    """
    user_model = None
    wmu_user_model = None
    model_updated = False

    # Get UserIntermediary value for user.
    user_intermediary = UserIntermediary.objects.get(bronco_net=uid)

    # Before anything, make sure UserIntermediary has Winno field populated.
    if user_intermediary.winno == '':
        # For now, default to the UserIntermediary's BroncoNet, because that should be unique.
        user_intermediary.winno = user_intermediary.bronco_net
        user_intermediary.save()

    # Attempt to get associated (login) User model.
    try:
        user_model = User.objects.get(username=uid)
    except ObjectDoesNotExist:
        pass    # BroncoNet does not have an associated (login) User model.

    # Attempt to get associated WmuUser model.
    try:
        wmu_user_model = WmuUser.objects.get(bronco_net=uid)
    except ObjectDoesNotExist:
        pass    # BroncoNet does not have an associated WmuUser model.

    # Verify model had at least one of (login) User or WmuUser models.
    if not user_model and not wmu_user_model:
        # BroncoNet somehow does not have an associated (login) User model or WmuUser model.
        raise ValidationError('Could not find associated user models for BroncoNet {0}.'.format(id))

    # Below logic attempts to update corresponding (login) User, WmuUser, and UserIntermediary models.

    # Sync winno values.
    if wmu_user_model:
        # WmuUser model exists.
        if user_intermediary.winno != wmu_user_model.winno:
            user_intermediary.winno = wmu_user_model.winno
            model_updated = True

    # Sync first_name values.
    if user_model and wmu_user_model:
        # Both (login) User and WmuUser models exist.
        if user_model.first_name != wmu_user_model.first_name:
            # WmuUser model has priority for this field. If empty for WmuUser model, fallback to User model value.
            model_updated = True
            first_name = wmu_user_model.first_name.strip()
            if first_name != '':
                user_model.first_name = first_name
            else:
                wmu_user_model.first_name = user_model.first_name
    if user_model:
        # (Login) User exists, so also compare first_name in UserIntermediary.
        if user_intermediary.first_name != user_model.first_name:
            user_intermediary.first_name = user_model.first_name
            model_updated = True
    if wmu_user_model:
        # WmuUser exists, so also compare first_name in UserIntermediary.
        if user_intermediary.first_name != wmu_user_model.first_name:
            user_intermediary.first_name = wmu_user_model.first_name
            model_updated = True

    # Sync last_name values.
    if user_model and wmu_user_model:
        # Both (login) User and WmuUser models exist.
        if user_model.last_name != wmu_user_model.last_name:
            # WmuUser model has priority for this field. If empty for WmuUser model, fallback to User model value.
            model_updated = True
            last_name = wmu_user_model.last_name.strip()
            if last_name != '':
                user_model.last_name = last_name
            else:
                wmu_user_model.last_name = user_model.last_name
    if user_model:
        # (Login) User exists, so also compare last_name in UserIntermediary.
        if user_intermediary.last_name != user_model.last_name:
            user_intermediary.last_name = user_model.last_name
            model_updated = True
    if wmu_user_model:
        # WmuUser exists, so also compare last_name in UserIntermediary.
        if user_intermediary.last_name != wmu_user_model.last_name:
            user_intermediary.last_name = wmu_user_model.last_name
            model_updated = True

    # Sync email values.
    if user_model and wmu_user_model:
        # Both (login) User and WmuUser models exist.
        if (
            user_model.email != wmu_user_model.official_email and
            (wmu_user_model.official_email is not None and wmu_user_model.official_email != '')
        ):
            user_model.email = wmu_user_model.official_email
            model_updated = True

    # Sync is_active values.
    if user_model:
        # (Login) User model exists.

        # if user_intermediary.cae_is_active or user_intermediary.wmu_is_active:
        #     # At least one of the LDAP auths came back as "active". Set (login) User model accordingly.
        #     if not user_model.is_active:
        #         user_model.is_active = True
        #         model_updated = True
        # else:
        #     # Neither LDAP auth came back as "active". Set (login) User model accordingly.
        #     if user_model.is_active:
        #         user_model.is_active = False
        #         user_model.is_staff = False
        #         model_updated = True

        # Previously (above), we tried to set (Login)User is_active value based on the return values of LDAP.
        # However, that had occasional syncing issues, due to main campus LDAP being an unorganized nightmare.
        # Instead, as of summer 2022, we now have manual "set user group" pages for each project.
        #
        # If the (Login)User model has a valid group in one or more of the expected projects, we also set the
        # (Login)User model as active, so that person can access the respective site(s) they need.
        # No valid group means the user is set to inactive, so they cannot login to our projects.
        #
        # Meanwhile, the WmuUser model is_active is set based on either of the LDAP values (CAE or main campus)
        # returning that the user is active.
        user_groups = user_model.groups.all()
        orig_active = user_model.is_active
        orig_staff = user_model.is_staff
        user_model.is_active = False
        user_model.is_staff = False
        for group in user_groups:
            if group.name in (settings.CAE_ADMIN_GROUPS + ['CAE Programmer']):
                user_model.is_staff = True
            if group.name in settings.CAE_CENTER_GROUPS:
                user_model.is_active = True
            if group.name in settings.SUCCESS_CENTER_GROUPS:
                user_model.is_active = True
            if group.name in settings.GRAD_APPS_GROUPS:
                user_model.is_active = True
        # Extra handling for development. Seed users are always set to active + staff.
        if user_model.username in settings.SEED_USERS:
            user_model.is_active = True
            user_model.is_staff = True
        if user_model.is_active != orig_active or user_model.is_staff != orig_staff:
            model_updated = True

    if wmu_user_model:
        # WmuUser model exists.
        if user_intermediary.cae_is_active or user_intermediary.wmu_is_active:
            # At least one of the LDAP auths came back as "active". Set WmuUser model accordingly.
            if not wmu_user_model.is_active:
                wmu_user_model.is_active = True
                model_updated = True
        else:
            # Neither LDAP auth came back as "active". Set WmuUser model accordingly.
            if wmu_user_model.is_active:
                wmu_user_model.is_active = False
                model_updated = True

    # Handle group membership based on is_active status.
    # Note that above, we already iterated over groups and set is_active accordingly.
    # So this is effectively a "safe fallback" for any edge-case scenarios/new logic that we might not have handled for.
    if user_model:
        # (Login) User model exists.
        if user_model.is_active is False:
            # (Login) User is not active.
            if user_model.groups.all().exists():
                # However, model has one or more Auth Group relations. Remove all.
                user_model.groups.clear()
                model_updated = True

    # If any model values were updated, then save all three corresponding models.
    if model_updated:
        if user_model:
            user_model.save()
        if wmu_user_model:
            wmu_user_model.save()
        user_intermediary.save()

    # Handle for potential GradApps membership.
    handle_grad_apps_membership(user_intermediary)

    # Handle if SuccessCtr is installed.
    if 'success_center' in settings.INSTALLED_CAE_PROJECTS:
        # SuccessCtr project is present.
        from apps.Success_Center.success_center_core import models as success_ctr_models

        # Verify that active (Login)User has an associated "SuccessCtr Profile" model.
        if user_model and user_model.is_active:
            user_profile = user_intermediary.profile
            try:
                success_ctr_models.SuccessCtrProfile.objects.get(profile=user_profile)
            except success_ctr_models.SuccessCtrProfile.DoesNotExist:
                # Failed to find profile. Create new one.
                success_ctr_models.SuccessCtrProfile.objects.create(profile=user_profile)


def check_user_group_membership(uid):
    """
    Checks/updates membership of groups for user.
    Aka, specifically the GroupMember ship model, not the auth Group model (these are separate, but related. The auth
    Group one is provided by Django, and tracks general site-access permissions. But does NOT record history of "who
    used to be part of what group, years ago". GroupMembership is custom and specifically tracks history).

    Intended to run on model save.
    """
    user = User.objects.get(username=uid)
    user_auth_groups = user.groups.all()

    # Get list of all current values in user GroupMemberships.
    group_membership_list = GroupMembership.objects.filter(user=user, date_left=None)

    # Loop through current GroupMemberships and update models.
    found_groups = []
    for group_membership in group_membership_list:
        # Save group as having known membership in GroupMemberships.
        found_groups.append(group_membership.group)

        # Find groups user is no longer member of.
        if group_membership.group not in user_auth_groups:
            # User is no longer member. Update GroupMembership.
            group_membership.date_left = timezone.datetime.today()
            group_membership.save()

    # Loop through current group membership and update group dates accordingly.
    for auth_group in user_auth_groups:

        # Find groups user has joined membership of.
        if auth_group not in found_groups:
            GroupMembership.objects.create(user=user, group=auth_group, date_joined=timezone.datetime.today())


def check_all_group_memberships():
    """
    Checks/updates membership of groups for all existing users.
    Aka, specifically the GroupMember ship model, not the auth Group model (these are separate, but related. The auth
    Group one is provided by Django, and tracks general site-access permissions. But does NOT record history of "who
    used to be part of what group, years ago". GroupMembership is custom and specifically tracks history).
    """
    # First, update for active users.
    active_users = User.objects.filter(is_active=True)

    # Loop through all active users.
    for user in active_users:
        check_user_group_membership(user.username)

    # Now, update for inactive users.
    inactive_users = User.objects.filter(is_active=False)

    # Attempt to find any open GroupMembership that reference inactive users.
    group_membership_list = GroupMembership.objects.filter(user__in=inactive_users, date_left=None)

    # End all existing GroupMemberships for inactive users.
    for inactive_group_membership in group_membership_list:
        inactive_group_membership.date_left = timezone.datetime.today()
        inactive_group_membership.save()


def handle_grad_apps_membership(user_intermediary):
    """
    Extra user logic to run when GradApps project is installed.
    Ensures that, if a GradApps user is added or removed, their user model should always have the correct setup,
    so as to not raise errors or lead to "bad"/"unexpected" data states.
    """
    # Only proceed if we have a (Login)user AND WmuUser model.
    if not user_intermediary.user or not user_intermediary.wmu_user:
        return
    # Only proceed if GradApps project is installed.
    if 'grad_applications' not in settings.INSTALLED_CAE_PROJECTS:
        return

    # Pull user fresh to ensure we have most up-to-date data.
    user_id = user_intermediary.user.username
    user = User.objects.get(username=user_id)
    wmu_user = WmuUser.objects.get(bronco_net=user_id)

    # Check for GradApps project groups.
    user_groups = user.groups.all()
    is_grad_member = False
    for group in user_groups:
        if group.name in settings.GRAD_APPS_GROUPS:
            is_grad_member = True

    # Special imports that can't be up top, to avoid circular logic.
    from apps.Grad_Applications.grad_applications_core import models as grad_apps_models
    from cae_home.models import Department
    na_department = Department.objects.get(code='NA')
    default_department = Department.objects.get(code='EDO')

    # Ensure default committees exist.
    try:
        grad_apps_models.Committee.objects.get(department=na_department)
    except grad_apps_models.Committee.DoesNotExist:
        grad_apps_models.Committee.objects.create(department=na_department, is_active=True)
    try:
        default_committee = grad_apps_models.Committee.objects.get(department=default_department)
    except grad_apps_models.Committee.DoesNotExist:
        default_committee = grad_apps_models.Committee.objects.create(department=default_department, is_active=True)

    if is_grad_member:
        # Handle if is GradApps member.
        try:
            # Attempt to grab CommitteeMember.
            grad_apps_models.CommitteeMember.objects.get(faculty=wmu_user, is_active=True)

        except grad_apps_models.CommitteeMember.DoesNotExist:
            # CommitteeMember does not exist. Create new one.
            grad_apps_models.CommitteeMember.objects.create(
                faculty=wmu_user,
                committee=default_committee,
                start_date=timezone.now(),
                is_active=True,
            )

    else:
        # Handle if not GradApps member.
        # Disable any active CommitteeMember models.
        committee_member_models = grad_apps_models.CommitteeMember.objects.filter(faculty=wmu_user, is_active=True)
        for committee_member_model in committee_member_models:
            committee_member_model.is_active = False
            if committee_member_model.leave_date is None:
                committee_member_model.leave_date = timezone.now().date()
            committee_member_model.save()

# endregion Model Functions


# region Model Intermediaries

class WmuUserMajorRelationship(models.Model):
    """
    WmuUser and Major model many-to-many relationship.
    """
    # Relationship keys.
    wmu_user = models.ForeignKey('WmuUser', on_delete=models.CASCADE)
    major = models.ForeignKey('Major', on_delete=models.CASCADE)

    # Model fields.
    is_active = models.BooleanField(default=True)
    date_started = models.DateTimeField(default=timezone.now)
    date_stopped = models.DateTimeField(blank=True, null=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'WmuUser to Major Relationship'
        verbose_name_plural = 'WmuUser to Major Relationships'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._previous_active_value = self.is_active

    def clean(self, *args, **kwargs):
        """
        Custom cleaning implementation. Includes validation, setting fields, etc.
        """
        # Check if model's "active" field has changed, and is now inactive.
        # Means WmuUser is no longer pursuing Major. Either they graduated and got the degree or switched majors.
        if self.is_active != self._previous_active_value and not self.is_active:
            # Set date when student stopped pursuing Major.
            self.date_stopped = timezone.now()

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def check_if_user_has_major_active(wmu_user, major):
        """
        Checks for relation where wmu_user is associated with major and actively pursuing it.
        :param wmu_user: WmuUser model object to check against.
        :param major: Major model object to check against.
        :return: Boolean indicating if student is actively pursuing major.
        """
        if WmuUserMajorRelationship.objects.filter(wmu_user=wmu_user, major=major, is_active=True).exists():
            # Relation exists where "active" field is True. User is actively pursuing major.
            return True
        else:
            # Relation does not exist where active is True. User is not actively pursuing major.
            return False

# endregion Model Intermediaries


# region Models

class User(AbstractUser):
    """
    An extension of Django's default user, allowing for additional functionality.
    One of three User model types. Contains all information directly related to Django authentication.
    """
    @staticmethod
    def get_or_create_superuser(username, email, password):
        """
        Attempts to either get or create user with the given information.
        """
        try:
            new_user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            new_user = User.objects.create_superuser(username, email, password)
        return new_user

    @staticmethod
    def get_or_create_user(username, email, password, inactive=False):
        """
        Attempts to either get or create user with given information.
        """
        new_user, created = User.objects.get_or_create(username=username, email=email)
        if isinstance(new_user, tuple):
            new_user = new_user[0]

        # If user was newly created, set new password.
        if created:
            new_user.set_password(password)
            if inactive:
                new_user.is_active = False
                new_user.userintermediary.cae_is_active = False
                new_user.userintermediary.wmu_is_active = False
            new_user.save()
        else:
            new_user.set_password(password)
            new_user.save()

        return new_user

    @staticmethod
    def get_cae_users():
        """
        Returns set of all active attendants, admins, and programmers for the CAE Center.
        """
        return User.objects.filter(
            is_active=True
        ).filter(
            Q(groups__name='CAE Attendant') |
            Q(groups__name='CAE Admin') | Q(groups__name='CAE Admin GA') |
            Q(groups__name='CAE Programmer') | Q(groups__name='CAE Programmer GA')
        ).distinct()

    @staticmethod
    def get_cae_admins():
        """
        Returns set of all active admins for the CAE Center.
        """
        return User.objects.filter(
            is_active=True
        ).filter(
            Q(groups__name='CAE Admin') | Q(groups__name='CAE Admin GA')
        )

    @staticmethod
    def get_cae_programmers():
        """
        Returns set of all active programmers for the CAE Center.
        """
        return User.objects.filter(
            is_active=True
        ).filter(
            Q(groups__name='CAE Programmer') | Q(groups__name='CAE Programmer GA')
        ).distinct()

    @staticmethod
    def get_cae_ga():
        """
        Returns set of all active GA users for the CAE Center.
        """
        return User.objects.filter(
            is_active=True
        ).filter(
            Q(groups__name='CAE Admin GA') | Q(groups__name='CAE Programmer GA')
        ).distinct()

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.
        Used for testing.
        """
        return User.get_or_create_user('dummy_user', 'dummy@gmail.com', settings.USER_SEED_PASSWORD)


class GroupMembership(models.Model):
    """
    Retains the dates in which a user was part of a given group.
    """
    # Relationship Keys.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_membership')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    # Model fields.
    date_joined = models.DateField(default=timezone.datetime.today)
    date_left = models.DateField(blank=True, null=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Group Membership'
        verbose_name_plural = 'Group Memberships'

    def __str__(self):
        return '{0} - {1}: {2} - {3}'.format(self.user, self.group, self.date_joined, self.date_left)

    def clean(self, *args, **kwargs):
        """
        Custom cleaning implementation. Includes validation, setting fields, etc.
        """

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super().save(*args, **kwargs)


class UserIntermediary(models.Model):
    """
    Intermediary to connect the three User model types: (login) User models, user Profile models, and WmuUser models.
    """
    # Relationship Keys.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    wmu_user = models.OneToOneField('cae_home.WMUUser', on_delete=models.CASCADE, blank=True, null=True)
    profile = models.OneToOneField('Profile', on_delete=models.CASCADE, blank=True, null=True)

    # Model fields.
    bronco_net = models.CharField(max_length=MAX_LENGTH, blank=True, unique=True)
    winno = models.CharField(max_length=MAX_LENGTH, blank=True, default='')
    first_name = models.CharField(max_length=MAX_LENGTH, blank=True)
    last_name = models.CharField(max_length=MAX_LENGTH, blank=True)

    # LDAP sync values.
    # Note that the two is_active values default to True.
    # This is so that authentication when LDAP is disabled (such as in development) doesn't automatically disable users.
    # If LDAP is enabled, then the below values should set to proper values on first login so it doesn't matter.
    cae_is_active = models.BooleanField(default=True, help_text='Tracks if CAE LDAP says user is active.')
    wmu_is_active = models.BooleanField(default=True, help_text='Tracks if WMU LDAP says user is active.')
    last_ldap_check = models.DateField(default=timezone.now, help_text='Date of user\'s last sync with LDAP.')

    # Self-setting/Non-user-editable fields.
    slug = models.SlugField(
        max_length=MAX_LENGTH,
        unique=True,
        help_text='Used for urls referencing this User and related models.',
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Intermediary'
        verbose_name_plural = 'User Intermediaries'

    def __str__(self):
        return '{0}'.format(self.bronco_net)

    def clean(self, *args, **kwargs):
        """
        Custom cleaning implementation. Includes validation, setting fields, etc.
        """
        # Check that at least one of either "User" or "WmuUser" is provided.
        if self.user is None and self.wmu_user is None:
            raise ValidationError('Must have relation to either "User" or "WmuUser" model.')

        # Set fields on model creation.
        if self.pk is None:
            # Attempt to pull bronco_net from login model. Otherwise, get from wmu_user model.
            if self.user is not None:
                self.bronco_net = self.user.username
            else:
                self.bronco_net = self.wmu_user.bronco_net

            # Set slug.
            self.slug = slugify(self.bronco_net)
        else:
            # Do not allow null profiles after initial creation.
            if self.profile is None:
                raise ValidationError('Must have associated user profile model.')

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.clean()    # Seems to error on validation without this line.
        self.full_clean()
        super().save(*args, **kwargs)


class WmuUser(models.Model):
    """
    An entity with WMU ldap credentials.
    One of three User model types. Contains all information directly related Wmu LDAP information.
    Generally will be a student, professor, or faculty.
    """
    # Preset field choices.
    STUDENT = 0
    PROFESSOR = 1
    FACULTY = 2
    OTHER = 3
    USER_TYPE_CHOICES = (
        (STUDENT, 'Student'),
        (PROFESSOR, 'Professor'),
        (FACULTY, 'Faculty'),
        (OTHER, 'Other'),
    )

    # Relationship keys.
    major = models.ManyToManyField('Major', through=WmuUserMajorRelationship, blank=True)

    # Model fields.
    bronco_net = models.CharField(max_length=MAX_LENGTH, unique=True)
    winno = models.CharField(max_length=MAX_LENGTH, unique=True)
    first_name = models.CharField(max_length=MAX_LENGTH)
    middle_name = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    last_name = models.CharField(max_length=MAX_LENGTH)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=0)
    is_active = models.BooleanField(default=True)

    # Self-setting/Non-user-editable fields.
    official_email = models.EmailField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'WMU User'
        verbose_name_plural = 'WMU Users'

    def __str__(self):
        return '{0}: {1} {2}'.format(self.bronco_net, self.first_name, self.last_name)

    def clean(self, *args, **kwargs):
        """
        Custom cleaning implementation. Includes validation, setting fields, etc.
        """
        # Make sure there is always some value for official email.
        if self.official_email is None or self.official_email == '':
            self.official_email = self.shorthand_email()

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super().save(*args, **kwargs)

    def shorthand_email(self):
        """
        Returns a string of student's shorthand email.
        """
        return '{0}@wmich.edu'.format(self.bronco_net)

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.

        Useful for when UnitTesting requires an instance of this model,
        but test does not care what values the model actually has.
        """
        # Define "dummy model" values.
        major = Major.create_dummy_model()
        bronco_net = 'dummy123'
        winno = 'dummy12345'
        first_name = 'Dummy First'
        last_name = 'Dummy Last'

        # Attempt to get corresponding model instance, if there is one.
        try:
            wmu_user = WmuUser.objects.get(
                bronco_net=bronco_net,
                winno=winno,
                first_name=first_name,
                last_name=last_name,
            )
        except WmuUser.DoesNotExist:
            # Instance not found. Create new model.
            wmu_user = WmuUser.objects.create(
                bronco_net=bronco_net,
                winno=winno,
                first_name=first_name,
                last_name=last_name,
            )

            # Also add relationship of WmuUser to Major.
            WmuUserMajorRelationship.objects.create(
                wmu_user=wmu_user,
                major=major,
            )

        # Return "dummy model" instance.
        return wmu_user


class Profile(models.Model):
    """
    A profile for a given user.
    One of three User model types. Contains all site settings, plus any info that doesn't fit within the other two User
    model types.
    """
    # Preset field choices.
    FONT_XS = 0
    FONT_SM = 1
    FONT_BASE = 2
    FONT_MD = 3
    FONT_LG = 4
    FONT_XL = 5
    FONT_SIZE_CHOICES = (
        (FONT_XS, 'Extra Small'),
        (FONT_SM, 'Small'),
        (FONT_BASE, 'Default'),
        (FONT_MD, 'Medium'),
        (FONT_LG, 'Large'),
        (FONT_XL, 'Extra Large'),
    )

    # Relationship Keys.
    address = models.ForeignKey('Address', on_delete=models.CASCADE, blank=True, null=True)
    site_theme = models.ForeignKey('SiteTheme', on_delete=models.CASCADE, blank=True)

    # Model fields.
    phone_number = PhoneNumberField(blank=True, null=True)
    user_timezone = models.CharField(
        choices=[(x, x) for x in pytz.common_timezones], blank=True, default='America/Detroit',
        max_length=255
    )
    desktop_font_size = models.PositiveSmallIntegerField(choices=FONT_SIZE_CHOICES, blank=True, default=2)
    mobile_font_size = models.PositiveSmallIntegerField(choices=FONT_SIZE_CHOICES, blank=True, default=2)
    fg_color = models.CharField(
        blank=True,
        help_text='Foreground css color for schedule. E.g. "red" or "#FF0000"',
        max_length=30,
    )
    bg_color = models.CharField(
        blank=True,
        help_text='Foreground css color for schedule. E.g. "red" or "#FF0000"',
        max_length=30,
    )
    employee_shift_display_default = models.BooleanField(default=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        try:
            return '{0}'.format(self.userintermediary.bronco_net)
        except Profile.userintermediary.RelatedObjectDoesNotExist:
            # Profile for a User that had associated models deleted.
            # Ideally, the profile should be deleted as well so this never occurs.
            return 'Deleted User Profile'

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def get_font_size(self, value):
        """
        Return text description for font size options.
        """
        if value == 0:
            return 'xs'
        elif value == 1:
            return 'sm'
        elif value == 3:
            return 'md'
        elif value == 4:
            return 'lg'
        elif value == 5:
            return 'xl'
        else:
            return 'base'

    def get_desktop_font_size(self, value=None):
        """
        Return text description for profile's desktop font size.
        """
        if value is None:
            value = self.desktop_font_size
        return self.get_font_size(value)

    def get_mobile_font_size(self, value=None):
        """
        Return text description for profile's mobile font size.
        """
        if value is None:
            value = self.mobile_font_size
        return self.get_font_size(value)

    def get_official_email(self):
        """
        Return official email for user profile.
        """
        return '{0}@wmich.edu'.format(self.userintermediary.bronco_net)

    @staticmethod
    def get_profile(bronco_net):
        """
        Given a valid bronco id, return the associated profile.
        """
        try:
            user_intermediary = UserIntermediary.objects.get(bronco_net=bronco_net)
            return user_intermediary.profile
        except UserIntermediary.DoesNotExist:
            return None


class Address(models.Model):
    """
    Address for a user.
    """
    # Preset field choices.
    STATE_CHOICES = (
        (0, 'AL - Alabama'),
        (1, 'AK - Alaska'),
        (2, 'AZ - Arizona'),
        (3, 'AR - Arkansas'),
        (4, 'CA - California'),
        (5, 'CO - Colorado'),
        (6, 'CT - Connecticut'),
        (7, 'DE - Delaware'),
        (8, 'FL - Florida'),
        (9, 'GA - Georgia'),
        (10, 'HI - Hawaii'),
        (11, 'ID - Idaho'),
        (12, 'IL - Illinois'),
        (13, 'IN - Indiana'),
        (14, 'IA - Iowa'),
        (15, 'KS - Kansas'),
        (16, 'KY - Kentucky'),
        (17, 'LA - Louisiana'),
        (18, 'ME - Maine'),
        (19, 'MD - Maryland'),
        (20, 'MA - Massachusetts'),
        (21, 'MI - Michigan'),
        (22, 'MN - Minnesota'),
        (23, 'MS - Mississippi'),
        (24, 'MO - Missouri'),
        (25, 'MT - Montana'),
        (26, 'NE - Nebraska'),
        (27, 'NV - Nevada'),
        (28, 'NH - New Hampshire'),
        (29, 'NJ - New Jersey'),
        (30, 'NM - New Mexico'),
        (31, 'NY - New York'),
        (32, 'NC - North Carolina'),
        (33, 'ND - North Dakota'),
        (34, 'OH - Ohio'),
        (35, 'OK - Oklahoma'),
        (36, 'OR - Oregon'),
        (37, 'PA - Pennsylvannia'),
        (38, 'RI - Rhode Island'),
        (39, 'SC - South Carolina'),
        (40, 'SD - South Dakota'),
        (41, 'TN - Tennessee'),
        (42, 'TX - Texas'),
        (43, 'UT - Utah'),
        (44, 'VT - Vermont'),
        (45, 'VA - Virginia'),
        (46, 'WA - Washington'),
        (47, 'WV - West Virginia'),
        (48, 'WI - Wisconsin'),
        (49, 'WY - Wyoming'),
    )

    # Model fields.
    street = models.CharField(max_length=MAX_LENGTH)
    optional_street = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    city = models.CharField(max_length=MAX_LENGTH)
    state = models.PositiveSmallIntegerField(choices=STATE_CHOICES, default=21)
    zip = models.CharField(max_length=7)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        unique_together = ('street', 'optional_street', 'city', 'state', 'zip')

    def __str__(self):
        if self.optional_street is not None:
            return '{0} {1} {2}, {3}, {4}'.format(
                self.street,
                self.optional_street,
                self.city,
                self.get_state_abbrev_as_string(),
                self.zip
            )
        else:
            return '{0} {1}, {2}, {3}'.format(
                self.street,
                self.city,
                self.get_state_abbrev_as_string(),
                self.zip
            )

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super().save(*args, **kwargs)

    def get_state_as_string(self, value=None):
        """
        Returns state name as string.
        :param value: Integer of value to get. If none, uses current model value.
        :return: State name.
        """
        if value is None:
            value = self.state
        state_string = self.STATE_CHOICES[value][1][5:]
        return state_string

    def get_state_abbrev_as_string(self, value=None):
        """
        Returns state abbreviation as string.
        :param value: Integer of value to get. If none, uses current model value.
        :return: State abbreviation.
        """
        if value is None:
            value = self.state
        state_string = self.STATE_CHOICES[value][1][:2]
        return state_string

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.

        Useful for when UnitTesting requires an instance of this model,
        but test does not care what values the model actually has.
        """
        # Define "dummy model" values.
        street = '1234 Dummy Lane'
        optional_street = 'Apt 1234'
        city = 'Kalamazoo'
        state = 21
        zip = '49008'

        # Attempt to get corresponding model instance, if there is one.
        try:
            address = Address.objects.get(
                street=street,
                optional_street=optional_street,
                city=city,
                state=state,
                zip=zip
            )
        except Address.DoesNotExist:
            # Instance not found. Create new model.
            address = Address.objects.create(
                street=street,
                optional_street=optional_street,
                city=city,
                state=state,
                zip=zip
            )

        # Return "dummy model" instance.
        return address


class SiteTheme(models.Model):
    """
    A theme for the site. Users can select these to change the site's overall look.
    """
    # Model fields.
    display_name = models.CharField(max_length=MAX_LENGTH, unique=True)     # The value displayed to users.
    file_name = models.CharField(max_length=MAX_LENGTH, unique=True)        # The value used in files and templating.
    gold_logo = models.BooleanField(default=True)
    ordering = models.PositiveSmallIntegerField(default=0)

    # Self-setting/Non-user-editable fields.
    slug = models.SlugField(
        max_length=MAX_LENGTH,
        unique=True,
        help_text='Used for urls referencing this Site Theme.',
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Theme'
        verbose_name_plural = 'Site Themes'
        ordering = ('ordering', 'display_name')

    def __str__(self):
        return '{0}'.format(str(self.display_name))

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.
        Used for testing.
        """
        # Define "dummy model" values.
        name = 'Dummy Site Theme'
        slug = slugify(name)

        # Attempt to get corresponding model instance, if there is one.
        try:
            site_theme = SiteTheme.objects.get(
                display_name=name,
                file_name=slug,
                slug=slug,
            )
        except SiteTheme.DoesNotExist:
            # Instance not found. Create new model.
            site_theme = SiteTheme.objects.create(
                display_name=name,
                file_name=slug,
                slug=slug,
            )

        # Return "dummy model" instance.
        return site_theme

# endregion Models
