import Redis from "ioredis";

const redis = new Redis({
  host: 'localhost',
  port: 6379,
});

async function getWordData(word) {
  try {
    const result = await redis.hgetall(`word:${word}`)
  }
}
