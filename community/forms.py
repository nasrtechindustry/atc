from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import (
    User, Profile, Event, EventSpeaker, EventAgendaItem, EventMaterial,
    ContactInquiry, Announcement, Resource, Project, Certificate, EventFeedback
)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match")
        return cleaned


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio', 'phone', 'university', 'course', 'department',
                   'skill_level', 'interests', 'github_url', 'linkedin_url', 'portfolio_url']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'interests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'university': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'skill_level': forms.Select(attrs={'class': 'form-select'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control'}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'status', 'location',
                   'venue_details', 'has_food', 'food_details', 'has_payment',
                   'payment_details', 'components',
                   'start_date', 'end_date', 'capacity', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'venue_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Building, room, directions...'}),
            'has_food': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'food_details': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Breakfast & Lunch'}),
            'has_payment': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'payment_details': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 50,000 TZS'}),
            'components': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'One per line - certificates, materials, etc.'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ContactInquiryForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'image', 'is_published', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'category', 'file', 'url', 'is_published', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'tech_stack', 'github_url',
                   'live_demo_url', 'screenshot', 'contributors']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'tech_stack': forms.TextInput(attrs={'class': 'form-control'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control'}),
            'live_demo_url': forms.URLInput(attrs={'class': 'form-control'}),
            'screenshot': forms.FileInput(attrs={'class': 'form-control'}),
            'contributors': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['event', 'user']


class EventFeedbackForm(forms.ModelForm):
    class Meta:
        model = EventFeedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class EventSpeakerForm(forms.ModelForm):
    class Meta:
        model = EventSpeaker
        fields = ['name', 'bio', 'phone', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+255 xxx xxx xxx'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class EventAgendaItemForm(forms.ModelForm):
    class Meta:
        model = EventAgendaItem
        fields = ['title', 'description', 'start_time', 'end_time', 'speaker', 'order', 'resource_file', 'resource_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'speaker': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'resource_file': forms.FileInput(attrs={'class': 'form-control'}),
            'resource_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/...'}),
        }


class EventMaterialForm(forms.ModelForm):
    class Meta:
        model = EventMaterial
        fields = ['title', 'file', 'url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
        }
