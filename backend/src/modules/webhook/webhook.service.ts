import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class WebhookService {
  constructor(private readonly prisma: PrismaService) {}

  async logMedia(payload: any) {
    try {
      const media = await this.prisma.savedMedia.create({
        data: {
          userId: payload.userId,
          mediaType: payload.media_type?.toUpperCase() || 'DOCUMENT',
          originalChatId: BigInt(payload.original_chat_id),
          originalMsgId: payload.original_msg_id,
          savedMsgId: payload.saved_msg_id,
          fileName: payload.file_name,
          filePath: payload.file_path,
          fileSize: payload.file_size,
          mimeType: payload.mime_type,
          caption: payload.caption,
          senderUsername: payload.sender_username,
          senderName: payload.sender_name,
          isViewOnce: payload.is_view_once || false,
          metadata: payload.metadata || {},
        },
      });

      await this.logWebhookEvent('media_saved', payload, 'success');
      
      return { success: true, id: media.id };
    } catch (error) {
      await this.logWebhookEvent('media_saved', payload, 'error', error.message);
      throw error;
    }
  }

  async logStory(payload: any) {
    try {
      const story = await this.prisma.storyLog.create({
        data: {
          userId: payload.userId,
          targetUsername: payload.target_username,
          storyId: payload.story_id,
          mediaType: payload.media_type?.toUpperCase() || 'PHOTO',
          filePath: payload.file_path,
          fileSize: payload.file_size,
          caption: payload.caption,
          viewCount: payload.view_count,
          expiresAt: payload.expires_at ? new Date(payload.expires_at) : null,
          metadata: payload.metadata || {},
        },
      });

      await this.logWebhookEvent('story_saved', payload, 'success');
      
      return { success: true, id: story.id };
    } catch (error) {
      await this.logWebhookEvent('story_saved', payload, 'error', error.message);
      throw error;
    }
  }

  async updateSessionStatus(userId: string, isActive: boolean) {
    try {
      const session = await this.prisma.botSession.update({
        where: { userId },
        data: {
          isActive,
          lastActive: new Date(),
        },
      });

      await this.logWebhookEvent('session_status', { userId, isActive }, 'success');
      
      return { success: true, session };
    } catch (error) {
      await this.logWebhookEvent('session_status', { userId, isActive }, 'error', error.message);
      throw error;
    }
  }

  private async logWebhookEvent(event: string, payload: any, status: string, error?: string) {
    try {
      await this.prisma.webhookLog.create({
        data: {
          event,
          payload,
          status,
          error,
        },
      });
    } catch (err) {
      console.error('Failed to log webhook event:', err);
    }
  }
}
