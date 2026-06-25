from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


class Profile(models.Model):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('organizer', 'Organizer'),
        ('mentor', 'Mentor'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
    ]
    SKILL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    university = models.CharField(max_length=200, blank=True)
    course = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=200, blank=True)
    skill_level = models.CharField(max_length=20, choices=SKILL_CHOICES, blank=True)
    interests = models.TextField(blank=True, help_text="Comma separated")
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    def completion_percentage(self):
        fields = [self.bio, self.phone, self.university, self.course,
                  self.department, self.skill_level, self.interests,
                  self.github_url, self.linkedin_url, self.portfolio_url, self.photo]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)


class Event(models.Model):
    CATEGORY_CHOICES = [
        ('meetup', 'Meetup'),
        ('workshop', 'Workshop'),
        ('hackathon', 'Hackathon'),
        ('bootcamp', 'Bootcamp'),
        ('webinar', 'Webinar'),
        ('training', 'Training'),
        ('competition', 'Competition'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='meetup')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    location = models.CharField(max_length=300, blank=True, default='')
    venue_details = models.TextField(blank=True, help_text="Building, room number, directions, etc.")
    has_food = models.BooleanField(default=False, help_text="Food provided")
    food_details = models.CharField(max_length=300, blank=True, help_text="e.g. Breakfast & Lunch, Snacks, etc.")
    has_payment = models.BooleanField(default=False, help_text="Payment required")
    payment_details = models.CharField(max_length=300, blank=True, help_text="e.g. 50,000 TZS, Free for members")
    components = models.TextField(blank=True, help_text="What's included - certificates, materials, etc. One per line")
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    capacity = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    def registration_count(self):
        return self.registrations.exclude(status='cancelled').count()

    def is_full(self):
        if self.capacity == 0:
            return False
        return self.registration_count() >= self.capacity

    def attendance_count(self):
        return self.attendances.filter(status='present').count()

    @property
    def status_label(self):
        now = timezone.now()
        if self.status == 'published' and self.start_date > now:
            return 'upcoming'
        if self.start_date <= now <= self.end_date:
            return 'ongoing'
        if self.end_date < now:
            return 'completed'
        return self.status


class EventSpeaker(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='speakers')
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True, help_text="Phone number for call/text")
    photo = models.ImageField(upload_to='speakers/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.event.title}"


class EventAgendaItem(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='agenda_items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    speaker = models.ForeignKey(EventSpeaker, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    resource_file = models.FileField(upload_to='agenda_resources/', blank=True, null=True, help_text="PDF, Excel, Jupyter notebook, etc.")
    resource_url = models.URLField(blank=True, help_text="Link to codebase, slides, or external resource")

    class Meta:
        ordering = ['order', 'start_time']

    def __str__(self):
        return f"{self.title} - {self.event.title}"


class EventMaterial(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='materials/', blank=True, null=True)
    url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('cancelled', 'Cancelled'),
        ('attended', 'Attended'),
        ('missed', 'Missed'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"


class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendances')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=20, choices=[('present', 'Present'), ('absent', 'Absent')], default='present')
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendances')
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.event.title}: {self.status}"


class ContactInquiry(models.Model):
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('responded', 'Responded'),
    ]
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unread')
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.name}"


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title


class Resource(models.Model):
    CATEGORY_CHOICES = [
        ('python', 'Python'),
        ('django', 'Django'),
        ('javascript', 'JavaScript'),
        ('ui_ux', 'UI/UX'),
        ('cybersecurity', 'Cybersecurity'),
        ('ai', 'AI'),
        ('data_science', 'Data Science'),
        ('career', 'Career'),
        ('git', 'Git/GitHub'),
        ('other', 'Other'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    url = models.URLField(blank=True)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title

    def is_youtube(self):
        return 'youtube.com/watch?v=' in self.url or 'youtu.be/' in self.url

    def icon_data(self):
        title_lower = self.title.lower()
        url_lower = self.url.lower()
        combined = title_lower + ' ' + url_lower

        if 'youtube.com/watch?v=' in self.url or 'youtu.be/' in self.url:
            return {'bg': '#fee2e2', 'color': '#dc2626', 'icon': 'bi bi-play-circle-fill', 'devicon': ''}
        if 'github' in combined:
            return {'bg': '#e5e7eb', 'color': '#111827', 'icon': 'bi bi-github', 'devicon': 'devicon-github-original'}
        if 'docs.djangoproject' in url_lower or 'django' in combined:
            return {'bg': '#dbeafe', 'color': '#092e20', 'icon': '', 'devicon': 'devicon-django-plain'}
        if 'python' in combined:
            return {'bg': '#fff7ed', 'color': '#3776ab', 'icon': '', 'devicon': 'devicon-python-plain'}
        if 'react' in combined:
            return {'bg': '#e0f2fe', 'color': '#61dafb', 'icon': '', 'devicon': 'devicon-react-original'}
        if 'vue' in combined or 'vuejs' in combined:
            return {'bg': '#dcfce7', 'color': '#4fc08d', 'icon': '', 'devicon': 'devicon-vuejs-plain'}
        if 'node' in combined or 'nodejs' in combined:
            return {'bg': '#dcfce7', 'color': '#339933', 'icon': '', 'devicon': 'devicon-nodejs-plain'}
        if 'docker' in combined:
            return {'bg': '#e0f2fe', 'color': '#2496ed', 'icon': '', 'devicon': 'devicon-docker-plain'}
        if 'kubernetes' in combined or 'k8s' in combined:
            return {'bg': '#e0f2fe', 'color': '#326ce5', 'icon': '', 'devicon': 'devicon-kubernetes-plain'}
        if 'go' in combined.split() or 'golang' in combined:
            return {'bg': '#e0f2fe', 'color': '#00add8', 'icon': '', 'devicon': 'devicon-go-original-wordmark'}
        if 'rust' in combined:
            return {'bg': '#fef2f2', 'color': '#000000', 'icon': '', 'devicon': 'devicon-rust-plain'}
        if 'typescript' in combined or 'ts' in combined.split():
            return {'bg': '#e0f2fe', 'color': '#3178c6', 'icon': '', 'devicon': 'devicon-typescript-plain'}
        if 'figma' in combined or 'design' in combined:
            return {'bg': '#fdf2f8', 'color': '#f24e1e', 'icon': '', 'devicon': 'devicon-figma-plain'}
        if 'sql' in combined or 'database' in combined:
            return {'bg': '#fef2f2', 'color': '#336791', 'icon': '', 'devicon': 'devicon-mysql-plain'}
        if 'aws' in combined or 'cloud' in combined:
            return {'bg': '#fefce8', 'color': '#ff9900', 'icon': '', 'devicon': 'devicon-amazonwebservices-original'}
        if 'javascript' in combined or 'js' in combined.split():
            return {'bg': '#fefce8', 'color': '#f7df1e', 'icon': '', 'devicon': 'devicon-javascript-plain'}
        if 'html' in combined:
            return {'bg': '#fef2f2', 'color': '#e34f26', 'icon': '', 'devicon': 'devicon-html5-plain'}
        if 'css' in combined:
            return {'bg': '#e0f2fe', 'color': '#1572b6', 'icon': '', 'devicon': 'devicon-css3-plain'}
        if 'tailwind' in combined:
            return {'bg': '#e0f2fe', 'color': '#06b6d4', 'icon': '', 'devicon': 'devicon-tailwindcss-plain'}
        if 'bootstrap' in combined:
            return {'bg': '#f3e8ff', 'color': '#7952b3', 'icon': '', 'devicon': 'devicon-bootstrap-plain'}
        if 'mongodb' in combined or 'mongo' in combined:
            return {'bg': '#dcfce7', 'color': '#47a248', 'icon': '', 'devicon': 'devicon-mongodb-plain'}
        if 'redis' in combined:
            return {'bg': '#fef2f2', 'color': '#dc382d', 'icon': '', 'devicon': 'devicon-redis-plain'}
        if 'linux' in combined or 'ubuntu' in combined:
            return {'bg': '#fefce8', 'color': '#fcc624', 'icon': '', 'devicon': 'devicon-linux-plain'}
        if 'nginx' in combined:
            return {'bg': '#dcfce7', 'color': '#009639', 'icon': '', 'devicon': 'devicon-nginx-original'}
        if 'postgresql' in combined or 'postgres' in combined or 'psql' in combined:
            return {'bg': '#e0f2fe', 'color': '#336791', 'icon': '', 'devicon': 'devicon-postgresql-plain'}
        if 'redis' in combined:
            return {'bg': '#fef2f2', 'color': '#dc382d', 'icon': '', 'devicon': 'devicon-redis-plain'}
        if self.file:
            return {'bg': '#f3f4f6', 'color': '#6b7280', 'icon': 'bi bi-file-earmark', 'devicon': ''}
        if self.url:
            return {'bg': '#f3f4f6', 'color': '#6b7280', 'icon': 'bi bi-link-45deg', 'devicon': ''}
        return {'bg': '#f3f4f6', 'color': '#6b7280', 'icon': 'bi bi-file-earmark', 'devicon': ''}

    def youtube_embed_url(self):
        if 'youtube.com/watch?v=' in self.url:
            vid = self.url.split('v=')[1].split('&')[0]
            return f'https://www.youtube.com/embed/{vid}?rel=0'
        if 'youtu.be/' in self.url:
            vid = self.url.split('youtu.be/')[1].split('?')[0]
            return f'https://www.youtube.com/embed/{vid}?rel=0'
        return ''

    def youtube_video_id(self):
        if 'youtube.com/watch?v=' in self.url:
            return self.url.split('v=')[1].split('&')[0]
        if 'youtu.be/' in self.url:
            return self.url.split('youtu.be/')[1].split('?')[0]
        return ''

    def youtube_thumbnail(self):
        vid = self.youtube_video_id()
        if vid:
            return f'https://img.youtube.com/vi/{vid}/mqdefault.jpg'
        return ''


class ResourceView(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['resource', 'user']

    def __str__(self):
        return f"{self.resource.title} viewed by {self.user or 'anonymous'}"


class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    tech_stack = models.CharField(max_length=500, blank=True)
    github_url = models.URLField(blank=True)
    live_demo_url = models.URLField(blank=True)
    screenshot = models.ImageField(upload_to='projects/', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    contributors = models.TextField(blank=True, help_text="Comma separated usernames")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title


class Certificate(models.Model):
    certificate_id = models.CharField(max_length=20, unique=True, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='certificates')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    issued_at = models.DateTimeField(auto_now_add=True)
    is_revoked = models.BooleanField(default=False)

    class Meta:
        unique_together = ['event', 'user']

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.certificate_id} - {self.user.username}"


class EventFeedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.event.title}: {self.rating}/5"


class EventChatMessage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField(blank=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    voice = models.FileField(upload_to='chat_voice/', blank=True, null=True)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    reply_to = models.CharField(max_length=20, blank=True, null=True, help_text="ID of message being replied to")
    reply_user = models.CharField(max_length=100, blank=True, null=True, help_text="Username of replied message author")
    reply_snippet = models.CharField(max_length=200, blank=True, null=True, help_text="Snippet of replied message")

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.message[:30]}"


class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='badges/', blank=True, null=True)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'badge']

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class AppSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key


def get_setting(key, default=''):
    try:
        return AppSetting.objects.get(key=key).value
    except AppSetting.DoesNotExist:
        return default


def set_setting(key, value):
    setting, _ = AppSetting.objects.get_or_create(key=key)
    setting.value = value
    setting.save()


class HackathonTeam(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='teams', limit_choices_to={'category': 'hackathon'})
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_teams')
    created_at = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True, help_text="Open for new members to join")

    class Meta:
        unique_together = ['event', 'name']

    def __str__(self):
        return f"{self.name} - {self.event.title}"

    def member_count(self):
        return self.members.count()


class HackathonTeamMember(models.Model):
    team = models.ForeignKey(HackathonTeam, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hackathon_memberships')
    role = models.CharField(max_length=20, choices=[('leader', 'Leader'), ('member', 'Member')], default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['team', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.team.name}"


class HackathonSubmission(models.Model):
    team = models.ForeignKey(HackathonTeam, on_delete=models.CASCADE, related_name='submissions')
    title = models.CharField(max_length=200)
    description = models.TextField()
    github_url = models.URLField(blank=True)
    live_demo_url = models.URLField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.PositiveIntegerField(blank=True, null=True)
    is_winner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.team.name}"
