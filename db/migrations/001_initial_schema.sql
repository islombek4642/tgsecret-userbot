-- TgSecret Core Local - Initial Database Schema
-- PostgreSQL Migration

-- Create custom types
CREATE TYPE "MediaType" AS ENUM ('PHOTO', 'VIDEO', 'AUDIO', 'DOCUMENT', 'VOICE', 'STICKER', 'ANIMATION');
CREATE TYPE "AIProvider" AS ENUM ('OPENAI', 'CLAUDE', 'GEMINI', 'CUSTOM');

-- Users table
CREATE TABLE "User" (
    "id" TEXT NOT NULL,
    "telegramId" BIGINT NOT NULL,
    "username" TEXT,
    "firstName" TEXT NOT NULL,
    "lastName" TEXT,
    "photoUrl" TEXT,
    "email" TEXT,
    "password" TEXT,
    "isAdmin" BOOLEAN NOT NULL DEFAULT false,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- Bot Sessions table
CREATE TABLE "BotSession" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "sessionString" TEXT NOT NULL,
    "phoneNumber" TEXT,
    "isActive" BOOLEAN NOT NULL DEFAULT false,
    "lastActive" TIMESTAMP(3),
    "apiId" TEXT NOT NULL,
    "apiHash" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "BotSession_pkey" PRIMARY KEY ("id")
);

-- Saved Media table
CREATE TABLE "SavedMedia" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "mediaType" "MediaType" NOT NULL,
    "originalChatId" BIGINT NOT NULL,
    "originalMsgId" INTEGER NOT NULL,
    "savedMsgId" INTEGER,
    "fileName" TEXT,
    "filePath" TEXT,
    "fileSize" INTEGER,
    "mimeType" TEXT,
    "caption" TEXT,
    "senderUsername" TEXT,
    "senderName" TEXT,
    "isViewOnce" BOOLEAN NOT NULL DEFAULT false,
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "SavedMedia_pkey" PRIMARY KEY ("id")
);

-- Story Logs table
CREATE TABLE "StoryLog" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "targetUsername" TEXT NOT NULL,
    "storyId" TEXT NOT NULL,
    "mediaType" "MediaType" NOT NULL,
    "filePath" TEXT,
    "fileSize" INTEGER,
    "caption" TEXT,
    "viewCount" INTEGER,
    "expiresAt" TIMESTAMP(3),
    "downloadedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "metadata" JSONB,

    CONSTRAINT "StoryLog_pkey" PRIMARY KEY ("id")
);

-- Force Subscribe Channels table
CREATE TABLE "ForceSubscribeChannel" (
    "id" TEXT NOT NULL,
    "channelId" BIGINT NOT NULL,
    "username" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "isRequired" BOOLEAN NOT NULL DEFAULT true,
    "addedBy" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ForceSubscribeChannel_pkey" PRIMARY KEY ("id")
);

-- User Subscriptions table
CREATE TABLE "UserSubscription" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "channelId" TEXT NOT NULL,
    "isSubscribed" BOOLEAN NOT NULL DEFAULT false,
    "lastChecked" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "subscribedAt" TIMESTAMP(3),

    CONSTRAINT "UserSubscription_pkey" PRIMARY KEY ("id")
);

-- API Keys table
CREATE TABLE "APIKey" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "provider" "AIProvider" NOT NULL,
    "keyName" TEXT NOT NULL,
    "encryptedKey" TEXT NOT NULL,
    "encryptedIv" TEXT NOT NULL,
    "endpoint" TEXT,
    "model" TEXT,
    "maxTokens" INTEGER NOT NULL DEFAULT 4096,
    "usageCount" INTEGER NOT NULL DEFAULT 0,
    "lastUsed" TIMESTAMP(3),
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "APIKey_pkey" PRIMARY KEY ("id")
);

-- Refresh Tokens table
CREATE TABLE "RefreshToken" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "expiresAt" TIMESTAMP(3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "RefreshToken_pkey" PRIMARY KEY ("id")
);

-- Webhook Logs table
CREATE TABLE "WebhookLog" (
    "id" TEXT NOT NULL,
    "event" TEXT NOT NULL,
    "payload" JSONB NOT NULL,
    "status" TEXT NOT NULL,
    "error" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "WebhookLog_pkey" PRIMARY KEY ("id")
);

-- Create unique indexes
CREATE UNIQUE INDEX "User_telegramId_key" ON "User"("telegramId");
CREATE UNIQUE INDEX "User_username_key" ON "User"("username");
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");
CREATE UNIQUE INDEX "BotSession_userId_key" ON "BotSession"("userId");
CREATE UNIQUE INDEX "ForceSubscribeChannel_channelId_key" ON "ForceSubscribeChannel"("channelId");
CREATE UNIQUE INDEX "ForceSubscribeChannel_username_key" ON "ForceSubscribeChannel"("username");
CREATE UNIQUE INDEX "UserSubscription_userId_channelId_key" ON "UserSubscription"("userId", "channelId");
CREATE UNIQUE INDEX "APIKey_userId_provider_key" ON "APIKey"("userId", "provider");
CREATE UNIQUE INDEX "RefreshToken_token_key" ON "RefreshToken"("token");

-- Create additional indexes for performance
CREATE INDEX "SavedMedia_userId_createdAt_idx" ON "SavedMedia"("userId", "createdAt");
CREATE INDEX "StoryLog_userId_downloadedAt_idx" ON "StoryLog"("userId", "downloadedAt");
CREATE INDEX "UserSubscription_userId_isSubscribed_idx" ON "UserSubscription"("userId", "isSubscribed");
CREATE INDEX "APIKey_userId_isActive_idx" ON "APIKey"("userId", "isActive");
CREATE INDEX "RefreshToken_userId_idx" ON "RefreshToken"("userId");
CREATE INDEX "RefreshToken_expiresAt_idx" ON "RefreshToken"("expiresAt");
CREATE INDEX "WebhookLog_createdAt_idx" ON "WebhookLog"("createdAt");

-- Add foreign key constraints
ALTER TABLE "BotSession" ADD CONSTRAINT "BotSession_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "SavedMedia" ADD CONSTRAINT "SavedMedia_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "StoryLog" ADD CONSTRAINT "StoryLog_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "UserSubscription" ADD CONSTRAINT "UserSubscription_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "UserSubscription" ADD CONSTRAINT "UserSubscription_channelId_fkey" FOREIGN KEY ("channelId") REFERENCES "ForceSubscribeChannel"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "APIKey" ADD CONSTRAINT "APIKey_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "RefreshToken" ADD CONSTRAINT "RefreshToken_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- Add updatedAt trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW."updatedAt" = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updatedAt
CREATE TRIGGER update_User_updatedAt BEFORE UPDATE ON "User" FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_BotSession_updatedAt BEFORE UPDATE ON "BotSession" FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_ForceSubscribeChannel_updatedAt BEFORE UPDATE ON "ForceSubscribeChannel" FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_APIKey_updatedAt BEFORE UPDATE ON "APIKey" FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
