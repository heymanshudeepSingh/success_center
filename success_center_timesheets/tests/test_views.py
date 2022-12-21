"""
Test for Success Center Timesheet views logic.
"""

# System Imports.

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from cae_home import models as cae_home_models
from cae_home.tests.utils import IntegrationTestCase

# User Class Imports.
from .. import models
from ..views import populate_pay_periods
from .. import forms

# Module-level Variables.
success_center_test_users = settings.SUCCESS_CENTER_TEST_USERS


class SuccessCenterTimesheetsViewTests(IntegrationTestCase):
    """
    Tests for CAEWeb Shifts utils.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Logic to initialize model/testing variable data.
        This is run exactly once, before any class tests are run.
        """
        # Call parent logic.
        super().setUpTestData()

        populate_pay_periods()
        # Get current PayPeriod model.
        cls.current_date = timezone.localdate()
        cls.future_date = timezone.localdate() + timezone.timedelta(days=1)
        cls.pay_period = models.PayPeriod.get_payperiod()

        cls.step_admin = cae_home_models.User.create_dummy_model()

    def test_redirect(self):
        # Get current PayPeriod.
        pay_period = models.PayPeriod.get_payperiod()

        # Test unauthenticated. Should lead to login page.
        self.assertGetResponse(
            reverse('success_center_timesheets:index'),
            'Login | CAE Center',
            expected_redirect_url=(
                reverse('cae_home:login') + '?next=' + reverse('success_center_timesheets:index')
            ),
        )

        # Test authenticated as Success Center Employee.
        whitelist_user = ['step_employee', ]
        self.assertWhitelistUserAccess(
            reverse('success_center_timesheets:index'),
            None,
            whitelist_user,
            expected_content=[
                'Success Center | Timesheets',
                "Timesheets For: {}".format(whitelist_user),
                'Pay Period of {0} - {1}'.format(
                    pay_period.date_start.strftime('%b %d, %Y'),
                    pay_period.date_end.strftime('%b %d, %Y'),
                ),
            ],
        )

        # Test authenticated as Success Center Admin.
        whitelist_user = ['step_admin']
        self.assertWhitelistUserAccess(
            reverse('success_center_timesheets:index'),
            None,
            whitelist_user,
            expected_redirect_url=reverse('success_center_timesheets:admin_view'),
            expected_content=[
                'Success Center | Timesheets | Admin Panel',
                "STEP Employees",
                'Employees',
                'Submitted',
                'Remove',
            ],
        )

    def test_search_timesheet(self):
        # test if user searched for future timesheets
        form = forms.SearchTimesheet(data={"date": self.future_date})
        self.assertEqual(form.errors['date'], ["Incorrect data received, did u select a future date?"])
