import csv
from django.http import HttpResponse
from django.utils import timezone
from .models import User, Profile, Event, EventRegistration, Attendance, Certificate, ContactInquiry, Project, Resource


def get_admin_stats():
    now = timezone.now()
    first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    users = User.objects.all()
    profiles = Profile.objects.all()
    events = Event.objects.all()
    registrations = EventRegistration.objects.all()

    return {
        'total_members': users.count(),
        'active_members': users.filter(is_active=True).count(),
        'inactive_members': users.filter(is_active=False).count(),
        'new_members_this_month': users.filter(date_joined__gte=first_of_month).count(),
        'total_events': events.count(),
        'upcoming_events': events.filter(status__in=['published', 'upcoming'], start_date__gt=now).count(),
        'completed_events': events.filter(status='completed').count(),
        'cancelled_events': events.filter(status='cancelled').count(),
        'total_registrations': registrations.count(),
        'total_inquiries': ContactInquiry.objects.count(),
        'unread_inquiries': ContactInquiry.objects.filter(status='unread').count(),
        'total_projects': Project.objects.count(),
        'pending_projects': Project.objects.filter(status='pending').count(),
        'approved_projects': Project.objects.filter(status='approved').count(),
        'total_certificates': Certificate.objects.count(),
        'total_resources': Resource.objects.count(),
        'recent_members': users.order_by('-date_joined')[:5],
        'recent_registrations': registrations.select_related('user', 'event').order_by('-registered_at')[:5],
    }


def export_members_csv(queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="members.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Phone', 'Role', 'Skill Level',
                      'University', 'Course', 'Department', 'Is Active', 'Date Joined'])
    for user in queryset:
        p = getattr(user, 'profile', None)
        writer.writerow([
            user.username, user.email,
            p.phone if p else '', p.get_role_display() if p and p.role else 'member',
            p.get_skill_level_display() if p and p.skill_level else '',
            p.university if p else '', p.course if p else '', p.department if p else '',
            'Yes' if user.is_active else 'No', user.date_joined
        ])
    return response


def export_event_registrations_csv(event):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="registrations_{event.id}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Status', 'Registered At'])
    for reg in event.registrations.select_related('user').all():
        writer.writerow([reg.user.username, reg.user.email, reg.status, reg.registered_at])
    return response


def issue_certificate(event, user):
    if event.status_label != 'completed':
        return None
    attendance = Attendance.objects.filter(event=event, user=user, status='present').first()
    if not attendance:
        return None
    cert, created = Certificate.objects.get_or_create(event=event, user=user)
    return cert if created else None
