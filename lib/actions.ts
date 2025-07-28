"use server";

import { redis } from "@/lib/redis";
import {toARPABET } from "phonemize";
import { PartialData } from "./definitions";
import { WordScore } from "./definitions";

const redisPath = "$"; // Root path for RedisJSON

export async function getWordData(word: string) {
  if (!word) return null;
  try {
    const result = await redis.json.get(`word:${word.toLowerCase()}`, redisPath);
    return result || null;
  } catch (err) {
    console.error("Failed to get word:", word, err);
    return null;
  }
}

export async function setWordData(word: string, data: PartialData) {
  if (!word || typeof data !== "object") return false;
  if (await getWordData(word) === true) return console.log("Word already exists")
   const phonem = toARPABET(word);
console.log(phonem)
    // I figure microserveices may go here or something of the sort
  if (Object.keys(data).length === 0){
  data = {
    pronunciation: phonem,
    oneLetterOff: [{word: "", score: 0}],
    anagram: [{word: "", score: 0}],
    rhyme: [{word: "", score: 0}],
}
  };
    const passdata = {
    pronunciation: phonem,
    oneLetterOff: data.oneLetterOff,
    anagram: data.anagram,
    rhyme: data.rhyme,
}

  try {
    await redis.json.merge(`word:${word.toLowerCase()}`, redisPath, passdata);
    return true;
  } catch (err) {
    console.error("Failed to set word:", word, err);
    return false;
  }
}

function mergeUniqueWordScores(
  currentArr: WordScore[] = [],
  newArr: WordScore[] = []
): WordScore[] {
  const map = new Map<string, WordScore>();

  currentArr.forEach((item) => map.set(item.word, item));
  newArr.forEach((item) => map.set(item.word, item)); // overwrites or adds

  return Array.from(map.values());
}

export async function updateWordData(word: string, partialData: Partial<PartialData>) {
  const current = (await getWordData(word)) as PartialData;
  if (!current) return false;

  const updated: PartialData = {
    pronunciation:
      partialData.pronunciation || current.pronunciation || toARPABET(word),

    oneLetterOff: mergeUniqueWordScores(
      current.oneLetterOff,
      partialData.oneLetterOff
    ),

    anagram: mergeUniqueWordScores(
      current.anagram,
      partialData.anagram
    ),

    rhyme: mergeUniqueWordScores(
      current.rhyme,
      partialData.rhyme
    ),
  };

  return await setWordData(word.toLowerCase(), updated);
}
