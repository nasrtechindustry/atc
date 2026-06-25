from django.urls import path
from community import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('code-of-conduct/', views.code_of_conduct, name='code_of_conduct'),
    path('contact/', views.contact, name='contact'),

    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/password-change/', views.password_change, name='password_change'),

    path('dashboard/', views.member_dashboard, name='member_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('members/', views.member_list, name='member_list'),
    path('members/<int:pk>/', views.member_detail, name='member_detail'),
    path('members/<int:pk>/activate/', views.member_activate, name='member_activate'),
    path('members/<int:pk>/role/', views.member_change_role, name='member_change_role'),
    path('members/export/', views.export_members, name='export_members'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    path('events/<int:pk>/register/', views.event_register, name='event_register'),
    path('events/<int:pk>/cancel-registration/', views.event_cancel_registration, name='event_cancel_registration'),
    path('events/<int:pk>/registrations/', views.event_registrations, name='event_registrations'),
    path('events/<int:pk>/registrations/<int:user_id>/cancel/', views.event_cancel_user_registration, name='event_cancel_user_registration'),
    path('events/<int:pk>/registrations/export/', views.event_export_registrations, name='event_export_registrations'),
    path('events/<int:pk>/attendance/<int:user_id>/', views.event_attendance, name='event_attendance'),
    path('my-events/', views.my_events, name='my_events'),

    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/create/', views.announcement_create, name='announcement_create'),
    path('announcements/<int:pk>/edit/', views.announcement_edit, name='announcement_edit'),
    path('announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),

    path('resources/', views.resource_list, name='resource_list'),
    path('resources/create/', views.resource_create, name='resource_create'),
    path('resources/<int:pk>/edit/', views.resource_edit, name='resource_edit'),
    path('resources/<int:pk>/delete/', views.resource_delete, name='resource_delete'),
    path('resources/<int:pk>/view/', views.resource_view_track, name='resource_view'),

    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/submit/', views.project_submit, name='project_submit'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/approve/', views.project_approve, name='project_approve'),
    path('projects/<int:pk>/reject/', views.project_reject, name='project_reject'),
    path('projects/<int:pk>/feature/', views.project_feature, name='project_feature'),

    path('certificates/', views.certificate_list, name='certificate_list'),
    path('certificates/<int:pk>/', views.certificate_detail, name='certificate_detail'),
    path('certificates/verify/', views.certificate_verify, name='certificate_verify'),
    path('certificates/create/', views.certificate_create, name='certificate_create'),

    path('feedback/event/<int:event_id>/', views.submit_feedback, name='submit_feedback'),

    path('chat/<int:event_id>/', views.event_chat_page, name='event_chat'),
    path('chat/<int:event_id>/token/', views.chat_token, name='chat_token'),
    path('chat/<int:event_id>/typing/', views.chat_typing, name='chat_typing'),
    path('chat/search-users/', views.chat_search_users, name='chat_search_users'),
    path('chat/<int:event_id>/messages/', views.chat_messages, name='chat_messages'),
    path('chat/delete/<int:msg_id>/', views.chat_delete, name='chat_delete'),

    path('hackathons/', views.hackathon_list, name='hackathon_list'),
    path('hackathons/create/', views.hackathon_create_view, name='hackathon_create'),
    path('hackathons/<int:pk>/', views.hackathon_detail, name='hackathon_detail'),
    path('hackathons/<int:pk>/register/', views.hackathon_register, name='hackathon_register'),
    path('hackathons/<int:pk>/create-team/', views.hackathon_create_team, name='hackathon_create_team'),
    path('hackathons/join-team/<int:team_id>/', views.hackathon_join_team, name='hackathon_join_team'),
    path('hackathons/<int:pk>/submit/', views.hackathon_submit_project, name='hackathon_submit_project'),
    path('admin-settings/', views.admin_settings, name='admin_settings'),
    path('admin-inquiries/', views.admin_inquiries, name='admin_inquiries'),
    path('admin-inquiries/<int:pk>/mark/', views.admin_inquiry_mark, name='admin_inquiry_mark'),
]
