from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model, authenticate, login as auth_login
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Event

User = get_user_model()

# Create your views here.
def about(request):
    return render(request, 'commune/about.html', {'title': 'About'})

def events(request):
    events_list = Event.objects.all()  # Fetch all events from the database
    return render(request, 'commune/events.html', {'title': 'Event', 'events': events_list})

def code_of_conduct(request):
    return render(request, 'commune/code-of-conduct.html', {'title': 'Code of Conduct'})

def register(request):
    return render(request, 'commune/register.html', {'title': 'Register'})

def index(request):
    return render(request, 'commune/index.html', {'title': 'Home'})

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('index')  # Redirect to home page after login
        else:
            return render(request, 'commune/login.html', {'error': 'Invalid username or password'})

    return render(request, 'commune/login.html')

def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'commune/register.html', {'error': 'Username already exists'})

        # Create new user
        user = User(
            username=username,
            email=email,
            phone_number=phone_number,
            password=make_password(password)
        )
        user.save()

        return redirect('login')  # Redirect to login page after registration

    return render(request, 'commune/register.html')

#update user
def update_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')

        # Check if password is provided and hash it
        password = request.POST.get('password')
        if password:
            user.password = make_password(password)

        user.save()
        return redirect('profile', user_id=user.id)  # Redirect to user's profile page

    return render(request, 'commune/update_user.html', {'user': user})

#reset password
def rest_password(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        password = request.POST.get('password')
        user.password = make_password(password)
        user.save()
        return redirect('login')  # Redirect to login page after password reset

    return render(request, 'commune/reset_password.html', {'user': user})

#delete user
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('index')  # Redirect to home page after deletion

#CRUD for events
def create_event(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        event_date = request.POST.get('event_date')

        # Create new event
        event = Event(
            title=title,
            description=description,
            event_date=event_date
        )
        event.save()

        return redirect('events')  # Redirect to events page after creation

    return render(request, 'commune/create_event.html')

def update_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.description = request.POST.get('description')
        event.event_date = request.POST.get('event_date')

        event.save()
        return redirect('events')  # Redirect to events page after update

    return render(request, 'commune/update_event.html', {'event': event})

def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return redirect('events')  # Redirect to events page after deletion

###  return render(request, 'commune/event_detail.html', {'event': event})
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        # Process the registration form (e.g., save user info to the database)
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        # You can save this information to a registration model or send an email
        # For now, just redirect to a success page
        return redirect('events')  # Redirect to the events page
    return render(request, 'register.html', {'event': event})