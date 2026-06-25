from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from community.models import User, Profile, Event, EventSpeaker, EventAgendaItem, EventMaterial, Announcement, Resource, Project, Badge
import random


class Command(BaseCommand):
    help = 'Seed demo data'

    def handle(self, *args, **kwargs):
        admin, _ = User.objects.get_or_create(username='nasrtechindustry', defaults={
            'email': 'nasrkihagila@gmail.com', 'is_superuser': True, 'is_staff': True
        })

        demo_users = [
            ('john', 'john@demo.com', 'member', 'John', 'Beginner'),
            ('jane', 'jane@demo.com', 'member', 'Jane', 'Intermediate'),
            ('bob', 'bob@demo.com', 'organizer', 'Bob', 'Advanced'),
            ('alice', 'alice@demo.com', 'mentor', 'Alice', 'Advanced'),
            ('mod', 'mod@demo.com', 'moderator', 'Mod', 'Intermediate'),
        ]
        for username, email, role, name, skill in demo_users:
            user, created = User.objects.get_or_create(username=username, defaults={
                'email': email, 'phone_number': '1234567890'
            })
            if created:
                user.set_password('demo123')
                user.save()
            Profile.objects.update_or_create(user=user, defaults={
                'role': role, 'bio': f'Hi, I am {name}', 'skill_level': skill,
                'university': 'Ardhi University', 'course': 'Computer Science',
                'department': 'CSM',
            })
            if created:
                self.stdout.write(f'Created user: {username}')

        now = timezone.now()
        events = [
            {
                'title': 'Python for Beginners Workshop',
                'category': 'workshop',
                'start': now + timedelta(days=7),
                'end': now + timedelta(days=7, hours=4),
                'cap': 40,
                'location': 'CSM Lab 3, Ardhi University',
                'desc': 'A hands-on workshop introducing Python programming. Learn variables, data types, control flow, functions, and build your first Python project. No prior experience needed. Bring your laptop!',
                'speakers': [('Glory Msasalaga', 'Chapter Lead & Python Developer'), ('Innocent Kiwoly', 'Executive Lead & Mentor')],
                'agenda': [
                    ('Introduction & Setup', '09:00', '09:30'),
                    ('Python Basics', '09:30', '11:00'),
                    ('Hands-on Project', '11:30', '13:00'),
                ],
            },
            {
                'title': 'Web Development Hackathon',
                'category': 'hackathon',
                'start': now + timedelta(days=21),
                'end': now + timedelta(days=23),
                'cap': 60,
                'location': 'Innovation Hub, Ardhi University',
                'desc': 'A 48-hour hackathon where teams build web applications solving real community challenges. Use Django, React, or any stack you prefer. Mentors will be available throughout. Prizes for top 3 teams!',
                'speakers': [('Goodluck Moshi', 'Project Manager & Full Stack Dev'), ('Rajabu Rajabu', 'Software Developer')],
                'agenda': [
                    ('Opening & Team Formation', '09:00', '10:30'),
                    ('Hacking Begins', '10:30', '18:00'),
                    ('Final Presentations', '15:00', '18:00'),
                ],
            },
            {
                'title': 'AI & Machine Learning Meetup',
                'category': 'meetup',
                'start': now + timedelta(days=14),
                'end': now + timedelta(days=14, hours=3),
                'cap': 0,
                'location': 'Conference Hall, Ardhi University',
                'desc': 'An evening meetup exploring AI and ML trends. Featuring talks from industry professionals on computer vision, NLP, and building ML pipelines. Networking session with refreshments.',
                'speakers': [('Godfrey Enoshi', 'AI/ML Engineer at Sartfy')],
                'agenda': [
                    ('Welcome & Introductions', '16:00', '16:15'),
                    ('Computer Vision Talk', '16:15', '17:00'),
                    ('NLP in Production', '17:00', '17:45'),
                    ('Networking', '17:45', '19:00'),
                ],
            },
            {
                'title': 'Django Girls Bootcamp',
                'category': 'bootcamp',
                'start': now + timedelta(days=45),
                'end': now + timedelta(days=47),
                'cap': 30,
                'location': 'CSM Computer Lab, Ardhi University',
                'desc': 'A free 3-day bootcamp for women who want to learn web development with Django. Build a blog application from scratch. Breakfast and lunch provided. All skill levels welcome!',
                'speakers': [('Agath Mkeng\'e', 'Project Manager at IPF Technology')],
                'agenda': [
                    ('Day 1: HTML/CSS Basics', '09:00', '16:00'),
                    ('Day 2: Django Intro', '09:00', '16:00'),
                    ('Day 3: Build & Deploy', '09:00', '16:00'),
                ],
            },
            {
                'title': 'Cyber Security Webinar',
                'category': 'webinar',
                'start': now + timedelta(days=10),
                'end': now + timedelta(days=10, hours=2),
                'cap': 0,
                'location': 'Online (Zoom)',
                'desc': 'An online webinar covering essential cyber security concepts. Topics include ethical hacking, penetration testing, network security, and how to start a career in cyber security. Certificate of attendance provided.',
                'speakers': [('Innocent Kiwoly', 'Security Researcher')],
                'agenda': [
                    ('Introduction to Cyber Security', '14:00', '14:30'),
                    ('Live Demo: Pen Testing', '14:30', '15:15'),
                    ('Career Path Discussion', '15:15', '16:00'),
                ],
            },
        ]

        for data in events:
            event, created = Event.objects.get_or_create(title=data['title'], defaults={
                'category': data['category'],
                'status': 'published',
                'description': data['desc'],
                'location': data['location'],
                'start_date': data['start'],
                'end_date': data['end'],
                'capacity': data['cap'],
                'created_by': admin,
            })
            if created:
                for name, bio in data['speakers']:
                    EventSpeaker.objects.get_or_create(event=event, name=name, defaults={'bio': bio})
                for title, start, end in data['agenda']:
                    EventAgendaItem.objects.get_or_create(
                        event=event, title=title,
                        defaults={'start_time': start, 'end_time': end}
                    )
                self.stdout.write(f'Created event: {data["title"]}')

        announcements = [
            ('Welcome to Aru Tech Community!', 'We are excited to have you join our community. Stay tuned for upcoming events and workshops.'),
            ('Python Workshop Registration Open', 'Our Python for Beginners workshop is now open for registration. Limited spots available!'),
            ('Community Meetup This Friday', 'Dont miss our monthly community meetup. Great networking opportunities!'),
        ]
        for title, content in announcements:
            Announcement.objects.get_or_create(title=title, defaults={
                'content': content, 'is_published': True, 'is_pinned': title.startswith('Welcome'),
                'created_by': admin,
            })

        resources = [
            ('Python for Beginners', 'python', 'https://docs.python.org/3/tutorial/'),
            ('Django Official Docs', 'django', 'https://docs.djangoproject.com/'),
            ('JavaScript Guide', 'javascript', 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide'),
        ]
        for title, category, url in resources:
            Resource.objects.get_or_create(title=title, defaults={
                'category': category, 'url': url, 'is_published': True,
                'is_featured': title == 'Python for Beginners',
                'created_by': admin,
            })

        john = User.objects.get(username='john')
        Project.objects.get_or_create(title='Personal Portfolio', defaults={
            'description': 'A Django portfolio website with blog, project showcase, and contact form.',
            'tech_stack': 'Django, Bootstrap, PostgreSQL',
            'github_url': 'https://github.com/john/portfolio', 'owner': john,
            'status': 'approved', 'is_featured': True,
        })

        badge_names = ['New Member', 'Event Attendee', 'Workshop Graduate', 'Hackathon Participant', 'Project Contributor']
        for name in badge_names:
            Badge.objects.get_or_create(name=name)

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully'))
