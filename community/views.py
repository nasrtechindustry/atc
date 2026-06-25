import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import *
from .forms import *
from .decorators import *
from .services import *
from .utils import *


def index(request):
    now = timezone.now()
    announcements = Announcement.objects.filter(is_published=True)
    featured_projects = Project.objects.filter(status='approved', is_featured=True)
    upcoming_events = Event.objects.filter(
        status__in=['published', 'upcoming'],
        start_date__gt=now
    )[:6]
    return render(request, 'community/index.html', {
        'announcements': announcements,
        'featured_projects': featured_projects,
        'upcoming_events': upcoming_events,
    })


def about(request):
    return render(request, 'community/about.html')


def code_of_conduct(request):
    return render(request, 'community/code-of-conduct.html')


def contact(request):
    if request.method == 'POST':
        form = ContactInquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully.')
            return redirect('contact')
    else:
        form = ContactInquiryForm()
    return render(request, 'community/contact.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Profile.objects.get_or_create(user=user)
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'community/auth/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        login_input = request.POST.get('username')
        password = request.POST.get('password')
        user = None
        if '@' in login_input:
            try:
                user_obj = User.objects.get(email=login_input)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        if not user:
            user = authenticate(request, username=login_input, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            if user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('member_dashboard')
        else:
            messages.error(request, 'Invalid username/email or password.')
    return render(request, 'community/auth/login.html')


def logout_view(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated.')
            return redirect('index')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'community/auth/password_change.html', {'form': form})


@admin_required
def admin_dashboard(request):
    stats = get_admin_stats()
    announcements = Announcement.objects.filter(is_published=True)[:5]
    return render(request, 'community/dashboard/admin_dashboard.html', {'stats': stats, 'announcements': announcements})


@admin_required
def member_list(request):
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')

    users = User.objects.all().order_by('-date_joined')

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(profile__phone__icontains=query) |
            Q(profile__university__icontains=query)
        )

    if role_filter:
        users = users.filter(profile__role=role_filter)

    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)

    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'community/members/member_list.html', {
        'members': page_obj,
        'query': query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'roles': Profile.ROLE_CHOICES,
    })


@admin_required
def member_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = getattr(user, 'profile', None)
    events = user.event_registrations.select_related('event').all()
    projects = user.projects.all()
    certificates = user.certificates.all()
    return render(request, 'community/members/member_detail.html', {
        'member': user,
        'profile': profile,
        'events': events,
        'projects': projects,
        'certificates': certificates,
    })


@admin_required
def member_activate(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'{user.username} has been {status}.')
    return redirect(request.META.get('HTTP_REFERER', 'member_list'))


@admin_required
def member_change_role(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        new_role = request.POST.get('role')
        profile = getattr(user, 'profile', None)
        if profile and new_role in dict(Profile.ROLE_CHOICES):
            profile.role = new_role
            profile.save()
            messages.success(request, f"{user.username}'s role updated to {profile.get_role_display()}.")
        else:
            messages.error(request, 'Invalid role or profile not found.')
    return redirect(request.META.get('HTTP_REFERER', 'member_list'))


@admin_required
def export_members(request):
    queryset = User.objects.all()
    return export_members_csv(queryset)


def event_list(request):
    now = timezone.now()
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    status = request.GET.get('status', '')

    events = Event.objects.all().order_by('-start_date')

    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )

    if category:
        events = events.filter(category=category)

    if status:
        events = events.filter(status=status)
    else:
        events = events.exclude(status='draft')

    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    template = 'community/events/event_list.html'
    if not request.user.is_authenticated:
        template = 'community/events/public_event_list.html'
    return render(request, template, {
        'events': page_obj,
        'query': query,
        'category': category,
        'status': status,
        'categories': Event.CATEGORY_CHOICES,
    })


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    speakers = event.speakers.all()
    agenda_items = event.agenda_items.all()
    materials = event.materials.all()
    is_registered = False
    has_attended = False
    if request.user.is_authenticated:
        reg = EventRegistration.objects.filter(event=event, user=request.user).first()
        if reg:
            is_registered = reg.status == 'registered'
            has_attended = reg.status == 'attended'
    template = 'community/events/event_detail.html'
    if not request.user.is_authenticated:
        template = 'community/events/public_event_detail.html'
    return render(request, template, {
        'event': event,
        'speakers': speakers,
        'agenda_items': agenda_items,
        'materials': materials,
        'is_registered': is_registered,
        'has_attended': has_attended,
    })


@organizer_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            # Save speakers
            names = request.POST.getlist('speaker_name')
            bios = request.POST.getlist('speaker_bio')
            phones = request.POST.getlist('speaker_phone')
            for i, name in enumerate(names):
                if name.strip():
                    EventSpeaker.objects.create(event=event, name=name.strip(), bio=bios[i].strip() if i < len(bios) else '', phone=phones[i].strip() if i < len(phones) else '')
            # Save agenda items
            titles = request.POST.getlist('agenda_title')
            start_times = request.POST.getlist('agenda_start')
            end_times = request.POST.getlist('agenda_end')
            descs = request.POST.getlist('agenda_desc')
            speaker_names = request.POST.getlist('agenda_speaker')
            for i, title in enumerate(titles):
                if title.strip():
                    speaker = None
                    if i < len(speaker_names) and speaker_names[i]:
                        speaker = event.speakers.filter(name=speaker_names[i]).first()
                    EventAgendaItem.objects.create(event=event, title=title.strip(), start_time=start_times[i] if i < len(start_times) else '00:00', end_time=end_times[i] if i < len(end_times) else '00:00', description=descs[i].strip() if i < len(descs) else '', speaker=speaker, order=i)
            messages.success(request, 'Event created successfully.')
            return redirect('event_list')
    else:
        initial = {}
        category = request.GET.get('category')
        if category:
            initial['category'] = category
        form = EventForm(initial=initial)
    return render(request, 'community/events/event_form.html', {'form': form, 'event': None})


@organizer_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            # Update speakers: remove old, add new
            event.speakers.all().delete()
            names = request.POST.getlist('speaker_name')
            bios = request.POST.getlist('speaker_bio')
            phones = request.POST.getlist('speaker_phone')
            for i, name in enumerate(names):
                if name.strip():
                    EventSpeaker.objects.create(event=event, name=name.strip(), bio=bios[i].strip() if i < len(bios) else '', phone=phones[i].strip() if i < len(phones) else '')
            # Update agenda: delete old, create new
            event.agenda_items.all().delete()
            titles = request.POST.getlist('agenda_title')
            start_times = request.POST.getlist('agenda_start')
            end_times = request.POST.getlist('agenda_end')
            descs = request.POST.getlist('agenda_desc')
            speaker_names = request.POST.getlist('agenda_speaker')
            for i, title in enumerate(titles):
                if title.strip():
                    speaker = None
                    if i < len(speaker_names) and speaker_names[i]:
                        speaker = event.speakers.filter(name=speaker_names[i]).first()
                    EventAgendaItem.objects.create(event=event, title=title.strip(), start_time=start_times[i] if i < len(start_times) else '00:00', end_time=end_times[i] if i < len(end_times) else '00:00', description=descs[i].strip() if i < len(descs) else '', speaker=speaker, order=i)
            messages.success(request, 'Event updated successfully.')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'community/events/event_form.html', {'form': form, 'event': event})


@organizer_required
def event_delete(request, pk):
    if request.method == 'POST':
        event = get_object_or_404(Event, pk=pk)
        event.delete()
        messages.success(request, 'Event deleted successfully.')
    return redirect('event_list')


@login_required
def event_register(request, pk):
    event = get_object_or_404(Event, pk=pk)
    now = timezone.now()

    if event.status in ['cancelled', 'completed']:
        messages.error(request, 'This event is no longer accepting registrations.')
        return redirect('event_detail', pk=event.pk)

    if event.is_full():
        messages.error(request, 'This event is already full.')
        return redirect('event_detail', pk=event.pk)

    reg, created = EventRegistration.objects.get_or_create(event=event, user=request.user, defaults={'status': 'registered'})
    if not created:
        if reg.status == 'cancelled':
            reg.status = 'registered'
            reg.save()
            messages.success(request, f'You have registered for {event.title}!')
        else:
            messages.info(request, 'You are already registered for this event.')
    else:
        messages.success(request, f'You have registered for {event.title}!')
    return redirect('event_detail', pk=event.pk)


@login_required
def event_cancel_registration(request, pk):
    event = get_object_or_404(Event, pk=pk)
    registration = get_object_or_404(EventRegistration, event=event, user=request.user)
    registration.status = 'cancelled'
    registration.save()
    messages.success(request, 'Your registration has been cancelled.')
    return redirect('event_detail', pk=event.pk)


@organizer_required
def event_registrations(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        reg_id = request.POST.get('registration_id')
        new_status = request.POST.get('status')
        if reg_id and new_status in ['registered', 'cancelled', 'attended', 'missed']:
            registration = get_object_or_404(EventRegistration, pk=reg_id, event=event)
            registration.status = new_status
            registration.save()
            messages.success(request, 'Registration status updated.')
        return redirect('event_registrations', pk=event.pk)

    registrations = event.registrations.select_related('user__profile').all()
    return render(request, 'community/events/event_registrations.html', {
        'event': event,
        'registrations': registrations,
    })


@organizer_required
def event_export_registrations(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return export_event_registrations_csv(event)


@organizer_required
def event_cancel_user_registration(request, pk, user_id):
    event = get_object_or_404(Event, pk=pk)
    registration = get_object_or_404(EventRegistration, event=event, user_id=user_id)
    registration.status = 'cancelled'
    registration.save()
    messages.success(request, 'Registration cancelled.')
    return redirect('event_registrations', pk=event.pk)


def event_attendance(request, pk, user_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, pk=pk)
        status = request.POST.get('status', 'present')

        if user_id and status in ['present', 'absent']:
            user = get_object_or_404(User, pk=user_id)
            attendance, created = Attendance.objects.update_or_create(
                event=event,
                user=user,
                defaults={'status': status, 'marked_by': request.user},
            )
            # Update registration status to match attendance
            reg = EventRegistration.objects.filter(event=event, user=user, status='registered').first()
            if reg:
                reg.status = 'attended' if status == 'present' else 'missed'
                reg.save()
            if created:
                messages.success(request, f'Attendance marked for {user.username}.')
            else:
                messages.success(request, f'Attendance updated for {user.username}.')

            if status == 'present':
                event_status = event.status_label
                if event_status == 'completed' and not Certificate.objects.filter(event=event, user=user).exists():
                    issue_certificate(event, user)

    return redirect(request.META.get('HTTP_REFERER', 'event_registrations'))


@login_required
@profile_required
def member_dashboard(request):
    now = timezone.now()
    registrations = request.user.event_registrations.select_related('event').filter(
        status='registered',
        event__start_date__gt=now
    )[:5]
    history = request.user.event_registrations.select_related('event').filter(
        event__end_date__lt=now
    )[:5]
    announcements = Announcement.objects.filter(is_published=True)[:5]
    certificates = request.user.certificates.select_related('event').all()
    projects = request.user.projects.all()
    upcoming_events = Event.objects.filter(
        status__in=['published', 'upcoming'],
        start_date__gt=now
    ).order_by('start_date')[:6]
    return render(request, 'community/dashboard/member_dashboard.html', {
        'registrations': registrations,
        'history': history,
        'announcements': announcements,
        'certificates': certificates,
        'projects': projects,
        'upcoming_events': upcoming_events,
    })


@login_required
def profile_view(request):
    profile = getattr(request.user, 'profile', None)
    return render(request, 'community/members/profile.html', {'profile': profile})


@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'community/members/profile_form.html', {'form': form})


def announcement_list(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser or hasattr(request.user, 'profile') and request.user.profile.role in ['super_admin', 'admin']):
        announcements = Announcement.objects.all()
    else:
        announcements = Announcement.objects.filter(is_published=True)

    announcements = announcements.order_by('-is_pinned', '-created_at')
    paginator = Paginator(announcements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'community/announcements/announcement_list.html', {'announcements': page_obj})


@admin_required
def announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, 'Announcement created.')
            return redirect('announcement_list')
    else:
        form = AnnouncementForm()
    return render(request, 'community/announcements/announcement_form.html', {'form': form})


@admin_required
def announcement_edit(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated.')
            return redirect('announcement_list')
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'community/announcements/announcement_form.html', {'form': form, 'announcement': announcement})


@admin_required
def announcement_delete(request, pk):
    if request.method == 'POST':
        announcement = get_object_or_404(Announcement, pk=pk)
        announcement.delete()
        messages.success(request, 'Announcement deleted.')
    return redirect('announcement_list')


def resource_list(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    resources = Resource.objects.filter(is_published=True)

    if query:
        resources = resources.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    if category:
        resources = resources.filter(category=category)

    resources = resources.order_by('-is_featured', '-created_at')
    paginator = Paginator(resources, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        html = render_to_string('community/resources/_resource_items.html', {'resources': page_obj})
        return HttpResponse(html)

    return render(request, 'community/resources/resource_list.html', {
        'resources': page_obj,
        'query': query,
        'category': category,
        'categories': Resource.CATEGORY_CHOICES,
        'total': paginator.count,
    })


@staff_or_admin_required
def resource_create(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.created_by = request.user
            resource.save()
            messages.success(request, 'Resource created.')
            return redirect('resource_list')
    else:
        form = ResourceForm()
    return render(request, 'community/resources/resource_form.html', {'form': form})


@staff_or_admin_required
def resource_edit(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated.')
            return redirect('resource_list')
    else:
        form = ResourceForm(instance=resource)
    return render(request, 'community/resources/resource_form.html', {'form': form, 'resource': resource})


@login_required
def event_chat_page(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'community/chat/event_chat.html', {'event': event})


def resource_view_track(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    user = request.user if request.user.is_authenticated else None
    ip = request.META.get('REMOTE_ADDR', '')
    view, created = ResourceView.objects.get_or_create(resource=resource, user=user, defaults={'ip_address': ip})
    if created:
        resource.views_count += 1
        resource.save(update_fields=['views_count'])
    if resource.url:
        return redirect(resource.url)
    return redirect('resource_list')


def resource_delete(request, pk):
    if request.method == 'POST':
        resource = get_object_or_404(Resource, pk=pk)
        resource.delete()
        messages.success(request, 'Resource deleted.')
    return redirect('resource_list')


def project_list(request):
    if request.user.is_authenticated:
        projects = Project.objects.filter(
            Q(status='approved') | Q(owner=request.user)
        ).order_by('-is_featured', '-created_at')
    else:
        projects = Project.objects.filter(status='approved').order_by('-is_featured', '-created_at')
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'community/projects/project_list.html', {'projects': page_obj})


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'community/projects/project_detail.html', {'project': project})


@login_required
def project_submit(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, 'Project submitted for review.')
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'community/projects/project_form.html', {'form': form})


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        messages.error(request, 'You can only edit your own projects.')
        return redirect('project_detail', pk=project.pk)
    if project.status not in ['pending', 'rejected']:
        messages.error(request, 'Only pending or rejected projects can be edited.')
        return redirect('project_detail', pk=project.pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            project.status = 'pending'
            project.save()
            messages.success(request, 'Project updated and resubmitted for review.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'community/projects/project_form.html', {'form': form, 'project': project})


@moderator_required
def project_approve(request, pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=pk)
        project.status = 'approved'
        project.save()
        messages.success(request, f'"{project.title}" has been approved.')
    return redirect('project_list')


@moderator_required
def project_reject(request, pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=pk)
        project.status = 'rejected'
        project.save()
        messages.success(request, f'"{project.title}" has been rejected.')
    return redirect('project_list')


@admin_required
def project_feature(request, pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=pk)
        project.is_featured = not project.is_featured
        project.save()
        status = 'featured' if project.is_featured else 'unfeatured'
        messages.success(request, f'"{project.title}" has been {status}.')
    return redirect('project_list')


@login_required
def certificate_list(request):
    certificates = request.user.certificates.select_related('event').all()
    return render(request, 'community/certificates/certificate_list.html', {'certificates': certificates})


def certificate_detail(request, pk):
    certificate = get_object_or_404(Certificate, pk=pk)
    return render(request, 'community/certificates/certificate_detail.html', {'certificate': certificate})


def certificate_verify(request):
    cert_id = request.GET.get('id')
    certificate = None
    if cert_id:
        try:
            certificate = Certificate.objects.get(certificate_id=cert_id)
        except Certificate.DoesNotExist:
            messages.error(request, 'Certificate not found.')
    return render(request, 'community/certificates/certificate_verify.html', {'certificate': certificate})


@admin_required
def certificate_create(request):
    if request.method == 'POST':
        form = CertificateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Certificate issued.')
            return redirect('certificate_list')
    else:
        form = CertificateForm()
    return render(request, 'community/certificates/certificate_form.html', {'form': form})


@login_required
def submit_feedback(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    attended = Attendance.objects.filter(event=event, user=request.user, status='present').exists()
    if not attended:
        messages.error(request, 'You must have attended the event to leave feedback.')
        return redirect('event_detail', pk=event.pk)

    if EventFeedback.objects.filter(event=event, user=request.user).exists():
        messages.error(request, 'You have already submitted feedback for this event.')
        return redirect('event_detail', pk=event.pk)

    if request.method == 'POST':
        form = EventFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.event = event
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventFeedbackForm()
    return render(request, 'community/events/feedback_form.html', {'form': form, 'event': event})


@login_required
def my_events(request):
    now = timezone.now()
    all_regs = request.user.event_registrations.select_related('event').all()
    upcoming = all_regs.filter(event__start_date__gte=now).exclude(status='cancelled').order_by('event__start_date')
    past = all_regs.filter(event__start_date__lt=now).order_by('-event__start_date')
    # Also get events where user was marked as attended but never registered
    attended_ids = request.user.attendances.filter(status='present').values_list('event_id', flat=True)
    attended_events = Event.objects.filter(id__in=attended_ids, start_date__lt=now)
    return render(request, 'community/events/my_events.html', {'upcoming': upcoming, 'past': past, 'attended_events': attended_events})


def hackathon_list(request):
    now = timezone.now()
    hackathons = Event.objects.filter(category='hackathon').order_by('-start_date')
    return render(request, 'community/events/hackathon_list.html', {'hackathons': hackathons, 'now': now})


def hackathon_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, category='hackathon')
    teams = event.teams.all()
    is_registered = False
    user_team = None
    if request.user.is_authenticated:
        user_team = HackathonTeamMember.objects.filter(user=request.user, team__event=event).first()
        is_registered = EventRegistration.objects.filter(event=event, user=request.user, status='registered').exists()
    return render(request, 'community/events/hackathon_detail.html', {
        'event': event, 'teams': teams, 'is_registered': is_registered, 'user_team': user_team,
    })


@login_required
def hackathon_register(request, pk):
    event = get_object_or_404(Event, pk=pk, category='hackathon')
    if event.status in ['cancelled', 'completed']:
        messages.error(request, 'Cannot register for this event.')
        return redirect('hackathon_detail', pk=pk)
    reg, created = EventRegistration.objects.get_or_create(event=event, user=request.user, defaults={'status': 'registered'})
    if not created:
        messages.info(request, 'You are already registered.')
    else:
        messages.success(request, 'Registered for hackathon! Create or join a team.')
    return redirect('hackathon_detail', pk=pk)


@organizer_required
def hackathon_create_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.category = 'hackathon'
            event.created_by = request.user
            event.save()
            # Save speakers
            names = request.POST.getlist('speaker_name')
            bios = request.POST.getlist('speaker_bio')
            phones = request.POST.getlist('speaker_phone')
            for i, name in enumerate(names):
                if name.strip():
                    EventSpeaker.objects.create(event=event, name=name.strip(), bio=bios[i].strip() if i < len(bios) else '', phone=phones[i].strip() if i < len(phones) else '')
            # Save agenda
            titles = request.POST.getlist('agenda_title')
            start_times = request.POST.getlist('agenda_start')
            end_times = request.POST.getlist('agenda_end')
            descs = request.POST.getlist('agenda_desc')
            speaker_names = request.POST.getlist('agenda_speaker')
            for i, title in enumerate(titles):
                if title.strip():
                    speaker = None
                    if i < len(speaker_names) and speaker_names[i]:
                        speaker = event.speakers.filter(name=speaker_names[i]).first()
                    EventAgendaItem.objects.create(event=event, title=title.strip(), start_time=start_times[i] if i < len(start_times) else '00:00', end_time=end_times[i] if i < len(end_times) else '00:00', description=descs[i].strip() if i < len(descs) else '', speaker=speaker, order=i)
            messages.success(request, 'Hackathon created successfully!')
            return redirect('hackathon_detail', pk=event.pk)
    else:
        form = EventForm(initial={'category': 'hackathon'})
    return render(request, 'community/events/hackathon_form.html', {'form': form})


@login_required
def hackathon_create_team(request, pk):
    event = get_object_or_404(Event, pk=pk, category='hackathon')
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name:
            messages.error(request, 'Team name is required.')
            return redirect('hackathon_detail', pk=pk)
        team = HackathonTeam.objects.create(event=event, name=name, created_by=request.user)
        HackathonTeamMember.objects.create(team=team, user=request.user, role='leader')
        messages.success(request, f'Team "{name}" created!')
        return redirect('hackathon_detail', pk=pk)
    return redirect('hackathon_detail', pk=pk)


@login_required
def hackathon_join_team(request, team_id):
    team = get_object_or_404(HackathonTeam, pk=team_id)
    if not team.is_open:
        messages.error(request, 'This team is closed for new members.')
        return redirect('hackathon_detail', pk=team.event.pk)
    if HackathonTeamMember.objects.filter(user=request.user, team__event=team.event).exists():
        messages.error(request, 'You are already in a team for this hackathon.')
        return redirect('hackathon_detail', pk=team.event.pk)
    HackathonTeamMember.objects.create(team=team, user=request.user)
    messages.success(request, f'Joined team "{team.name}"!')
    return redirect('hackathon_detail', pk=team.event.pk)


@login_required
def hackathon_submit_project(request, pk):
    event = get_object_or_404(Event, pk=pk, category='hackathon')
    team_member = HackathonTeamMember.objects.filter(user=request.user, team__event=event).first()
    if not team_member:
        messages.error(request, 'You must be in a team to submit.')
        return redirect('hackathon_detail', pk=pk)
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('description')
        github = request.POST.get('github_url', '')
        demo = request.POST.get('live_demo_url', '')
        if not title or not desc:
            messages.error(request, 'Title and description required.')
            return redirect('hackathon_detail', pk=pk)
        HackathonSubmission.objects.create(team=team_member.team, title=title, description=desc, github_url=github, live_demo_url=demo)
        messages.success(request, 'Project submitted!')
        return redirect('hackathon_detail', pk=pk)
    return render(request, 'community/events/hackathon_submit.html', {'event': event})


import jwt as pyjwt
import json
import requests as req_lib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings

CENTRIFUGO_SECRET = os.getenv('CENTRIFUGO_TOKEN_HMAC_SECRET', 'aru-community-secret-key-change-in-production')
CENTRIFUGO_URL = os.getenv('CENTRIFUGO_URL', 'http://localhost:8001')
CENTRIFUGO_WS_URL = os.getenv('CENTRIFUGO_WS_URL', 'ws://localhost:8001/connection/websocket')
CENTRIFUGO_API_KEY = os.getenv('CENTRIFUGO_API_KEY', 'aru-api-key-change-in-production')


def get_centrifugo_token(user, channel):
    claims = {
        'sub': str(user.id),
        'name': user.username,
        'channels': [channel],
        'iat': int(timezone.now().timestamp()),
        'exp': int((timezone.now() + timezone.timedelta(hours=24)).timestamp()),
    }
    return pyjwt.encode(claims, CENTRIFUGO_SECRET, algorithm='HS256')


@login_required
def chat_typing(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    try:
        channel = f'event_{event.id}'
        req_lib.post(f'{CENTRIFUGO_URL}/api/publish', json={
            'channel': channel,
            'data': {'type': 'typing', 'user': request.user.username, 'user_id': request.user.id},
        }, headers={'Authorization': f'apikey {CENTRIFUGO_API_KEY}'}, timeout=2)
    except:
        pass
    return JsonResponse({'ok': True})


@login_required
def chat_search_users(request):
    q = request.GET.get('q', '')
    if len(q) < 1:
        return JsonResponse({'users': []})
    users = User.objects.filter(username__icontains=q)[:10]
    data = []
    for u in users:
        profile = getattr(u, 'profile', None)
        photo = profile.photo.url if profile and profile.photo else None
        data.append({'id': u.id, 'username': u.username, 'photo': photo})
    return JsonResponse({'users': data})


@login_required
def chat_token(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    channel = f'event_{event.id}'
    token = get_centrifugo_token(request.user, channel)
    return JsonResponse({
        'token': token,
        'client': str(request.user.id),
        'channel': channel,
        'ws_url': CENTRIFUGO_WS_URL,
    })


@login_required
def chat_messages(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'GET':
        msgs = EventChatMessage.objects.filter(event=event, is_deleted=False).select_related('user')[:100]
        data = []
        for m in msgs:
            profile = getattr(m.user, 'profile', None)
            photo_url = None
            if profile and profile.photo:
                photo_url = profile.photo.url
            data.append({
                'id': m.id,
                'user': m.user.username,
                'user_id': m.user.id,
                'photo': photo_url,
                'message': m.message,
                'image': m.image.url if m.image else None,
                'file': m.file.url if m.file else None,
                'file_name': m.file.name.split('/')[-1] if m.file else None,
                'voice': m.voice.url if m.voice else None,
                'is_pinned': m.is_pinned,
                'created_at': m.created_at.isoformat(),
                'is_owner': m.user == request.user,
                'reply_to': m.reply_to,
                'reply_user': m.reply_user,
                'reply_snippet': m.reply_snippet,
            })
        return JsonResponse({'messages': data})

    if request.method == 'POST':
        message = request.POST.get('message', '')
        file = request.FILES.get('file')
        image = request.FILES.get('image')
        voice = request.FILES.get('voice')

        if not message and not file and not image and not voice:
            return JsonResponse({'error': 'Empty message'}, status=400)

        reply_to = request.POST.get('reply_to')
        reply_user = request.POST.get('reply_user')
        reply_snippet = request.POST.get('reply_snippet')

        chat_msg = EventChatMessage.objects.create(
            event=event,
            user=request.user,
            message=message,
            file=file,
            image=image,
            voice=voice,
            reply_to=reply_to,
            reply_user=reply_user,
            reply_snippet=reply_snippet,
        )

        profile = getattr(request.user, 'profile', None)
        photo_url = None
        if profile and profile.photo:
            photo_url = profile.photo.url
        msg_data = {
            'id': chat_msg.id,
            'user': request.user.username,
            'user_id': request.user.id,
            'photo': photo_url,
            'message': chat_msg.message,
            'image': chat_msg.image.url if chat_msg.image else None,
            'file': chat_msg.file.url if chat_msg.file else None,
            'file_name': chat_msg.file.name.split('/')[-1] if chat_msg.file else None,
            'voice': chat_msg.voice.url if chat_msg.voice else None,
            'created_at': chat_msg.created_at.isoformat(),
            'is_owner': True,
            'reply_to': reply_to,
            'reply_user': reply_user,
            'reply_snippet': reply_snippet,
        }
        # Publish to Centrifugo for real-time delivery (exclude sender via skip_users)
        try:
            pub_data = {k: v for k, v in msg_data.items() if k != 'is_owner'}
            channel = f'event_{event.id}'
            req_lib.post(f'{CENTRIFUGO_URL}/api/publish', json={
                'channel': channel,
                'data': pub_data,
                'skip_users': [str(request.user.id)],
            }, headers={'Authorization': f'apikey {CENTRIFUGO_API_KEY}'}, timeout=2)
        except:
            pass
        return JsonResponse(msg_data)


@login_required
@csrf_exempt
def chat_delete(request, msg_id):
    if request.method == 'POST':
        msg = get_object_or_404(EventChatMessage, pk=msg_id)
        if msg.user != request.user and not request.user.is_staff:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        msg.is_deleted = True
        msg.save(update_fields=['is_deleted'])
        # Publish delete event in real-time
        try:
            channel = f'event_{msg.event.id}'
            req_lib.post(f'{CENTRIFUGO_URL}/api/publish', json={
                'channel': channel,
                'data': {'type': 'delete', 'id': msg.id},
            }, headers={'Authorization': f'apikey {CENTRIFUGO_API_KEY}'}, timeout=2)
        except:
            pass
        return JsonResponse({'ok': True})
    return JsonResponse({'error': 'POST required'}, status=400)


@admin_required
def admin_inquiries(request):
    inquiries = ContactInquiry.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        inquiries = inquiries.filter(status=status_filter)
    return render(request, 'community/dashboard/admin_inquiries.html', {'inquiries': inquiries, 'status_filter': status_filter})


@admin_required
def admin_inquiry_mark(request, pk):
    inquiry = get_object_or_404(ContactInquiry, pk=pk)
    action = request.GET.get('action', 'read')
    if action == 'read':
        inquiry.status = 'read'
    elif action == 'responded':
        inquiry.status = 'responded'
        inquiry.responded_at = timezone.now()
    inquiry.save()
    return redirect('admin_inquiries')


@admin_required
def admin_settings(request):
    import smtplib
    from django.conf import settings as django_settings
    tab = request.GET.get('tab', 'app')
    test_result = None

    if request.method == 'POST':
        tab = request.POST.get('tab', 'app')
        if request.POST.get('action') == 'test_smtp':
            # Test SMTP
            try:
                host = request.POST.get('smtp_host', '')
                port = int(request.POST.get('smtp_port', 587))
                user = request.POST.get('smtp_user', '')
                pwd = request.POST.get('smtp_pass', '')
                use_tls = request.POST.get('smtp_tls') == 'on'
                to_email = request.POST.get('test_email', '')
                server = smtplib.SMTP(host, port, timeout=10)
                if use_tls:
                    server.starttls()
                if user:
                    server.login(user, pwd)
                if to_email:
                    server.sendmail(user or 'test@aru.com', [to_email], 'Subject: Test Email from Aru Tech Community\n\nThis is a test email. If you receive this, your SMTP settings are working!')
                server.quit()
                test_result = 'SMTP test successful! Email sent to ' + to_email
            except Exception as e:
                test_result = f'SMTP test failed: {str(e)}'
        else:
            # Save settings
            for key in request.POST:
                if key.startswith('setting_'):
                    setting_key = key[8:]
                    set_setting(setting_key, request.POST[key])
            messages.success(request, 'Settings saved successfully.')
        return redirect(f'/admin-settings/?tab={tab}')

    app_settings = {
        'site_name': get_setting('site_name', 'Aru Tech Community'),
        'site_description': get_setting('site_description', 'Community platform for developers'),
        'contact_email': get_setting('contact_email', 'admin@aru.com'),
        'max_members': get_setting('max_members', '1000'),
    }
    payment_settings = {
        'currency': get_setting('currency', 'TZS'),
        'payment_gateway': get_setting('payment_gateway', ''),
        'api_key': get_setting('payment_api_key', ''),
        'api_secret': get_setting('payment_api_secret', ''),
    }
    sms_settings = {
        'sms_provider': get_setting('sms_provider', ''),
        'sms_api_key': get_setting('sms_api_key', ''),
        'sms_sender_id': get_setting('sms_sender_id', 'ARU'),
    }
    smtp_settings = {
        'smtp_host': get_setting('smtp_host', ''),
        'smtp_port': get_setting('smtp_port', '587'),
        'smtp_user': get_setting('smtp_user', ''),
        'smtp_pass': get_setting('smtp_pass', ''),
        'smtp_tls': get_setting('smtp_tls', 'True'),
    }

    return render(request, 'community/dashboard/admin_settings.html', {
        'tab': tab,
        'app_settings': app_settings,
        'payment_settings': payment_settings,
        'sms_settings': sms_settings,
        'smtp_settings': smtp_settings,
        'test_result': test_result,
    })
