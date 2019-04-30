"""
CAE Home test utility functions and classes.
"""

import sys

from channels.testing import ChannelsLiveServerTestCase
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models import ObjectDoesNotExist
from django.http import QueryDict
from django.test import TestCase
from django.urls import reverse
from django.utils.six.moves.urllib.parse import ParseResult, urlparse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .. import models
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


class IntegrationTestCase(TestCase):
    """
    Python Unit Testing extension (without Selenium).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._debug_print = False

    def setUp(self):
        """
        Logic to reset state before each individual test.
        """
        super().setUp()

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
                    self.fail(
                        "{0!r} != {1!r} Path's don't match".format(url, expected))
            if parse_qs and attr == 'query':
                x, y = QueryDict(x), QueryDict(y)
            if x and y and x != y:
                self.fail("%r != %r (%s doesn't match)" %
                          (url, expected, attr))

    def assertPage(self, url, get=True, data=None, expected_url=None, status=200, is_admin_form=False, secure=False):
        data = data or {}
        self.client.force_login(self.user)
        if get:
            response = self.client.get(
                url, data=data, follow=True, secure=secure)
        else:
            response = self.client.post(
                url, data=data, follow=True, secure=secure)

        if self._debug_print:
            print('-'*80)
            print(response.content)
            print('-'*80)
            print(response.content.decode('utf-8'))
            print('-'*80)

            context = response.context or {}

            # Print form errors if available
            if is_admin_form:
                for error in context.get('errors', []):
                    print(error)
            if 'form' in context:
                print("Form Invalid {0!r}:".format(
                    not context['form'].is_valid()))
                for error in context['form'].non_field_errors():
                    print("\t{0}".format(error))
                for error in context['form'].errors:
                    print("\t{0}".format(error))
                print('-'*80)

            if 'formset' in context:
                for form in context['formset']:
                    print("Form(set) Errors:")
                    for error in form.non_field_errors():
                        print("\t{0}".format(error))
                    for error in form.errors:
                        print("\t{0}".format(error))
                    print('-'*80)

            if 'messages' in context:
                print("Messages")
                for message in context['messages']:
                    print("\t{0}".format(message))

        self.assertEqual(status, response.status_code)

        if expected_url is not None:
            # Check if redirect is at correct url
            self.assertTrue(
                response.redirect_chain,
                "Page did not redirect!")
            self.assertURLEqual(
                response.redirect_chain[-1][0],
                expected_url,
                parse_qs=True)

        return response

    def assertPageGet(self, url, **kwargs):
        return self.assertPage(url, True, **kwargs)

    def assertPagePost(self, url, data=None, **kwargs):
        data = data or {}
        return self.assertPage(url, False, data, **kwargs)


class LiveServerTestCase(ChannelsLiveServerTestCase):
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
    serve_static = True

    #region Class Setup and Teardown

    @classmethod
    def setUpClass(cls):
        """
        Logic to run once, before any tests.
        """
        super().setUpClass()

        try:
            if settings.SELENIUM_TESTS_BROWSER == 'chrome':
                # NOTE: Requires "chromedriver" binary to be installed in $PATH
                # https://sites.google.com/a/chromium.org/chromedriver/getting-started
                cls._options = webdriver.ChromeOptions()
            elif settings.SELENIUM_TESTS_BROWSER == 'firefox':
                cls._options = webdriver.FirefoxOptions()
            else:
                raise ValueError('Unknown browser defined in selenium settings.')

            if settings.SELENIUM_TESTS_HEADLESS:
                cls._options.add_argument('headless')  # --headless
            cls._drivers = []
        except:
            if settings.SELENIUM_TESTS_BROWSER == 'chrome':
                sys.stderr.write('\n\n {0} \n |\n'.format('-' * 80))
                sys.stderr.write(' | ERROR: See {0} on how to setup Selenium with Chrome.\n'.format(
                    'https://sites.google.com/a/chromium.org/chromedriver/getting-started'
                ))
                sys.stderr.write(' |\n {0} \n\n'.format('-' * 80))
                super().tearDownClass()
            elif settings.SELENIUM_TESTS_BROWSER == 'firefox':
                sys.stderr.write('\n\n {0} \n |\n'.format('-' * 80))
                sys.stderr.write(' | ERROR: See {0} on how to setup Selenium with Firefox.\n'.format(
                    'https://github.com/mozilla/geckodriver'
                ))
                sys.stderr.write(" |\n {0} \n\n".format('-' * 80))
                super().tearDownClass()
            else:
                super().tearDownClass()
                raise ValueError('Unknown browser defined in selenium settings.')
            raise

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
                driver = webdriver.Chrome(options=cls._options)
            elif settings.SELENIUM_TESTS_BROWSER == 'firefox':
                driver = webdriver.Firefox(options=cls._options)
            else:
                raise ValueError('Unknown browser defined in selenium settings.')
            cls._drivers.append(driver)
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
                sys.stderr.write(" |\n {0} \n\n".format('-' * 80))
            else:
                raise ValueError('Unknown browser defined in selenium settings.')
            raise

        return driver

    @classmethod
    def tearDownClass(cls):
        """
        Logic to run once, after all tests.
        """
        # Quit all browser windows
        for driver in cls._drivers:
            driver.quit()
        super().tearDownClass()

    def setUp(self):
        """
        Logic to reset state before each individual test.
        """
        super().setUp()

    def tearDown(self):
        """
        Logic to reset state after each individual test.
        """
        super().tearDown()

        # Close all windows
        for driver in self._drivers:
            self._close_all_new_windows(driver)

    #endregion Class Setup and Teardown


    #region Helper Functions

    #region User Management Helper Functions

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

    def create_user(self, username, password=default_password, permissions=None, groups=None, **kwargs):
        """
        Create new user. Optionally pass permissions/groups.
        :param username: Username to use.
        :param password: Password for user.
        :param permissions: Optional permissions to add.
        :param groups: Optional permission groups to add.
        :param kwargs: Passed to UserModel.objects.create_user().
        :return: Instance of created user.
        """
        # Create user.
        user = UserModel.objects.create_user(username=username, password=password, **kwargs)
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
            raise ObjectDoesNotExist('Permission matching {0} was not found.'.format(name))


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

    def _login(self, driver, username, password):
        """
        Attempt to login on given browser window with given user.
        :param driver: Browser manager instance to login on.
        :param username: Username to login with.
        :param password: Password associated with user.
        """
        # Get proper login url.
        login_url = settings.LOGIN_URL
        if not login_url.startswith('/'):
            # Might be a named url pattern.
            login_url = reverse(login_url)

        # Attempt login.
        driver.get(self.live_server_url + login_url)
        driver.find_element_by_name('username').send_keys(username)
        driver.find_element_by_name('password').send_keys(password)
        driver.find_element_by_css_selector('[type="submit"]').click()

    #endregion User Management Helper Functions

    #region Wait Helper Functions

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
            self.fail(msg or "Element not found within time limit.")

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
