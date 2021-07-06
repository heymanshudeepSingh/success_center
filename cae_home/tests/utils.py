"""
CAE Home app testing Utility Functions and Classes.
"""

# System Imports.
import re, sys
from channels.testing import ChannelsLiveServerTestCase
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.http import QueryDict
from django.test import TestCase
from django.urls import reverse
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from urllib.parse import ParseResult, urlparse

# User Class Imports.
from cae_home.management.commands.fixtures.user import create_site_themes
from cae_home.management.commands.seeders.user import create_groups, create_permission_group_users
from workspace import logging as init_logging


# Import logger.
logger = init_logging.get_logger(__name__)


# Module Variables.
default_password = settings.USER_SEED_PASSWORD


# region Util Functions

def debug_response_content(response_content):
    """
    Print debug page output, with any repeating whitespace characters trimmed down.

    Trimming down helps because Django templating, by default, adds a lot of unnecessary extra whitespace.
    We don't see this extra whitespace in browsers but it's noticeable if the page is printed out to console.
    """
    print('{0} {1} {0}'.format('=' * 10, 'response.content.decode(\'utf-8\')'))

    if len(response_content) > 0:
        # Replace any repeating space characters.
        response_content = re.sub('  +', ' ', response_content)

        # Replace any repeating newline characters.
        response_content = re.sub('\n \n', '\n', response_content)
        response_content = re.sub('\n\n+', '\n', response_content)

        # Print formatted page content string.
        print(response_content)
    else:
        # No context provided.
        print('Request "response.context" is empty.')

    print('')


def debug_response_context(response_context):
    """
    Print debug context output.

    Any individual values that are excessively long are trimmed down.
    """
    print('{0} {1} {0}'.format('=' * 10, 'response.context'))

    # Response context object is strange, in that it's basically a dictionary, and it allows .keys() but not .values().
    # Thus, iterate on keys only and pull respective value.
    for key in response_context.keys():
        context_value = str(response_context[key])
        if len(context_value) > 80:
            context_value = '"{0}" ... "{1}"'.format(context_value[:40], context_value[-40:])
        print('{0}: {1}'.format(key, context_value))

    print('')


def debug_forms(response_context):
    """
    Print debug form output.
    """
    if 'form' in response_context or 'formset' in response_context:
        print('{0} {1} {0}'.format('=' * 10, 'response_context form data'))

    # Print form errors if available.
    if 'form' in response_context:
        form = response_context['form']

        print('Provided Form Fields:')
        fields_submitted = False
        for key, value in form.data.items():
            print('    {0}: {1}'.format(key, value))
            fields_submitted = True
        if not fields_submitted:
            print('    No form field data submitted.')
        print('')

        if not form.is_valid():
            if len(form.errors) > 0 or len(form.non_field_errors()) > 0:
                print('Form Invalid:'.format(not form.is_valid()))
                if len(form.non_field_errors()) > 0:
                    print('    Non-field Frrors:')
                    for error in form.non_field_errors():
                        print('        {0}'.format(error))

                if len(form.errors) > 0:
                    print('    Field Errors:')
                    for error in form.errors:
                        print('        {0}'.format(error))

        else:
            print('Form Valid.')
        print('')

    # Print formset errors if available.
    if 'formset' in response_context:
        formset = response_context['formset']
        for form in formset:
            print('Form(set) Errors:')
            for error in form.non_field_errors():
                print('\t{0}'.format(error))
            for error in form.errors:
                print('\t{0}'.format(error))
        print('')


def debug_messages(response_context):
    """
    Print debug message output.
    """
    # Print message text, if available.
    if 'messages' in response_context:
        context_value = response_context['messages']

        if len(context_value) > 0:
            print('{0} {1} {0}'.format('=' * 10, 'response.context[\'messages\']'))
            for message in response_context:
                print('\t{0}'.format(message))
        print('')


def debug_permissions(user):
    """
    Print debug user permission/group output.
    """
    # Check if user proper user provided.
    if isinstance(user, get_user_model()):
        print('{0} {1} {0}'.format('=' * 10, 'User Groups & Permissions'))

        # Print current user.
        print('Username: {0}    -    {1} {2}'.format(user.username, user.first_name, user.last_name))

        # Print user groups.
        print('User Groups: {0}'.format(user.groups.all()))
        print('')

        # Print user permissions.
        print('User Permissions: {0}'.format(user.user_permissions.all()))
        print('')

# endregion Util Functions


# region Util Classes

class AbstractTestHelper():
    """
    General expanded test functionality, applicable to all test types.
    """
    def __init__(self, *args, debug_print=True, **kwargs):
        # Run parent setup logic.
        super().__init__(*args, **kwargs)

        # Save class variables.
        self._debug_print = debug_print

    # region Debug Util Functions

    def debug_print(self, response):
        """
        Debug printing for when a test has an error.

        With command `python manage.py test`, stdout is displayed for all tests.
        Thus, until we can figure out how to only display stdout on error, there's not really a better way for this.
        Must be called manually, when debugging tests.

        :param response: Page response object, generally generated from `self.client.get()` or `self.client.post()`.
        """
        # Print out file name.
        print('')
        print('')
        print('')
        print('-' * 80)
        print('{0} {1} Debug Printing {0}'.format('-' * 20, self.__class__.__name__))
        print('-' * 80)
        print('')

        # Display page content to console.
        self.debug_print_content(response)

        # Display page context (aka template variables) to console.
        self.debug_print_context(response)

        # Display any form data to console.
        self.debug_print_forms(response)

        # Display any message data to console.
        self.debug_print_messages(response)

        # Display user groups

        print('')
        print('')
        print('')

    def debug_print_content(self, response):
        debug_response_content(response.content.decode('utf-8'))

    def debug_print_context(self, response):
        debug_response_context(response.context)

    def debug_print_forms(self, response):
        debug_forms(response.context)

    def debug_print_messages(self, response):
        debug_messages(response.context)

    def debug_print_permissions(self, response):
        debug_messages(response.context['user'])

    # endregion Debug Util Functions

    def create_default_users_and_groups(self, password=default_password):
        """
        Create expected/default groups and dummy users to associate with them.
        """
        create_groups()
        create_permission_group_users(password=password, with_names=False)

    def create_user(self, username, password=default_password, permissions=None, groups=None):
        """
        Create new user. Optionally pass permissions/groups.
        :param username: Username to use.
        :param password: Password for user.
        :param permissions: Optional permissions to add.
        :param groups: Optional permission groups to add.
        :return: Instance of created user.
        """
        # Create user.
        user = get_user_model().objects.create_user(username=username, password=password)
        user.password_string = password

        # Check for optional permissions.
        if permissions:
            if isinstance(permissions, list) or isinstance(permissions, tuple):
                for permission in permissions:
                    self.add_user_permission(permission, user)
            else:
                self.add_user_permission(permissions, user)

        # Check for optional groups.
        if groups:
            if isinstance(groups, list) or isinstance(groups, tuple):
                for group in groups:
                    self.add_user_group(group, user)
            else:
                self.add_user_group(groups, user)

        return user

    def get_user(self, user, password=default_password):
        """
        Returns a user with the given username.
        :param user: User to return.
        :param password: Password for user.
        """
        # Check if already User model.
        if isinstance(user, get_user_model()):
            # Is User model. Return as-is.
            user = user

        try:
            # Get user.
            user = get_user_model().objects.get(username=user)

        except get_user_model().DoesNotExist:
            # Failed to find user.
            print(list(get_user_model().objects.all().values_list('username')))
            raise get_user_model().DoesNotExist('User matching {0} was not found.')

        # If we made it this far, valid (login) User model returned.
        # Check that user has associated password string saved.
        if not hasattr(user, 'password_string'):
            user.password_string = password

        return user

    def add_user_permission(self, user_permission, user):
        """
        Add a permission to the given user.
        On failure, prints out all possible permissions.
        :param user_permission: Permission name to add.
        :param user: User to add permission to.
        """
        # Check if already permission model.
        if isinstance(user_permission, Permission):
            # Is already Permission model.
            permission = user_permission

        else:
            # Is not Permission model. Attempt to get.
            try:
                permission = Permission.objects.get(codename=user_permission)
            except Permission.DoesNotExist:
                # Failed to get by codename. Try by name.
                try:
                    permission = Permission.objects.get(name=user_permission)

                except Permission.DoesNotExist:
                    # Failed to find permission.
                    print(list(Permission.objects.all().values_list('codename')))
                    raise Permission.DoesNotExist('Permission matching "{0}" not found.'.format(user_permission))

        # If we made it this far, then valid Permission acquired. Add to User.
        self.get_user(user).user_permissions.add(permission)

    def add_user_group(self, user_group, user):
        """
        Add a permission group to the given user.
        Ex: 'CAE Admin'

        :param user_group: Group to add.
        :param user: User to add Group to.
        """
        # Check if already Group model.
        if isinstance(user_group, Group):
            # Is already Group model.
            group = user_group

        else:
            # Is not Group model. Attempt to get.
            try:
                group = Group.objects.get(name=user_group)
            except Group.DoesNotExist:
                # Failed to find group.
                print(list(Group.objects.all().values_list('name')))
                raise Group.DoesNotExist('Group matching "{0}" was not found.'.format(user_group))

        # If we made it this far, then valid Group acquired. Add to User.
        self.get_user(user).groups.add(group)


class IntegrationTestCase(AbstractTestHelper, TestCase):
    """
    Python Unit Testing extension (without Selenium).
    Most minimalistic test class that inherits from AbstractTestHelper.

    Inherits from the standard django.test.TestCase, so it has all functionality the default Django Testing class does.
    """
    def __init__(self, *args, **kwargs):
        # Run parent setup logic.
        super().__init__(*args, **kwargs)

        # Get home url.
        self.login_url = reverse('cae_home:login')

    def setUp(self):
        """
        Logic to reset state before each individual test.
        """
        # Run parent setup logic.
        super().setUp()

    def assertURLEqual(self, url, expected, parse_qs=False):
        """
        Given two URLs, make sure all their components (the ones given by
        urlparse) are equal, only comparing components that are present in both
        URLs.

        If `parse_qs` is True, then the querystrings are parsed with QueryDict.
        This is useful if you don't want the order of parameters to matter.
        Otherwise, the query strings are compared as-is.

        Adapted from django.tests.auth_tests.test_views.AuthViewsTestCase
        """
        fields = ParseResult._fields

        for attr, x, y in zip(fields, urlparse(url), urlparse(expected)):
            if attr == 'path':
                if x != y:
                    self.fail('{0!r} != {1!r} Path\'s don\'t match'.format(url, expected))

            if parse_qs and attr == 'query':
                x, y = QueryDict(x), QueryDict(y)

            if x and y and x != y:
                self.fail('%r != %r (%s doesn\'t match)' % (url, expected, attr))

    def assertResponse(
        self,
        url, title, *args,
        user=None, get=False, data=None, status=200, expected_redirect_url=None, expected_messages=None,
        expected_context=None, **kwargs,
    ):
        """
        Assert for expected view Title, StatusCode, and UrlRedirect.
        :param url: Url to test.
        :param title: Expected page title. This is what displays on the browser tab.
        :param get: Bool indicating if request is GET or POST. Defaults POST.
        :param user: User to login with. If None, then tests response when not logged in.
        :param data: Optional POST data to sent to page. Should be in dictionary format.
        :param status: Expected status code for page, after redirections. Defaults to 200.
        :param expected_redirect_url: Optional url if page is expected to redirect. This should be what it redirects to.
        :param expected_messages: Expected message(s) to see on page. Aka, notifications that appear near top of page.
        :param expected_context: Expected context to see on page. Can be text or html elements.
        :return: The page response object, generated from the request.
        """
        # Either get value or an empty list/dict, to prevent mutability errors.
        data = data or {}
        expected_messages = expected_messages or []
        expected_context = expected_context or []

        # Handle user.
        if user is not None:
            # Get corresponding User model and login.
            user = self.get_user(user)
            self.client.force_login(user)
        else:
            # No user value provided. Ensure no user is currently logged in.
            self.client.logout()

        # Get page response.
        if get:
            response = self.client.get(url, data=data, follow=True)
        else:
            response = self.client.post(url, data=data, follow=True)

        # Handle debug printing.
        if self._debug_print:
            self.debug_print(response)

        # Verify request status code against expected value (after potential redirects).
        if status is not None:
            self.assertEqual(status, response.status_code)

        # Check redirects.
        if response.redirect_chain:
            # Redirect occurred. Check if it was expected.
            if expected_redirect_url is not None:
                # Redirect was expected. Ensure is at correct url.
                self.assertURLEqual(response.redirect_chain[-1][0], expected_redirect_url, parse_qs=True)

                # If redirecting to login page and no custom messages provided, then check for basic login message.
                if (
                    (expected_redirect_url == self.login_url) and
                    (expected_messages is None or len(expected_messages) == 0)
                ):
                    expected_messages = ['Please login to see this page.']

            else:
                # Redirect was not expected.
                raise ValueError('Got unexpected redirects: {0}'.format(response.redirect_chain))

        else:
            # Redirect did not occur.
            if expected_redirect_url is not None:
                # Redirect was expected.
                raise ValueError('Expected redirect to "{0}". No redirect occurred.'.format(expected_redirect_url))

        # Check page title.
        if title is not None:
            self.assertEqual(title, response.context['page']['title'], 'Incorrect Page Title')

        # Check expected messages for page.
        if isinstance(expected_messages, list) or isinstance(expected_messages, tuple):
            # Is list of messages. Check all.
            for expected_message in expected_messages:
                self.assertContains(response, expected_message)
        elif expected_messages is not None:
            # Is likely single message. Check if exists in response.
            self.assertContains(response, str(expected_messages))

        # Check expected context for page.
        if isinstance(expected_context, list) or isinstance(expected_context, tuple):
            # Is list of context items. Check all.
            for expected_value in expected_context:
                self.assertContains(response, expected_value)
        elif expected_context is not None:
            # Is likely single context item. Check if exists in response.
            self.assertContains(response, str(expected_context))

        # All assertions passed so far. Return found page response.
        return response

    def assertGetResponse(
        self,
        url, title, *args,
        user=None, data=None, status=200, expected_redirect_url=None, expected_messages=None, expected_context=None,
        **kwargs,
    ):
        """
        Assert for expected view Title, StatusCode, and UrlRedirect, when page is a GET request.
        :param url: Url to test.
        :param title: Expected page title. This is what displays on the browser tab.
        :param user: User to login with. If None, then tests response when not logged in.
        :param data: Optional POST data to sent to page. Should be in dictionary format.
        :param status: Expected status code for page, after redirections. Defaults to 200.
        :param expected_redirect_url: Optional url if page is expected to redirect. This should be what it redirects to.
        :param expected_messages: Expected message(s) to see on page. Aka, notifications that appear near top of page.
        :param expected_context: Expected context to see on page. Can be text or html elements.
        :return: The page response object, generated from the request.
        """
        # Call base function to handle actual logic.
        return self.assertResponse(
            url,
            title,
            *args,
            user=user,
            get=True,
            data=data,
            status=status,
            expected_redirect_url=expected_redirect_url,
            expected_messages=expected_messages,
            expected_context=expected_context,
            **kwargs,
        )

    def assertPostResponse(
        self,
        url, title, *args,
        user=None, data=None, status=200, expected_redirect_url=None, expected_messages=None, expected_context=None,
        **kwargs,
    ):
        """
        Assert for expected view Title, StatusCode, and UrlRedirect, when page is a POST request.
        :param url: Url to test.
        :param title: Expected page title. This is what displays on the browser tab.
        :param user: User to login with. If None, then tests response when not logged in.
        :param data: Optional POST data to sent to page. Should be in dictionary format.
        :param status: Expected status code for page, after redirections. Defaults to 200.
        :param expected_redirect_url: Optional url if page is expected to redirect. This should be what it redirects to.
        :param expected_messages: Expected message(s) to see on page. Aka, notifications that appear near top of page.
        :param expected_context: Expected context to see on page. Can be text or html elements.
        :return: The page response object, generated from the request.
        """
        # Call base function to handle actual logic.
        return self.assertResponse(
            url,
            title,
            *args,
            user=user,
            get=False,
            data=data,
            status=status,
            expected_redirect_url=expected_redirect_url,
            expected_messages=expected_messages,
            expected_context=expected_context,
            **kwargs,
        )

    def assertWhitelistUserAccess(
        self,
        url, title, whitelist_users, *args,
        get=False, data=None, status=200, expected_redirect_url=None, expected_messages=None, expected_context=None,
        **kwargs
    ):
        """
        Assert that the given (login) User(s) can access the given url.
        Mostly used to verify expected User Permission/Group url accessing.

        :param url: Url to test.
        :param title: Expected page title. This is what displays on the browser tab.
        :param whitelist_users: User(s) that should be able to access view. Should result in anything except login
                                redirect, 403, or 404.
        :param user: User to login with. If None, then tests response when not logged in.
        :param data: Optional POST data to sent to page. Should be in dictionary format.
        :param status: Expected status code for page, after redirections. Defaults to 200.
        :param expected_redirect_url: Optional url if page is expected to redirect. This should be what it redirects to.
        :param expected_messages: Expected message(s) to see on page. Aka, notifications that appear near top of page.
        :param expected_context: Expected context to see on page. Can be text or html elements.
        :return: The page response object, generated from the request.
        """
        valid_users_provided = False
        whitelist_user_list = []

        # Validate provided whitelist user(s).
        if isinstance(whitelist_users, list) or isinstance(whitelist_users, tuple):
            # Is array of Users. Check that at least one is an actual valid user.
            for whitelist_user in whitelist_users:
                try:
                    whitelist_user_list.append(self.get_user(whitelist_user))
                    valid_users_provided = True
                except get_user_model().DoesNotExist:
                    # Not a valid (login) User. Provide warning but otherwise skip.
                    logger.warning('Invalid "whitelist user" of "{0}" provided.'.format(whitelist_user))

        else:
            # Likely a single User. Validate.
            try:
                whitelist_user_list.append(self.get_user(whitelist_users))
                valid_users_provided = True
            except get_user_model().DoesNotExist:
                # Not a valid (login) User. Provide warning but otherwise skip.
                logger.warning('Invalid "whitelist user" of "{0}" provided.'.format(whitelist_users))

        # Check that at least one valid user was provided to test view on.
        if not valid_users_provided:
            print('Provided whitelist_users: {0}'.format(whitelist_users))
            raise ValidationError('No valid users provided.')

        # Loop through all validated users in list.
        for whitelist_user in whitelist_user_list:
            print('Checking user: "{0}" at "{1}"'.format(whitelist_user, url))

            # Call base function to handle actual logic.
            response = self.assertResponse(
                url,
                title,
                *args,
                user=whitelist_user,
                get=get,
                data=data,
                status=None,
                expected_redirect_url=expected_redirect_url,
                expected_messages=expected_messages,
                expected_context=expected_context,
                **kwargs,
            )

            # Check status code. Should be anything except login redirect, 403, or 404.
            if response.status_code == 403:
                # Got 403. Raise error.
                raise ValueError(
                    'Whitelist user "{0}" unable to access url at "{1}". Got 403.'.format(whitelist_user, url),
                )

            elif response.status_code == 404:
                # Got 404. Raise error.
                raise ValueError(
                    'Whitelist user "{0}" unable to access url at "{1}". Got 404.'.format(whitelist_user, url),
                )

            elif response.redirect_chain:
                # Got redirect. Check if login url.
                if response.url == self.login_url:
                    # Redirected to login page. Raise error.
                    raise ValueError(
                        'Whitelist user "{0}" unable to access url at "{1}". Got redirect to login page.'.format(
                            whitelist_user,
                            url,
                        )
                    )

            # Any other response values should be fine.

            # Check exact status match, if provided.
            if status:
                self.assertEqual(response.status_code, status)

    def assertBlacklistUserAccess(
        self,
        url, title, blacklist_users, *args,
        get=False, data=None, status=None, expected_redirect_url=None, expected_messages=None, expected_context=None,
        **kwargs
    ):
        """
        Assert that the given (login) User(s) cannot access the given url.

        :param url: Url to test.
        :param title: Expected page title. This is what displays on the browser tab.
        :param blacklist_users: User(s) that should NOT be able to access view. Should result in either login redirect,
                                403, or 404.
        :param user: User to login with. If None, then tests response when not logged in.
        :param data: Optional POST data to sent to page. Should be in dictionary format.
        :param status: Expected status code for page, after redirections. Defaults to 200.
        :param expected_redirect_url: Optional url if page is expected to redirect. This should be what it redirects to.
        :param expected_messages: Expected message(s) to see on page. Aka, notifications that appear near top of page.
        :param expected_context: Expected context to see on page. Can be text or html elements.
        :return: The page response object, generated from the request.
        """
        valid_users_provided = False
        blacklist_user_list = []

        # Validate provided blacklist user(s).
        if isinstance(blacklist_users, list) or isinstance(blacklist_users, tuple):
            # Is array of Users. Check that at least one is an actual valid user.
            for blacklist_user in blacklist_users:
                try:
                    blacklist_user_list.append(self.get_user(blacklist_user))
                    valid_users_provided = True
                except get_user_model().DoesNotExist:
                    # Not a valid (login) User. Provide warning but otherwise skip.
                    logger.warning('Invalid "blacklist user" of "{0}" provided.'.format(blacklist_user))

        else:
            # Likely a single User. Validate.
            try:
                blacklist_user_list.append(self.get_user(blacklist_users))
                valid_users_provided = True
            except get_user_model().DoesNotExist:
                # Not a valid (login) User. Provide warning but otherwise skip.
                logger.warning('Invalid "blacklist user" of "{0}" provided.'.format(blacklist_users))

        # Check that at least one valid user was provided to test view on.
        if not valid_users_provided:
            print('Provided blacklist_users: {0}'.format(blacklist_users))
            raise ValidationError('No valid users provided.')

        # Loop through all validated users in list.
        for blacklist_user in blacklist_user_list:
            print('Checking user: "{0}" at "{1}"'.format(blacklist_user, url))

            # Call base function to handle actual logic.
            response = self.assertResponse(
                url,
                title,
                *args,
                user=blacklist_user,
                get=get,
                data=data,
                status=None,
                expected_redirect_url=expected_redirect_url,
                expected_messages=expected_messages,
                expected_context=expected_context,
                **kwargs,
            )

            # Check status code. Should be anything except login redirect or 404.
            if response.status_code == 403 or response.status_code == 404:
                # Got 403/404. This is fine.
                pass

            elif response.redirect_chain:
                # Got redirect. Check if login url.
                if response.url == self.login_url:
                    # Redirected to login page. This is fine.
                    pass

                else:
                    # Redirected to non-login page. Raise error.
                    raise ValueError(
                        'Blacklist user "{0}" is able to access url at "{1}". Got redirect but otherwise accessed '
                        'fine.'.format(
                            blacklist_user,
                            url,
                        )
                    )

            else:
                # Any other values should raise error.
                raise ValueError('Blacklist user "{0}" is able to access url at "{1}".'.format(blacklist_user, url))

            # Check exact status match, if provided.
            if status:
                self.assertEqual(response.status_code, status)


class LiveServerTestCase(AbstractTestHelper, ChannelsLiveServerTestCase):
    """
    Test with Selenium to verify things like javascript.

    In a subclass, in the setUpClass() method, call super().setUpClass() and
    then create the number of drivers you need using cls.create_driver().
    E.g. twice to test two people working on something at once.

    By default, this will create two users, self.user1 and self.user2.
    You can use the addPermssion() function to give them any necessary permissions.

    Example Usage:

        class MyTest(LiveServerTestCase):
            @classmethod
            def setUpClass(cls):
                super().setUpClass()

                # Two browser windows, each with a different user.
                driver_1 = cls.create_driver()
                driver_2 = cls.create_driver()

            def test_thing(self):
                # Login with first window (self.driver1).
                self._login(self.driver_1, self.user_1.username, self.password_1)
                # Go to a url.
                self.driver1.get(self.live_server_url + reverse('cae_web_core:room_schedule', args=['classroom']))

    See cae_web_core/tests/functional/test_room_schedules.py for a thorough example.

    For debugging a test you can sleep to let you inspect the web page:

        last_working_function()

        import time
        time.sleep(30) # Wait 30 seconds

        function_that_breaks()

    Note that by default, any checks for an element on the page will instantly fail if the element is not available at
    that exact second.
    To change this functionality, and say, "wait 3 seconds for element before failing", you can use the
    "implicitly_wait()" function:

        driver_1 = cls.create_driver()
        driver_1.implicitly_wait(3)

    This is particularly useful in cases such as JavaScript, where we can't have a "wait for page load" function to
    ensure the JavaScript is executed before continuing.

    """
    _drivers = None
    serve_static = True

    #region Class Setup and Teardown

    def __init__(self, *args, **kwargs):
        # Run parent setup logic.
        super().__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        """
        Logic to run once, before any tests.
        """
        # Call parent logic.
        super().setUpClass()

        cls._drivers = {}

        # Initialize default user and site theme models.
        create_site_themes(None)

    @classmethod
    def create_driver(cls):
        """
        Create a new browser window with it's own session for testing.
        Should be used within child's setUpClass after super().setUpClass() has
        been called.
        """
        driver = None

        try:
            if settings.SELENIUM_TESTS_BROWSER == 'chrome':
                from selenium.webdriver.chrome.webdriver import WebDriver
                driver = WebDriver()
            elif settings.SELENIUM_TESTS_BROWSER == 'firefox':
                from selenium.webdriver.firefox.webdriver import WebDriver
                driver = WebDriver()
            else:
                raise ValueError('Unknown browser defined in selenium settings.')

            driver_array_index = len(cls._drivers)
            driver._driver_array_index = driver_array_index
            cls._drivers[driver_array_index] = driver
        except:
            if settings.SELENIUM_TESTS_BROWSER == 'chrome':
                sys.stderr.write('\n\n {0} \n |\n'.format('-' * 80))
                sys.stderr.write(' | ERROR: See {0} on how to setup Selenium with Chrome.\n'.format(
                    'https://sites.google.com/a/chromium.org/chromedriver/getting-started'
                ))
                sys.stderr.write(' |\n {0} \n\n'.format('-' * 80))
            elif settings.SELENIUM_TESTS_BROWSER == 'firefox':
                sys.stderr.write('\n\n {0} \n |\n'.format('-' * 80))
                sys.stderr.write(' | ERROR: See {0} on how to setup Selenium with Firefox.\n'.format(
                    'https://github.com/mozilla/geckodriver'
                ))
                sys.stderr.write(' |\n {0} \n\n'.format('-' * 80))
            else:
                raise ValueError('Unknown browser defined in selenium settings.')
            raise

        # # Set driver "implicit wait".
        # # This is the number of seconds to have the driver wait, on searching for a DOM element that isn't present.
        # driver.implicitly_wait(3)

        return driver

    @classmethod
    def close_driver(cls, driver):
        """
        Closes browser window and associated driver.
        """
        driver_index = driver._driver_array_index
        driver.quit()
        del cls._drivers[driver_index]

    @classmethod
    def tearDownClass(cls):
        """
        Logic to run once, after all tests.
        """
        # Quit all browser windows
        for driver in cls._drivers.values():
            driver.quit()

        # Call parent logic.
        super().tearDownClass()

    def setUp(self):
        """
        Logic to reset state before each individual test.
        """
        # Call parent logic.
        super().setUp()

    def tearDown(self):
        """
        Logic to reset state after each individual test.
        """
        # Call parent logic.
        super().tearDown()

        # Close all windows
        for driver in self._drivers.values():
            self._close_all_new_windows(driver)

    #endregion Class Setup and Teardown

    def assertPageTitle(self, driver, expected_title, err_msg=None):
        """
        Asserts that current page matches expected title.
        :param driver: Driver for browser window to test in.
        :param expected_title: Expected title value.
        :param err_msg: Optional formatted error message for unique error.
        """
        if err_msg is None:
            'Page title ("{0}") does not exist. Did you load the correct url?'.format(expected_title)

        self.assertTrue(expected_title in driver.title, err_msg)

    def assertPageHeader(self, driver, expected_header, err_msg=None):
        """
        Asserts that current page matches the expected header.
        :param driver: Driver for browser window to test in.
        :param expected_header: Expected header value.
        :param err_msg: Optional formatted error message for unique error.
        """
        if err_msg is None:
            'Page header ("{0}") does not exist. Did you load the correct url?'.format(expected_header)

        self.assertTrue(expected_header in driver.page_source, err_msg)

    def assertPageContains(self, driver, expected_page_content):
        """
        Asserts that current page contains the expected content.
        :param driver: Driver for browser window to test in.
        :param expected_page_content: Expected content value.
        """
        self.assertTrue(expected_page_content in driver.page_source)

    def assertPageNotContains(self, driver, expected_page_content):
        """
        Asserts that current page does not contain the expected content.
        :param driver: Driver for browser window to test in.
        :param expected_page_content: Expected content value.
        """
        self.assertFalse(expected_page_content in driver.page_source)

    #region Helper Functions

    def _login(self, driver, username, password, redirect_page_title=None, redirect_page_header=None):
        """
        Attempt to login on given browser window with given user.
        :param driver: Browser manager instance to login on.
        :param username: Username to login with.
        :param password: Password associated with user.
        :param redirect_page_title: Optional title to check for after login redirect.
        :param redirect_page_header: Optional header (H1 element) to check for after login redirect.
        """
        self.page_stale_check = driver.find_element_by_tag_name('html')

        # Get proper login url.
        login_url = settings.LOGIN_URL
        if not login_url.startswith('/'):
            # Might be a named url pattern.
            login_url = reverse(login_url)

        # Load login page.
        driver.get('{0}{1}'.format(self.live_server_url, login_url))

        # Test that page loaded successfully.
        self.assertPageTitle(driver, 'Login | CAE Center')

        # Attempt login.
        driver.find_element_by_name('username').send_keys(username)
        driver.find_element_by_name('password').send_keys(password)
        driver.find_element_by_css_selector('[type="submit"]').click()

        # Wait for new page to load.
        self._wait_for_page_load(driver)

        # Check for optional page redirect title.
        if redirect_page_title:
            err_msg = 'Login redirect page title ("{0}") does not exist. Did you login with the correct user?'.format(
                redirect_page_title,
            )
            self.assertPageTitle(driver, redirect_page_title, err_msg=err_msg)

        # Check for optional page redirect header.
        if redirect_page_header:
            err_msg = 'Login redirect page header ("{0}") does not exist. Did you login with the correct user?'.format(
                redirect_page_header,
            )
            self.assertPageHeader(driver, redirect_page_header, err_msg)

    #region Wait Helper Functions

    # @contextmanager
    def _wait_for_page_load(self, driver, timeout=5):
        """
        Waits for a new page to load.
        Should be used directly after expecting a new page load, such as a form button click that takes the user to a
        new page.

        Logic source from:
        http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html

        :param driver: Browser manager instance to check for page load on.
        :param timeout: Seconds to wait for timeout. Default of 5.
        """
        old_page = driver.find_element_by_tag_name('html')
        yield
        WebDriverWait(driver, timeout).until(
            staleness_of(old_page)
        )

    def _wait_for_id(self, driver, element_id, msg=None, wait_time=10, wait_for_remove=False):
        """
        Wait for provided css id to show on page.
        :param driver: Browser manager instance to wait on.
        :param element_id: Css element to wait for.
        :param msg: Optional message to display on failure.
        :param wait_time: Time to wait. Defaults to 10 seconds.
        :param wait_for_remove: If True, then waits until the provided element is removed.
        """
        return self.__do_wait(driver, By.ID, element_id, msg, wait_time, wait_for_remove)

    def _wait_for_css(self, driver, element_css, msg=None, wait_time=10, wait_for_remove=False):
        """
        Wait for provided css class to show on page.
        :param driver: Browser manager instance to wait on.
        :param element_css: Css element to wait for.
        :param msg: Optional message to display on failure.
        :param wait_time: Time to wait. Defaults to 10 seconds.
        :param wait_for_remove: If True, then waits until the provided element is removed.
        """
        return self.__do_wait(driver, By.CSS_SELECTOR, element_css, msg, wait_time, wait_for_remove)

    def _wait_for_xpath(self, driver, element_xpath, msg=None, wait_time=10, wait_for_remove=False):
        """
        Wait for xpath (xml?) to show on page.
        :param driver: Browser manager instance to wait on.
        :param element_xpath: Xpath element to wait for.
        :param msg: Optional message to display on failure.
        :param wait_time: Time to wait. Defaults to 10 seconds.
        :param wait_for_remove: If True, then waits until the provided element is removed.
        """
        return self.__do_wait(driver, By.XPATH, element_xpath, msg, wait_time, wait_for_remove)

    def __do_wait(self, driver, by, query, msg, wait_time, wait_for_remove):
        """
        Attempt to wait for given value to show on page.
        After time expired, display fail message and quit test.
        """
        try:
            if wait_for_remove:
                # Wait until element is no longer present.
                WebDriverWait(driver, wait_time).until(
                    EC.invisibility_of_element_located((by, query)),
                )
            else:
                # Wait until element is present.
                WebDriverWait(driver, wait_time).until(
                    EC.visibility_of_element_located((by, query)),
                )
        except TimeoutException:
            self.fail(msg or 'Element not found within time limit.')

    #endregion Wait Helper Functions

    #region Window Manipulation Helper functions

    def _open_new_window(self, driver):
        """
        Open a new window under the given driver.
        :param driver: Driver to open window under.
        """
        driver.execute_script('window.open("about:blank", "_blank");')
        driver.switch_to.window(driver.window_handles[-1])

    def _close_all_new_windows(self, driver):
        """
        Close additional windows under the given driver.
        :param driver: Driver to close additional windows of.
        """
        while len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            driver.execute_script('window.close();')
        if len(driver.window_handles) == 1:
            driver.switch_to.window(driver.window_handles[0])

    def _switch_to_window(self, driver, window_index):
        """
        Switch to window held by given driver.
        :param driver: Driver to switch window of.
        :param window_index: Index of window under driver.
        """
        driver.switch_to.window(driver.window_handles[window_index])

    #endregion Window Manipulation Helper Functions

    #endregion Helper Functions

# endregion Util Classes
