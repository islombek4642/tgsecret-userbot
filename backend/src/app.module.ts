import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { ThrottlerModule } from '@nestjs/throttler';
import { AuthModule } from './modules/auth/auth.module';
import { UserbotSessionModule } from './modules/userbot-session/userbot-session.module';
import { AIConfigModule } from './modules/ai-config/ai-config.module';
import { ForceSubscribeModule } from './modules/force-subscribe/force-subscribe.module';
import { MediaLogModule } from './modules/media-log/media-log.module';
import { PrismaModule } from './modules/prisma/prisma.module';
import { RedisModule } from './modules/redis/redis.module';
import { WebhookModule } from './modules/webhook/webhook.module';
import { CryptoModule } from './modules/crypto/crypto.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: '.env',
    }),
    ThrottlerModule.forRoot([{
      ttl: 60000, // 1 minute
      limit: 60, // 60 requests per minute
    }]),
    PrismaModule,
    RedisModule,
    CryptoModule,
    AuthModule,
    UserbotSessionModule,
    AIConfigModule,
    ForceSubscribeModule,
    MediaLogModule,
    WebhookModule,
  ],
})
export class AppModule {}
