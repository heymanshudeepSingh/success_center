"""
Command to update GroupMembership models for all existing users.
"""

# System Imports.
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

# User Imports.
from cae_home.models.user import check_all_group_memberships


class Command(BaseCommand):
    help = 'Updates GroupMembership models for all existing users.'

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        # Run function from models.py file.
        check_all_group_memberships()
