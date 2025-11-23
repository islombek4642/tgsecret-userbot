import { Controller, Post, Body, Headers, UnauthorizedException, Get } from '@nestjs/common';
import { WebhookService } from './webhook.service';
import { ConfigService } from '@nestjs/config';
import { CryptoService } from '../crypto/crypto.service';
import { ApiTags, ApiOperation } from '@nestjs/swagger';

@ApiTags('Webhooks')
@Controller('webhook')
export class WebhookController {
  constructor(
    private readonly webhookService: WebhookService,
    private readonly configService: ConfigService,
    private readonly cryptoService: CryptoService,
  ) {}

  private validateWebhookSignature(signature: string, payload: any): boolean {
    const secret = this.configService.get<string>('USERBOT_WEBHOOK_SECRET');
    return this.cryptoService.validateWebhookSignature(
      JSON.stringify(payload),
      signature,
      secret,
    );
  }

  @Post('media')
  @ApiOperation({ summary: 'Log saved media from userbot' })
  async logMedia(
    @Headers('x-webhook-secret') signature: string,
    @Body() payload: any,
  ) {
    const secret = this.configService.get<string>('USERBOT_WEBHOOK_SECRET');
    if (signature !== secret) {
      throw new UnauthorizedException('Invalid webhook signature');
    }

    return this.webhookService.logMedia(payload);
  }

  @Post('story')
  @ApiOperation({ summary: 'Log downloaded story from userbot' })
  async logStory(
    @Headers('x-webhook-secret') signature: string,
    @Body() payload: any,
  ) {
    const secret = this.configService.get<string>('USERBOT_WEBHOOK_SECRET');
    if (signature !== secret) {
      throw new UnauthorizedException('Invalid webhook signature');
    }

    return this.webhookService.logStory(payload);
  }

  @Post('status')
  @ApiOperation({ summary: 'Update userbot session status' })
  async updateStatus(
    @Headers('x-webhook-secret') signature: string,
    @Body() payload: { userId: string; isActive: boolean },
  ) {
    const secret = this.configService.get<string>('USERBOT_WEBHOOK_SECRET');
    if (signature !== secret) {
      throw new UnauthorizedException('Invalid webhook signature');
    }

    return this.webhookService.updateSessionStatus(payload.userId, payload.isActive);
  }

  @Get('health')
  @ApiOperation({ summary: 'Health check endpoint' })
  async healthCheck() {
    return {
      status: 'ok',
      timestamp: new Date().toISOString(),
      service: 'TgSecret Backend',
    };
  }
}
