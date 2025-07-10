# filepath: my_django_backend/my_django_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from commune import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('events/', views.events, name='events'),
    path('code-of-conduct/', views.code_of_conduct, name='code_of_conduct'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('accounts/', include('allauth.urls')),
    path('create_user/', views.create_user, name='create_user'),
    path('update_user/<int:user_id>/', views.update_user, name='update_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<int:event_id>/update/', views.update_event, name='update_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('events/<int:event_id>/register/', views.register_for_event, name='register_for_event'),
]