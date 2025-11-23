# TgSecret Core Local - System Architecture

## System Overview

TgSecret Core Local is a production-grade Telegram userbot system with the following key components:

1. **Backend API** (NestJS + TypeScript) - REST API server handling auth, session management, and data storage
2. **Userbot Engine** (Python + Pyrogram) - Telegram client handling commands and media operations
3. **Admin Panel** (Next.js 14) - Web interface for configuration and monitoring
4. **PostgreSQL Database** - Primary data storage with encrypted sensitive data
5. **Redis Cache** - Session management and rate limiting

## Core Features

### 1. Disappearing Media Saver (.ok)
- Detects reply to view-once media
- Downloads media without notifying sender
- Saves to user's Saved Messages
- Logs metadata to backend

### 2. Story Viewer & Saver (.get/.story)
- Anonymous story viewing (no view count increase)
- Downloads all active stories from username
- Saves to Saved Messages with metadata
- Stores in organized file structure

### 3. AI Assistant (.ask)
- Supports multiple AI providers (OpenAI, Claude, Gemini)
- Secure API key storage (AES-256-GCM encryption)
- Rate limiting (10 requests/minute)
- Streaming support for long responses

### 4. Force Subscribe Module
- Requires subscription to specified channels
- Admin-managed channel list
- Caches subscription status
- Provides join links when blocked

## Sequence Diagrams

### .ok Command Flow
```
User -> Userbot: Reply .ok to media
Userbot -> ForceSubscribe: Check subscription
ForceSubscribe -> Backend: Verify channels
Backend -> ForceSubscribe: Return status

[If subscribed]
Userbot -> Telegram: Download media
Telegram -> Userbot: Media file
Userbot -> Storage: Save to temp
Userbot -> Telegram: Upload to Saved Messages
Userbot -> Storage: Move to permanent
Userbot -> Backend: Log metadata
Backend -> Database: Store record
Userbot -> User: Delete command message

[If not subscribed]
Userbot -> User: Show required channels
```

### .get/.story Command Flow
```
User -> Userbot: .get username
Userbot -> ForceSubscribe: Check subscription
ForceSubscribe -> Backend: Verify channels

[If subscribed]
Userbot -> Telegram: Get user stories
Telegram -> Userbot: Stories list
Userbot -> User: Update status "Fetching..."

[For each story]
  Userbot -> Telegram: Download story media
  Telegram -> Userbot: Media file
  Userbot -> Storage: Save temporary
  Userbot -> Telegram: Upload to Saved Messages
  Userbot -> Storage: Move to permanent
  Userbot -> Backend: Log story metadata
  Backend -> Database: Store record

Userbot -> User: "Saved X stories"
```

### .ask Command Flow
```
User -> Userbot: .ask [prompt]
Userbot -> ForceSubscribe: Check subscription

[If subscribed]
Userbot -> Backend: Get API key for user
Backend -> Database: Retrieve encrypted key
Backend -> CryptoService: Decrypt key
Backend -> Userbot: Return API config

Userbot -> RateLimiter: Check rate limit
[If within limit]
  Userbot -> AI Provider: Send prompt
  AI Provider -> Userbot: Stream response
  Userbot -> User: Display response
  Userbot -> Backend: Log usage stats

[If rate limited]
  Userbot -> User: "Rate limit exceeded"

[If no API key]
  Userbot -> User: "Configure key in admin panel"
```

## Security Architecture

### Encryption
- **API Keys**: AES-256-GCM encryption at rest
- **Session Strings**: Encrypted in database
- **JWT Tokens**: 15-minute access, 7-day refresh
- **Webhook Secret**: HMAC-SHA256 validation

### Rate Limiting
- Global: 60 requests/minute per IP
- AI Commands: 10 requests/minute per user
- Media Downloads: 3 concurrent per user
- Story Downloads: 1-second delay between items

### Authentication Flow
```
1. Telegram Login Widget -> Backend
2. Backend validates hash with bot token
3. Backend issues JWT tokens
4. Frontend stores tokens securely
5. All API requests include Bearer token
6. Backend validates and refreshes as needed
```

## Data Flow Architecture

### Media Storage
```
/storage/
  /saved_media/
    /YYYYMM/
      /{file_id}_{filename}
  /stories/
    /{username}/
      /YYYYMM/
        /{story_id}_{filename}
  /temp/
    /{session_files}
```

### Database Schema Key Relations
```
User (1) -> (N) SavedMedia
User (1) -> (N) StoryLog
User (1) -> (1) BotSession
User (1) -> (N) APIKey
User (1) -> (N) UserSubscription
ForceSubscribeChannel (1) -> (N) UserSubscription
```

## API Endpoints

### Public Endpoints
- `POST /auth/telegram` - Telegram widget login
- `POST /auth/refresh` - Refresh JWT token

### Protected Endpoints
- `GET /session/status` - Get bot session status
- `POST /session/start` - Start userbot session
- `POST /session/stop` - Stop userbot session
- `GET /force-subscribe/channels` - List required channels
- `POST /force-subscribe/check` - Check user subscription
- `POST /api-keys` - Store encrypted API key
- `GET /api-keys/user/:id` - Get user's API config
- `POST /media/log` - Log saved media
- `POST /stories/log` - Log downloaded story
- `GET /media/logs` - View media history
- `POST /ai/usage` - Log AI usage

### Webhook Endpoints
- `POST /webhook/media` - Media save notification
- `POST /webhook/story` - Story download notification
- `POST /webhook/status` - Session status update

## Performance Optimizations

### Caching Strategy
- Force-subscribe channels: 5-minute TTL
- User subscription status: 1-minute TTL
- AI rate limits: In-memory sliding window
- Session validation: Redis with 15-minute TTL

### Database Optimization
- Indexed columns for frequent queries
- JSONB for flexible metadata storage
- Partitioned tables for logs (monthly)
- Automatic cleanup of expired data

### File Management
- Temporary files cleanup after processing
- 30-day retention for media files
- Compressed storage for old logs
- Streaming downloads for large files

## Monitoring & Logging

### Log Levels
- **ERROR**: Critical failures requiring attention
- **WARN**: Recoverable issues or rate limits
- **INFO**: Normal operations and events
- **DEBUG**: Detailed execution flow

### Log Rotation
- Backend: Daily rotation, 14-day retention
- Userbot: 10MB max size, 5 file rotation
- Nginx: Monthly rotation, 3-month retention

### Health Checks
- `/health` - Basic service status
- `/health/db` - Database connectivity
- `/health/redis` - Redis connectivity
- `/health/userbot` - Userbot session status

## Deployment Architecture

### Local Development
```
PostgreSQL (5432) <-> Backend (3001) <-> Redis (6379)
                           ^
                           |
                    Admin Panel (3000)
                           |
                           v
                    Userbot (Python)
```

### Production Deployment
- Backend: PM2 process manager or systemd
- Userbot: Supervisor or systemd service
- Database: PostgreSQL with replication
- Redis: Redis Sentinel for HA
- Admin: Nginx reverse proxy with SSL

## Backup & Recovery

### Backup Strategy
1. **Database**: Daily pg_dump with 7-day retention
2. **Media Files**: Weekly tar archive to external storage
3. **Redis**: Daily RDB snapshots
4. **Configuration**: Git repository for all configs

### Recovery Procedures
1. Stop all services
2. Restore database from backup
3. Restore media files if needed
4. Update configuration
5. Start services in order: DB -> Redis -> Backend -> Userbot

## Scaling Considerations

### Horizontal Scaling
- Backend: Load balancer with multiple instances
- Userbot: Multiple sessions with different phone numbers
- Database: Read replicas for queries
- Redis: Redis Cluster for distributed caching

### Vertical Scaling
- Increase PostgreSQL connection pool
- Adjust Node.js memory limits
- Optimize Python asyncio concurrency
- Tune Redis memory allocation
