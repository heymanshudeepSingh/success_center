"""
Tests for CAE Home User app Models.

Note: Below "GroupMembershipModelTests" should work in theory.
    But the model signals don't seem to trigger in UnitTests, which is effectively what is being tested.
    StackOverflow had some supposed solutions, but they're from old version of Django and no longer seem to work.
    Fix test at a later date.
"""

# System Imports.
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from phonenumber_field.phonenumber import PhoneNumber

# User Class Imports.
from .. import models
from cae_home.management.commands.fixtures.user import create_groups
from cae_home.management.commands.fixtures.wmu import create_departments
from cae_home.tests.utils import IntegrationTestCase


# class GroupMembershipModelTests(IntegrationTestCase):
#     """
#     Tests to ensure valid GroupMembership model creation/logic.
#     """
#     @classmethod
#     def setUpTestData(cls):
#         # Get current date.
#         cls.now = timezone.localdate()
#
#         # Create Auth Group models.
#         create_groups()
#
#         # Set up User model instance.
#         cls.username = 'test_user'
#         cls.user = get_user_model().objects.create_user(
#             cls.username,
#             '{0}@wmich.edu'.format(cls.username),
#             cls.username,
#         )
#
#     def test_group_syncing(self, login_user_mock, user_intermediary_mock, wmu_user_mock):
#         """
#         Tests GroupMembership model automatically syncing as groups are added to and removed from user models.
#         """
#         # Verify we start with no models.
#         self.assertEqual(0, len(models.GroupMembership.objects.all()))
#
#         # Add one group to user and save.
#         cae_admin_group = Group.objects.get(name='CAE Admin')
#         self.user.groups.add(cae_admin_group)
#         self.user.save()
#
#         # Verify user group was added.
#         self.assertIn(cae_admin_group, self.user.groups.all())
#
#         # Verify signals were called.
#         self.assertTrue(login_user_mock.called)
#         self.assertTrue(user_intermediary_mock.called)
#         self.assertTrue(wmu_user_mock.called)
#
#         # Verify corresponding GroupMembership model was created.
#         membership_models = models.GroupMembership.objects.all()
#         print('membership_models: {0}'.format(membership_models))
#         self.assertTrue(len(membership_models) == 1)
#         self.assertEqual(membership_models[0].date_joined, self.now)
#         self.assertEqual(membership_models[0].date_left, None)
#
#         # Remove group from user and save.
#         self.user.groups.remove(cae_admin_group)
#         self.user.save()
#
#         # Verify user group was removed.
#         self.assertNotIn(cae_admin_group, self.user.groups.all())
#
#         # Verify corresponding GroupMembership model was updated.
#         membership_models = models.GroupMembership.objects.all()
#         self.assertTrue(len(membership_models) == 1)
#         self.assertEqual(membership_models[0].date_joined, self.now)
#         self.assertEqual(membership_models[0].date_left, self.now)


class UserIntermediaryModelTests(IntegrationTestCase):
    """
    Tests to ensure valid UserIntermediary model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        # Create Auth Group models.
        create_groups()

        cls.major = models.Major.create_dummy_model()
        cls.user_type = models.WmuUser.PROFESSOR

        # Set up for User model instance.
        cls.user_bronco_net = 'user_temporary'
        cls.user = get_user_model().objects.create_user(
            cls.user_bronco_net,
            '{0}@wmich.edu'.format(cls.user_bronco_net),
            cls.user_bronco_net,
        )

        # Set up for WmuUser model instance.
        cls.wmu_user_bronco_net = 'wmu_temporary'
        cls.wmu_user = models.WmuUser.objects.create(
            bronco_net=cls.wmu_user_bronco_net,
            winno=cls.wmu_user_bronco_net,
            first_name='Test First',
            middle_name='Test Middle',
            last_name='Test Last',
            user_type=cls.user_type,
        )
        models.WmuUserMajorRelationship.objects.create(
            wmu_user=cls.wmu_user,
            major=cls.major,
        )

        # Set up for instance with both User and WmuUser. User model created first.
        cls.dual_bronco_net_1 = 'dual_1_temporary'
        cls.dual_user_1 = get_user_model().objects.create_user(
            cls.dual_bronco_net_1,
            '{0}@wmich.edu'.format(cls.dual_bronco_net_1),
            cls.dual_bronco_net_1,
        )
        cls.dual_wmu_user_1 = models.WmuUser.objects.create(
            bronco_net=cls.dual_bronco_net_1,
            winno=cls.dual_bronco_net_1,
            first_name='Test First',
            middle_name='Test Middle',
            last_name='Test Last',
            user_type=cls.user_type,
        )
        models.WmuUserMajorRelationship.objects.create(
            wmu_user=cls.dual_wmu_user_1,
            major=cls.major,
        )

        # Set up for instance with both User and WmuUser. WmuUser model created first.
        cls.dual_bronco_net_2 = 'dual_2_temporary'
        cls.dual_wmu_user_2 = models.WmuUser.objects.create(
            bronco_net=cls.dual_bronco_net_2,
            winno=cls.dual_bronco_net_2,
            first_name='Test First',
            middle_name='Test Middle',
            last_name='Test Last',
            user_type=cls.user_type,
        )
        models.WmuUserMajorRelationship.objects.create(
            wmu_user=cls.dual_wmu_user_2,
            major=cls.major,
        )
        cls.dual_user_2 = get_user_model().objects.create_user(
            cls.dual_bronco_net_2,
            '{0}@wmich.edu'.format(cls.dual_bronco_net_2),
            cls.dual_bronco_net_2,
        )

        # Refresh all models.
        # Because the relations are stored in memory, and are not updated when model.save() is called.
        # Thus if a relation is edited and then a related model (held in memory) is saved, the relation edit will revert.
        cls.user = get_user_model().objects.get(username=cls.user_bronco_net)
        cls.wmu_user = models.WmuUser.objects.get(bronco_net=cls.wmu_user_bronco_net)
        cls.dual_user_1 = models.User.objects.get(username=cls.dual_bronco_net_1)
        cls.dual_wmu_user_1 = models.WmuUser.objects.get(bronco_net=cls.dual_bronco_net_1)
        cls.dual_user_2 = models.User.objects.get(username=cls.dual_bronco_net_2)
        cls.dual_wmu_user_2 = models.WmuUser.objects.get(bronco_net=cls.dual_bronco_net_2)

    def setUp(self):
        # Set up for User model instance.
        self.test_intermediary_with_user = models.UserIntermediary.objects.get(user=self.user)
        self.profile_with_user = self.test_intermediary_with_user.profile

        # Set up for WmuUser model instance.
        self.test_intermediary_with_wmuuser = models.UserIntermediary.objects.get(wmu_user=self.wmu_user)
        self.profile_with_wmuuser = self.test_intermediary_with_wmuuser.profile

        # Set up for instance with both User and WmuUser. User model created first.
        self.test_intermediary_with_dual_1 = models.UserIntermediary.objects.get(user=self.dual_user_1)
        self.profile_with_dual_1 = self.test_intermediary_with_dual_1.profile

        # Set up for instance with both User and WmuUser. WmuUser model created first.
        self.test_intermediary_with_dual_2 = models.UserIntermediary.objects.get(wmu_user=self.dual_wmu_user_2)
        self.profile_with_dual_2 = self.test_intermediary_with_dual_2.profile

    def test_model_creation_with_user(self):
        with self.subTest('Test User Intermediary with User model.'):
            # Test User Intermediary model.
            self.assertEqual(self.test_intermediary_with_user.user, self.user)
            self.assertEqual(self.test_intermediary_with_user.profile, self.profile_with_user)
            self.assertEqual(self.test_intermediary_with_user.bronco_net, self.user_bronco_net)

            # Test related bronco_net integrity.
            self.assertEqual(self.user.username, self.user_bronco_net)
            self.assertEqual(self.profile_with_user.userintermediary.bronco_net, self.user_bronco_net)

        with self.subTest('Test User Intermediary with WmuUser model.'):
            # Test User Intermediary model.
            self.assertEqual(self.test_intermediary_with_wmuuser.wmu_user, self.wmu_user)
            self.assertEqual(self.test_intermediary_with_wmuuser.profile, self.profile_with_wmuuser)
            self.assertEqual(self.test_intermediary_with_wmuuser.bronco_net, self.wmu_user_bronco_net)

            # Test related bronco_net integrity.
            self.assertEqual(self.wmu_user.bronco_net, self.wmu_user_bronco_net)
            self.assertEqual(self.profile_with_wmuuser.userintermediary.bronco_net, self.wmu_user_bronco_net)

        with self.subTest('Test User Intermediary with both User and WmuUser. User model created first.'):
            # Test User Intermediary model.
            self.assertEqual(self.test_intermediary_with_dual_1.user, self.dual_user_1)
            self.assertEqual(self.test_intermediary_with_dual_1.wmu_user, self.dual_wmu_user_1)
            self.assertEqual(self.test_intermediary_with_dual_1.profile, self.profile_with_dual_1)
            self.assertEqual(self.test_intermediary_with_dual_1.bronco_net, self.dual_bronco_net_1)

            # Test related bronco_net integrity.
            self.assertEqual(self.dual_user_1.username, self.dual_bronco_net_1)
            self.assertEqual(self.dual_wmu_user_1.bronco_net, self.dual_bronco_net_1)
            self.assertEqual(self.profile_with_dual_1.userintermediary.bronco_net, self.dual_bronco_net_1)

        with self.subTest('Test User Intermediary with both User and WmuUser. WmuUser model created first.'):
            # Test User Intermediary model.
            self.assertEqual(self.test_intermediary_with_dual_2.user, self.dual_user_2)
            self.assertEqual(self.test_intermediary_with_dual_2.wmu_user, self.dual_wmu_user_2)
            self.assertEqual(self.test_intermediary_with_dual_2.profile, self.profile_with_dual_2)
            self.assertEqual(self.test_intermediary_with_dual_2.bronco_net, self.dual_bronco_net_2)

            # Test related bronco_net integrity.
            self.assertEqual(self.dual_user_2.username, self.dual_bronco_net_2)
            self.assertEqual(self.dual_wmu_user_2.bronco_net, self.dual_bronco_net_2)
            self.assertEqual(self.profile_with_dual_2.userintermediary.bronco_net, self.dual_bronco_net_2)

    def test_shared_first_name_field(self):
        """
        Note that User, WmuUser, and UserIntermediary models essentially share a first_name field.
        The WmuUser model is intended to manage this field, so in the event that a User has both model types, then
        the WmuUser version should take priority and handle management of this field.
        """
        with self.subTest('Associated with (login) User model only.'):
            # Verify original values.
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.user_bronco_net)
            self.assertEqual(self.user.first_name, '')
            self.assertEqual(self.user.first_name, user_intermediary.first_name)

            # Test updating values.
            self.user.first_name = 'Updated first name - User'
            self.user.save()
            self.user = models.User.objects.get(username=self.user_bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.user_bronco_net)

            self.assertEqual(self.user.first_name, 'Updated first name - User')
            self.assertEqual(self.user.first_name, user_intermediary.first_name)

            # Revert back to original values for next tests. While we're at it, verify correctness.
            self.user.first_name = 'Test First'
            self.user.save()
            self.user = models.User.objects.get(username=self.user_bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.user_bronco_net)

            self.assertEqual(self.user.first_name, 'Test First')
            self.assertEqual(self.user.first_name, user_intermediary.first_name)

        with self.subTest('Associated with WmuUser model only.'):
            # Verify original values.
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.wmu_user_bronco_net)
            self.assertEqual(self.wmu_user.first_name, 'Test First')
            self.assertEqual(self.wmu_user.first_name, user_intermediary.first_name)

            # Test updating values.
            self.wmu_user.first_name = 'Updated first name - WmuUser'
            self.wmu_user.save()
            self.wmu_user = models.WmuUser.objects.get(bronco_net=self.wmu_user_bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.wmu_user_bronco_net)

            self.assertEqual(self.wmu_user.first_name, 'Updated first name - WmuUser')
            self.assertEqual(self.wmu_user.first_name, user_intermediary.first_name)

            # Revert back to original values for next tests. While we're at it, verify correctness.
            self.wmu_user.first_name = 'Test First'
            self.wmu_user.save()
            self.wmu_user = models.WmuUser.objects.get(bronco_net=self.wmu_user_bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.wmu_user_bronco_net)

            self.assertEqual(self.wmu_user.first_name, 'Test First')
            self.assertEqual(self.wmu_user.first_name, user_intermediary.first_name)

        with self.subTest('Associated with both User and WmuUser models. Save on User model.'):
            # Verify original values.
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_1)
            self.assertEqual(self.dual_wmu_user_1.first_name, 'Test First')
            self.assertEqual(self.dual_wmu_user_1.first_name, user_intermediary.first_name)
            self.assertEqual(self.dual_wmu_user_1.first_name, self.dual_user_1.first_name)

            # Test updating values.
            # This should fail and keep the same value, because WmuUser gets precedence.
            self.dual_user_1.first_name = 'Updated first name - dual, User'
            self.dual_user_1.save()
            self.dual_user_1 = models.User.objects.get(username=self.dual_bronco_net_1)
            self.dual_wmu_user_1 = models.WmuUser.objects.get(bronco_net=self.dual_bronco_net_1)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_1)

            self.assertEqual(self.dual_user_1.first_name, 'Test First')
            self.assertEqual(self.dual_user_1.first_name, user_intermediary.first_name)
            self.assertEqual(self.dual_user_1.first_name, self.dual_wmu_user_1.first_name)

        with self.subTest('Associated with both User and WmuUser models. Save on WmuUser model.'):
            # Verify original values.
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_2)
            self.assertEqual(self.dual_wmu_user_2.first_name, 'Test First')
            self.assertEqual(self.dual_wmu_user_2.first_name, user_intermediary.first_name)
            self.assertEqual(self.dual_wmu_user_2.first_name, self.dual_user_2.first_name)

            # Test updating values.
            self.dual_wmu_user_2.first_name = 'Updated first name - dual, WmuUser first'
            self.dual_wmu_user_2.save()
            self.dual_user_2 = models.User.objects.get(username=self.dual_bronco_net_2)
            self.dual_wmu_user_2 = models.WmuUser.objects.get(bronco_net=self.dual_bronco_net_2)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_2)

            self.assertEqual(self.dual_wmu_user_2.first_name, 'Updated first name - dual, WmuUser first')
            self.assertEqual(self.dual_wmu_user_2.first_name, user_intermediary.first_name)
            self.assertEqual(self.dual_wmu_user_2.first_name, self.dual_user_2.first_name)

            # Revert back to original values for next tests. While we're at it, verify correctness.
            self.dual_wmu_user_2.first_name = 'Test First'
            self.dual_wmu_user_2.save()
            self.dual_user_2 = models.User.objects.get(username=self.dual_bronco_net_2)
            self.dual_wmu_user_2 = models.WmuUser.objects.get(bronco_net=self.dual_bronco_net_2)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_2)

            self.assertEqual(self.dual_wmu_user_2.first_name, 'Test First')
            self.assertEqual(self.dual_wmu_user_2.first_name, user_intermediary.first_name)
            self.assertEqual(self.dual_wmu_user_2.first_name, self.dual_user_2.first_name)

    def test_shared_last_name_field(self):
        """
        Note that User, WmuUser, and UserIntermediary models essentially share a last_name field.
        The WmuUser model is intended to manage this field, so in the event that a User has both model types, then
        the WmuUser version should take priority and handle management of this field.
        """
        with self.subTest('Associated with (login) User model only.'):
            # Verify original values.
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.user_bronco_net)
            self.assertEqual(self.user.last_name, '')
            self.assertEqual(self.user.last_name, user_intermediary.last_name)

            # Test updating values.
            self.user.last_name = 'Updated last name - User'
            self.user.save()
            self.user = models.User.objects.get(username=self.user_bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.user_bronco_net)

            self.assertEqual(self.user.last_name, 'Updated last name - User')
            self.assertEqual(self.user.last_name, user_intermediary.last_name)

            # Revert back to original values for next tests. While we're at it, verify correctness.
            self.user.last_name = 'Test Last'
            self.user.save()
            self.user = models.User.objects.get(username=self.user_bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.user_bronco_net)

            self.assertEqual(self.user.last_name, 'Test Last')
            self.assertEqual(self.user.last_name, user_intermediary.last_name)

        with self.subTest('Associated with WmuUser model only.'):
            # Verify original values.
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.wmu_user_bronco_net)
            self.assertEqual(self.wmu_user.last_name, 'Test Last')
            self.assertEqual(self.wmu_user.last_name, user_intermediary.last_name)

            # Test updating values.
            self.wmu_user.last_name = 'Updated last name - WmuUser'
            self.wmu_user.save()
            self.mu_user = models.WmuUser.objects.get(bronco_net=self.wmu_user_bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.wmu_user_bronco_net)

            self.assertEqual(self.wmu_user.last_name, 'Updated last name - WmuUser')
            self.assertEqual(self.wmu_user.last_name, user_intermediary.last_name)

            # Revert back to original values for next tests. While we're at it, verify correctness.
            self.wmu_user.last_name = 'Test Last'
            self.wmu_user.save()
            self.wmu_user = models.WmuUser.objects.get(bronco_net=self.wmu_user_bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.wmu_user_bronco_net)

            self.assertEqual(self.wmu_user.last_name, 'Test Last')
            self.assertEqual(self.wmu_user.last_name, user_intermediary.last_name)

        with self.subTest('Associated with both User and WmuUser models. Save on User model.'):
            # Verify original values.
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_1)
            self.assertEqual(self.dual_wmu_user_1.last_name, 'Test Last')
            self.assertEqual(self.dual_wmu_user_1.last_name, user_intermediary.last_name)
            self.assertEqual(self.dual_wmu_user_1.last_name, self.dual_user_1.last_name)

            # Test updating values.
            # This should fail and keep the same value, because WmuUser gets precedence.
            self.dual_user_1.last_name = 'Updated last name - dual, User'
            self.dual_user_1.save()
            self.dual_user_1 = models.User.objects.get(username=self.dual_bronco_net_1)
            self.dual_wmu_user_1 = models.WmuUser.objects.get(bronco_net=self.dual_bronco_net_1)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_1)

            self.assertEqual(self.dual_user_1.last_name, 'Test Last')
            self.assertEqual(self.dual_user_1.last_name, user_intermediary.last_name)
            self.assertEqual(self.dual_user_1.last_name, self.dual_wmu_user_1.last_name)

        with self.subTest('Associated with both User and WmuUser models. Save on WmuUser model.'):
            # Verify original values.
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_2)
            self.assertEqual(self.dual_wmu_user_2.last_name, 'Test Last')
            self.assertEqual(self.dual_wmu_user_2.last_name, user_intermediary.last_name)
            self.assertEqual(self.dual_wmu_user_2.last_name, self.dual_user_2.last_name)

            # Test updating values.
            self.dual_wmu_user_2.last_name = 'Updated last name - dual, WmuUser first'
            self.dual_wmu_user_2.save()
            self.dual_user_2 = models.User.objects.get(username=self.dual_bronco_net_2)
            self.dual_wmu_user_2 = models.WmuUser.objects.get(bronco_net=self.dual_bronco_net_2)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_2)

            self.assertEqual(self.dual_wmu_user_2.last_name, 'Updated last name - dual, WmuUser first')
            self.assertEqual(self.dual_wmu_user_2.last_name, user_intermediary.last_name)
            self.assertEqual(self.dual_wmu_user_2.last_name, self.dual_user_2.last_name)

            # Revert back to original values for next tests. While we're at it, verify correctness.
            self.dual_wmu_user_2.last_name = 'Test Last'
            self.dual_wmu_user_2.save()
            self.dual_user_2 = models.User.objects.get(username=self.dual_bronco_net_2)
            self.dual_wmu_user_2 = models.WmuUser.objects.get(bronco_net=self.dual_bronco_net_2)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_2)

            self.assertEqual(self.dual_wmu_user_2.last_name, 'Test Last')
            self.assertEqual(self.dual_wmu_user_2.last_name, user_intermediary.last_name)
            self.assertEqual(self.dual_wmu_user_2.last_name, self.dual_user_2.last_name)

    def test_shared_email_field(self):
        """
        Note that both User and WmuUser models essentially share an email field for "<bronconet>@wmich.edu".
        However, WmuUser model's version is a method that cannot be changed. It should always be correct, and override
        the User model when variations exist.
        """
        with self.subTest('Associated with User model only.'):
            # Change name on User model. Should succeed since there's no associated WmuUser model.
            self.user.email = 'ChangedEmail@wmich.edu'
            self.user.save()
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.user_bronco_net)

            self.assertEqual(user_intermediary.user.email, 'ChangedEmail@wmich.edu')
            self.assertEqual(user_intermediary.wmu_user, None)

        with self.subTest('Associated with both User and WmuUser models. Save on User model.'):
            expected_email = '{0}@wmich.edu'.format(self.dual_bronco_net_1)
            self.assertEqual(self.dual_user_1.email, expected_email)
            self.assertEqual(self.dual_wmu_user_1.shorthand_email(), expected_email)

            # Change name on User model.
            # This should fail and keep the same value, because WmuUser gets precedence.
            self.dual_user_1.email = 'ChangedEmail@wmich.edu'
            self.dual_user_1.save()
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_1)

            self.assertEqual(user_intermediary.user.email, expected_email)
            self.assertEqual(user_intermediary.wmu_user.shorthand_email(), expected_email)
            self.assertEqual(user_intermediary.user.email, user_intermediary.wmu_user.shorthand_email())

        with self.subTest('Associated with both User and WmuUser models. User model created first.'):
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_1)
            expected_email = '{0}@wmich.edu'.format(self.dual_bronco_net_1)

            # Models were not created with the same values, but should be identical now.
            self.assertEqual(user_intermediary.user.email, expected_email)
            self.assertEqual(user_intermediary.wmu_user.shorthand_email(), expected_email)
            self.assertEqual(user_intermediary.user.email, user_intermediary.wmu_user.shorthand_email())

        with self.subTest('Associated with both User and WmuUser models. WmuUser model created first.'):
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_2)
            expected_email = '{0}@wmich.edu'.format(self.dual_bronco_net_2)

            # Models were not created with the same values, but should be identical now.
            self.assertEqual(user_intermediary.user.email, expected_email)
            self.assertEqual(user_intermediary.wmu_user.shorthand_email(), expected_email)
            self.assertEqual(user_intermediary.user.email, user_intermediary.wmu_user.shorthand_email())

    def test_shared_is_active_field(self):
        """
        Note that User, WmuUser, and UserIntermediary models essentially share an is_active field.
        Most users will have both a User and WmuUser account active at the same time.
        If either model is_active is true, then UserIntermediary is_active should be true.
        If User and WmuUser models are missing or inactive, then UserIntermediary is_active should be false.
        """
        with self.subTest('Associated with (login) User model only.'):
            # Verify when only (login) User exists.

            # Test with neither LDAP returning as active.
            self.user.userintermediary.cae_is_active = False
            self.user.userintermediary.wmu_is_active = False
            self.user.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.user = models.User.objects.get(username=self.user.username)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.user_bronco_net)

            # Check updated values.
            self.assertFalse(self.user.is_active)
            self.assertFalse(user_intermediary.cae_is_active)
            self.assertFalse(user_intermediary.wmu_is_active)

            # Reset to "inactive" to verify full "set to active" logic.
            self.user.userintermediary.cae_is_active = False
            self.user.userintermediary.wmu_is_active = False
            self.user.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.user = models.User.objects.get(username=self.user.username)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.user_bronco_net)

            # Test with only CAE LDAP returning as active.
            self.user.userintermediary.cae_is_active = True
            self.user.userintermediary.wmu_is_active = False
            self.user.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.user = models.User.objects.get(username=self.user.username)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.user_bronco_net)

            # Check updated values.
            self.assertTrue(self.user.is_active)
            self.assertTrue(user_intermediary.cae_is_active)
            self.assertFalse(user_intermediary.wmu_is_active)

            # Reset to "inactive" to verify full "set to active" logic.
            self.user.userintermediary.cae_is_active = False
            self.user.userintermediary.wmu_is_active = False
            self.user.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.user = models.User.objects.get(username=self.user.username)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.user_bronco_net)

            # Test with only WMU LDAP returning as active.
            self.user.userintermediary.cae_is_active = False
            self.user.userintermediary.wmu_is_active = True
            self.user.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.user = models.User.objects.get(username=self.user.username)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.user_bronco_net)

            # Check updated values.
            self.assertTrue(self.user.is_active)
            self.assertFalse(user_intermediary.cae_is_active)
            self.assertTrue(user_intermediary.wmu_is_active)

            # Reset to "inactive" to verify full "set to active" logic.
            self.user.userintermediary.cae_is_active = False
            self.user.userintermediary.wmu_is_active = False
            self.user.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.user = models.User.objects.get(username=self.user.username)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.user_bronco_net)

            # Test with both LDAPs returning as active.
            self.user.userintermediary.cae_is_active = True
            self.user.userintermediary.wmu_is_active = True
            self.user.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.user = models.User.objects.get(username=self.user.username)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.user_bronco_net)

            # Check updated values.
            self.assertTrue(self.user.is_active)
            self.assertTrue(user_intermediary.cae_is_active)
            self.assertTrue(user_intermediary.wmu_is_active)

        with self.subTest('Associated with WmuUser model only.'):
            # Verify for when only WmuUser exists.

            # Test with neither LDAP returning as active.
            self.wmu_user.userintermediary.cae_is_active = False
            self.wmu_user.userintermediary.wmu_is_active = False
            self.wmu_user.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.wmu_user = models.WmuUser.objects.get(bronco_net=self.wmu_user.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.wmu_user_bronco_net)

            # Check updated values.
            self.assertFalse(self.wmu_user.is_active)
            self.assertFalse(user_intermediary.cae_is_active)
            self.assertFalse(user_intermediary.wmu_is_active)

            # Reset to "inactive" to verify full "set to active" logic.
            self.wmu_user.userintermediary.cae_is_active = False
            self.wmu_user.userintermediary.wmu_is_active = False
            self.wmu_user.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.wmu_user = models.WmuUser.objects.get(bronco_net=self.wmu_user.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.wmu_user_bronco_net)

            # Test with only CAE LDAP returning as active.
            self.wmu_user.userintermediary.cae_is_active = True
            self.wmu_user.userintermediary.wmu_is_active = False
            self.wmu_user.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.wmu_user = models.WmuUser.objects.get(bronco_net=self.wmu_user.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.wmu_user_bronco_net)

            # Check updated values.
            self.assertTrue(self.wmu_user.is_active)
            self.assertTrue(user_intermediary.cae_is_active)
            self.assertFalse(user_intermediary.wmu_is_active)

            # Reset to "inactive" to verify full "set to active" logic.
            self.wmu_user.userintermediary.cae_is_active = False
            self.wmu_user.userintermediary.wmu_is_active = False
            self.wmu_user.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.wmu_user = models.WmuUser.objects.get(bronco_net=self.wmu_user.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.wmu_user_bronco_net)

            # Test with only WMU LDAP returning as active.
            self.wmu_user.userintermediary.cae_is_active = False
            self.wmu_user.userintermediary.wmu_is_active = True
            self.wmu_user.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.wmu_user = models.WmuUser.objects.get(bronco_net=self.wmu_user.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.wmu_user_bronco_net)

            # Check updated values.
            self.assertTrue(self.wmu_user.is_active)
            self.assertFalse(user_intermediary.cae_is_active)
            self.assertTrue(user_intermediary.wmu_is_active)

            # Reset to "inactive" to verify full "set to active" logic.
            self.wmu_user.userintermediary.cae_is_active = False
            self.wmu_user.userintermediary.wmu_is_active = False
            self.wmu_user.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.wmu_user = models.WmuUser.objects.get(bronco_net=self.wmu_user.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.wmu_user_bronco_net)

            # Test with both LDAPs returning as active.
            self.wmu_user.userintermediary.cae_is_active = True
            self.wmu_user.userintermediary.wmu_is_active = True
            self.wmu_user.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.wmu_user = models.WmuUser.objects.get(bronco_net=self.wmu_user.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.wmu_user_bronco_net)

            # Check updated values.
            self.assertTrue(self.wmu_user.is_active)
            self.assertTrue(user_intermediary.cae_is_active)
            self.assertTrue(user_intermediary.wmu_is_active)

        with self.subTest('Associated with both User and WmuUser models. Save on (login) User model.'):
            # Verify for when both (login) User and WmuUser exists. With User updated only.

            # Test with neither LDAP returning as active.
            self.dual_user_1.userintermediary.cae_is_active = False
            self.dual_user_1.userintermediary.wmu_is_active = False
            self.dual_user_1.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.dual_user_1 = models.User.objects.get(username=self.dual_user_1.username)
            self.dual_wmu_user_1 = models.WmuUser.objects.get(bronco_net=self.dual_wmu_user_1.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_1)

            # Check updated values.
            self.assertFalse(self.dual_user_1.is_active)
            self.assertFalse(self.dual_wmu_user_1.is_active)
            self.assertFalse(user_intermediary.cae_is_active)
            self.assertFalse(user_intermediary.wmu_is_active)

            # Reset to "inactive" to verify full "set to active" logic.
            self.dual_user_1.userintermediary.cae_is_active = False
            self.dual_user_1.userintermediary.wmu_is_active = False
            self.dual_user_1.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.dual_user_1 = models.User.objects.get(username=self.dual_user_1.username)
            self.dual_wmu_user_1 = models.WmuUser.objects.get(bronco_net=self.dual_wmu_user_1.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_1)

            # Test with only CAE LDAP returning as active.
            self.dual_user_1.userintermediary.cae_is_active = True
            self.dual_user_1.userintermediary.wmu_is_active = False
            self.dual_user_1.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.dual_user_1 = models.User.objects.get(username=self.dual_user_1.username)
            self.dual_wmu_user_1 = models.WmuUser.objects.get(bronco_net=self.dual_wmu_user_1.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_1)

            # Check updated values.
            self.assertTrue(self.dual_user_1.is_active)
            self.assertTrue(self.dual_wmu_user_1.is_active)
            self.assertTrue(user_intermediary.cae_is_active)
            self.assertFalse(user_intermediary.wmu_is_active)

            # Reset to "inactive" to verify full "set to active" logic.
            self.dual_user_1.userintermediary.cae_is_active = False
            self.dual_user_1.userintermediary.wmu_is_active = False
            self.dual_user_1.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.dual_user_1 = models.User.objects.get(username=self.dual_user_1.username)
            self.dual_wmu_user_1 = models.WmuUser.objects.get(bronco_net=self.dual_wmu_user_1.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_1)

            # Test with only WMU LDAP returning as active.
            self.dual_user_1.userintermediary.cae_is_active = False
            self.dual_user_1.userintermediary.wmu_is_active = True
            self.dual_user_1.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.dual_user_1 = models.User.objects.get(username=self.dual_user_1.username)
            self.dual_wmu_user_1 = models.WmuUser.objects.get(bronco_net=self.dual_wmu_user_1.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_1)

            # Check updated values.
            self.assertTrue(self.dual_user_1.is_active)
            self.assertTrue(self.dual_wmu_user_1.is_active)
            self.assertFalse(user_intermediary.cae_is_active)
            self.assertTrue(user_intermediary.wmu_is_active)

            # Reset to "inactive" to verify full "set to active" logic.
            self.dual_user_1.userintermediary.cae_is_active = False
            self.dual_user_1.userintermediary.wmu_is_active = False
            self.dual_user_1.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.dual_user_1 = models.User.objects.get(username=self.dual_user_1.username)
            self.dual_wmu_user_1 = models.WmuUser.objects.get(bronco_net=self.dual_wmu_user_1.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_1)

            # Test with both LDAPs returning as active.
            self.dual_user_1.userintermediary.cae_is_active = True
            self.dual_user_1.userintermediary.wmu_is_active = True
            self.dual_user_1.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.dual_user_1 = models.User.objects.get(username=self.dual_user_1.username)
            self.dual_wmu_user_1 = models.WmuUser.objects.get(bronco_net=self.dual_wmu_user_1.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_1)

            # Check updated values.
            self.assertTrue(self.dual_user_1.is_active)
            self.assertTrue(self.dual_wmu_user_1.is_active)
            self.assertTrue(user_intermediary.cae_is_active)
            self.assertTrue(user_intermediary.wmu_is_active)

        with self.subTest('Associated with both User and WmuUser models. Save on WmuUser model.'):
            # Verify for when both (login) User and WmuUser exists. With WmuUser updated.

            # Test with neither LDAP returning as active.
            self.dual_wmu_user_2.userintermediary.cae_is_active = False
            self.dual_wmu_user_2.userintermediary.wmu_is_active = False
            self.dual_wmu_user_2.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.dual_user_2 = models.User.objects.get(username=self.dual_user_2.username)
            self.dual_wmu_user_2 = models.WmuUser.objects.get(bronco_net=self.dual_wmu_user_2.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_2)

            # Check updated values.
            self.assertFalse(self.dual_user_2.is_active)
            self.assertFalse(self.dual_wmu_user_2.is_active)
            self.assertFalse(user_intermediary.cae_is_active)
            self.assertFalse(user_intermediary.wmu_is_active)

            # Reset to "inactive" to verify full "set to active" logic.
            self.dual_wmu_user_2.userintermediary.cae_is_active = False
            self.dual_wmu_user_2.userintermediary.wmu_is_active = False
            self.dual_wmu_user_2.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.dual_user_2 = models.User.objects.get(username=self.dual_user_2.username)
            self.dual_wmu_user_2 = models.WmuUser.objects.get(bronco_net=self.dual_wmu_user_2.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_2)

            # Test with only CAE LDAP returning as active.
            self.dual_wmu_user_2.userintermediary.cae_is_active = True
            self.dual_wmu_user_2.userintermediary.wmu_is_active = False
            self.dual_wmu_user_2.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.dual_user_2 = models.User.objects.get(username=self.dual_user_2.username)
            self.dual_wmu_user_2 = models.WmuUser.objects.get(bronco_net=self.dual_wmu_user_2.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_2)

            # Check updated values.
            self.assertTrue(self.dual_user_2.is_active)
            self.assertTrue(self.dual_wmu_user_2.is_active)
            self.assertTrue(user_intermediary.cae_is_active)
            self.assertFalse(user_intermediary.wmu_is_active)

            # Reset to "inactive" to verify full "set to active" logic.
            self.dual_wmu_user_2.userintermediary.cae_is_active = False
            self.dual_wmu_user_2.userintermediary.wmu_is_active = False
            self.dual_wmu_user_2.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.dual_user_2 = models.User.objects.get(username=self.dual_user_2.username)
            self.dual_wmu_user_2 = models.WmuUser.objects.get(bronco_net=self.dual_wmu_user_2.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_2)

            # Test with only WMU LDAP returning as active.
            self.dual_wmu_user_2.userintermediary.cae_is_active = False
            self.dual_wmu_user_2.userintermediary.wmu_is_active = True
            self.dual_wmu_user_2.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.dual_user_2 = models.User.objects.get(username=self.dual_user_2.username)
            self.dual_wmu_user_2 = models.WmuUser.objects.get(bronco_net=self.dual_wmu_user_2.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_2)

            # Check updated values.
            self.assertTrue(self.dual_user_2.is_active)
            self.assertTrue(self.dual_wmu_user_2.is_active)
            self.assertFalse(user_intermediary.cae_is_active)
            self.assertTrue(user_intermediary.wmu_is_active)

            # Reset to "inactive" to verify full "set to active" logic.
            self.dual_wmu_user_2.userintermediary.cae_is_active = False
            self.dual_wmu_user_2.userintermediary.wmu_is_active = False
            self.dual_wmu_user_2.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.dual_user_2 = models.User.objects.get(username=self.dual_user_2.username)
            self.dual_wmu_user_2 = models.WmuUser.objects.get(bronco_net=self.dual_wmu_user_2.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_2)

            # Test with both LDAPs returning as active.
            self.dual_wmu_user_2.userintermediary.cae_is_active = True
            self.dual_wmu_user_2.userintermediary.wmu_is_active = True
            self.dual_wmu_user_2.save()
            # Refresh models from database, so we aren't using cached/memory data.
            self.dual_user_2 = models.User.objects.get(username=self.dual_user_2.username)
            self.dual_wmu_user_2 = models.WmuUser.objects.get(bronco_net=self.dual_wmu_user_2.bronco_net)
            user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.dual_bronco_net_2)

            # Check updated values.
            self.assertTrue(self.dual_user_2.is_active)
            self.assertTrue(self.dual_wmu_user_2.is_active)
            self.assertTrue(user_intermediary.cae_is_active)
            self.assertTrue(user_intermediary.wmu_is_active)

    def test_user_auth_groups_field(self):
        """
        Tests that Group models are updated accordingly, based on is_active UserIntermediary values.
        """
        # Get all CAE groups to test.
        cae_building_coordinator = Group.objects.get(name='CAE Building Coordinator')
        cae_director = Group.objects.get(name='CAE Director')
        cae_attendant_group = Group.objects.get(name='CAE Attendant')
        cae_admin_group = Group.objects.get(name='CAE Admin GA')
        cae_admin_ga_group = Group.objects.get(name='CAE Admin')
        cae_programmer_ga_group = Group.objects.get(name='CAE Programmer GA')
        cae_programmer_group = Group.objects.get(name='CAE Programmer')

        # Get arbitrary non-CAE group to also test. In this case, it's a random STEP Center group.
        step_group = Group.objects.get(name='STEP Admin')

        # Add all above groups to user, so that we can test removing during is_active toggle.
        self.user.groups.add(*[
            cae_building_coordinator,
            cae_director,
            cae_attendant_group,
            cae_admin_ga_group,
            cae_admin_group,
            cae_programmer_ga_group,
            cae_programmer_group,
            step_group,
        ])
        self.user.save()

        # Refresh models from database, so we aren't using cached/memory data.
        self.user = models.User.objects.get(username=self.user.username)

        # Verify expected groups.
        user_groups = self.user.groups.all().values_list('name', flat=True)
        for group_name in settings.CAE_CENTER_GROUPS:
            self.assertIn(group_name, user_groups)
        # Also verify non-CAE group membership.
        self.assertIn(step_group.name, user_groups)

        # Now toggle "cae_is_active" to false. This should remove all CAE groups only.
        self.user.userintermediary.cae_is_active = False
        self.user.save()

        # Refresh models from database, so we aren't using cached/memory data.
        self.user = models.User.objects.get(username=self.user.username)

        # Verify groups have automatically changed.
        user_groups = self.user.groups.all().values_list('name', flat=True)
        for group_name in settings.CAE_CENTER_GROUPS:
            self.assertNotIn(group_name, user_groups)
        # Also verify non-CAE group membership has remained unchanged.
        self.assertIn(step_group.name, user_groups)

    def test_string_representation_with_user(self):
        self.assertEqual(str(self.test_intermediary_with_user), str(self.test_intermediary_with_user.bronco_net))

    def test_plural_representation(self):
        self.assertEqual(str(self.test_intermediary_with_user._meta.verbose_name), 'User Intermediary')
        self.assertEqual(str(self.test_intermediary_with_user._meta.verbose_name_plural), 'User Intermediaries')

    def test_dummy_creation(self):
        dummy_model = get_user_model().create_dummy_model()
        self.assertIsNotNone(dummy_model)
        self.assertTrue(isinstance(dummy_model, get_user_model()))

    def test_field_removal(self):
        # Test that removing profile field creates error.
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                self.test_intermediary_with_user.profile = None
                self.test_intermediary_with_user.save()

        # Test that removing bronco_net field creates error.
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                self.test_intermediary_with_user.bronco_net = None
                self.test_intermediary_with_user.save()

        # Test that cannot remove user field when it's the only relation.
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                self.test_intermediary_with_user.user = None
                self.test_intermediary_with_user.save()

        # Test that cannot remove wmu_user field when it's the only relation.
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                self.test_intermediary_with_wmuuser.wmu_user = None
                self.test_intermediary_with_wmuuser.save()


class WmuUserTests(IntegrationTestCase):
    """
    Tests to ensure valid WMU User model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        # Import Department model fixtures.
        create_departments(None)

        cls.major = models.Major.create_dummy_model()
        cls.user_type = models.WmuUser.PROFESSOR

    def setUp(self):
        self.bronco_net='abc1234'
        self.test_wmu_user = models.WmuUser.objects.create(
            bronco_net=self.bronco_net,
            winno='123456789',
            first_name='Test First',
            last_name='Test Last',
            user_type=self.user_type,
        )
        models.WmuUserMajorRelationship.objects.create(
            wmu_user=self.test_wmu_user,
            major=self.major,
        )
        self.user_intermediary = models.UserIntermediary.objects.get(bronco_net=self.bronco_net)
        self.majors_for_student = self.test_wmu_user.major.all()

    def test_model_creation(self):
        self.assertEqual(self.user_intermediary.wmu_user, self.test_wmu_user)
        self.assertEqual(self.test_wmu_user.bronco_net, 'abc1234')
        self.assertEqual(self.test_wmu_user.winno, '123456789')
        self.assertEqual(self.test_wmu_user.first_name, 'Test First')
        self.assertEqual(self.test_wmu_user.last_name, 'Test Last')
        self.assertEqual(self.test_wmu_user.user_type, self.user_type)
        self.assertEqual(self.majors_for_student[0], self.major)

    def test_multiple_majors(self):
        # Test adding a second major.
        new_major = models.Major.objects.create(
            student_code='New Major',
            program_code='New Major',
            name='New Major',
            slug='new-major',
        )
        models.WmuUserMajorRelationship.objects.create(
            wmu_user=self.test_wmu_user,
            major=new_major,
        )

        # Verify added correctly.
        majors_for_student = self.test_wmu_user.major.all()
        self.assertEqual(len(majors_for_student), 2)
        self.assertEqual(majors_for_student[0], self.major)
        self.assertEqual(majors_for_student[1], new_major)
        self.assertEqual(majors_for_student[0].is_active, True)
        self.assertEqual(majors_for_student[1].is_active, True)

        # Now set first major to "inactive". Aka, student either finished major or changed to different one.
        majors_for_student[0].is_active = False
        majors_for_student[0].save()

        majors_for_student = self.test_wmu_user.major.all()
        self.assertEqual(majors_for_student[0].is_active, False)
        self.assertEqual(majors_for_student[1].is_active, True)

    def test_string_representation(self):
        self.assertEqual(str(self.test_wmu_user), 'abc1234: Test First Test Last')

    def test_plural_representation(self):
        self.assertEqual(str(self.test_wmu_user._meta.verbose_name), 'WMU User')
        self.assertEqual(str(self.test_wmu_user._meta.verbose_name_plural), 'WMU Users')

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.WmuUser.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.WmuUser))

        # Test get.
        dummy_model_2 = models.WmuUser.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.WmuUser))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)


class WmuUserMajorRelationModelTests(IntegrationTestCase):
    """
    Tests to ensure valid WmuUserMajorRelation model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user_type = models.WmuUser.STUDENT
        cls.department = models.Department.create_dummy_model()
        cls.wmu_user_1 = models.WmuUser.objects.create(
            bronco_net='test_user_1',
            winno='123456789',
            first_name='Test User 1',
            last_name='Test User 1',
            user_type=cls.user_type,
        )
        cls.wmu_user_2 = models.WmuUser.objects.create(
            bronco_net='test_user_2',
            winno='987654321',
            first_name='Test User 2',
            last_name='Test User 2',
            user_type=cls.user_type,
        )
        cls.major_1 = models.Major.objects.create(
            department=cls.department,
            student_code='major_1',
            program_code='major_1',
            name='Test Major 1',
            slug='major-1',
        )
        cls.major_2 = models.Major.objects.create(
            department=cls.department,
            student_code='major_2',
            program_code='major_2',
            name='Test Major 2',
            slug='major-2',
        )

    def test_check_if_user_has_major_active(self):
        # First add Major 1 to Student 1.
        models.WmuUserMajorRelationship.objects.create(
            wmu_user=self.wmu_user_1,
            major=self.major_1,
        )

        self.assertTrue(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_1, self.major_1))
        self.assertFalse(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_2, self.major_1))
        self.assertFalse(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_1, self.major_2))
        self.assertFalse(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_2, self.major_2))

        # Add Major 2 to Student 2.
        models.WmuUserMajorRelationship.objects.create(
            wmu_user=self.wmu_user_2,
            major=self.major_2,
        )

        self.assertTrue(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_1, self.major_1))
        self.assertFalse(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_2, self.major_1))
        self.assertFalse(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_1, self.major_2))
        self.assertTrue(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_2, self.major_2))

        # Now give Student 1 all majors.
        models.WmuUserMajorRelationship.objects.create(
            wmu_user=self.wmu_user_1,
            major=self.major_2,
        )

        self.assertTrue(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_1, self.major_1))
        self.assertFalse(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_2, self.major_1))
        self.assertTrue(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_1, self.major_2))
        self.assertTrue(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_2, self.major_2))

        # Now remove Major 2 from Student 1 by setting "active" field to False.
        intermediary_relationship = models.WmuUserMajorRelationship.objects.get(
            wmu_user=self.wmu_user_1,
            major=self.major_2,
        )
        intermediary_relationship.is_active = False
        intermediary_relationship.save()

        self.assertTrue(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_1, self.major_1))
        self.assertFalse(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_2, self.major_1))
        self.assertFalse(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_1, self.major_2))
        self.assertTrue(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_2, self.major_2))

        # Finally, remove all Majors from Student 1 by setting "active" field to False.
        intermediary_relationship = models.WmuUserMajorRelationship.objects.get(
            wmu_user=self.wmu_user_1,
            major=self.major_1,
        )
        intermediary_relationship.is_active = False
        intermediary_relationship.save()

        self.assertFalse(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_1, self.major_1))
        self.assertFalse(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_2, self.major_1))
        self.assertFalse(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_1, self.major_2))
        self.assertTrue(models.WmuUserMajorRelationship.check_if_user_has_major_active(self.wmu_user_2, self.major_2))


class ProfileModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Profile model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.bronco_net = 'temporary'
        cls.user = cls.create_user(cls, cls.bronco_net)
        cls.user_intermediary = models.UserIntermediary.objects.get(user=cls.user)
        cls.address = models.Address.create_dummy_model()
        cls.phone_number = '+12693211234'
        cls.site_theme = models.SiteTheme.create_dummy_model()
        cls.user_timezone = 'America/Detroit'
        cls.font_size = models.Profile.FONT_BASE

    def setUp(self):
        self.test_profile = self.user_intermediary.profile
        self.test_profile.address = self.address
        self.test_profile.phone_number = PhoneNumber.from_string(self.phone_number)
        self.test_profile.site_theme = self.site_theme
        self.test_profile.save()

    def test_model_creation(self):
        # Test related models.
        self.assertEqual(self.user_intermediary.user, self.user)
        self.assertEqual(self.user_intermediary.profile, self.test_profile)
        self.assertEqual(self.user_intermediary.bronco_net, self.bronco_net)

        # Test Profile model.
        self.assertEqual(self.test_profile.address, self.address)
        self.assertEqual(self.test_profile.phone_number, self.phone_number)
        self.assertEqual(self.test_profile.site_theme, self.site_theme)
        self.assertEqual(self.test_profile.user_timezone, self.user_timezone)
        self.assertEqual(self.test_profile.desktop_font_size, self.font_size)
        self.assertEqual(self.test_profile.mobile_font_size, self.font_size)

    def test_string_representation(self):
        self.assertEqual(str(self.test_profile), self.test_profile.userintermediary.bronco_net)

    def test_plural_representation(self):
        self.assertEqual(str(self.test_profile._meta.verbose_name), 'Profile')
        self.assertEqual(str(self.test_profile._meta.verbose_name_plural), 'Profiles')


class AddressModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Address model creation/logic.
    """
    def setUp(self):
        self.test_address = models.Address.objects.create(
            street="1234 TestStreet",
            optional_street="Test Apt",
            city="Test City",
            state=25,
            zip="49006",
        )

    def test_model_creation(self):
        self.assertEqual(self.test_address.street, '1234 TestStreet')
        self.assertEqual(self.test_address.optional_street, 'Test Apt')
        self.assertEqual(self.test_address.city, 'Test City')
        self.assertEqual(self.test_address.state, 25)
        self.assertEqual(self.test_address.zip, '49006')

    def test_string_representation(self):
        self.assertEqual(str(self.test_address),
                         (self.test_address.street + " " + self.test_address.optional_street +
                          " " + self.test_address.city + ", " + self.test_address.get_state_abbrev_as_string() +
                          ", " + self.test_address.zip))

    def test_plural_representation(self):
        self.assertEqual(str(self.test_address._meta.verbose_name), 'Address')
        self.assertEqual(str(self.test_address._meta.verbose_name_plural), 'Addresses')

    def test_state_as_string(self):
        self.assertEqual(self.test_address.get_state_as_string(), 'Montana')
        self.assertEqual(self.test_address.get_state_as_string(1), 'Alaska')
        self.assertEqual(self.test_address.get_state_as_string(21), 'Michigan')
        self.assertEqual(self.test_address.get_state_as_string(49), 'Wyoming')

    def test_state_abbrev_as_string(self):
        self.assertEqual(self.test_address.get_state_abbrev_as_string(), 'MT')
        self.assertEqual(self.test_address.get_state_abbrev_as_string(1), 'AK')
        self.assertEqual(self.test_address.get_state_abbrev_as_string(21), 'MI')
        self.assertEqual(self.test_address.get_state_abbrev_as_string(49), 'WY')

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.Address.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.Address))

        # Test get.
        dummy_model_2 = models.Address.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.Address))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)


class SiteThemeModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Site Theme model creation/logic.
    """
    def setUp(self):
        self.test_theme = models.SiteTheme.objects.create(
            display_name='Test Theme',
            file_name='test-theme',
            gold_logo=False,
            slug='test-theme',
        )

    def test_model_creation(self):
        self.assertEqual(self.test_theme.display_name, 'Test Theme')
        self.assertEqual(self.test_theme.file_name, 'test-theme')
        self.assertEqual(self.test_theme.gold_logo, False)

    def test_string_representation(self):
        self.assertEqual(str(self.test_theme), self.test_theme.display_name)

    def test_plural_representation(self):
        self.assertEqual(str(self.test_theme._meta.verbose_name), 'Site Theme')
        self.assertEqual(str(self.test_theme._meta.verbose_name_plural), 'Site Themes')

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.SiteTheme.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.SiteTheme))

        # Test get.
        dummy_model_2 = models.SiteTheme.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.SiteTheme))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)
