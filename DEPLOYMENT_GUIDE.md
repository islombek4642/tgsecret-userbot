# TgSecret Core Local - Complete Deployment Guide

## 🎯 Overview

This guide provides step-by-step instructions for deploying TgSecret Core Local on Ubuntu 22.04 LTS without Docker containers. All components run directly on the host system.

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 22.04 LTS (or compatible)
- **RAM**: Minimum 2GB, recommended 4GB+
- **Storage**: 10GB+ free space for media storage
- **CPU**: 2+ cores recommended

### Required Accounts
1. **Telegram Account**: For userbot authentication
2. **Telegram API Credentials**: From https://my.telegram.org
3. **Bot Token**: Create a bot with @BotFather (for login widget)
4. **AI Provider** (Optional): OpenAI, Claude, or Gemini API key

## 🛠️ Installation Steps

### 1. System Dependencies Installation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install PostgreSQL 14+
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Install Redis Server
sudo apt install redis-server -y
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js 20.x LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y

# Install build essentials
sudo apt install build-essential git curl wget -y

# Verify installations
psql --version
redis-cli --version
python3.11 --version
node --version
npm --version
```

### 2. Database Configuration

```bash
# Switch to postgres user
sudo -u postgres psql

# Execute SQL commands
CREATE USER tgsecret WITH PASSWORD 'your_very_secure_password_here';
CREATE DATABASE tgsecret_db OWNER tgsecret;
GRANT ALL PRIVILEGES ON DATABASE tgsecret_db TO tgsecret;

# Configure PostgreSQL for network access (optional)
ALTER USER tgsecret WITH ENCRYPTED PASSWORD 'your_very_secure_password_here';

# Exit PostgreSQL
\q

# Test connection
psql -U tgsecret -d tgsecret_db -h localhost -W
# Enter password when prompted, then \q to exit
```

### 3. Redis Configuration

```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Recommended settings:
# maxmemory 256mb
# maxmemory-policy allkeys-lru
# appendonly yes

# Restart Redis
sudo systemctl restart redis-server

# Test Redis
redis-cli ping
# Should return: PONG
```

### 4. Project Setup

```bash
# Clone or extract project
cd /opt
sudo mkdir tgsecret
sudo chown $USER:$USER tgsecret
cd tgsecret

# Create directory structure
mkdir -p storage/{saved_media,stories,temp} logs userbot/sessions
chmod 755 storage logs
```

### 5. Backend Configuration

```bash
cd backend

# Create environment file
cp .env.example .env
nano .env

# Configure the following variables:
# DATABASE_URL="postgresql://tgsecret:your_password@localhost:5432/tgsecret_db"
# REDIS_URL="redis://localhost:6379"
# JWT_SECRET="$(openssl rand -hex 32)"
# JWT_REFRESH_SECRET="$(openssl rand -hex 32)"
# SERVER_ENCRYPTION_KEY="$(openssl rand -hex 32)"
# TELEGRAM_API_ID="your_api_id"
# TELEGRAM_API_HASH="your_api_hash"
# TELEGRAM_BOT_TOKEN="your_bot_token"
# USERBOT_WEBHOOK_SECRET="$(openssl rand -hex 32)"

# Install dependencies
npm install

# Generate Prisma client
npx prisma generate

# Run database migrations
npx prisma migrate deploy

# Or run SQL migration directly
psql -U tgsecret -d tgsecret_db -h localhost -f ../db/migrations/001_initial_schema.sql
```

### 6. Userbot Configuration

```bash
cd ../userbot

# Create environment file
cp .env.example .env
nano .env

# Configure:
# API_ID="your_telegram_api_id"
# API_HASH="your_telegram_api_hash"
# BACKEND_URL="http://localhost:3001"
# WEBHOOK_SECRET="same_as_backend_USERBOT_WEBHOOK_SECRET"
# PHONE_NUMBER="+1234567890"

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Initialize Telegram session (FIRST TIME ONLY)
python -m src.init_session
# Follow prompts to authenticate with Telegram
# This creates a session file and saves session string to .env
```

### 7. Admin Panel Configuration

```bash
cd ../admin

# Create environment file
cp .env.example .env.local
nano .env.local

# Configure:
# NEXT_PUBLIC_API_URL="http://localhost:3001"
# NEXTAUTH_URL="http://localhost:3000"
# NEXTAUTH_SECRET="$(openssl rand -hex 32)"
# NEXT_PUBLIC_TELEGRAM_BOT_USERNAME="your_bot_username"

# Install dependencies
npm install

# Build for production (optional)
npm run build
```

## 🚀 Starting Services

### Manual Start (Development)

**Terminal 1 - Backend:**
```bash
cd /opt/tgsecret
./scripts/start-backend.sh
# Or manually:
# cd backend && npm run dev
```

**Terminal 2 - Userbot:**
```bash
cd /opt/tgsecret
./scripts/start-userbot.sh
# Or manually:
# cd userbot && source venv/bin/activate && python -m src.main
```

**Terminal 3 - Admin Panel:**
```bash
cd /opt/tgsecret
./scripts/start-admin.sh
# Or manually:
# cd admin && npm run dev
```

### Production Start with systemd

Create service files:

**/etc/systemd/system/tgsecret-backend.service:**
```ini
[Unit]
Description=TgSecret Backend API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/opt/tgsecret/backend
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**/etc/systemd/system/tgsecret-userbot.service:**
```ini
[Unit]
Description=TgSecret Userbot
After=network.target tgsecret-backend.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/opt/tgsecret/userbot
ExecStart=/opt/tgsecret/userbot/venv/bin/python -m src.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**/etc/systemd/system/tgsecret-admin.service:**
```ini
[Unit]
Description=TgSecret Admin Panel
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/opt/tgsecret/admin
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tgsecret-backend tgsecret-userbot tgsecret-admin
sudo systemctl start tgsecret-backend
sudo systemctl start tgsecret-userbot
sudo systemctl start tgsecret-admin

# Check status
sudo systemctl status tgsecret-backend
sudo systemctl status tgsecret-userbot
sudo systemctl status tgsecret-admin

# View logs
sudo journalctl -u tgsecret-backend -f
sudo journalctl -u tgsecret-userbot -f
```

## ✅ Verification

### 1. Check Services
```bash
# PostgreSQL
sudo systemctl status postgresql
psql -U tgsecret -d tgsecret_db -h localhost -c "SELECT version();"

# Redis
redis-cli ping

# Backend API
curl http://localhost:3001/webhook/health

# Admin Panel
curl http://localhost:3000
```

### 2. Test Userbot Commands

Open Telegram on your phone/desktop:
1. Send yourself a test message
2. Reply to any message with `.help`
3. You should see the help menu

### 3. Test Admin Panel

1. Open browser: http://localhost:3000
2. Login with Telegram
3. Navigate to dashboard
4. Check statistics

## 🔒 Security Hardening

### Firewall Configuration
```bash
# Install UFW
sudo apt install ufw -y

# Allow SSH (if remote)
sudo ufw allow 22/tcp

# Allow only local connections (recommended)
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Or allow specific IPs only
# sudo ufw allow from YOUR_IP_ADDRESS to any port 3000
# sudo ufw allow from YOUR_IP_ADDRESS to any port 3001

# Enable firewall
sudo ufw enable
```

### PostgreSQL Security
```bash
# Edit pg_hba.conf
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Ensure local connections only:
# local   all             postgres                                peer
# local   all             all                                     peer
# host    all             all             127.0.0.1/32            md5
# host    all             all             ::1/128                 md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### File Permissions
```bash
cd /opt/tgsecret

# Protect environment files
chmod 600 backend/.env
chmod 600 userbot/.env
chmod 600 admin/.env.local

# Protect session files
chmod 700 userbot/sessions
chmod 600 userbot/sessions/*

# Protect storage
chmod 750 storage
chmod 640 storage/**/*
```

## 📊 Monitoring

### Log Management
```bash
# View backend logs
tail -f logs/backend-$(date +%Y-%m-%d).log

# View userbot logs
tail -f logs/userbot.log

# Rotate logs manually
logrotate -f /etc/logrotate.d/tgsecret
```

### Database Maintenance
```bash
# Vacuum database (weekly)
psql -U tgsecret -d tgsecret_db -c "VACUUM ANALYZE;"

# Check database size
psql -U tgsecret -d tgsecret_db -c "SELECT pg_size_pretty(pg_database_size('tgsecret_db'));"

# Clean old webhook logs (monthly)
psql -U tgsecret -d tgsecret_db -c "DELETE FROM \"WebhookLog\" WHERE \"createdAt\" < NOW() - INTERVAL '30 days';"
```

## 🔄 Backup & Restore

### Automated Backup Script
```bash
#!/bin/bash
# /opt/tgsecret/scripts/backup.sh

BACKUP_DIR="/opt/backups/tgsecret"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump -U tgsecret tgsecret_db > $BACKUP_DIR/db_$DATE.sql

# Backup Redis
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Backup media files
tar -czf $BACKUP_DIR/storage_$DATE.tar.gz /opt/tgsecret/storage

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Restore from Backup
```bash
# Restore database
psql -U tgsecret -d tgsecret_db < /opt/backups/tgsecret/db_YYYYMMDD_HHMMSS.sql

# Restore Redis
sudo systemctl stop redis-server
sudo cp /opt/backups/tgsecret/redis_YYYYMMDD_HHMMSS.rdb /var/lib/redis/dump.rdb
sudo systemctl start redis-server

# Restore media files
tar -xzf /opt/backups/tgsecret/storage_YYYYMMDD_HHMMSS.tar.gz -C /
```

## 🆘 Troubleshooting

### Common Issues

**1. Userbot won't start**
```bash
# Check session file
ls -la userbot/sessions/

# Re-initialize session
cd userbot
source venv/bin/activate
python -m src.init_session
```

**2. Database connection failed**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U tgsecret -d tgsecret_db -h localhost

# Check logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

**3. Redis connection failed**
```bash
# Check Redis status
sudo systemctl status redis-server

# Test Redis
redis-cli ping

# Check logs
sudo tail -f /var/log/redis/redis-server.log
```

**4. Port already in use**
```bash
# Find process using port
sudo lsof -i :3001
sudo lsof -i :3000

# Kill process if needed
sudo kill -9 PID
```

### Debug Mode

Enable debug logging:
```bash
# Backend
export LOG_LEVEL=debug
npm run dev

# Userbot
export LOG_LEVEL=DEBUG
python -m src.main
```

## 📈 Performance Tuning

### PostgreSQL
```sql
-- /etc/postgresql/14/main/postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
max_connections = 100
```

### Redis
```conf
# /etc/redis/redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

### Node.js
```bash
# Increase memory limit
export NODE_OPTIONS="--max-old-space-size=2048"
```

## 🎓 Next Steps

1. **Configure AI Provider**: Add API key in admin panel
2. **Setup Force Subscribe**: Add required channels
3. **Test Commands**: Try `.ok`, `.get`, `.ask`
4. **Monitor Logs**: Check for errors
5. **Setup Backups**: Enable automated backups
6. **Configure Alerts**: Setup monitoring (optional)

## 📚 Additional Resources

- **Telegram API Docs**: https://core.telegram.org/api
- **Pyrogram Docs**: https://docs.pyrogram.org
- **NestJS Docs**: https://docs.nestjs.com
- **Next.js Docs**: https://nextjs.org/docs

## 💡 Best Practices

1. **Regular Updates**: Keep dependencies updated
2. **Monitor Logs**: Check daily for errors
3. **Database Maintenance**: Run VACUUM weekly
4. **Backup Strategy**: Daily automated backups
5. **Security Audits**: Review access logs monthly
6. **Storage Cleanup**: Remove old media files
7. **Rate Limiting**: Monitor API usage
8. **Session Security**: Rotate session strings if compromised

---

**Support**: For issues, check logs in `/opt/tgsecret/logs/` first, then review troubleshooting section above.
