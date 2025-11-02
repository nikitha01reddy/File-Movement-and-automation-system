from django.urls import path
from . import views  # Import views from the same app

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashbd'),
    path('admin/disapproved/', views.disapproved_requests, name='disapproved_requests'),
    path('admin/pending/', views.pending_requests, name='pending_requests'),
    path('admin/approved/', views.approved_requests, name='approved_requests'),
    path('admin/request/<uuid:request_id>/', views.request_detail, name='request_detail'),
    path('user/dashboard/', views.user_dashboard, name='user_dashbd'),    
    path('user/received/', views.user_received_requests, name='user_received'),
    path('user/sent/', views.user_sent_requests, name='user_sent'),
    path('submit_request/', views.submit_request, name='submit_request'), 
    path('logout/', views.logout_view, name='logout'),
    path('user/history/', views.user_history, name='user_history'),
     # Add this new URL for handling request actions
    path('request/<uuid:request_id>/action/', views.handle_request_action, name='handle_request_action'),
    path('resubmit/<uuid:request_id>/', views.resubmit_request, name='resubmit_request'),
    # path('users/', views.user_list, name='user_list'),
    # path('users/get_data/<str:user_id>/', views.get_user_data, name='get_user_data'), 
    # path('edit_user/', views.edit_user, name='edit_user'),
    # path('create_user/', views.create_user, name='create_user'),
    # path('delete_user/', views.delete_user, name='delete_user'),
    path('admin/users/', views.user_list, name='user_list'),
    path("change-password/", views.change_password, name="change_password"),


]
