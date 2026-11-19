# Blog Post API

A REST API for user registration, JWT authentication, and user posts, built with FastAPI and SQLAlchemy async support.

## Tech Stack

- FastAPI
- SQLAlchemy 2 async
- SQLite with `aiosqlite`
- Pydantic v2
- Passlib with bcrypt and Argon2
- Python-JOSE for JWT authentication

## Project Structure

```text
blog_post/
├── main.py
├── config.py
├── database.py
├── dependency.py
├── models.py
├── schemas.py
├── crud.py
├── router/
│   ├── auth.py
│   └── post.py
├── requirements.txt
└── .env
```

## Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Create `.env` in the project root:

```env
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Generate a secure secret with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

Open:

- API documentation: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Routes

| Method | Endpoint | Authentication | Description |
|---|---|---:|---|
| `POST` | `/auth/signup` | No | Register a user |
| `POST` | `/auth/login` | No | Login and receive a JWT |
| `POST` | `/post/` | Yes | Create a post |
| `GET` | `/post/me` | Yes | List the current user's posts |
| `GET` | `/post/user/{user_id}` | No | List posts for a user |
| `GET` | `/post/{post_id}` | No | Get a post |
| `PATCH` | `/post/{post_id}` | Yes | Update a post owned by the current user |
| `DELETE` | `/post/{post_id}` | Yes | Delete a post owned by the current user |

## Application Flow

```mermaid
flowchart TD
    Client[API Client] --> Main[FastAPI Application]
    Main --> Auth[Auth Router]
    Main --> Post[Post Router]

    Auth --> Database[(SQLite Database)]
    Post --> Database

    Auth --> AuthFlow[Signup or Login]
    AuthFlow --> JWT[JWT Token]

    Post --> Dependency[JWT Dependency]
    Dependency --> JWT
```

## Signup Flow

```mermaid
sequenceDiagram
    actor User
    participant API
    participant Database

    User->>API: POST /auth/signup
    API->>Database: Check whether email exists

    alt Email already exists
        Database-->>API: Existing user found
        API-->>User: 400 Email already registered
    else Email is available
        API->>API: Hash password
        API->>Database: Insert user
        Database-->>API: Created user
        API-->>User: 201 User details
    end
```

## Login and Authorization Flow

```mermaid
sequenceDiagram
    actor User
    participant API
    participant Database

    User->>API: POST /auth/login with username and password
    API->>Database: Find user by email

    alt Invalid credentials
        Database-->>API: User missing or password mismatch
        API-->>User: 401 Incorrect email or password
    else Valid credentials
        API->>API: Create signed JWT
        API-->>User: 200 Access token
        User->>API: Protected request with Bearer token
        API->>API: Verify JWT and load user
        API-->>User: Protected resource
    end
```

## Post CRUD Flow

```mermaid
flowchart LR
    Request[Client Request] --> Route{Route and Method}

    Route -->|POST| Create[Validate payload]
    Route -->|GET| Read[Load post or posts]
    Route -->|PATCH| Update[Verify owner and update]
    Route -->|DELETE| Delete[Verify owner and delete]

    Create --> CurrentUser{Authenticated?}
    Update --> CurrentUser
    Delete --> CurrentUser

    CurrentUser -->|No| Unauthorized[401 Unauthorized]
    CurrentUser -->|Yes| Ownership{Owns post?}

    Ownership -->|No| Forbidden[403 Forbidden]
    Ownership -->|Yes| CRUD[Execute CRUD operation]

    Read --> CRUD
    CRUD --> Database[(SQLite Database)]
    Database --> Response[API Response]
```
