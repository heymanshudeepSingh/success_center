"""
CAE Home app testing Utility Functions and Classes.
"""

# System Imports.
import re, sys
from contextlib import contextmanager
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.db.models import ObjectDoesNotExist
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
from .. import models
from cae_home.management.commands.fixtures.user import create_site_themes
from cae_home.management.commands.seeders.user import create_groups, create_permission_group_users


UserModel = get_user_model()  # pylint: disable=invalid-name
default_password = settings.USER_SEED_PASSWORD


# |-----------------------------------------------------------------------------
# | Helpers - Used in below functions
# |-----------------------------------------------------------------------------


# NOTE: These two aren't currently used, since tests can load fixtures.
# They are here as example create_blank functions in tests/utils.py of an app.
def create_room_type(name, slug, **kwargs):
    room_type = models.RoomType.objects.create(
        name=name,
        slug=slug,
        **kwargs,
    )

    return room_type


def create_room(room_type, name, slug, **kwargs):
    room = models.Room.objects.create(
        room_type=room_type,
        name=name,
        slug=slug,
        **kwargs,
    )


# |-----------------------------------------------------------------------------
# | Classes - Util Classes for testing
# |-----------------------------------------------------------------------------


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


class AbstractTestHelper():
    """
    General expanded test functionality, applicable to all test types.
    Inherits from the standard django.test.TestCase, so it has all functionality the default Django Testing class does.
    """
    def __init__(self, *args, **kwargs):
        # Run parent setup logic.
        super().__init__(*args, **kwargs)

        # Save class variables.
        self._debug_print = False

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

        print('')
        print('')
        print('')

    def debug_print_content(self, response):
        debug_response_content(response_content=response.content.decode('utf-8'))

    def debug_print_context(self, response):
        debug_response_context(response_context=response.context)

    def debug_print_forms(self, response):
        debug_forms(response_context=response.context)

    def debug_print_messages(self, response):
        debug_messages(response_context=response.context)

    def create_default_users_and_groups(self, password=default_password):
        """
        Create expected/default groups and dummy users to associate with them.
        """
        create_groups()
        create_permission_group_users(password=password, with_names=False)

    def get_user(self, username, password=default_password):
        """
        Returns a user with the given username.
        :param username: Username to search.
        :param password: Password for user.
        """
        try:
            # Get user.
            user = UserModel.objects.get(username=username)

            # Check that user has associated password string saved.
            if not hasattr(user, 'password_string'):
                user.password_string = password

            return user
        except ObjectDoesNotExist:
            # Failed to find user.
            print(list(UserModel.objects.all().values_list('username')))
            raise ObjectDoesNotExist('User matching {0} was not found.')

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
        user = UserModel.objects.create_user(username=username, password=password)
        user.password_string = password

        # Check for optional permissions.
        if permissions:
            if isinstance(permissions, list) or isinstance(permissions, tuple):
                for permission in permissions:
                    self.add_permission(user, permission)
            else:
                self.add_permission(user, permissions)

        # Check for optional groups.
        if groups:
            if isinstance(groups, list) or isinstance(groups, tuple):
                for group in groups:
                    self.add_group(user, group)
            else:
                self.add_group(user, groups)

        return user

    def add_permission(self, user, name):
        """
        Add a permission to the given user.
        Ex: 'change_order'
        On failure, prints out all possible permissions and moves to next test.
        :param user: User object to add permission to.
        :param name: Permission name to add.
        """
        try:
            # Add permission.
            permission = Permission.objects.get(codename=name)
            user.user_permissions.add(permission)
        except ObjectDoesNotExist:
            # Failed to find permission.
            print(list(Permission.objects.all().values_list('codename')))
            raise ObjectDoesNotExist('Permission matching {0} not found.'.format(name))

    def add_group(self, user, name):
        """
        Add a permission group to the given user.
        Ex: 'CAE Admin'
        :param user: User object to add permission to.
        :param name: Group name to add.
        """
        try:
            # Add group.
            group = Group.objects.get(name=name)
            user.groups.add(group)
        except ObjectDoesNotExist:
            # Failed to find group.
            print(list(Group.objects.all().values_list('name')))
            raise ObjectDoesNotExist('Group matching {0} was not found.'.format(name))


class BaseTestCase(TestCase, AbstractTestHelper):
    pass


class IntegrationTestCase(TestCase, AbstractTestHelper):
    """
    Python Unit Testing extension (without Selenium).
    """
    def __init__(self, *args, **kwargs):
        # Run parent setup logic.
        super().__init__(*args, **kwargs)

        self._debug_print = False
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

    def assertResponse(self, url, title, *args, data=None, expected_redirect_url=None, status=200, get=False, **kwargs):
        """
        Assert for expected view Title, StatusCode, and UrlRedirect.
        :param url: Url to test.
        :param title: Expected page title. This is what displays on the browser tab.
        :param data: Optional POST data to sent to page. Should be in dictionary format.
        :param expected_redirect_url: Optional url if page is expected to redirect. This should be what it redirects to.
        :param status: Expected status code for page, after redirections. Defaults to 200.
        :param get: Bool indicating if request is GET or POST. Defaults POST.
        :return: The page response object, generated from the request.
        """
        # Either get data value or an empty dictionary, to prevent mutability errors.
        data = data or {}

        # Get page response.
        # self.client.force_login(self.user)
        if get:
            response = self.client.get(url, data=data, follow=True)
        else:
            response = self.client.post(url, data=data, follow=True)

        if self._debug_print:
            self.debug_print(response)

        # Verify request status code against expected value.
        self.assertEqual(status, response.status_code)

        # Check if redirect was expected.
        if expected_redirect_url is not None:
            # Redirect was expected. Check if redirect is at correct url.
            self.assertTrue(response.redirect_chain, 'Page did not redirect!')
            self.assertURLEqual(response.redirect_chain[-1][0], expected_redirect_url, parse_qs=True)

            # Extra testing if redirecting to login page.
            if expected_redirect_url == self.login_url:
                self.assertContains(response, 'Please login to see this page.')

        # Check page title.
        if title is not None:
            self.assertEqual(title, response.context['page']['title'], 'Incorrect Page Title')

        return response

    def assertGetResponse(self, url, title, *args, data=None, expected_redirect_url=None, status=200, **kwargs):
        """
        Assert for expected view Title, StatusCode, and UrlRedirect, when page is a GET request.
        :param url: Url to test.
        :param title: Expected page title. This is what displays on the browser tab.
        :param data: Optional POST data to sent to page. Should be in dictionary format.
        :param expected_redirect_url: Optional url if page is expected to redirect. This should be what it redirects to.
        :param status: Expected status code for page, after redirections. Defaults to 200.
        :param get: Bool indicating if request is GET or POST. Defaults POST.
        :return: The page response object, generated from the request.
        """
        return self.assertResponse(
            url,
            title,
            *args,
            get=True,
            data=data,
            expected_redirect_url=expected_redirect_url,
            status=status,
            **kwargs,
        )

    def assertPostResponse(self, url, title, *args, data=None, expected_redirect_url=None, status=200, **kwargs):
        """
        Assert for expected view Title, StatusCode, and UrlRedirect, when page is a POST request.
        :param url: Url to test.
        :param title: Expected page title. This is what displays on the browser tab.
        :param data: Optional POST data to sent to page. Should be in dictionary format.
        :param expected_redirect_url: Optional url if page is expected to redirect. This should be what it redirects to.
        :param status: Expected status code for page, after redirections. Defaults to 200.
        :param get: Bool indicating if request is GET or POST. Defaults POST.
        :return: The page response object, generated from the request.
        """
        # Either get data value or an empty dictionary, to prevent mutability errors.
        data = data or {}

        return self.assertResponse(
            url,
            title,
            *args,
            data=data,
            expected_redirect_url=expected_redirect_url,
            status=status,
            **kwargs,
        )


class LiveServerTestCase(StaticLiveServerTestCase, AbstractTestHelper):
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
                cls.driver1 = cls.create_driver()
                cls.driver2 = cls.create_driver()

            def test_thing(self):
                # Login with first window (self.driver1)
                self._login(self.driver1, self.user1.username, self.password1)
                # Go to a url
                self.driver1.get(self.live_server_url + reverse('cae_web_core:room_schedule', args=['classroom']))

    See cae_web_core/tests/functional/test_room_schedules.py for a thorough example.

    For debugging a test you can sleep to let you inspect the web page:

        last_working_function()

        import time
        time.sleep(30) # Wait 30 seconds

        function_that_breaks()

    """
    _drivers = None
    serve_static = True

    #region Class Setup and Teardown

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
