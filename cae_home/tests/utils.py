"""
CAE Home app testing Utility Functions and Classes.
"""

# System Imports.
import logging, re, sys
from channels.testing import ChannelsLiveServerTestCase
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
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

    Note the the below IntegrationTestCase class' get_response_content() function has a similar purpose, but trims much
    more thoroughly. We use a less thorough version here for printout, so that the values are actually human-readable
    and not a giant wall of unmanageable text.
    """
    print('{0} {1} {0}'.format('=' * 10, 'response.content.decode(\'utf-8\')'))

    if len(response_content) > 0:

        # Replace any repeating space characters.
        response_content = re.sub(r'  +', ' ', response_content)

        # Replace any repeating newline characters.
        response_content = re.sub(r'<br>|</br>', '\n', response_content)
        response_content = re.sub(r'(\n|\r)+', '\n', response_content)
        response_content = re.sub(r'((\n)+)((\s)+)|((\s)+)((\n)+)', '\n', response_content)

        # Print formatted page content string.
        print(response_content)
    else:
        # No context provided.
        print('Request "response.content" is empty.')

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
            for message in context_value:
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
        self._error_displayed = False

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

        # Display user groups.
        self.debug_print_permissions(response)

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
        debug_permissions(response.context['user'])

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
        # Check for iterable types. Likely an accident and meant to iterate through said types.
        if isinstance(user, list):
            raise TypeError('Expected type "User", got type "List". Did you mean to iterate on this list?')

        elif isinstance(user, tuple):
            raise TypeError('Expected type "User", got type "Tuple". Did you mean to iterate on this tuple?')

        elif isinstance(user, QuerySet):
            raise TypeError('Expected type "User", got type "QuerySet". Did you mean to iterate on this QuerySet?')

        # Check if already User model.
        if isinstance(user, get_user_model()):
            # Is User model. Return as-is.
            user = user

        else:
            # Is not user model. Attempt to get.
            try:
                print('Attempting to get user "{0}"'.format(user))
                user = get_user_model().objects.get(username=user)

            except get_user_model().DoesNotExist:
                # Failed to find user. Output messages.
                print('Valid Users: {0}'.format(list(get_user_model().objects.all().values_list('username'))))
                raise get_user_model().DoesNotExist('User matching {0} was not found.'.format(user))

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
                    print('Valid Permissions: {0}'.format(list(Permission.objects.all().values_list('codename'))))
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
                print('Valid Groups: {0}'.format(list(Group.objects.all().values_list('name'))))
                raise Group.DoesNotExist('Group matching "{0}" was not found.'.format(user_group))

        # If we made it this far, then valid Group acquired. Add to User.
        self.get_user(user).groups.add(group)

    def _handle_test_error(self, err):
        """
        Handling for graceful exit upon test error.
        """
        # Only handle if a child function has not already done so.
        if not self._error_displayed:
            print(logging.traceback.format_exc())
            self._error_displayed = True


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

    @classmethod
    def setUpClass(cls):
        """
        Logic to run once, before any tests.
        """
        # Call parent logic.
        super().setUpClass()
        
        # Initialize default user and site theme models.
        create_site_themes(None)

        # Initialize user models.
        cls.create_default_users_and_groups(cls)

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
        url, expected_title, *args,
        get=False, user=None, data=None, status=200, expected_redirect_url=None, expected_messages=None,
        allow_partial_messages=True, expected_content=None, **kwargs,
    ):
        """
        Assert for expected view Title, StatusCode, and UrlRedirect.
        :param url: Url to test.
        :param expected_title: Expected page title. This is what displays on the browser tab.
        :param get: Bool indicating if request is GET or POST. Defaults POST.
        :param user: User to login with. If None, then tests response when not logged in.
        :param data: Optional POST data to sent to page. Should be in dictionary format.
        :param status: Expected status code for page, after redirections. Defaults to 200.
        :param expected_redirect_url: Optional url if page is expected to redirect. This should be what it redirects to.
        :param expected_messages: Expected message(s) to see on page. Aka, notifications that appear near top of page.
        :param allow_partial_messages: Bool indicating if partial message matching is allowed. Defaults to True.
        :param expected_content: Expected context to see on page. Can be text or html elements.
        :return: The page response object, generated from the request.
        """
        # Surround everything in TryCatch, and display error at end.
        # This ensures that the actual error will always display at bottom of test, instead of having to scroll up.
        try:
            # Either get value or an empty list/dict, to prevent mutability errors.
            data = data or {}
            expected_messages = expected_messages or []
            expected_content = expected_content or []

            # Validate data types.
            if not isinstance(data, dict):
                raise TypeError('Provided "data" arg must be a dict, for passing into POST request.')

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

            # Get response content and context. We have both trimmed, to have contain whitespace data and no newlines.
            response_content = self.get_minimized_response_content(response)

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

                    # Cut off any url args, if present, to compare url directly.
                    trimmed_url = response.redirect_chain[-1][0]
                    trimmed_url = trimmed_url.split('?')[0] if '?' in trimmed_url else trimmed_url

                    # Check if redirecting to login page.
                    if trimmed_url == self.login_url:

                        # If no page context provided, check for basic login page values.
                        if len(expected_content) == 0:
                            expected_content = ['Login', 'Username', 'Password', 'Keep Me Logged In', 'Submit']

                else:
                    # Redirect was not expected.
                    raise AssertionError('Got unexpected redirects: {0}'.format(response.redirect_chain))

            else:
                # Redirect did not occur.
                if expected_redirect_url is not None:
                    # Redirect was expected.
                    raise AssertionError(
                        'Expected redirect to "{0}". No redirect occurred.'.format(expected_redirect_url),
                    )

            # Check page title.
            if expected_title is not None:
                # Get actual title and trim any extra whitespace characters.
                actual_title = self.get_page_title(response_content)

                # Check value against expected.
                self.assertEqual(expected_title, actual_title, 'Incorrect Page Title')

            # Check expected messages for page.
            self.assertPageMessages(response, expected_messages, allow_partial_messages=allow_partial_messages)

            # Check expected context for page.
            self.assertPageContent(response, expected_content)

            # All assertions passed so far. Return found page response.
            return response

        except Exception as err:
            # If we get any error at all, stop and display trace to console. Then raise error as normal.
            # This ensures actual error is always displayed at bottom, underneath all other output this Assertion gives.
            self._handle_test_error(err)
            raise err

    def assertGetResponse(
        self,
        url, title, *args,
        user=None, data=None, status=200, expected_redirect_url=None, expected_messages=None,
        allow_partial_messages=True, expected_content=None, **kwargs,
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
        :param allow_partial_messages: Bool indicating if partial message matching is allowed. Defaults to True.
        :param expected_content: Expected context to see on page. Can be text or html elements.
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
            allow_partial_messages=allow_partial_messages,
            expected_content=expected_content,
            **kwargs,
        )

    def assertPostResponse(
        self,
        url, title, *args,
        user=None, data=None, status=200, expected_redirect_url=None, expected_messages=None,
        allow_partial_messages=True, expected_content=None, **kwargs,
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
        :param allow_partial_messages: Bool indicating if partial message matching is allowed. Defaults to True.
        :param expected_content: Expected context to see on page. Can be text or html elements.
        :return: The page response object, generated from the request.
        """
        # Handle mutable data defaults.
        data = data or {}

        # Forcibly add values to "data" dict, so that POST doesn't validate to empty in view.
        # This guarantees that view serves as POST, like this specific assertion expects.
        if data == {}:
            # Has no values. Forcibly add a single key-value pair.
            data = {'UnitTest': True}

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
            allow_partial_messages=allow_partial_messages,
            expected_content=expected_content,
            **kwargs,
        )

    def assertPageMessages(self, response, expected_messages, allow_partial_messages=True):
        """
        Asserts that the given expected_messages text is found in the response "messages" context variable.

        Note that this function does not care if messages exist in response, but are not in the expected_messages value.
        It only cares if we pass expected_messages values which do not show up in the response.
        :param response: Response to parse actual served messages from.
        :param expected_messages: One or more messages to check for.
        :param allow_partial_messages: Bool indicating if partial message matching is allowed. Defaults to True.
        """
        if 'messages' not in response.context or len(response.context['messages']) == 0:
            # No message data found in response.

            # Verify expected messages is empty.
            if len(expected_messages) > 0:
                # One or more messages were expected. Print out data and raise error.
                print('Expected Messages:')
                if isinstance(expected_messages, list) or isinstance(expected_messages, tuple):
                    for expected_message in expected_messages:
                        print('    {0}'.format(expected_message))
                else:
                    print('    {0}'.format(expected_messages))

                err_msg = 'No messages found in response, yet messages were expected.'
                print(err_msg)
                raise AssertionError(err_msg)

        else:
            # Message data found in response. Gather into easy to compare list format.
            if expected_messages is not None and len(expected_messages) > 0:
                # One or more values in expected_messages param. Compare data.

                # First parse data from response context.
                temp_msg_data = response.context['messages']
                response_messages = []
                for response_message in temp_msg_data:
                    response_messages.append(response_message.message)

                # Compare values.
                if isinstance(expected_messages, list) or isinstance(expected_messages, tuple):
                    # Is list of messages. Check all.
                    for expected_message in expected_messages:

                        # Try to find current expected_message.
                        self._assertPageMessages(str(expected_message), response_messages, allow_partial_messages)

                elif expected_messages:
                    # Is likely single message. Check if exists in response message data.
                    self._assertPageMessages(str(expected_messages), response_messages, allow_partial_messages)

    def _assertPageMessages(self, expected_message, response_messages, allow_partial_messages):
        """
        Inner call for assertPageMessage function.

        Guarantees that behavior is the same, regardless of one message/multiple, and regardless of allowing partial
        matches or not.
        :param expected_message: One or more messages to check for.
        :param response_messages: Full set of actual messages served by response.
        :param allow_partial_messages: Bool indicating if partial message matching is allowed. Defaults to True.
        """
        # Check if allowing partial matches (allowed by default).
        if allow_partial_messages:

            # Partial message matches allowed.
            # To allow partial matches, we have to loop through each response_message value and check contains.
            # If all checks fail for all response_messages, then expected_message was not found.
            found_message = False
            for response_message in response_messages:
                try:
                    self.assertIn(expected_message, response_message)
                    found_message = True
                except AssertionError:
                    # Did not find partial match in current response_message. Attempt next one.
                    pass

            self.assertTrue(
                found_message,
                'Could not find message "{0}" in response.'.format(expected_message),
            )

        else:
            # Partial message matches not allowed. Check for direct match.
            self.assertIn(
                expected_message,
                response_messages,
                'Could not find message "{0}" in response.'.format(expected_message),
            )

    def assertPageContent(self, response, expected_content):
        """
        Behaves similar to default assertContains() function.
        The main difference is that Django templating may create large amounts of whitespace in the literal html value.
        Sometimes in places where we don't expected it.

        This custom assertion accounts for that, by taking the "expected_content" variable, and replaces all spaces with
        regex whitespace matches.
        :param response: Page response to compare against.
        :param expected_content: Expected value to find on page
        """
        # Check if expected_content exists.
        if expected_content is not None and len(expected_content) > 0:
            # Value expected_content exists. Attempt to search for content.

            # Replace page contents with minimized equivalent from get_minimized_response_content() function.
            response_content = self.get_minimized_response_content(response)

            if isinstance(expected_content, list) or isinstance(expected_content, tuple):
                # Is list of context items. Check all.

                # Loop through all items to verify.
                for expected_value in expected_content:
                    self._assertPageContent(response_content, expected_value)
            else:
                # Is likely single context item. Check if exists in response.
                self._assertPageContent(response_content, str(expected_content))

    def _assertPageContent(self, response, expected_content):
        """
        Inner call for assertPageContent function.

        Guarantees that behavior is the same, regardless of single value comparison or array comparison.
        """
        # Save original value for error output, on failure.
        orig_expected_content = expected_content

        # Ensure expected value is a string.
        expected_content = str(expected_content)

        # Format expected_content value for easier, more programmatic comparison.
        # Replace html linebreak with newline character equivalent.
        expected_content = re.sub(r'(<br>|</br>|<br/>|<br />)+', '\n', expected_content)

        # Replace html non-break spaces with character equivalent.
        expected_content = re.sub(r'&nbsp;', ' ', expected_content)

        # Reduce any whitespace (including repeated whitespace) down to a single space.
        expected_content = re.sub(r'((\s)+)', ' ', expected_content)

        # Escape dollar sign and up carrot. See get_minimized_response_content() description for more info.
        expected_content = re.sub(r'\$', '&#36;', expected_content)
        expected_content = re.sub(r'\^', '&#94;', expected_content)

        # Convert expected_content value to regex, for more dynamic comparison.
        # Split on spaces, to convert to regex.
        expected_content_split = expected_content.split(' ')

        # Convert to regex, such that anything previously a space will match any amount of whitespace in the response.
        expected_content = r'((\s)*)'
        for value in expected_content_split:
            # Add section to string.
            expected_content += value

            # Add check for 0 or more whitespace.
            expected_content += r'((\s)*)'

        # Get trimmed response content to compare against.
        response_content = self.get_minimized_response_content(response)

        # Escape any regex special characters, to prevent unexpected errors/mismatches.
        # Not currently used, but left for debugging purposes. Uncomment to escape known special regex characters.
        # response_content = self.escape_special_regex_chars(response_content)

        # Compare expected (and formatted) regex string against actual page content.
        if not re.search(expected_content, response_content):
            # Failed to find match. Raise validation error.
            raise AssertionError('Failed to find "{0}" in page content.'.format(orig_expected_content))

    def assertWhitelistUserAccess(
        self,
        url, title, whitelist_users, *args,
        data=None, status=200, expected_redirect_url=None, expected_messages=None, expected_content=None,
        **kwargs
    ):
        """
        Assert that the given (login) User(s) can access the given url.
        Mostly used to verify expected User Permission/Group url accessing.

        :param url: Url to test.
        :param title: Expected page title. This is what displays on the browser tab.
        :param whitelist_users: User(s) that should be able to access view. Should result in anything except login
                                redirect, 403, or 404.
        :param data: Optional POST data to sent to page. Should be in dictionary format.
        :param status: Expected status code for page, after redirections. Defaults to 200.
        :param expected_redirect_url: Optional url if page is expected to redirect. This should be what it redirects to.
        :param expected_messages: Expected message(s) to see on page. Aka, notifications that appear near top of page.
        :param expected_content: Expected context to see on page. Can be text or html elements.
        :return: The page response object, generated from the request.
        """
        # Surround everything in TryCatch, and display error at end.
        # This ensures that the actual error will always display at bottom of test, instead of having to scroll up.
        try:
            valid_users_provided = False
            whitelist_user_list = []

            # Validate provided whitelist user(s).
            if (
                isinstance(whitelist_users, list) or
                isinstance(whitelist_users, tuple) or
                isinstance(whitelist_users, QuerySet)
            ):
                # Is array of Users. Check that at least one is an actual valid user.
                for whitelist_user in whitelist_users:
                    try:
                        whitelist_user_list.append(self.get_user(whitelist_user))
                        valid_users_provided = True
                    except get_user_model().DoesNotExist:
                        # Not a valid (login) User. Provide warning but otherwise skip.
                        err_msg = 'Invalid "whitelist user" of "{0}" provided.'.format(whitelist_user)
                        print(err_msg)
                        logger.warning(err_msg)

            else:
                # Likely a single User. Validate.
                try:
                    whitelist_user_list.append(self.get_user(whitelist_users))
                    valid_users_provided = True
                except get_user_model().DoesNotExist:
                    # Not a valid (login) User. Provide warning but otherwise skip.
                    err_msg = 'Invalid "whitelist user" of "{0}" provided.'.format(whitelist_users)
                    print(err_msg)
                    logger.warning(err_msg)

            # Check that at least one valid user was provided to test view on.
            if not valid_users_provided:
                print('Provided whitelist_users: {0}'.format(whitelist_users))
                raise ValidationError('No valid users provided.')

            # Loop through all validated users in list.
            for whitelist_user in whitelist_user_list:
                print('Checking whitelist user: "{0}" at "{1}"'.format(whitelist_user, url))

                # Call base function to handle actual logic.
                response = self.assertResponse(
                    url,
                    title,
                    *args,
                    user=whitelist_user,
                    get=False if data else True,
                    data=data,
                    status=None,
                    expected_redirect_url=expected_redirect_url,
                    expected_messages=expected_messages,
                    expected_content=expected_content,
                    **kwargs,
                )

                # Check status code. Should be anything except login redirect, 403, or 404.
                if response.status_code == 403:
                    # Got 403. Raise error.
                    raise AssertionError(
                        'Whitelist user "{0}" unable to access url at "{1}". Got 403.'.format(whitelist_user, url),
                    )

                elif response.status_code == 404:
                    # Got 404. Raise error.
                    raise AssertionError(
                        'Whitelist user "{0}" unable to access url at "{1}". Got 404.'.format(whitelist_user, url),
                    )

                elif response.redirect_chain:
                    # Got redirect. Check if login url.
                    if response.redirect_chain[-1][0] == self.login_url:
                        # Redirected to login page. Raise error.
                        raise AssertionError(
                            'Whitelist user "{0}" unable to access url at "{1}". Got redirect to login page.'.format(
                                whitelist_user,
                                url,
                            )
                        )

                # Any other response values should be fine.

                # Check exact status match, if provided.
                if status:
                    self.assertEqual(response.status_code, status)

        except Exception as err:
            # If we get any error at all, stop and display trace to console. Then raise error as normal.
            # This ensures actual error is always displayed at bottom, underneath all other output this Assertion gives.
            self._handle_test_error(err)
            raise err

    def assertBlacklistUserAccess(
        self,
        url, title, blacklist_users, *args,
        data=None, status=None, expected_redirect_url=None, expected_messages=None, expected_content=None,
        **kwargs
    ):
        """
        Assert that the given (login) User(s) cannot access the given url.

        :param url: Url to test.
        :param title: Expected page title. This is what displays on the browser tab.
        :param blacklist_users: User(s) that should NOT be able to access view. Should result in either login redirect,
                                403, or 404.
        :param data: Optional POST data to sent to page. Should be in dictionary format.
        :param status: Expected status code for page, after redirections. Defaults to 200.
        :param expected_redirect_url: Optional url if page is expected to redirect. This should be what it redirects to.
        :param expected_messages: Expected message(s) to see on page. Aka, notifications that appear near top of page.
        :param expected_content: Expected context to see on page. Can be text or html elements.
        :return: The page response object, generated from the request.
        """
        # Surround everything in TryCatch, and display error at end.
        # This ensures that the actual error will always display at bottom of test, instead of having to scroll up.
        try:
            valid_users_provided = False
            blacklist_user_list = []

            # Validate provided blacklist user(s).
            if (
                isinstance(blacklist_users, list) or
                isinstance(blacklist_users, tuple) or
                isinstance(blacklist_users, QuerySet)
            ):
                # Is array of Users. Check that at least one is an actual valid user.
                for blacklist_user in blacklist_users:
                    try:
                        blacklist_user_list.append(self.get_user(blacklist_user))
                        valid_users_provided = True
                    except get_user_model().DoesNotExist:
                        # Not a valid (login) User. Provide warning but otherwise skip.
                        err_msg = 'Invalid "blacklist user" of "{0}" provided.'.format(blacklist_user)
                        print(err_msg)
                        logger.warning(err_msg)

            else:
                # Likely a single User. Validate.
                try:
                    blacklist_user_list.append(self.get_user(blacklist_users))
                    valid_users_provided = True
                except get_user_model().DoesNotExist:
                    # Not a valid (login) User. Provide warning but otherwise skip.
                    err_msg = 'Invalid "blacklist user" of "{0}" provided.'.format(blacklist_users)
                    print(err_msg)
                    logger.warning(err_msg)

            # Check that at least one valid user was provided to test view on.
            if not valid_users_provided:
                print('Provided blacklist_users: {0}'.format(blacklist_users))
                raise ValidationError('No valid users provided.')

            # Loop through all validated users in list.
            for blacklist_user in blacklist_user_list:
                print('Checking blacklist user: "{0}" at "{1}"'.format(blacklist_user, url))

                # Call base function to handle actual logic.
                response = self.assertResponse(
                    url,
                    title,
                    *args,
                    user=blacklist_user,
                    get=False if data else True,
                    data=data,
                    status=None,
                    expected_redirect_url=expected_redirect_url,
                    expected_messages=expected_messages,
                    expected_content=expected_content,
                    **kwargs,
                )

                # Check status code. Should be anything except login redirect or 404.
                if response.status_code == 403 or response.status_code == 404:
                    # Got 403/404. This is fine.
                    pass

                elif response.redirect_chain:
                    # Got redirect. Check if login url.
                    if response.redirect_chain[-1][0] == self.login_url:
                        # Redirected to login page. This is fine.
                        pass

                    else:
                        # Redirected to non-login page. Raise error.
                        raise AssertionError(
                            'Blacklist user "{0}" is able to access url at "{1}". Got redirect but otherwise accessed '
                            'fine.'.format(
                                blacklist_user,
                                url,
                            )
                        )

                else:
                    # Any other values should raise error.
                    raise AssertionError('Blacklist user "{0}" is able to access url at "{1}".'.format(blacklist_user, url))

                # Check exact status match, if provided.
                if status:
                    self.assertEqual(response.status_code, status)
        except Exception as err:
            # If we get any error at all, stop and display trace to console. Then raise error as normal.
            # This ensures actual error is always displayed at bottom, underneath all other output this Assertion gives.
            self._handle_test_error(err)
            raise err

    def get_minimized_response_content(self, response):
        """
        Returns response content, but stripped to be much more minimal, while otherwise equivalent.
        For example, this trims all newline characters and repeating spaces.

        Note that the above, module-level debug_response_content() function has a similar purpose, but trims much less
        thoroughly. We use a more thorough version here, because it's less human-readable but better for matching direct
        expected values programmatically.
        :param response: Page content from the response object. This is what displays as html.
        :return: Trimmed response content.
        """
        # Get base response content.
        if isinstance(response, str):
            # Is str. Assume is already the decoded response content value.
            response_content = response
        else:
            # Not a str. Assume we need to parse the decoded response content value.
            response_content = response.content.decode('utf-8')

        # Replace html linebreak with actual newline character.
        response_content = re.sub('<br>|</br>|<br/>|<br />', '\n', response_content)

        # Replace html non-break spaces with actual space character.
        response_content = re.sub('(&nbsp;)+', ' ', response_content)

        # Replace any whitespace trapped between newline characters.
        # This is empty/dead space, likely generated by how Django handles templating.
        response_content = re.sub(r'((\n|\r)+)((\s)+)((\n|\r)+)', '\n', response_content)

        # Replace any newline characters.
        response_content = re.sub(r'(\n|\r)+', '', response_content)

        # Replace any repeating whitespace characters.
        response_content = re.sub(r'(\s)+', ' ', response_content)

        # Convert any special characters back down to what we would expect.
        # For example, Django form errors seem to auto-escape apostrophe (') characters to the html code.
        # This is not very intuitive when testing and likely to lead to confusion/wasted time troubleshooting.
        # For some reason, Django seems to convert to hex version, so we need to account for those too.
        # Thus, search values are:  ( decimal_equivalent | hex_equivalent | english_equivalent ).
        response_content = re.sub(r'(&#39;|&#x27;|&apos;)', "'", response_content)  # Apostrophe character.
        response_content = re.sub(r'(&#34;|&#x22;|&quot;)', '"', response_content)  # Quotation character.
        response_content = re.sub(r'(&#60;|&#x3c;|&lt;)', '<', response_content)  # Opening bracket character.
        response_content = re.sub(r'(&#62;|&#x3e;|&gt;)', '>', response_content)  # Closing bracket character.
        response_content = re.sub(r'(&#91;|&#x5b;|&lbrack;)', '[', response_content)  # Opening array bracket character.
        response_content = re.sub(r'(&#93;|&#x5d;|&rbrack;)', ']', response_content)  # Closing array bracket character.
        response_content = re.sub(r'(&#123;|&#x7b;|&lbrace;)', '{', response_content)  # Opening dict bracket character.
        response_content = re.sub(r'(&#125;|&#x7d;|&rbrace;)', '}', response_content)  # Closing dict bracket character.

        # Special handling for dollar. The standard dollar sign breaks our regex search so we have to escape it.
        # Thus, we swap the "decimal_equivalent" and standard symbol values.
        response_content = re.sub(r'(\$|&#x24;|&dollar;)', '&#36;', response_content)  # Closing dict bracket character.

        # Similar handling for up-carrot as we do with dollar sign (above).
        response_content = re.sub(r'(\^|&#x5e;|&Hat;)', '&#94;', response_content)  # Closing dict bracket character.

        # Remove any whitespace directly before an opening html bracket ( < ).
        response_content = re.sub(r'((\s)+)<', '<', response_content)

        # Remove any whitespace directly after a closing html bracket ( > ).
        response_content = re.sub(r'>((\s)+)', '>', response_content)

        # Remove any whitespace around an opening array bracket ( [ ).
        response_content = re.sub(r'((\s)*)\[((\s)*)', '[', response_content)

        # Remove any whitespace around a closing array bracket ( ] ).
        response_content = re.sub(r'((\s)*)]((\s)*)', ']', response_content)

        # Remove any whitespace around an opening dict bracket ( { ).
        response_content = re.sub(r'((\s)*){((\s)*)', '{', response_content)

        # Remove any whitespace around a closing dict bracket ( } ).
        response_content = re.sub(r'((\s)*)}((\s)*)', '}', response_content)

        # Return minimized content value.
        return response_content

    def get_page_title(self, response_content):
        """
        Returns direct title from page content. Title is stripped to have no newline characters, and no repeating
        whitespace characters.
        :param response_content: Page content from the response object. This is what displays as html.
        :return: Trimmed page title.
        """
        # Find title html element.
        response_title = re.search(r'<title>([\S\s]+)</title>', response_content).group(1)

        # Strip any newlines from title. This is unnecessary if above get_response_content() function is called prior to
        # this one. But this line is present anyways in case the above function is skipped for whatever reason.
        response_title = re.sub(r'(\n|\r)+', '', response_title)

        # Remove any repeating whitespace, and remove any outer whitespace on title string.
        return re.sub(r'(\s)+', ' ', response_title).strip()

    def escape_special_regex_chars(self, str_value):
        """
        Escapes known possible "special characters" in regex to the equivalent html code.

        Note: Was used in debugging assertPageContains() function. Is not currently called.
        Left here in case further debugging of regex comparison is needed in the future.

        :param str_value: String to replace characters of.
        :return: Converted string.
        """
        # Escape special characters.
        special_char_list = ['.', '+', '*', '?', '^', '$', '(', ')', '[', ']', '{', '}', '|', '\\']

        # Find any special characters in strings and escape them.
        for special_char in special_char_list:

            # Check if in provided string.
            if special_char in str_value:
                # Character is in string. Replace with corresponding html code.

                if special_char == '.':
                    str_value = str_value.replace('.', '&#46;')
                elif special_char == '+':
                    str_value = str_value.replace('+', '&#43;')
                elif special_char == '*':
                    str_value = str_value.replace('*', '&#42;')
                elif special_char == '?':
                    str_value = str_value.replace('?', '&#63;')
                elif special_char == '^':
                    str_value = str_value.replace('^', '&#94;')
                elif special_char == '$':
                    str_value = str_value.replace('$', '&#36;')
                elif special_char == '(':
                    str_value = str_value.replace('(', '&#40;')
                elif special_char == ')':
                    str_value = str_value.replace(')', '&#41;')
                elif special_char == '[':
                    str_value = str_value.replace('[', '&#91;')
                elif special_char == ']':
                    str_value = str_value.replace(']', '&#93;')
                elif special_char == '{':
                    str_value = str_value.replace('{', '&#123;')
                elif special_char == '}':
                    str_value = str_value.replace('}', '&#125;')
                elif special_char == '|':
                    str_value = str_value.replace('|', '&#124;')
                elif special_char == '\\':
                    str_value = str_value.replace('\\', '&#92;')

        return str_value


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
