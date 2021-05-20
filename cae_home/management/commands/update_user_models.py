"""
Command that uses LDAP to verify what uses are "active" or not.
Updates (login) User models accordingly.

LDAP verification logic is courtesy of Tyler.
"""

# System Imports.
import random
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

# User Class Imports.
from cae_home import models
from workspace.ldap_backends.wmu_auth import cae_backend, wmu_backend


class Command(BaseCommand):
    help = 'Updates project User models, based on pulled LDAP properties.'

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        handled_list = self.handle_login_user_models()
        self.handle_wmu_user_models(handled_list)

    def handle_login_user_models(self):
        """
        Iterates through existing and "active" (login) User models.

        For any records that haven't been checked against Ldap for more than a month, they are unconditionally checked.

        Otherwise, there is a 1/30 chance of checking anyways. This means each record should (on average) be handled
        once a month, on a completely random day of the month. This is to avoid having large chunks of users potentially
        do Ldap calls all on one single day.

        For similar handling of WmuUser models, see handle_wmu_user_models().
        """
        wmu_auth = wmu_backend.WmuAuthBackend()

        # Get list of all active user models.
        active_user_list = get_user_model().objects.filter(is_active=True)
        handled_list = []

        for user_model in active_user_list:
            last_user_ldap_check = user_model.userintermediary.last_ldap_check

            # Check for custom/special UserNames to exclude from LDAP logic.
            if str(user_model.username).strip() not in ['step_admin']:

                # To avoid flooding main campus LDAP with a bunch of calls on a single day, do calls randomly.
                # We want to check (login) User is_active once a month, so give approximately a one in 30 chance.
                # Assumes one call per night.
                if random.randint(1, 30) == 1:
                    # RNG has dictated we check this user's ldap info.
                    wmu_auth.create_or_update_user_model(user_model.username)
                    handled_list.append(str(user_model.username).strip())
                else:
                    # RNG didn't dictate we check user.
                    # However, run anyways if it's been more than a full month since last LDAP check.
                    month_ago = timezone.now().date() - timezone.timedelta(days=30)
                    if last_user_ldap_check < month_ago:
                        # Check user's Ldap info.
                        wmu_auth.create_or_update_user_model(user_model.username)
                        handled_list.append(str(user_model.username).strip())

        return handled_list

    def handle_wmu_user_models(self, handled_list):
        """
        Iterates through existing and "active" WmuUser models.

        For any records that haven't been checked against Ldap for more than two months, they are unconditionally
        checked.

        Otherwise, there is a 1/60 chance of checking anyways. This means each record should (on average) be handled
        once a month, on a completely random day of the month. This is to avoid having large chunks of users potentially
        do Ldap calls all on one single day.

        For similar handling of (login) User models, see handle_login_user_models().
        """
        wmu_auth = wmu_backend.WmuAuthBackend()

        # Get list of all active user models.
        active_user_list = models.WmuUser.objects.filter(is_active=True)

        for user_model in active_user_list:
            last_user_ldap_check = user_model.userintermediary.last_ldap_check

            # Check for custom/special UserNames to exclude from LDAP logic.
            if str(user_model.bronco_net).strip() not in ['ceas_cae', 'ceas_prog']:

                # Verify we didn't already handle this user in (login) User logic, above.
                if str(user_model.bronco_net).strip() not in handled_list:

                    # To avoid flooding main campus LDAP with a bunch of calls on a single day, do calls randomly.
                    # We want to check (login) User is_active once a month, so give approximately a one in 30 chance.
                    # Assumes one call per night.
                    if random.randint(1, 60) == 1:
                        # RNG has dictated we check this user's ldap info.
                        wmu_auth.create_or_update_wmu_user_model(user_model.bronco_net)
                    else:
                        # RNG didn't dictate we check user.
                        # However, run anyways if it's been more than a full month since last LDAP check.
                        two_months_ago = timezone.now().date() - timezone.timedelta(days=60)
                        if last_user_ldap_check < two_months_ago:
                            # Check user's Ldap info.
                            wmu_auth.create_or_update_wmu_user_model(user_model.bronco_net)
