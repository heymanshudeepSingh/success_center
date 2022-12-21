"""
Urls for success center Timesheets app.
"""

# System Imports.
from django.urls import path

# User Class Imports.
from . import views

app_name = 'success_center_timesheets'
urlpatterns = [
    # Home page.
    path('timesheets/', views.index, name='index'),

    path('timesheets/edit/', views.edit_timesheets, name='edit_timesheets'),
    path('timesheets/edit/<pk>', views.edit_timesheets, name='edit_timesheets_pk'),
    path('timesheets/edit/<pk>/<date>', views.edit_timesheets, name='edit_timesheets_shift_pk'),

    # admin urls
    path('timesheets/admin/', views.admin_view_index, name='admin_view'),
    path('timesheets/search_timesheets/', views.search_timesheets, name='admin_search_timesheets'),
    # path('timesheets/search_timesheets/<pk>', views.search_timesheets, name='admin_search_new_timesheets'),
    path('timesheets/admin/past_employees', views.display_past_step_employees, name='admin_past_employees'),
    path('timesheets/admin/past_employees/remove/<pk>', views.remove_step_employee, name='admin_remove_employee'),
    path('timesheets/admin/past_employees/restore/<pk>', views.restore_inactive_step_employee, name='admin_restore_inactive_employee'),
    path('timesheets/admin/email', views.admin_email, name='admin_email'),
    path('timesheets/admin/current_employees', views.current_employees, name='current_employees'),


]
