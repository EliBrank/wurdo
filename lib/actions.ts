"use server";

import { redis } from "@/lib/redis";
import { toARPABET } from "phonemize";
import {
  FullWordData,
  PartialUpdateData,
  BatchWordUpdate,
  WordScore,
} from "./definitions";

export async function getWordData(word: string): Promise<FullWordData | null> {
  if (!word) {
    console.warn("getWordData called with empty word.");
    return null;
  }

  try {
    const result = await redis.json.get(`word:${word.toLowerCase()}`, "$");
    return (result as FullWordData) || null;
  } catch (err) {
    console.error(`Failed to get word data for "${word}":`, err);
    return null;
  }
}

/**
 * Creates a NEW word entry in RedisJSON.
 * This should only be used when the word does NOT already exist.
 * It initializes pronunciation and empty objects for olo, anagram, rhyme.
 * @param {string} word - The word to create.
 * @param {string} [initialPronunciation] - Optional initial pronunciation.
 * @returns {Promise<boolean>} True if successful, false otherwise.
 */
export async function createWordEntry(
  word: string,
  initialPronunciation?: string
): Promise<boolean> {
  if (!word) {
    console.warn("createWordEntry called with empty word.");
    return false;
  }

  const key = `word:${word.toLowerCase()}`;
  const existingData = await getWordData(word);
  if (existingData) {
    console.log(`Word "${word}" already exists. Skipping creation.`);
    return false;
  }

  const pronunciation = initialPronunciation ?? toARPABET(word);

  const initialData: FullWordData = {
    pronunciation: pronunciation,
    olo: {},
    ana: {},
    rhy: {},
  };

  try {
    await redis.json.set(key, "$", JSON.stringify(initialData));
    console.log(`Successfully created word "${word}" in Redis.`);
    return true;
  } catch (err) {
    console.error(`Failed to create word "${word}" in Redis:`, err);
    return false;
  }
}

/**
 * Updates specific fields of an existing word entry in RedisJSON.
 * - `pronunciation` is updated directly.
 * - `olo`, `anagram`, `rhyme` are MERGED (new word-score pairs added, existing ones updated).
 * Values will NOT be overwritten if not provided in `partialData`.
 * @param {string} word - The word (key) to update.
 * @param {WordUpdateData} partialData - The partial data to update with.
 * @returns {Promise<boolean>} True if successful, false otherwise.
 */
export async function updateWordData(
  word: string,
  partialData: PartialUpdateData
): Promise<boolean> {
  if (
    !word ||
    typeof partialData !== "object" ||
    Object.keys(partialData).length === 0
  ) {
    console.warn(
      "Invalid input for updateWordData: word or partialData missing/empty."
    );
    return false;
  }

  const key = `word:${word.toLowerCase()}`;
  const existingData = await getWordData(word);

  // If the word doesn't exist, we can optionally create it here,
  // or return false and expect createWordEntry to be called first.
  if (!existingData) {
    console.warn(
      `Word "${word}" does not exist. Cannot update. Consider calling createWordEntry first.`
    );
    return createWordEntry(word, partialData.pronunciation);
  }

  try {
    if (partialData.pronunciation !== undefined) {
      await redis.json.set(
        key,
        "$.pronunciation",
        JSON.stringify(partialData.pronunciation)
      );
      console.log(`Updated pronunciation for "${word}".`);
    }

    // --- Merge OLO, Anagram, Rhyme Objects (if provided) ---
    // Iterate over the object fields (olo, anagram, rhyme) that you want to merge.
    // JSON.MERGE at a specific path will add new key-value pairs or update existing ones,
    // leaving other key-value pairs at that path untouched.
    const objectFieldsToMerge: Array<
      keyof Pick<PartialUpdateData, "oneLetterOff" | "anagram" | "rhyme">
    > = ["oneLetterOff", "anagram", "rhyme"];

    for (const field of objectFieldsToMerge) {
      if (
        partialData[field] !== undefined &&
        typeof partialData[field] === "object" &&
        partialData[field] !== null
      ) {
        // Ensure the target path exists and is an object, or JSON.MERGE will create it.
        // It's safer to ensure the parent path exists and is an object.
        // For top-level fields like these, `redis.json.merge(key, '$.field', ...)` works perfectly.
        await redis.json.merge(
          key,
          `$.${String(field)}`,
          JSON.stringify(partialData[field])
        );
        console.log(`Merged "${String(field)}" data for "${word}".`);
      } else if (partialData[field] !== undefined) {
        console.warn(
          `Field "${String(
            field
          )}" in partialData for "${word}" is not a valid object for merging.`
        );
      }
    }

    console.log(`Successfully updated word "${word}" in Redis.`);
    return true;
  } catch (err) {
    console.error(`Failed to update word "${word}" in Redis:`, err);
    return false;
  }
}

// NOT COMPLETED YET DO NO USE
/**
 * Updates multiple word entries in a single, atomic Redis transaction.
 * This is highly efficient for bulk updates.
 *
 * @param {BatchWordUpdate[]} updates - An array of word updates.
 * @returns {Promise<boolean>} True if the transaction was successful, false otherwise.
 */
export async function updateMultipleWords(
  updates: BatchWordUpdate[]
): Promise<boolean> {
  if (!updates || updates.length === 0) {
    console.warn("No updates provided to updateMultipleWords.");
    return true;
  }

  // Start a new transaction pipeline
  const transaction = redis.multi();

  for (const update of updates) {
    const { word, data } = update;
    if (!word || typeof data !== "object" || Object.keys(data).length === 0) {
      console.warn(`Skipping invalid entry in batch for word: ${word}`);
      continue;
    }

    const key = `word:${word.toLowerCase()}`;

    // Queue pronunciation update if provided
    if (data.pronunciation !== undefined) {
      transaction.json.set(
        key,
        "$.pronunciation",
        JSON.stringify(data.pronunciation)
      );
    }

    // Queue merging of object fields (olo, anagram, rhyme)
    const fieldsToMerge: Array<
      keyof Pick<PartialUpdateData, "oneLetterOff" | "anagram" | "rhyme">
    > = ["oneLetterOff", "anagram", "rhyme"];

    for (const field of fieldsToMerge) {
      if (data[field] && typeof data[field] === "object") {
        transaction.json.merge(
          key,
          `$.${String(field)}`,
          JSON.stringify(data[field])
        );
      }
    }
  }

  //Execute the transaction
  try {
    // `exec()` sends all queued commands to Redis at once.
    const results = await transaction.exec();

    if (results.some((res) => res[0] !== null)) {
      console.error("Some commands in the batch transaction failed:", results);
      // Depending on requirements, you might want more granular error handling here.
      return false;
    }

    console.log(
      `Successfully executed a batch update for ${updates.length} words.`
    );
    return true;
  } catch (err) {
    console.error("Failed to execute batch update transaction:", err);
    return false;
  }
}
