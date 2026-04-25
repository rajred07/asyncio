# Curate

> The social home for YouTube playlists — discover, organize, and collaborate.

[Live Demo](https://curatelist.vercel.app)

---

## What is Curate?

Curate is a full-stack social platform for YouTube power users. It solves the problem of disorganized video libraries by letting users save, categorize, and share YouTube playlists — with a smart discovery feed, collaborative group playlists, and an AI-powered Watch Later sorter.

Built on a fully asynchronous Python backend, Curate handles real-time social interactions, background YouTube imports, and personalized feed ranking — all without blocking I/O.

---

## Features

### Social Feed
Three discovery tabs, each with server-side pagination and Redis caching:
- **For You** — playlists ranked by engagement score (`likes×2 + saves×3 + views×0.5`) with a 1.5× boost for your preferred categories
- **Following** — chronological feed from users you follow
- **Trending** — ranked by the last 24-hour engagement window (recent likes + saves only)

Horizontal sections on the home screen: **Editor's Picks**, **Trending Now**, **Because You Liked X**, and **New & Rising**.

### Smart Playlist Organization
A three-level hierarchical tag system:
- **Category** → Gaming, Entertainment, Education, Music
- **Scenario** → Meal Time, Study Session, Workout, Binge Session, and more
- **Vibe** → 30+ sub-genre tags (Lo-Fi/Beats, Speedrun, Video Essay, etc.)

### Group Playlists
- Create shared playlists with multiple collaborators
- Role-based permissions (owner / member)
- Invite system with accept/decline flow
- Import an entire YouTube playlist as a background task with real-time Redis progress tracking

### Watch Later Sorter
- Chrome Extension scrapes the user's private YouTube Watch Later list
- Data is piped into a FastAPI background worker
- **Google Gemini 2.5 Flash** autonomously categorizes videos into the tag hierarchy

### Auth
- JWT (HS256) with per-token revocation via Redis blacklisting (`jti` claim)
- Tokens auto-expire from Redis when their lifetime ends — no unbounded growth
- Fail-open on Redis outage — users are never locked out

### YouTube Integration
- YouTube Data API v3 with 7-day Redis metadata cache
- Batch video fetching (up to 50 IDs per API call)
- ISO 8601 duration parsing
- Background playlist import with Redis progress tracking

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL (Neon serverless) |
| DB Driver | asyncpg |
| Cache & Blacklist | Redis (Upstash, TLS) |
| Auth | JWT HS256 + JTI blacklist |
| External API | YouTube Data API v3 + Google Gemini 2.5 Flash |
| Frontend | Next.js 14 (App Router) |
| Styling | Tailwind CSS |
| API Client | Auto-generated TypeScript client (OpenAPI) |
| Deployment | Render (backend) · Vercel (frontend) |
| Containerization | Docker |

---

## Project Structure

```
curate/
├── app/                        # FastAPI backend
│   ├── crud/                   # Database query logic
│   │   ├── feed.py             # Feed ranking algorithm
│   │   ├── user.py             # User & social graph
│   │   ├── playlist.py         # Playlist CRUD
│   │   ├── group_playlist.py   # Group playlists
│   │   └── ...
│   ├── models/                 # SQLAlchemy ORM models (11 tables)
│   ├── routes/                 # FastAPI routers
│   ├── schemas/                # Pydantic request/response schemas
│   ├── utils/
│   │   ├── auth.py             # JWT creation & validation
│   │   ├── cache.py            # Redis: feed cache, JWT blacklist, task progress
│   │   ├── youtube.py          # YouTube API v3 integration
│   │   ├── background_tasks.py # Async playlist import worker
│   │   └── ...
│   ├── constant.py             # Tag system constants (categories/scenarios/vibes)
│   ├── database.py             # Async engine & session factory
│   ├── main.py                 # App entry point
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Next.js 14 frontend
│   ├── app/                    # App Router pages
│   ├── components/             # UI components
│   ├── context/                # Auth & global state
│   └── lib/api/                # Auto-generated OpenAPI TS client
└── eatue/                      # Chrome Extension + AI pipeline
    └── chromeextension/        # Watch Later scraper extension
```

---

## Database Schema

11 relational models:

| Model | Description |
|---|---|
| `User` | Auth, profile, preferred categories, social graph |
| `followers_table` | Many-to-many follow relationships |
| `Playlist` | Public/private playlists with denormalized engagement counts |
| `Video` | YouTube videos with cached metadata |
| `PlaylistLike` | Like events (timestamped for trending window) |
| `PlaylistSave` | Save events |
| `PlaylistView` | View events |
| `GroupPlaylist` | Collaborative group playlists |
| `GroupPlaylistMember` | Member roles within group playlists |
| `GroupPlaylistVideo` | Videos inside group playlists |
| `GroupInvite` | Invite records with status |

---

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL or a [Neon](https://neon.tech) account
- Redis or an [Upstash](https://upstash.com) account
- YouTube Data API v3 key

### Backend

```bash
cd app
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Copy and fill in your environment variables
cp .env.example .env

uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
# Create frontend/.env.local with NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

API docs available at `http://localhost:8000/docs`

### Docker (Backend)

```bash
cd app
docker build -t curate-api .
docker run -p 8000:8000 --env-file .env curate-api
```

---

## Environment Variables

See `app/.env.example` for the full list. Key variables:

```
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=...
REDIS_URL=rediss://...
YOUTUBE_API_KEY=...
```

---

## Feed Ranking Algorithm

**For You tab:**
```
score = (likes_count × 2) + (saves_count × 3) + (views_count × 0.5)
```
If the playlist's category matches the user's preferred categories:
```
boosted_score = score × 1.5
```

**Trending tab:**
Only counts engagement events from the last 24 hours — so viral content rises regardless of historical totals.

**Caching:**
All feed responses are cached in Redis with a 5-minute TTL. Cache is invalidated per-user on any social action (like, save, follow).

---

## License

MIT
