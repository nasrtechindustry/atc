# Aru Tech Community

A community platform for developers, tech enthusiasts, and learners built with Django.

## Features

- Community events, workshops, and hackathons
- User registration and authentication
- Event management (CRUD)
- Code of Conduct page
- Responsive design with Bootstrap 5

## Tech Stack

- **Backend:** Django 4.2, Python 3
- **Frontend:** Bootstrap 5, Swiper.js, jQuery
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Static Files:** WhiteNoise

## Quick Start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Project Structure

```
config/              # Django project settings
community/           # Main Django app
  templates/         # HTML templates
  static/            # CSS, JS, images
  models.py          # Database models
  views.py           # View logic
  urls.py            # URL routes
staticfiles/         # Collected static (generated)
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `SECRET_KEY` - Django secret key
- `DEBUG` - Set to True for development
- `DATABASE_URL` - Database connection string
