from django.contrib import admin
from .models import User, Profile, Event, EventSpeaker, EventAgendaItem, EventMaterial, EventRegistration, Attendance, ContactInquiry, Announcement, Resource, Project, Certificate, EventFeedback, Badge, UserBadge, HackathonTeam, HackathonTeamMember, HackathonSubmission


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff']
    search_fields = ['username', 'email']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'skill_level', 'university']
    list_filter = ['role', 'skill_level']
    search_fields = ['user__username', 'university']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'start_date', 'capacity', 'created_by']
    list_filter = ['category', 'status']
    search_fields = ['title']
    date_hierarchy = 'start_date'


@admin.register(EventSpeaker)
class EventSpeakerAdmin(admin.ModelAdmin):
    list_display = ['name', 'event']
    search_fields = ['name']


@admin.register(EventAgendaItem)
class EventAgendaItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'event', 'start_time', 'end_time', 'order']
    list_filter = ['event']


@admin.register(EventMaterial)
class EventMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'event', 'created_at']
    list_filter = ['event']


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'status', 'registered_at']
    list_filter = ['status', 'event']
    search_fields = ['user__username', 'event__title']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'status', 'marked_at']
    list_filter = ['status']


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'email', 'subject']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'is_pinned', 'created_at']
    list_filter = ['is_published', 'is_pinned']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'is_featured', 'views_count']
    list_filter = ['category', 'is_published', 'is_featured']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'status', 'is_featured', 'created_at']
    list_filter = ['status', 'is_featured']
    search_fields = ['title', 'owner__username']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_id', 'user', 'event', 'issued_at', 'is_revoked']
    list_filter = ['is_revoked']
    search_fields = ['certificate_id', 'user__username']


@admin.register(EventFeedback)
class EventFeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'rating', 'created_at']
    list_filter = ['rating']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at']


@admin.register(HackathonTeam)
class HackathonTeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'created_by', 'member_count', 'is_open']
    list_filter = ['is_open', 'event']


@admin.register(HackathonTeamMember)
class HackathonTeamMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'team', 'role', 'joined_at']


@admin.register(HackathonSubmission)
class HackathonSubmissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'team', 'score', 'is_winner', 'submitted_at']
