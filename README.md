# Warehouse Management API

A Django-based warehouse/inventory project.

## Tech Stack
- Python
- Django REST Framework (project API)

## Setup
1. Create and activate a virtual environment.
2. Install dependencies from the project's dependency file, if available.
3. Configure local settings and environment variables.
4. Initialize the database and run the development server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Database
The local SQLite database is not stored in this repository. Apply migrations to create a local database.

## Development
Keep virtual environments, local databases, caches, secrets, and generated files out of Git.
