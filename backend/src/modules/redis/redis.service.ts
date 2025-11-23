import { Injectable, OnModuleDestroy } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import Redis from 'ioredis';

@Injectable()
export class RedisService implements OnModuleDestroy {
  private readonly client: Redis;

  constructor(private readonly configService: ConfigService) {
    const redisUrl = this.configService.get<string>('REDIS_URL', 'redis://localhost:6379');
    this.client = new Redis(redisUrl);
    
    this.client.on('error', (err) => {
      console.error('Redis Client Error:', err);
    });
    
    this.client.on('connect', () => {
      console.log('Redis Client Connected');
    });
  }

  async onModuleDestroy() {
    await this.client.quit();
  }

  /**
   * Get a value from Redis
   */
  async get(key: string): Promise<string | null> {
    return await this.client.get(key);
  }

  /**
   * Set a value in Redis with optional TTL
   */
  async set(key: string, value: string, ttl?: number): Promise<'OK'> {
    if (ttl) {
      return await this.client.set(key, value, 'EX', ttl);
    }
    return await this.client.set(key, value);
  }

  /**
   * Delete a key from Redis
   */
  async del(key: string): Promise<number> {
    return await this.client.del(key);
  }

  /**
   * Check if a key exists
   */
  async exists(key: string): Promise<number> {
    return await this.client.exists(key);
  }

  /**
   * Set a hash field
   */
  async hset(key: string, field: string, value: string): Promise<number> {
    return await this.client.hset(key, field, value);
  }

  /**
   * Get a hash field
   */
  async hget(key: string, field: string): Promise<string | null> {
    return await this.client.hget(key, field);
  }

  /**
   * Get all hash fields
   */
  async hgetall(key: string): Promise<Record<string, string>> {
    return await this.client.hgetall(key);
  }

  /**
   * Increment a value
   */
  async incr(key: string): Promise<number> {
    return await this.client.incr(key);
  }

  /**
   * Set expiration on a key
   */
  async expire(key: string, seconds: number): Promise<number> {
    return await this.client.expire(key, seconds);
  }

  /**
   * Add to a set
   */
  async sadd(key: string, ...members: string[]): Promise<number> {
    return await this.client.sadd(key, ...members);
  }

  /**
   * Check if member exists in set
   */
  async sismember(key: string, member: string): Promise<number> {
    return await this.client.sismember(key, member);
  }

  /**
   * Get all members of a set
   */
  async smembers(key: string): Promise<string[]> {
    return await this.client.smembers(key);
  }

  /**
   * Get the Redis client for advanced operations
   */
  getClient(): Redis {
    return this.client;
  }
}
