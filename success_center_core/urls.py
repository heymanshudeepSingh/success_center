"""
Urls for Success Center Core app.
"""

# System Imports.
from django.urls import path

# User Imports.
from . import views

app_name = 'success_center_core'
urlpatterns = [
    # Home page.
    path('', views.Index.as_view(), name='index'),

    # For links to student usages.
    path('usage/<bronco_net>/', views.student_redirect, name='student_redirect'),
    path('student_checkout/<bronco_net>/', views.student_checkout, name='student_checkout'),

    # Admin Urls
    path('user_admin/', views.user_admin_panel, name='user_admin_panel'),
    path('user_admin/<pk>', views.user_admin_edit, name='user_admin_edit'),
    path('add_new_student', views.add_new_student, name='add_new_student'),
    path('change_step_admin/<pk>', views.change_step_employee_to_admin, name='change_step_employee_to_admin'),
    path('change_step_employee/<pk>', views.change_step_admin_to_employee, name='change_step_admin_to_employee'),
    path('change_step_employee_location/<pk>', views.change_step_employee_location, name='change_step_employee_location'),
    path('remove_from_step/<pk>', views.remove_from_step, name='remove_from_step'),

    # Location Admin URLs
    path('location_admin/', views.location_admin_panel, name='location_admin_panel'),
    path('location_admin/edit/<pk>', views.location_admin_edit, name='location_admin_edit'),
    path('location_admin/add', views.location_admin_add, name='location_admin_add'),
    path('location_admin/delete/<pk>', views.location_admin_delete, name='delete-location'),

    # student Usage Urls
    path('student_usage/', views.student_usage_panel, name='student_usage_panel'),
    path('student_usage/edit/<pk>', views.student_usage_edit, name='student_usage_edit'),
    path('student_usage/add', views.student_add, name='student_add'),
    path('student_usage/delete/<pk>', views.student_delete, name='student_delete'),
    path('student_usage/approve/<pk>', views.student_approve, name='student_approve'),
    path('student_usage/approve_ajax/', views.student_approve_ajax, name='approve_ajax'), # Nihal: Create an API View for checkbox system (unchecking and checking)
    path('student_usage/approve_all/', views.student_approve_all, name='student_approve_all'),
]
