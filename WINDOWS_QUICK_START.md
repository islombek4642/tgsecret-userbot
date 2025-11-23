# 🪟 TgSecret - Windows Quick Start Guide

## ⚡ Tezkor Boshlash

### 1️⃣ Oldindan Tayyorlik

Sizda o'rnatilgan:
- ✅ Python 3.13.7
- ✅ Node.js 22.20.0

Kerak bo'ladi:
- ❌ PostgreSQL (yoki SQLite ishlatamiz)
- ❌ Redis (memory fallback ishlatamiz)

### 2️⃣ Backend Ishga Tushirish

```powershell
# 1. Dependencies o'rnatish (birinchi marta)
cd D:\USERBOT\backend
npm install
npx prisma generate
npx prisma db push

# 2. Backend ishga tushirish
npm run dev
```

### 3️⃣ Userbot Ishga Tushirish (Yangi PowerShell oyna)

```powershell
# 1. Virtual environment yaratish (birinchi marta)
cd D:\USERBOT\userbot
python -m venv venv

# 2. Virtual environment faollashtirish
.\venv\Scripts\Activate.ps1

# Agar xatolik bo'lsa:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. Dependencies o'rnatish
pip install -r requirements.txt

# 4. Session yaratish (BIRINCHI MARTA)
# .env fayldagi API_ID va API_HASH ni to'ldiring!
python -m src.init_session

# 5. Bot ishga tushirish
python -m src.main
```

### 4️⃣ Admin Panel (Yangi PowerShell oyna)

```powershell
cd D:\USERBOT\admin
npm install
npm run dev
```

## 🔧 Telegram API Credentials

1. https://my.telegram.org ga kiring
2. API Development Tools bo'limiga o'ting
3. `API_ID` va `API_HASH` oling
4. Bu ma'lumotlarni `D:\USERBOT\userbot\.env` fayliga yozing:

```env
API_ID=1234567
API_HASH=abcdef1234567890abcdef1234567890
PHONE_NUMBER=+998901234567
```

## 🎯 URL Manzillar

Ishga tushgandan keyin:
- **Backend API**: http://localhost:3001
- **Admin Panel**: http://localhost:3000
- **Health Check**: http://localhost:3001/webhook/health

## 🤖 Telegram Botda Test

1. Telegram ochish
2. O'zingizga xabar: `.help`
3. Ko'rishingiz kerak: barcha komandalar ro'yxati

## ⚠️ Agar Muammo Bo'lsa

**PostgreSQL/Redis yo'q:**
- SQLite ishlatamiz (avtomatik)
- In-memory fallback (avtomatik)

**Python venv faollashtirish xatosi:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**npm install sekin ishlayotir:**
- Sabr qiling, birinchi marta uzoq davom etadi

## 📝 Minimal Test (Database/Redis siz)

Faqat kodning to'g'ri ishlashini tekshirish uchun:

```powershell
# Backend
cd D:\USERBOT\backend
npm install
# TypeScript errorlar yo'qoladi

# Admin
cd D:\USERBOT\admin  
npm install
# TypeScript errorlar yo'qoladi
```

## 🚀 Avtomatik Ishga Tushirish

`start-all.ps1` faylini ishga tushiring:

```powershell
cd D:\USERBOT
.\start-all.ps1
```

Yoki qo'lda har bir servisni alohida PowerShell oynasida ishga tushiring.
