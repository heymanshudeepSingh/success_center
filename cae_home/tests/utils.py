"""CAE Home Test utility functions and classes"""
import sys

from channels.testing import ChannelsLiveServerTestCase
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
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


UserModel = get_user_model()  # pylint: disable=invalid-name


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
    """Test without Selenium"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._debug_print = False

    def setUp(self):
        super().setUp()
        self.user = UserModel.objects.create_user(
            username='steven', password='test')

    def addPermission(self, name):
        self.user.user_permissions.add(Permission.objects.get(codename=name))

    # Adapted from django.tests.auth_tests.test_views.AuthViewsTestCase
    def assertURLEqual(self, url, expected, parse_qs=False):
        """
        Given two URLs, make sure all their components (the ones given by
        urlparse) are equal, only comparing components that are present in both
        URLs.
        If `parse_qs` is True, then the querystrings are parsed with QueryDict.
        This is useful if you don't want the order of parameters to matter.
        Otherwise, the query strings are compared as-is.
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

    def assertPage(self, url, get=True, data={}, expected_url=None, status=200, is_admin_form=False, secure=False):
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

    def assertPagePost(self, url, data={}, **kwargs):
        return self.assertPage(url, False, data, **kwargs)


class LiveServerTestCase(ChannelsLiveServerTestCase):
    """
    Test with Selenium to verify things like javascript.

    In a subclass, set NUM_DRIVERS to how many browswers you need.
    E.g. to 2 to test two people working on something at once.

    By default, this will create two users, self.user1 and self.user2.
    You can use the addPermssion() function to give them any necessary permissions.

    Example Usage:

        class MyTest(LiveServerTestCase):
            NUM_DRIVERS = 2 # I want two browsers

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
    NUM_DRIVERS = 1

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            # NOTE: Requires "chromedriver" binary to be installed in $PATH
            # https://sites.google.com/a/chromium.org/chromedriver/getting-started
            options = webdriver.ChromeOptions()
            if settings.SELENIUM_TESTS_HEADLESS:
                options.add_argument('headless')  # --headless

            # Create NUM_DRIVERS number of browser windows
            cls._drivers = []
            for i in range(cls.NUM_DRIVERS):
                driver = webdriver.Chrome(options=options)
                cls._drivers.append(driver)
                setattr(cls, 'driver{}'.format(i+1), driver)
        except:
            sys.stderr.write("\n\n " + "-" * 80 + "\n |\n")
            sys.stderr.write(" | ERROR: See https://sites.google.com/a/chromium.org/chromedriver/getting-started on how to setup Selenium with Chrome.\n")
            sys.stderr.write(" |\n " + "-" * 80 + "\n\n")
            super().tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        # Quit all browser windows
        for driver in cls._drivers:
            driver.quit()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.password1 = 'password'
        self.user1 = UserModel.objects.create_user(
            username='user1', password=self.password1)
        self.password2 = self.password1
        self.user2 = UserModel.objects.create_user(
            username='user2', password=self.password2)

    def tearDown(self):
        super().tearDown()
        # Close all windows
        for driver in self._drivers:
            self._close_all_new_windows(driver)

    # Helper functions
    def addPermission(self, user, name):
        """Add a permission to the given user. E.g. 'change_order'"""
        perm = Permission.objects.filter(codename=name).first()

        if not perm:
            print(list(Permission.objects.all().values_list('codename')))
            raise Exception("Permission matching {} not found".format(name))

        user.user_permissions.add(perm)

    def _wait_for_id(self, driver, element_id, msg=None):
        return self._do_wait(driver, By.ID, element_id, msg)

    def _wait_for_css(self, driver, element_css, msg=None):
        return self._do_wait(driver, By.CSS_SELECTOR, element_css, msg)

    def _wait_for_xpath(self, driver, element_xpath, msg=None):
        return self._do_wait(driver, By.XPATH, element_xpath, msg)

    def _do_wait(self, driver, by, query, msg):
        """Show an error message if wait times out"""
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((by, query)),
            )
        except TimeoutException:
            self.fail(msg or "Element not found within time limit.")

    def _login(self, driver, username, password):
        login_url = settings.LOGIN_URL
        if not login_url.startswith('/'):
            # Might be a named url pattern
            login_url = reverse(login_url)
        driver.get(self.live_server_url + login_url)
        driver.find_element_by_name('username').send_keys(username)
        driver.find_element_by_name('password').send_keys(password)
        driver.find_element_by_css_selector('[type="submit"]').click()

    def _open_new_window(self, driver):
        driver.execute_script('window.open("about:blank", "_blank");')
        driver.switch_to.window(driver.window_handles[-1])

    def _close_all_new_windows(self, driver):
        while len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            driver.execute_script('window.close();')
        if len(driver.window_handles) == 1:
            driver.switch_to.window(driver.window_handles[0])

    def _switch_to_window(self, driver, window_index):
        driver.switch_to.window(driver.window_handles[window_index])
