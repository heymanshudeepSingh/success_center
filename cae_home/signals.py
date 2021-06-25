"""
Signals for CAE Home app.
"""

# System Imports.
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.management import call_command
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from os import devnull

# User Class Imports.
from . import models
from .models.user import compare_user_and_wmuuser_models, check_user_group_membership


@receiver(post_save, sender=models.User)
def user_model_post_save(sender, instance, created, **kwargs):
    """
    Post-save handling for User model.
    """
    # Handling for associated User model.
    if created:
        # Handle for new (login) User being created. Attempt to find existing Intermediary with bronco_net.
        # On failure, create new UserIntermediary instance.
        try:
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=instance.username)

            # Check that User has not been provided to UserIntermediary.
            if user_intermediary.user is not None:
                raise ValidationError('User Intermediary model already has associated User model.')
            else:
                user_intermediary.user = instance
                user_intermediary.save()
        except ObjectDoesNotExist:
            models.UserIntermediary.objects.create(user=instance)
    else:
        # Just updating an existing UserIntermediary. Save.
        instance.userintermediary.save()

    # Check that values are consistent between user models.
    # First disconnect related post_save signals to prevent recursion errors.
    post_save.disconnect(user_model_post_save, sender=models.User)
    post_save.disconnect(userintermediary_model_post_save, sender=models.UserIntermediary)
    post_save.disconnect(wmuuser_model_post_save, sender=models.WmuUser)

    # Run comparison method to sync AuthUser and WmuUser models.
    compare_user_and_wmuuser_models(instance.username)

    # Run logic to update group membership dates.
    # Note that we have to wait for the full transaction to complete, as per:
    # https://stackoverflow.com/questions/1925383/issue-with-manytomany-relationships-not-updating-immediately-after-save
    # https://stackoverflow.com/questions/950214/run-code-after-transaction-commit-in-django
    transaction.on_commit(
        lambda: check_user_group_membership(instance.username)
    )

    # Reconnect related post_save signals.
    post_save.connect(user_model_post_save, sender=models.User)
    post_save.connect(userintermediary_model_post_save, sender=models.UserIntermediary)
    post_save.connect(wmuuser_model_post_save, sender=models.WmuUser)


@receiver(post_save, sender=models.UserIntermediary)
def userintermediary_model_post_save(sender, instance, created, **kwargs):
    """
    Post-save handling for UserIntermediary model.
    """
    # Handling for associated Profile model.
    if created:
        # Handle for new UserIntermediary being created. Create new profile as well.
        try:
            # Attempt to get default theme.
            site_theme = models.SiteTheme.objects.get(slug='wmu')
        except ObjectDoesNotExist:
            # Failed to get theme. Likely a unit test. Run site_theme fixtures and attempt again.
            with open(devnull, 'a') as null:
                call_command('loaddata', 'production_models/site_themes', stdout=null)
            site_theme = models.SiteTheme.objects.get(slug='wmu')

        # Create new profile object for new user.
        profile = models.Profile.objects.create(site_theme=site_theme)

        # Associate profile with UserIntermediary.
        instance.profile = profile

        # Set "last ldap check" value such that user will be ran on next script execution.
        instance.last_ldap_check = timezone.now() - timezone.timedelta(days=365)

        # Save all changes to UserIntermediary model.
        instance.save()

    else:
        # Just updating an existing profile. Save.
        instance.profile.save()


@receiver(post_save, sender=models.WmuUser)
def wmuuser_model_post_save(sender, instance, created, **kwargs):
    """
    Post-save handling for Wmu User model.
    """
    # Handling for associated User Intermediary model.
    if created:
        # Handle for new WmuUser being created. Attempt to find existing Intermediary with bronco_net.
        # On failure, create new UserIntermediary instance.
        try:
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=instance.bronco_net)

            # Check that WmuUser has not been provided to UserIntermediary.
            if user_intermediary.wmu_user is not None:
                raise ValidationError('User Intermediary model already has associated WmuUser model.')
            else:
                user_intermediary.wmu_user = instance
                user_intermediary.save()
        except ObjectDoesNotExist:
            models.UserIntermediary.objects.create(wmu_user=instance)
    else:
        # Just updating an existing UserIntermediary. Save.
        instance.userintermediary.save()

    # Check that values are consistent between user models.
    # First disconnect related post_save signals to prevent recursion errors.
    post_save.disconnect(user_model_post_save, sender=models.User)
    post_save.disconnect(userintermediary_model_post_save, sender=models.UserIntermediary)
    post_save.disconnect(wmuuser_model_post_save, sender=models.WmuUser)

    # Run comparison method.
    compare_user_and_wmuuser_models(instance.bronco_net)

    # Reconnect related post_save signals.
    post_save.connect(user_model_post_save, sender=models.User)
    post_save.connect(userintermediary_model_post_save, sender=models.UserIntermediary)
    post_save.connect(wmuuser_model_post_save, sender=models.WmuUser)
