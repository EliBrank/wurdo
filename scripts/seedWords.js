// scripts/seedWords.js

// 1. Load environment variables from .env.local
import dotenv from "dotenv";
dotenv.config({ path: ".env.local" });

// 2. Import necessary Node.js modules for file system operations
import fs from "fs";
import path from "path";
// 3. Import csv-parser for easy CSV file processing
import csv from "csv-parser";
// 4. Import the Redis client from @upstash/redis
import { Redis } from "@upstash/redis";
// 5. Utilities to get __dirname in ES Modules (Node.js newer versions)
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 6. Initialize Redis Client
// It uses environment variables for URL and token for secure connection.
const redis = new Redis({
  url: process.env.KV_REST_API_URL,
  token: process.env.KV_REST_API_TOKEN,
});

// 7. Define the path to your CSV file
const csvFilePath = path.resolve(__dirname, "./data.csv");

/**
 * 8. Build the RedisJSON object structure for a single word.
 * This is crucial for setting up the initial empty objects for later data.
 *
 * @param {object} row - A row object parsed from the CSV file.
 * @returns {object} The structured data ready for RedisJSON.
 */
function buildRedisObject(row) {
  // `row.pronunciation` comes directly from the CSV.
  // We use `|| ""` to ensure it's always a string, even if empty in CSV.
  // olo, anagram, rhyme are initialized as EMPTY OBJECTS `{}`.
  // This is because the CSV only provides 'word' and 'pronunciation',
  // and these fields will store 'word: score' pairs, which will be added later.
  return {
    pronunciation: row.pronunciation || "",
    olo: {}, // Initialize as empty object, not an array
    anagram: {}, // Initialize as empty object
    rhyme: {}, // Initialize as empty object
  };
}

/**
 * 9. Main seeding function to read CSV and populate Redis.
 */
async function seed() {
  const promises = []; // Array to hold all the Redis set promises

  console.log(`Starting to seed data from: ${csvFilePath}`);

  // 10. Create a readable stream from the CSV file
  fs.createReadStream(csvFilePath)
    // 11. Pipe the stream through the csv-parser to get row objects
    .pipe(csv())
    // 12. 'on("data")' event: This runs for each row successfully parsed from the CSV.
    .on("data", (row) => {
      const word = row.word?.toLowerCase(); // Get the word and convert to lowercase for key consistency.
      if (!word) {
        console.warn("Skipping row with missing word:", row);
        return; // Skip if the word field is empty
      }

      const dataToStore = buildRedisObject(row); // Get the structured object for this word.

      // 13. Call redis.json.set to store the entire JSON object for the word.
      // `word:${word}` is the key (e.g., "word:hello").
      // `$` means we are setting the value at the root of the JSON document.
      // `dataToStore` is the JavaScript object, which redis.json.set will stringify to JSON.
      const setPromise = redis.json.set(`word:${word}`, "$", dataToStore);
      promises.push(setPromise); // Add the promise to our array
    })
    // 14. 'on("end")' event: This runs once the entire CSV file has been processed.
    .on("end", async () => {
      console.log("CSV parsing finished. Waiting for Redis operations...");
      try {
        // 15. Wait for all Redis set operations to complete concurrently.
        await Promise.all(promises);
        console.log(`✅ Successfully seeded ${promises.length} words to Redis!`);
      } catch (err) {
        console.error("❌ Error during Redis operations:", err);
      }
    })
    // 16. 'on("error")' event: Catches any errors during file reading or CSV parsing.
    .on("error", (err) => {
      console.error("❌ Error reading or parsing CSV file:", err);
    });
}

// 17. Execute the seeding function and catch any top-level errors.
seed().catch((err) => {
  console.error("❌ Seeding process failed overall:", err);
});