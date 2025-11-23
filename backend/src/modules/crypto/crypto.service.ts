import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as crypto from 'node:crypto';

@Injectable()
export class CryptoService {
  private readonly algorithm = 'aes-256-gcm';
  private readonly key: Buffer;

  constructor(private readonly configService: ConfigService) {
    const keyHex = this.configService.get<string>('SERVER_ENCRYPTION_KEY');
    if (!keyHex?.length || keyHex.length !== 64) {
      throw new Error('SERVER_ENCRYPTION_KEY must be a 32-byte hex string (64 characters)');
    }
    this.key = Buffer.from(keyHex, 'hex');
  }

  /**
   * Encrypts a string using AES-256-GCM
   * @param text - The plaintext to encrypt
   * @returns Object containing encrypted text, IV, and auth tag
   */
  encrypt(text: string): { encrypted: string; iv: string; authTag: string } {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(this.algorithm, this.key, iv);
    
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return {
      encrypted,
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex'),
    };
  }

  /**
   * Decrypts a string encrypted with AES-256-GCM
   * @param encrypted - The encrypted text
   * @param iv - The initialization vector
   * @param authTag - The authentication tag
   * @returns The decrypted plaintext
   */
  decrypt(encrypted: string, iv: string, authTag: string): string {
    const decipher = crypto.createDecipheriv(
      this.algorithm,
      this.key,
      Buffer.from(iv, 'hex'),
    );
    
    decipher.setAuthTag(Buffer.from(authTag, 'hex'));
    
    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }

  /**
   * Generates a random hex string
   * @param length - Length in bytes
   * @returns Hex string
   */
  generateRandomHex(length: number = 32): string {
    return crypto.randomBytes(length).toString('hex');
  }

  /**
   * Hashes a string using SHA-256
   * @param text - Text to hash
   * @returns Hash hex string
   */
  hash(text: string): string {
    return crypto.createHash('sha256').update(text).digest('hex');
  }

  /**
   * Validates a webhook signature
   * @param payload - The webhook payload
   * @param signature - The provided signature
   * @param secret - The webhook secret
   * @returns Whether the signature is valid
   */
  validateWebhookSignature(payload: string, signature: string, secret: string): boolean {
    const expectedSignature = crypto
      .createHmac('sha256', secret)
      .update(payload)
      .digest('hex');
    
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expectedSignature),
    );
  }
}
