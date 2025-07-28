//This is the redis connection, it will be exported
// It uses the environment key in the wurdo settings/environment variables
// lib/redis.ts
import { Redis } from '@upstash/redis';

export const redis = new Redis({
  url: process.env.KV_REST_API_URL!,
  token: process.env.KV_REST_API_TOKEN!,
});