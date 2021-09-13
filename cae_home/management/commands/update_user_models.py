"""
Command that uses LDAP to verify what uses are "active" or not.
Updates (login) User models accordingly.

LDAP verification logic is courtesy of Tyler, roughly 2018 to 2019-ish.
"""

# System Imports.
import random
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

# User Class Imports.
from cae_home import models
from cae_home.models.user import compare_user_and_wmuuser_models
from workspace.ldap_backends.wmu_auth import cae_backend, wmu_backend


class Command(BaseCommand):
    help = 'Updates project User models, based on pulled LDAP properties.'

    def add_arguments(self, parser):
        """
        Parser for command.
        """
        # Optional arguments.
        parser.add_argument(
            'user',
            type=str,
            nargs='?',
            default='',
            help='Single user to explicitly update. If not provided, then attempts to update all User/WmuUser models.',
        )
        parser.add_argument(
            '--update_all',
            action='store_true',
            help='If True, then will unconditionally attempt to update all existing models. Otherwise, will only try '\
            'to update models that have not updated in a while.',
        )

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        user_value = str(kwargs['user']).strip()
        update_all_bool = kwargs['update_all']

        # Check if single user value was provided. In most cases, it will not be.
        if user_value is None or user_value == '':
            # No user explicitly provided. Update all.
            handled_list = self.handle_login_user_models(update_all_bool)
            self.handle_wmu_user_models(handled_list, update_all_bool)
        else:
            # User explicitly provided. Attempt to update.
            self.handle_single_user(user_value)

    def handle_login_user_models(self, update_all_bool):
        """
        Iterates through existing and "active" (login) User models.

        For any records that haven't been checked against Ldap for more than a month, they are unconditionally checked.

        Otherwise, there is a 1/30 chance of checking anyways. This means each record should (on average) be handled
        once a month, on a completely random day of the month. This is to avoid having large chunks of users potentially
        do Ldap calls all on one single day.

        For similar handling of WmuUser models, see handle_wmu_user_models().
        :param update_all_bool: Boolean to override RNG logic, and force updating of all models.
        """
        wmu_auth = wmu_backend.WmuAuthBackend()

        # Get list of all active user models.
        active_user_list = get_user_model().objects.filter(is_active=True)
        handled_list = []
        non_ldap_usernames = ['step_admin']

        # Check for "update_all_bool".
        # If True, we automatically set all user model "last ldap check" values to two months ago.
        # This guarantees all user models will have update logic ran.
        if update_all_bool:
            for user_model in active_user_list:
                # Check for custom/special UserNames to exclude from LDAP logic.
                if str(user_model.username).strip() not in non_ldap_usernames:

                    # Get date of "two months ago".
                    two_months_ago = timezone.localdate() - timezone.timedelta(days=60)

                    # Set "last ldap check" field to above date.
                    user_model.userintermediary.last_ldap_check = two_months_ago
                    user_model.userintermediary.save()

        # Loop through all known active users.
        for user_model in active_user_list:
            last_user_ldap_check = user_model.userintermediary.last_ldap_check

            # Check for custom/special UserNames to exclude from LDAP logic.
            if str(user_model.username).strip() not in non_ldap_usernames:

                # To avoid flooding main campus LDAP with a bunch of calls on a single day, do calls randomly.
                # We want to check (login) User is_active once a month, so give approximately a one in 30 chance.
                # Assumes one call per night.
                if random.randint(1, 30) == 1:
                    # RNG has dictated we check this user's ldap info.
                    handled_list = self.login_user_update(wmu_auth, user_model, handled_list)
                else:
                    # RNG didn't dictate we check user.
                    # However, run anyways if it's been more than a full month since last LDAP check.
                    month_ago = timezone.now().date() - timezone.timedelta(days=30)
                    if last_user_ldap_check < month_ago:
                        # Check user's Ldap info.
                        handled_list = self.login_user_update(wmu_auth, user_model, handled_list)

        return handled_list

    def login_user_update(self, wmu_auth, user_model, handled_list):
        """
        Logic to actually update a given (login) User model.
        :param wmu_auth: Initialized Wmu Auth backend.
        :param user_model: (Login) User model to update.
        :param handled_list: List to hold all (login) User models that have been updated so far.
        :return: Updated handled_list variable.
        """
        print('Updating User "{0}"'.format(user_model))

        # First, sync existing Django database model data for user.
        # Usually not needed, but occasionally required such as when adding new database fields.
        compare_user_and_wmuuser_models(user_model.username)

        # Update user data using LDAP.
        wmu_auth.create_or_update_user_model(user_model.username)

        # Add user to handled list, to avoid potentially re-running update logic in WmuUser update function.
        handled_list.append(str(user_model.username).strip())

        return handled_list

    def handle_wmu_user_models(self, handled_list, update_all_bool):
        """
        Iterates through existing and "active" WmuUser models.

        For any records that haven't been checked against Ldap for more than two months, they are unconditionally
        checked.

        Otherwise, there is a 1/60 chance of checking anyways. This means each record should (on average) be handled
        once a month, on a completely random day of the month. This is to avoid having large chunks of users potentially
        do Ldap calls all on one single day.

        For similar handling of (login) User models, see handle_login_user_models().
        :param handled_list: List of all users already handled in (login) User update function.
        :param update_all_bool: Boolean to override RNG logic, and force updating of all models.
        """
        wmu_auth = wmu_backend.WmuAuthBackend()

        # Get list of all active user models.
        active_user_list = models.WmuUser.objects.filter(is_active=True)
        non_ldap_usernames = ['ceas_cae', 'ceas_prog']

        # Check for "update_all_bool".
        # If True, we automatically set all user model "last ldap check" values to two months ago.
        # This guarantees all user models will have update logic ran.
        if update_all_bool:
            for user_model in active_user_list:
                # Check for custom/special UserNames to exclude from LDAP logic.
                # Also exclude any users that were handled in the (login) User model function (above)
                if (
                    str(user_model.bronco_net).strip() not in non_ldap_usernames and
                    str(user_model.bronco_net).strip() not in handled_list
                ):
                    # Get date of "two months ago".
                    two_months_ago = timezone.localdate() - timezone.timedelta(days=60)

                    # Set "last ldap check" field to above date.
                    user_model.userintermediary.last_ldap_check = two_months_ago
                    user_model.userintermediary.save()

        for wmu_user_model in active_user_list:
            last_user_ldap_check = wmu_user_model.userintermediary.last_ldap_check

            # Check for custom/special UserNames to exclude from LDAP logic.
            if str(wmu_user_model.bronco_net).strip() not in non_ldap_usernames:

                # Verify we didn't already handle this user in (login) User logic, above.
                if str(wmu_user_model.bronco_net).strip() not in handled_list:

                    # To avoid flooding main campus LDAP with a bunch of calls on a single day, do calls randomly.
                    # We want to check (login) User is_active once a month, so give approximately a one in 30 chance.
                    # Assumes one call per night.
                    if update_all_bool or random.randint(1, 60) == 1:
                        # RNG has dictated we check this user's ldap info.
                        self.wmu_user_update(wmu_auth, wmu_user_model)
                    else:
                        # RNG didn't dictate we check user.
                        # However, run anyways if it's been more than a full month since last LDAP check.
                        two_months_ago = timezone.now().date() - timezone.timedelta(days=60)
                        if last_user_ldap_check < two_months_ago:
                            # Check user's Ldap info.
                            self.wmu_user_update(wmu_auth, wmu_user_model)

    def wmu_user_update(self, wmu_auth, wmu_user_model):
        """
        Logic to actually update a given WmuUser model.
        :param wmu_auth: Initialized Wmu Auth backend.
        :param wmu_user_model: WmuUser model to update.
        """
        print('Updating WmuUser "{0}"'.format(wmu_user_model))

        # First, sync existing Django database model data for user.
        # Usually not needed, but occasionally required such as when adding new database fields.
        compare_user_and_wmuuser_models(wmu_user_model.bronco_net)

        # Update user data using LDAP.
        wmu_auth.create_or_update_wmu_user_model(wmu_user_model.bronco_net)

    def handle_single_user(self, user_value):
        """
        Effectively runs the above two logic functions, but only for the User/WmuUser model(s) associated with a single
        user.

        This function is mostly to be used for debugging/testing, or for explicitly updating in instances of production
        errors/troubleshooting/etc.
        :param user_value: BroncoNet or Winno of user to update.
        """
        print('Running single user logic for "{0}".'.format(user_value))
        wmu_auth = wmu_backend.WmuAuthBackend()

        # First attempt to update User model, if one is associated with provided value.
        # Note that updating a User model also updates associated WmuUser models.
        user_intermediary_model = None
        try:
            # First search by BroncoNet.
            user_intermediary_model = models.UserIntermediary.objects.get(bronco_net=user_value)
            print('Found UserIntermediary model.')
        except models.UserIntermediary.DoesNotExist:
            # Failed to find by BroncoNet. Try by Winno.
            try:
                user_intermediary_model = models.UserIntermediary.objects.get(winno=user_value)
                print('Found UserIntermediary model.')
            except models.UserIntermediary.DoesNotExist:
                # Failed to find by BroncoNet or Winno. User/Wmu model does not exist for provided value.
                print('Could not find UserIntermediary model.')

        # Handle if new user. This is indicated by no UserIntermediary model existing.
        if user_intermediary_model is None:
            # Attempt to create associated (login) User model.
            wmu_auth.create_or_update_user_model(user_value)

            # Attempt to create associated WmuUser model.
            wmu_auth.create_or_update_wmu_user_model(user_value)

            # Attempt again to get user_intermediary.
            try:
                # First search by BroncoNet.
                user_intermediary_model = models.UserIntermediary.objects.get(bronco_net=user_value)
                print('Found UserIntermediary model.')
            except models.UserIntermediary.DoesNotExist:
                # Failed to find by BroncoNet. Try by Winno.
                try:
                    user_intermediary_model = models.UserIntermediary.objects.get(winno=user_value)
                    print('Found UserIntermediary model.')
                except models.UserIntermediary.DoesNotExist:
                    # Failed to find by BroncoNet or Winno. User/Wmu model does not exist for provided value.
                    print('Could not find UserIntermediary model.')

        # Run update logic on user.
        if user_intermediary_model.user is not None:
            # (Login) User model exists for associated UserIntermediary. Run updates with that.
            self.login_user_update(wmu_auth, user_intermediary_model.user, [])

        elif user_intermediary_model.wmu_user is not None:
            # WmuUser model exists for UserIntermediary. Run updates with that.
            self.wmu_user_update(wmu_auth, user_intermediary_model.wmu_user)

        else:
            # Neither (login) User or WmuUser models exist for UserIntermediary. This shouldn't ever happen.
            raise ValueError(
                'UserIntermediary of "{0}" does not seem to have associated User or WmuUser models.'.format(
                    user_intermediary_model,
                )
            )
