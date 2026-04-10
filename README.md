# Kick 360 Backend

Complete, production-ready backend for the Kick 360 – Football Skill Tracking & Tournament Management System. Built with Django and Django REST Framework.

## Tech Stack
- **Language**: Python 3.x
- **Framework**: Django + Django REST Framework
- **Auth**: JWT (SimpleJWT)
- **Database**: PostgreSQL (SQLite configured for local dev)
- **Storage**: AWS S3 (via django-storages)
- **Caching**: Redis
- **Architecture**: Domain-driven with a Service layer.

## Setup Instructions

### 1. Requirements
Ensure you have Python 3.9+ installed and PostgreSQL running if setting up for production.

### 2. Environment Variables
Copy `.env.example` to `.env` and configure your credentials.
```bash
cp .env.example .env
```
Ensure you set your AWS S3 credentials and Shopify API URL/Token.

### 3. Virtual Environment & Dependencies
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```
*(Note: A `requirements.txt` can be generated via `pip freeze > requirements.txt`)*

### 4. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 6. Run Server
```bash
python manage.py runserver
```

## API Documentation
The API adheres strictly to OpenAPI specs and provides an automated interactive UI with Swagger.
Once the server is running, visit:
- **Swagger UI**: `http://127.0.0.1:8000/api/docs/`
- **Redoc**: `http://127.0.0.1:8000/api/redoc/`
- **Raw Schema**: `http://127.0.0.1:8000/api/schema/`

admin@kick360.com

# Super Admin Credentials
ADMIN_EMAIL=parvinkona11@gmail.com
ADMIN_PASSWORD=kona1234



### List of Endpoints & Explanations

#### 1. Authentication (`/api/auth/`)
- `POST /api/auth/register/`: Registers a new user. Expects `name`, `country`, `position`, and `access_code`. The system verifies the code with Shopify; if valid and unused, creates the user and marks the code as consumed locally. Returns JWT tokens.
- `POST /api/auth/login/`: Logs in an existing user using their `access_code`. Returns JWT tokens.
- `POST /api/auth/refresh/`: Refreshes an expired JWT access token using a valid refresh token.
- `POST /api/auth/logout/`: Logs out the user (responds with success, client should drop the token).

#### 2. Sessions (`/api/sessions/`)
- `POST /api/sessions/complete/`: Completes a 360 playground session. Expects `total_kick`, and optionally `video_file`, `mode`, `is_story`, `is_shared_to_leaderboard`. Enforces a maximum of 5 uploaded videos limit. Atomically increases user's `total_kicks`, `points`, `streak` (if contiguous daily activity), and recalculates `rank`.
- `GET /api/sessions/history/`: Retrieves a paginated history of all sessions for the currently authenticated user.
- `PATCH /api/sessions/<id>/share/`: Toggles the visibility of a session. Expects `share_type` (`leaderboard` or `story`) and a boolean `state`.

#### 3. Dashboard (`/api/dashboard/`)
- `GET /api/dashboard/`: Returns the dashboard overview for the authenticated user, including profile stats (`total_kicks`, `rank`, `points`, `streak`) and `total_tournaments_joined`.

#### 4. Tournaments (`/api/tournaments/`)
- `GET /api/tournaments/`: Lists all active tournaments available to join.
- `GET /api/tournaments/<id>/`: Retrieves details of a specific tournament.
- `POST /api/tournaments/<id>/join/`: Allows the authenticated user to join a tournament.
- `GET /api/tournaments/<id>/leaderboard/`: Retrieves the paginated leaderboard for a specific tournament based on the kicks accumulated within the context of that tournament.

#### 5. Training Library (`/api/trainings/`)
- `GET /api/trainings/`: Lists available training videos. Supports filtering by `category` (e.g., `?category=1` or `?category__name=Dribbling`).
- `POST /api/trainings/<id>/complete/`: Marks a specific training video as completed. Expects `score_achieved`. Awards the specified default `points` assigned to that training video to the user's total points.

#### 6. Leaderboards (`/api/leaderboard/`)
- `GET /api/leaderboard/global/`: Retrieves the global leaderboard based on `total_kicks`. The response format includes a separated `top_3` array for highlighting the top players, a `full_list` (paginated), and the `current_user`'s absolute global rank and score.
- `GET /api/leaderboard/tournament/<id>/`: Helper endpoint that redirects to the tournament leaderboard representation.

#### 7. Stats (`/api/stats/`)
- `GET /api/stats/global/`: Returns high-level global aggregated statistics like total accumulated kicks across all users and the total platform user count.
- `GET /api/stats/country/<country_name>/`: Returns aggregate kicks and user count for a requested country (e.g., `/api/stats/country/Germany/`).
- `GET /api/stats/users/`: Returns a paginated list of users. This endpoint is highly filterable supporting queries like `?country=Germany&position=Forward`.

#### 8. Follow System (`/api/follows/`)
- `POST /api/follows/`: Connects the current user to follow another user. Expects `following_id` in the body.
- `DELETE /api/follows/<user_id>/`: Unfollows a specified user.
- `GET /api/follows/discover/`: Returns a paginated list of suggested users to follow, excluding the current user and profiles they already follow. Ordered by global rank (highest kickers first).
- `GET /api/follows/followers/`: Returns the list of users who follow the current authenticated user.
- `GET /api/follows/following/`: Returns the list of users that the current authenticated user follows.

#### 9. Settings (`/api/settings/`)
- `PATCH /api/settings/profile/`: Allows updating editable profile fields (`profile_image`, `country`, `position`). Handles multipart form data for parsing new image uploads replacing standard JSON.


## Running Tests
Run the provided unit tests for auth workflows, access code consumption, and session completion limits:
```bash
python manage.py test accounts sessions
```

## Deployment Notes (Gunicorn + Nginx)
For production, run using Gunicorn:
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```
Nginx should act as a reverse proxy forwarding requests to Gunicorn and serving static/media files directly. Make sure to collect static files prior to deployment:
```bash
python manage.py collectstatic
```

## Shopify Environment Configuration
The application relies on a service layer (`access_codes/services.py`) to verify Access Codes through a mockable Shopify Service.
If the following `.env` settings are missing, the app defaults to dummy verification strictly for local testing:
- `SHOPIFY_API_URL`
- `SHOPIFY_API_TOKEN`

## System Overview

The Kick 360 backend is designed to serve both the mobile application users and the web-based administrative panel.

### 1. User Application Flow (Mobile App)
- **Authentication**: Users log in leveraging "Access Codes" purchased via a Shopify integration. Once validated, users receive secure JWT tokens.
- **Engaging & Training**: Users can watch predefined categories of training videos, upload actual playground sessions (limited to 5 per record), and earn points and track streaks based on consecutive daily activities.
- **Social Connectivity**: A built-in follow system allows users to discover peers based on global ranking, tracking each other's progress.
- **Tournaments**: Users can dynamically join active tournaments, competing on exclusive leaderboards filtered strictly by activity within the tournament window.

### 2. Administrator Flow (Web Panel)
- **Authentication**: Administrators securely log in using a standard email and password system.
- **Password Reset (SendGrid)**: If an admin forgets their password, they can request a reset link. This flow generates a secure, single-use, 15-minute expiring token. Emails are configured and delivered securely utilizing **SendGrid**.
- **Management**: Admins have complete control over data metrics, tournament scheduling, training video management, and user moderation.

### 3. Dynamic Leaderboard Engine
The core of the application's gamification relies on a robust leaderboard system:
- **Calculation Formula**: Users are ranked dynamically based on descending values of **Points**, then total **Kicks**, and finally their active **Streak**.
- **Global & Contextual Ranks**: The API explicitly returns positional ranks (e.g., 1, 2, 3) ensuring immediate clarity on the frontend without relying solely on array indexing.

