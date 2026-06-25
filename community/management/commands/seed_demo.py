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
            ('Python for Beginners', 'python', 'Official Python tutorial covering basics to advanced topics.', 'https://docs.python.org/3/tutorial/'),
            ('Django Official Docs', 'django', 'Comprehensive Django framework documentation and guides.', 'https://docs.djangoproject.com/'),
            ('JavaScript Guide', 'javascript', 'In-depth JavaScript guide from MDN Web Docs.', 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide'),
            ('Figma UI/UX Design Course', 'ui_ux', 'Learn UI/UX design principles with Figma.', 'https://www.figma.com/resources/learn-design/'),
            ('Cybersecurity Basics', 'cybersecurity', 'Introduction to cybersecurity concepts and practices.', 'https://www.coursera.org/learn/introduction-to-cyber-security'),
            ('Machine Learning Crash Course', 'ai', "Google's fast-paced intro to ML with TensorFlow APIs.", 'https://developers.google.com/machine-learning/crash-course'),
            ('Data Science Handbook', 'data_science', 'Practical guide to data analysis, visualization, and ML.', 'https://jakevdp.github.io/PythonDataScienceHandbook/'),
            ('Tech Career Roadmap', 'career', 'Guide to building a career in tech from scratch.', 'https://roadmap.sh/'),
            ('Git & GitHub Handbook', 'git', 'Essential Git commands and GitHub workflows.', 'https://guides.github.com/introduction/git-handbook/'),
            ('React Frontend Guide', 'javascript', 'Learn React.js for building modern user interfaces.', 'https://react.dev/learn'),
            ('PostgreSQL Tutorial', 'other', 'Learn PostgreSQL database management and queries.', 'https://www.postgresqltutorial.com/'),
            ('Django REST Framework', 'django', 'Build REST APIs with Django REST Framework.', 'https://www.django-rest-framework.org/'),
            ('Python Data Structures & Algorithms', 'python', 'Master Python data structures, linked lists, trees, graphs.', 'https://realpython.com/python-data-structures/'),
            ('Python OOP Guide', 'python', 'Deep dive into Object-Oriented Programming in Python.', 'https://realpython.com/python3-object-oriented-programming/'),
            ('Python Flask Web Framework', 'python', 'Build web apps with Flask microframework.', 'https://flask.palletsprojects.com/'),
            ('Python FastAPI Guide', 'python', 'Modern fast web framework for building APIs.', 'https://fastapi.tiangolo.com/learn/'),
            ('Python Web Scraping', 'python', 'Scrape websites using BeautifulSoup and Scrapy.', 'https://docs.scrapy.org/en/latest/intro/tutorial.html'),
            ('Python Testing with Pytest', 'python', 'Write clean tests with pytest framework.', 'https://docs.pytest.org/en/stable/'),
            ('Python Async Programming', 'python', 'Learn asyncio and async/await in Python.', 'https://realpython.com/async-io-python/'),
            ('Advanced Django Topics', 'django', 'Django advanced querying, signals, cache, and more.', 'https://docs.djangoproject.com/en/stable/topics/'),
            ('Django Class-Based Views', 'django', 'Complete guide to Django class-based views.', 'https://ccbv.co.uk/'),
            ('Django Channels & WebSockets', 'django', 'Real-time Django with Channels and WebSockets.', 'https://channels.readthedocs.io/'),
            ('Django Testing Guide', 'django', 'How to test Django applications effectively.', 'https://docs.djangoproject.com/en/stable/topics/testing/'),
            ('Django Deployment Guide', 'django', 'Deploy Django to production with Docker and more.', 'https://docs.djangoproject.com/en/stable/howto/deployment/'),
            ('Django ORM Mastery', 'django', 'Master the Django ORM and database queries.', 'https://djangocentral.com/django-orm/'),
            ('Django Security Best Practices', 'django', 'Secure your Django applications.', 'https://docs.djangoproject.com/en/stable/topics/security/'),
            ('JavaScript ES6+ Features', 'javascript', 'Modern JavaScript features, arrow functions, destructuring.', 'https://www.javascripttutorial.net/es6/'),
            ('TypeScript Handbook', 'javascript', 'TypeScript language fundamentals and advanced types.', 'https://www.typescriptlang.org/docs/'),
            ('Node.js Backend Guide', 'javascript', 'Build server-side apps with Node.js and Express.', 'https://nodejs.org/en/docs/guides/'),
            ('Vue.js Framework Guide', 'javascript', 'Learn Vue.js for building interactive web interfaces.', 'https://vuejs.org/guide/introduction.html'),
            ('Angular Developer Guide', 'javascript', 'Comprehensive Angular framework documentation.', 'https://angular.io/docs'),
            ('Next.js Full Stack Guide', 'javascript', 'React framework for production with SSR and SSG.', 'https://nextjs.org/docs'),
            ('Svelte Frontend Guide', 'javascript', 'Svelte compiler-driven UI framework.', 'https://svelte.dev/docs'),
            ('jQuery Basics', 'javascript', 'jQuery DOM manipulation and event handling.', 'https://api.jquery.com/'),
            ('Web Accessibility Guide', 'ui_ux', 'Make websites accessible to all users (WCAG).', 'https://developer.mozilla.org/en-US/docs/Web/Accessibility'),
            ('UX Research Methods', 'ui_ux', 'User research techniques for better product design.', 'https://www.nngroup.com/articles/which-ux-research-methods/'),
            ('Adobe XD UI Design', 'ui_ux', 'Design prototypes and wireframes with Adobe XD.', 'https://helpx.adobe.com/xd/tutorials.html'),
            ('Material Design Guidelines', 'ui_ux', "Google's Material Design system and components.", 'https://m3.material.io/'),
            ('Color Theory for Designers', 'ui_ux', 'Understand color psychology and palettes.', 'https://www.canva.com/learn/color-theory-design/'),
            ('Typography for Web', 'ui_ux', 'Font pairing, hierarchy, and readability on the web.', 'https://typographyhandbook.com/'),
            ('Responsive Web Design', 'ui_ux', 'Build websites that work on any screen size.', 'https://web.dev/responsive-web-design-basics/'),
            ('Sketch App for UI Design', 'ui_ux', 'Design interfaces and prototypes with Sketch.', 'https://www.sketch.com/docs/'),
            ('Ethical Hacking Course', 'cybersecurity', 'Learn penetration testing and ethical hacking.', 'https://www.udemy.com/course/penetration-testing/'),
            ('Network Security Fundamentals', 'cybersecurity', 'Understand firewalls, VPNs, and network protection.', 'https://www.cisco.com/c/en/us/training-events/training-certifications/certifications/associate/ccna.html'),
            ('Web Security OWASP Top 10', 'cybersecurity', 'Most critical web application security risks.', 'https://owasp.org/www-project-top-ten/'),
            ('Cryptography Basics', 'cybersecurity', 'Encryption, hashing, and digital signatures explained.', 'https://www.coursera.org/learn/crypto'),
            ('Bug Bounty Guide', 'cybersecurity', 'How to start bug bounty hunting on HackerOne.', 'https://www.hackerone.com/vulnerability-management/bug-bounty-hunting-guide'),
            ('SOC Analyst Training', 'cybersecurity', 'Security operations center analyst fundamentals.', 'https://www.cybrary.it/course/security-operations-center/'),
            ('Digital Forensics Guide', 'cybersecurity', 'Investigate cyber crimes with forensics tools.', 'https://www.nist.gov/cyberframework'),
            ('Deep Learning Specialization', 'ai', 'Andrew Ng deep learning course on Coursera.', 'https://www.coursera.org/specializations/deep-learning'),
            ('TensorFlow Official Guide', 'ai', 'Build and deploy ML models with TensorFlow.', 'https://www.tensorflow.org/learn'),
            ('PyTorch Deep Learning', 'ai', 'PyTorch tutorials for neural networks and DL.', 'https://pytorch.org/tutorials/'),
            ('Natural Language Processing', 'ai', 'NLP with spaCy, NLTK, and transformers.', 'https://spacy.io/usage/spacy-101'),
            ('Computer Vision with OpenCV', 'ai', 'Image processing and CV using OpenCV Python.', 'https://docs.opencv.org/master/d9/df8/tutorial_root.html'),
            ('Reinforcement Learning Guide', 'ai', 'RL algorithms, Q-learning, and policy gradients.', 'https://spinningup.openai.com/en/latest/'),
            ('AI Ethics & Responsible AI', 'ai', 'Fairness, accountability, and transparency in AI.', 'https://www.elementsofai.com/'),
            ('LangChain LLM Framework', 'ai', 'Build LLM applications with LangChain.', 'https://python.langchain.com/docs/get_started/introduction'),
            ('Data Analysis with Pandas', 'data_science', 'Data manipulation and analysis using Pandas.', 'https://pandas.pydata.org/docs/'),
            ('Data Visualization with Matplotlib', 'data_science', 'Create charts and plots with Matplotlib.', 'https://matplotlib.org/stable/tutorials/index.html'),
            ('Data Visualization with Seaborn', 'data_science', 'Statistical data visualization with Seaborn.', 'https://seaborn.pydata.org/tutorial.html'),
            ('SQL for Data Science', 'data_science', 'SQL queries for data extraction and analysis.', 'https://www.sqlitetutorial.net/'),
            ('Statistics for Data Science', 'data_science', 'Statistical methods, hypothesis testing, probability.', 'https://www.khanacademy.org/math/statistics-probability'),
            ('Feature Engineering Guide', 'data_science', 'Transform raw data into ML-ready features.', 'https://www.feature-engine.com/'),
            ('Big Data with Apache Spark', 'data_science', 'Distributed computing and big data with Spark.', 'https://spark.apache.org/docs/latest/'),
            ('Tableau Data Visualization', 'data_science', 'Business intelligence dashboards with Tableau.', 'https://www.tableau.com/learn/training'),
            ('Resume Writing for Tech', 'career', 'Craft a standout tech resume that gets interviews.', 'https://www.freecodecamp.org/news/how-to-write-a-resume-for-software-engineer-jobs/'),
            ('Technical Interview Prep', 'career', 'Ace coding interviews with LeetCode and system design.', 'https://leetcode.com/explore/'),
            ('LinkedIn Profile Optimization', 'career', 'Optimize your LinkedIn for tech job opportunities.', 'https://www.linkedin.com/learning/topics/career-development'),
            ('Open Source Contribution Guide', 'career', 'Start contributing to open source projects.', 'https://opensource.guide/how-to-contribute/'),
            ('Freelancing in Tech', 'career', 'Start and grow your tech freelancing career.', 'https://www.upwork.com/resources/freelancing-tips'),
            ('Building a Tech Portfolio', 'career', 'Create a portfolio that showcases your skills.', 'https://www.freecodecamp.org/news/how-to-build-a-portfolio-as-a-developer/'),
            ('Networking for Developers', 'career', 'Build professional connections in tech.', 'https://www.meetup.com/'),
            ('Git Advanced Techniques', 'git', 'Rebasing, cherry-picking, bisecting, and submodules.', 'https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging'),
            ('GitHub Actions CI/CD', 'git', 'Automate workflows with GitHub Actions.', 'https://docs.github.com/en/actions/learn-github-actions'),
            ('Git Branching Strategies', 'git', 'Git flow, trunk-based development, and more.', 'https://www.atlassian.com/git/tutorials/comparing-workflows'),
            ('Docker Container Guide', 'other', 'Containerize applications with Docker.', 'https://docs.docker.com/get-started/'),
            ('Kubernetes Orchestration', 'other', 'Deploy and manage containers with Kubernetes.', 'https://kubernetes.io/docs/tutorials/'),
            ('Linux Command Line Basics', 'other', 'Essential Linux commands for developers.', 'https://linuxcommand.org/'),
            ('VS Code Tips & Tricks', 'other', 'Boost productivity with VS Code editor.', 'https://code.visualstudio.com/docs/getstarted/tips-and-tricks'),
            ('Redis Cache Guide', 'other', 'In-memory data store for caching and real-time.', 'https://redis.io/docs/getting-started/'),
            ('Nginx Web Server Guide', 'other', 'Configure Nginx as a reverse proxy and web server.', 'https://nginx.org/en/docs/'),
            ('MongoDB NoSQL Database', 'other', 'Document-oriented NoSQL database with MongoDB.', 'https://www.mongodb.com/docs/manual/tutorial/getting-started/'),
            ('GraphQL API Guide', 'other', 'Query language for APIs with GraphQL.', 'https://graphql.org/learn/'),
            ('WebAssembly (Wasm) Guide', 'other', 'Run high-performance code in the browser.', 'https://webassembly.org/getting-started/developers-guide/'),
            ('REST API Design Best Practices', 'other', 'Design scalable and maintainable REST APIs.', 'https://docs.microsoft.com/en-us/azure/architecture/best-practices/api-design'),
            ('Software Architecture Patterns', 'other', 'Microservices, monoliths, event-driven architecture.', 'https://martinfowler.com/articles/patterns-of-enterprise-application-architecture/'),
            ('System Design Fundamentals', 'other', 'Design large-scale systems for interviews.', 'https://github.com/donnemartin/system-design-primer'),
            ('Agile & Scrum Methodology', 'other', 'Project management with Agile and Scrum.', 'https://www.scrum.org/resources/what-is-scrum'),
            ('DevOps Culture & Practices', 'other', 'CI/CD, infrastructure as code, monitoring.', 'https://www.atlassian.com/devops'),
            ('Terraform Infrastructure as Code', 'other', 'Provision cloud infrastructure with Terraform.', 'https://developer.hashicorp.com/terraform/tutorials'),
            ('HTML5 Semantic Elements', 'javascript', 'Modern HTML5 semantic tags and best practices.', 'https://developer.mozilla.org/en-US/docs/Web/HTML'),
            ('CSS3 Flexbox & Grid', 'javascript', 'Modern CSS layouts with Flexbox and CSS Grid.', 'https://css-tricks.com/snippets/css/a-guide-to-flexbox/'),
            ('Tailwind CSS Framework', 'javascript', 'Utility-first CSS framework for rapid UI.', 'https://tailwindcss.com/docs'),
            ('Bootstrap 5 Guide', 'javascript', 'Build responsive sites with Bootstrap 5.', 'https://getbootstrap.com/docs/5.0/getting-started/introduction/'),
            ('Sass/SCSS Styling', 'javascript', 'CSS preprocessor for more maintainable stylesheets.', 'https://sass-lang.com/guide'),
            ('Web Performance Optimization', 'javascript', 'Optimize load times, Core Web Vitals, and more.', 'https://web.dev/learn-core-web-vitals/'),
            ('Progressive Web Apps (PWA)', 'javascript', 'Build installable web apps with offline support.', 'https://web.dev/learn/pwa/'),
            ('WebSockets Real-Time Guide', 'javascript', 'Real-time bidirectional communication with WebSockets.', 'https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API'),
            ('Three.js 3D Graphics', 'javascript', '3D graphics in the browser with Three.js.', 'https://threejs.org/docs/index.html#manual/en/introduction/Creating-a-scene'),
            ('D3.js Data Visualization', 'javascript', 'Data-driven documents with D3.js.', 'https://d3js.org/getting-started'),
            ('Python NumPy Guide', 'python', 'Numerical computing with NumPy arrays.', 'https://numpy.org/doc/stable/user/quickstart.html'),
            ('Python Selenium Automation', 'python', 'Browser automation and testing with Selenium.', 'https://selenium-python.readthedocs.io/'),
            ('Go Programming Language', 'other', 'Learn Go for backend and systems programming.', 'https://go.dev/doc/tutorial/getting-started'),
            ('Rust Programming Language', 'other', 'Systems programming with memory safety in Rust.', 'https://doc.rust-lang.org/book/'),
            ('Java Spring Boot Guide', 'other', 'Enterprise Java with Spring Boot framework.', 'https://spring.io/guides'),
            ('Kotlin Android Development', 'other', 'Build Android apps with Kotlin.', 'https://developer.android.com/kotlin'),
            ('Swift iOS Development', 'other', 'Build iOS apps with Swift and SwiftUI.', 'https://developer.apple.com/tutorials/swiftui'),
            ('Flutter Mobile Development', 'other', 'Cross-platform mobile apps with Flutter.', 'https://docs.flutter.dev/'),
        ]
        for title, category, desc, url in resources:
            Resource.objects.get_or_create(title=title, defaults={
                'category': category, 'url': url, 'description': desc, 'is_published': True,
                'is_featured': title in ['Python for Beginners', 'Git & GitHub Handbook', 'Machine Learning Crash Course'],
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
