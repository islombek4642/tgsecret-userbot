# TgSecret Core Local - Telegram Userbot System

## Quick Setup Checklist (Ubuntu 22.04)

### System Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y

# Install build tools
sudo apt install build-essential git curl -y
```

## Project Structure
```
tgsecret-core-local/
├── backend/                 # NestJS API Server
│   ├── src/
│   ├── prisma/
│   └── package.json
├── userbot/                # Python Pyrogram Bot
│   ├── src/
│   ├── sessions/
│   └── requirements.txt
├── admin/                  # Next.js Admin Panel
│   ├── app/
│   ├── components/
│   └── package.json
├── db/                     # Database Scripts
│   ├── migrations/
│   └── seeds/
├── scripts/                # Start/Stop Scripts
├── storage/                # Media Storage
└── logs/                   # Application Logs
```

## Step-by-Step Local Setup

### 1. Clone and Initialize
```bash
git clone <repository>
cd tgsecret-core-local
mkdir -p storage logs userbot/sessions
```

### 2. PostgreSQL Setup
```bash
# Create database and user
sudo -u postgres psql
CREATE USER tgsecret WITH PASSWORD 'your_secure_password';
CREATE DATABASE tgsecret_db OWNER tgsecret;
GRANT ALL PRIVILEGES ON DATABASE tgsecret_db TO tgsecret;
\q

# Test connection
psql -U tgsecret -d tgsecret_db -h localhost
```

### 3. Redis Setup
```bash
# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping
```

### 4. Environment Configuration

Create `.env` files in each directory:

**backend/.env**
```env
DATABASE_URL="postgresql://tgsecret:your_secure_password@localhost:5432/tgsecret_db"
REDIS_URL="redis://localhost:6379"
JWT_SECRET="your_jwt_secret_key_min_32_chars"
JWT_REFRESH_SECRET="your_jwt_refresh_secret_key_min_32_chars"
SERVER_ENCRYPTION_KEY="your_32_byte_hex_key_for_encryption"
TELEGRAM_API_ID="your_telegram_api_id"
TELEGRAM_API_HASH="your_telegram_api_hash"
TELEGRAM_BOT_TOKEN="your_bot_token"
PORT=3001
USERBOT_WEBHOOK_SECRET="shared_secret_with_userbot"
```

**userbot/.env**
```env
API_ID="your_telegram_api_id"
API_HASH="your_telegram_api_hash"
BACKEND_URL="http://localhost:3001"
WEBHOOK_SECRET="shared_secret_with_backend"
SESSION_STRING=""  # Will be generated on first run
PHONE_NUMBER="+1234567890"  # Your phone number
STORAGE_PATH="../storage"
LOG_LEVEL="INFO"
```

**admin/.env.local**
```env
NEXT_PUBLIC_API_URL="http://localhost:3001"
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your_nextauth_secret_key"
```

### 5. Backend Setup
```bash
cd backend

# Install dependencies
npm install

# Generate Prisma client
npx prisma generate

# Run migrations
npx prisma migrate deploy

# Start development server
npm run dev
```

### 6. Python Userbot Setup
```bash
cd userbot

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize session (first run only)
python -m src.init_session

# Run userbot
python -m src.run
```

### 7. Admin Panel Setup
```bash
cd admin

# Install dependencies
npm install

# Start development server
npm run dev
```

### 8. Create TLS Certificates (Optional for local HTTPS)
```bash
# Install mkcert
sudo apt install libnss3-tools
wget -O mkcert https://dl.filippo.io/mkcert/latest?for=linux/amd64
chmod +x mkcert
sudo mv mkcert /usr/local/bin/

# Create local CA
mkcert -install

# Generate certificates
mkcert localhost 127.0.0.1 ::1
```

## Testing Guide

### Test .ok Command (Disappearing Media Saver)
1. Send a view-once photo/video to your userbot account
2. Reply to it with `.ok`
3. Check Saved Messages for the saved media
4. Verify no notification was sent to original sender

### Test .get/.story Command (Story Saver)
1. Use `.get username` to fetch stories from a public account
2. Check Saved Messages for downloaded stories
3. Verify anonymous viewing (story view count shouldn't increase)

### Test .ask Command (AI Integration)
1. Add your AI API key in admin panel
2. Send `.ask What is the weather today?`
3. Receive AI response in chat

### Test Force Subscribe
1. Add required channels in admin panel
2. Try using a command without being subscribed
3. Join required channels and retry

## API Endpoints

### Backend (http://localhost:3001)
- `POST /auth/telegram` - Telegram login
- `GET /session/status` - Userbot session status
- `POST /session/start` - Start userbot
- `POST /session/stop` - Stop userbot
- `GET /force-subscribe/channels` - List required channels
- `POST /force-subscribe/check` - Check subscription
- `POST /api-keys` - Store AI API key
- `GET /media/logs` - View saved media logs

### Admin Panel (http://localhost:3000)
- `/login` - Admin login
- `/dashboard` - Main dashboard
- `/channels` - Manage force-subscribe
- `/api-keys` - Manage AI keys
- `/media` - View saved media
- `/session` - Control userbot

## Security Notes

- All API keys are encrypted at rest using AES-256-GCM
- JWT tokens expire after 15 minutes (refresh token: 7 days)
- Rate limiting: 10 requests/minute for .ask command
- Media files auto-cleanup after 30 days
- Session strings stored encrypted in database

## Backup Commands

```bash
# PostgreSQL backup
pg_dump -U tgsecret tgsecret_db > backup_$(date +%Y%m%d).sql

# Redis backup
redis-cli BGSAVE

# Media backup
tar -czf media_backup_$(date +%Y%m%d).tar.gz storage/
```

## Troubleshooting

### Common Issues
1. **Session expired**: Delete session file and re-authenticate
2. **Redis connection failed**: Check `redis-cli ping`
3. **PostgreSQL connection failed**: Check credentials and pg_hba.conf
4. **Port already in use**: Change PORT in .env files

### Log Locations
- Backend: `logs/backend-*.log`
- Userbot: `logs/userbot-*.log`
- Admin: Check browser console

## Production Deployment (Optional systemd)

See `scripts/systemd/` for service files to run as background services.
