import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../prisma/prisma.service';
import { CryptoService } from '../crypto/crypto.service';
import * as bcrypt from 'bcrypt';
import * as crypto from 'crypto';

interface TelegramAuthData {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

interface JwtPayload {
  sub: string;
  telegramId: string;
  username?: string;
  isAdmin: boolean;
}

@Injectable()
export class AuthService {
  constructor(
    private prisma: PrismaService,
    private jwtService: JwtService,
    private configService: ConfigService,
    private cryptoService: CryptoService,
  ) {}

  /**
   * Validates Telegram authentication data
   */
  validateTelegramAuth(authData: TelegramAuthData): boolean {
    const botToken = this.configService.get<string>('TELEGRAM_BOT_TOKEN');
    const { hash, ...data } = authData;
    
    // Check auth date (not older than 1 day)
    const currentTime = Math.floor(Date.now() / 1000);
    if (currentTime - authData.auth_date > 86400) {
      return false;
    }

    // Create data check string
    const dataCheckArr = [];
    for (const key of Object.keys(data).sort()) {
      dataCheckArr.push(`${key}=${data[key]}`);
    }
    const dataCheckString = dataCheckArr.join('\n');

    // Calculate hash
    const secretKey = crypto
      .createHash('sha256')
      .update(botToken)
      .digest();
    const calculatedHash = crypto
      .createHmac('sha256', secretKey)
      .update(dataCheckString)
      .digest('hex');

    return calculatedHash === hash;
  }

  /**
   * Authenticates user via Telegram and returns JWT tokens
   */
  async telegramLogin(authData: TelegramAuthData) {
    if (!this.validateTelegramAuth(authData)) {
      throw new UnauthorizedException('Invalid Telegram authentication');
    }

    // Find or create user
    let user = await this.prisma.user.findUnique({
      where: { telegramId: BigInt(authData.id) },
    });

    if (!user) {
      user = await this.prisma.user.create({
        data: {
          telegramId: BigInt(authData.id),
          firstName: authData.first_name,
          lastName: authData.last_name,
          username: authData.username,
          photoUrl: authData.photo_url,
        },
      });
    } else {
      // Update user info
      user = await this.prisma.user.update({
        where: { id: user.id },
        data: {
          firstName: authData.first_name,
          lastName: authData.last_name,
          username: authData.username,
          photoUrl: authData.photo_url,
        },
      });
    }

    return this.generateTokens(user);
  }

  /**
   * Admin login with email and password
   */
  async adminLogin(email: string, password: string) {
    const user = await this.prisma.user.findUnique({
      where: { email },
    });

    if (!user || !user.password || !user.isAdmin) {
      throw new UnauthorizedException('Invalid credentials');
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      throw new UnauthorizedException('Invalid credentials');
    }

    return this.generateTokens(user);
  }

  /**
   * Generates JWT access and refresh tokens
   */
  private async generateTokens(user: any) {
    const payload: JwtPayload = {
      sub: user.id,
      telegramId: user.telegramId.toString(),
      username: user.username,
      isAdmin: user.isAdmin,
    };

    const accessToken = this.jwtService.sign(payload, {
      secret: this.configService.get<string>('JWT_SECRET'),
      expiresIn: '15m',
    });

    const refreshToken = this.jwtService.sign(payload, {
      secret: this.configService.get<string>('JWT_REFRESH_SECRET'),
      expiresIn: '7d',
    });

    // Store refresh token
    await this.prisma.refreshToken.create({
      data: {
        userId: user.id,
        token: refreshToken,
        expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      },
    });

    // Clean up old refresh tokens
    await this.prisma.refreshToken.deleteMany({
      where: {
        userId: user.id,
        expiresAt: { lt: new Date() },
      },
    });

    return {
      accessToken,
      refreshToken,
      user: {
        id: user.id,
        telegramId: user.telegramId.toString(),
        username: user.username,
        firstName: user.firstName,
        lastName: user.lastName,
        photoUrl: user.photoUrl,
        isAdmin: user.isAdmin,
      },
    };
  }

  /**
   * Refreshes JWT tokens using refresh token
   */
  async refreshTokens(refreshToken: string) {
    try {
      const payload = this.jwtService.verify(refreshToken, {
        secret: this.configService.get<string>('JWT_REFRESH_SECRET'),
      });

      // Check if refresh token exists in database
      const storedToken = await this.prisma.refreshToken.findUnique({
        where: { token: refreshToken },
        include: { user: true },
      });

      if (!storedToken || storedToken.expiresAt < new Date()) {
        throw new UnauthorizedException('Invalid refresh token');
      }

      // Delete old refresh token
      await this.prisma.refreshToken.delete({
        where: { id: storedToken.id },
      });

      return this.generateTokens(storedToken.user);
    } catch (error) {
      throw new UnauthorizedException('Invalid refresh token');
    }
  }

  /**
   * Validates JWT token and returns user
   */
  async validateUser(payload: JwtPayload) {
    const user = await this.prisma.user.findUnique({
      where: { id: payload.sub },
    });

    if (!user || !user.isActive) {
      throw new UnauthorizedException('User not found or inactive');
    }

    return user;
  }

  /**
   * Logs out user by deleting refresh tokens
   */
  async logout(userId: string, refreshToken?: string) {
    if (refreshToken) {
      await this.prisma.refreshToken.deleteMany({
        where: { userId, token: refreshToken },
      });
    } else {
      await this.prisma.refreshToken.deleteMany({
        where: { userId },
      });
    }
  }
}
