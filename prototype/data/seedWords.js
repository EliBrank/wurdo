import fs from "fs";
import path from "path";
import csv from "csv-parser";
import Redis from "ioredis";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Initialize Local Redis Client
const redis = new Redis({
  host: "localhost",
  port: 6379,
});

// Get path to CSV file
const csvFilePath = path.resolve(__dirname, "./data.csv");

// Function called to build each row
function buildRedisObject(row) {
  return {
    arpa: row.pronunciation || "",
  };
}

async function seed() {
  const promises = [];

  console.log(`Starting to seed data from: ${csvFilePath}`);

  fs.createReadStream(csvFilePath)
    .pipe(csv())
    .on("data", (row) => {
      const word = row.word?.toLowerCase();
      if (!word) {
        console.warn("Skipping row with missing word:", row);
        return;
      }

      const dataToStore = buildRedisObject(row);

      // Save to database with hset
      const setPromise = redis.hset(`word:${word}`, dataToStore);
      promises.push(setPromise);
    })
    .on("end", async () => {
      console.log("CSV parsing finished. Waiting for Redis operations...");
      try {
        // Evaluate all set promises
        await Promise.all(promises);
        console.log(`Successfully seeded ${promises.length} words to Redis!`);
        // Close connection when done
        redis.disconnect();
      } catch (err) {
        console.error("Error during Redis operations:", err);
      }
    })
    .on("error", (err) => {
      console.error("Error reading or parsing CSV file:", err);
    });
}

// Execute with error handling
seed().catch((err) => {
  console.error("Seeding process failed overall:", err);
});
