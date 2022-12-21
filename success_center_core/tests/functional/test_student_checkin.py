"""
Selenium tests for CAEWeb Shifts app MyHours view.
"""

# System Imports.
from django.test import tag
from django.urls import reverse

# User Class Imports.
from cae_home.models import WmuUser
from cae_home.tests.utils import LiveServerTestCase


class TestMyHoursView(LiveServerTestCase):
    """
    Selenium Tests to verify things like javascript, sockets, and session logic.

    Note that selenium tends to take much longer to run than normal UnitTests. So any other logic should be run with
    standard UnitTesting, when possible.
    """
    @classmethod
    def setUpClass(cls):
        # Call parent logic.
        super().setUpClass()

    def setUp(self):
        """
        Logic to reset state before each individual test.
        """
        # Call parent logic.
        super().setUp()

        # Initialize user models.
        self.create_default_users_and_groups()

        # Initialize general models.
        self.wmu_student = WmuUser.objects.create(
            bronco_net='test_wmu_1',
            winno='12345',
            first_name='first_1',
            last_name='last_1',
        )
        self.login_user = self.get_user('step_admin')

    @tag('functional')
    def test_check_in_out(self):
        """
        Test that a student can be checked in and out.
        """
        # Create window instances.
        driver = self.create_driver()

        # Login user.
        self._login(
            driver,
            self.login_user.username,
            self.login_user.password_string,
            redirect_page_title='Index | Success Center',
            redirect_page_header='Success Center Home',
        )

        # Enter student value into form.
        driver.find_element_by_name('student_id').send_keys(self.wmu_student.bronco_net)
        driver.find_element_by_css_selector('[type="submit"]').click()

        # Wait for new page to load.
        self._wait_for_page_load(driver)

        # Verify we're on the student Check In page.
        self.assertPageTitle(driver, 'Index | Success Center')
        self.assertPageHeader(driver, 'Student Check In/Out')
        self.assertPageContains(driver, str(self.wmu_student.bronco_net).upper())
        self.assertPageContains(driver, self.wmu_student.winno)

        # Click "check in" button for student.
        driver.find_element_by_name('check_in').click()

        # Wait for new page to load.
        self._wait_for_page_load(driver)

        # Verify we're back to SuccessCtr index.
        self.assertPageTitle(driver, 'Index | Success Center')
        self.assertPageHeader(driver, 'Success Center Home')
        self.assertPageContains(driver, '<a href="/success_center/usage/{0}/">'.format(self.wmu_student.bronco_net))

        # Follow user link.
        driver.find_element_by_link_text(
            '{0}: {1} {2}'.format(
                self.wmu_student.bronco_net,
                self.wmu_student.first_name,
                self.wmu_student.last_name,
            )
        ).click()

        # Wait for new page to load.
        self._wait_for_page_load(driver)

        # Verify we're on the student Check Out page.
        self.assertPageTitle(driver, 'Index | Success Center')
        self.assertPageHeader(driver, 'Student Check In/Out')
        self.assertPageContains(driver, str(self.wmu_student.bronco_net).upper())
        self.assertPageContains(driver, self.wmu_student.winno)

        # Click "check out" button for student.
        driver.find_element_by_name('check_out').click()

        # Wait for new page to load.
        self._wait_for_page_load(driver)

        # Verify we're back to SuccessCtr index.
        self.assertPageTitle(driver, 'Index | Success Center')
        self.assertPageHeader(driver, 'Success Center Home')
        self.assertPageNotContains(driver, '<a href="/success_center/usage/{0}/">'.format(self.wmu_student.bronco_net))

        # If we got this far, test succeeded. Close windows.
        self.close_driver(driver)

    @tag('functional')
    def test_multi_window_attack(self):
        """
        Test attempting to check a student in or out with two windows, which originally could break session logic.

        Idk how/why SuccessCtr would do this, but we've gotten errors about it so it happened.
        """
        # Create window instances.
        driver_1 = self.create_driver()
        driver_2 = self.create_driver()

        # Login users.
        self._login(
            driver_1,
            self.login_user.username,
            self.login_user.password_string,
            redirect_page_title='Index | Success Center',
            redirect_page_header='Success Center Home',
        )
        self._login(
            driver_2,
            self.login_user.username,
            self.login_user.password_string,
            redirect_page_title='Index | Success Center',
            redirect_page_header='Success Center Home',
        )

        # Enter student value into form.
        driver_1.find_element_by_name('student_id').send_keys(self.wmu_student.bronco_net)
        driver_2.find_element_by_name('student_id').send_keys(self.wmu_student.bronco_net)
        driver_1.find_element_by_css_selector('[type="submit"]').click()
        driver_2.find_element_by_css_selector('[type="submit"]').click()

        # Wait for new page to load.
        self._wait_for_page_load(driver_1)
        self._wait_for_page_load(driver_2)

        # Verify we're on the student Check In page.
        self.assertPageTitle(driver_1, 'Index | Success Center')
        self.assertPageTitle(driver_2, 'Index | Success Center')
        self.assertPageHeader(driver_1, 'Student Check In/Out')
        self.assertPageHeader(driver_2, 'Student Check In/Out')
        self.assertPageContains(driver_1, str(self.wmu_student.bronco_net).upper())
        self.assertPageContains(driver_2, str(self.wmu_student.bronco_net).upper())
        self.assertPageContains(driver_1, self.wmu_student.winno)
        self.assertPageContains(driver_2, self.wmu_student.winno)

        # Click "check in" button for student in window 1.
        driver_1.find_element_by_name('check_in').click()

        # Wait for new page to load in window 1.
        self._wait_for_page_load(driver_1)

        # Click "check in" button for student in window 2.
        driver_2.find_element_by_name('check_in').click()

        # Wait for new page to load in window 2.
        self._wait_for_page_load(driver_2)

        # Verify window 1 (which should have clicked first) succeeded, while window 2 got a redirect.
        self.assertPageTitle(driver_1, 'Index | Success Center')
        self.assertPageHeader(driver_1, 'Success Center Home')
        self.assertPageContains(driver_1, '<a href="/success_center/usage/{0}/">'.format(self.wmu_student.bronco_net))
        self.assertPageTitle(driver_2, 'Index | Success Center')
        self.assertPageHeader(driver_2, 'Student Check In/Out')
        self.assertPageContains(driver_2, str(self.wmu_student.bronco_net).upper())
        self.assertPageContains(driver_2, self.wmu_student.winno)
        self.assertPageContains(driver_2, '<li class="message warning">')
        self.assertPageContains(driver_2, '<a href="/success_center/usage/{0}/">'.format(self.wmu_student.bronco_net))

        # Bring window 1 to Check Out page.
        driver_1.find_element_by_name('student_id').send_keys(self.wmu_student.bronco_net)
        driver_1.find_element_by_css_selector('[type="submit"]').click()

        # Wait for new page to load.
        self._wait_for_page_load(driver_1)

        # Verify window 1 is on Check Out page.
        self.assertPageTitle(driver_1, 'Index | Success Center')
        self.assertPageHeader(driver_1, 'Student Check In/Out')
        self.assertPageContains(driver_1, str(self.wmu_student.bronco_net).upper())
        self.assertPageContains(driver_1, self.wmu_student.winno)
        self.assertPageContains(driver_1, '<a href="/success_center/usage/{0}/">'.format(self.wmu_student.bronco_net))

        # Click "check out" button for student in window 1.
        driver_1.find_element_by_name('check_out').click()

        # Wait for new page to load in window 1.
        self._wait_for_page_load(driver_1)

        # Click "check in" button for student in window 2.
        driver_2.find_element_by_name('check_out').click()

        # Wait for new page to load in window 2.
        self._wait_for_page_load(driver_2)

        # Verify window 1 (which should have clicked first) succeeded, while window 2 got a redirect.
        self.assertPageTitle(driver_1, 'Index | Success Center')
        self.assertPageHeader(driver_1, 'Success Center Home')
        self.assertPageNotContains(
            driver_1,
            '<a href="/success_center/usage/{0}/">'.format(self.wmu_student.bronco_net),
        )
        self.assertPageTitle(driver_2, 'Index | Success Center')
        self.assertPageHeader(driver_2, 'Student Check In/Out')
        self.assertPageContains(driver_2, str(self.wmu_student.bronco_net).upper())
        self.assertPageContains(driver_2, self.wmu_student.winno)
        self.assertPageContains(driver_2, '<li class="message warning">')
        self.assertPageNotContains(
            driver_2,
            '<a href="/success_center/usage/{0}/">'.format(self.wmu_student.bronco_net),
        )

        # If we got this far, test succeeded. Close windows.
        self.close_driver(driver_1)
        self.close_driver(driver_2)
