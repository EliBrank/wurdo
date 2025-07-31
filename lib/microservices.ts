"use server";

import { getWordData, createWordEntry} from "./actions";
import { redis } from "@/lib/redis";
import {
  FullWordData,
  PartialUpdateData,
  BatchWordUpdate,
  WordScore,
} from "./definitions";



/**The Microservices are really just looking for two words right now
 * The @param word is the word to search 
 * the @param wordToAdd is the word to add. and the function will do the rest like converting
 * it to a object and storing it appropiatly
 * As of right now it adds one word per call tho
**/ 
export async function RhymeMicro(word:string, wordToAdd:string){
    const randomNum = (Math.floor(Math.random() * 100))

    if (!word) return console.warn("No word provided")
    const check = (await getWordData(word))
    const newWordToAdd = `${wordToAdd.toLowerCase()}`
    if ( check !== null){
        const rhyme:PartialUpdateData = {rhyme: {[newWordToAdd]: randomNum}}
        const data = await updateWordData(word, rhyme)
         data
    }
}

export async function oloMicro(word:string, wordToAdd:string){

    const randomNum = (Math.floor(Math.random() * 100))

    if (!word) return console.warn("No word provided")
    const check = (await getWordData(word))
    const newWordToAdd =`${wordToAdd.toLowerCase()}`
    if ( check !== null){
        const olo:PartialUpdateData = {oneLetterOff: {[newWordToAdd]: randomNum}}
        const data = await updateWordData(word, olo)
         data
    }
}

export async function anaMicro(word:string, wordToAdd:string){
    const randomNum = (Math.floor(Math.random() * 100))

    if (!word) return console.warn("No word provided")
    const check = (await getWordData(word))
    const newWordToAdd = `${wordToAdd.toLowerCase()}`
    if ( check !== null){
        const ana:PartialUpdateData = {anagram: {[newWordToAdd]: randomNum}}
        const data = await updateWordData(word, ana)
         data
    }
}


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
    return createWordEntry(word);
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
