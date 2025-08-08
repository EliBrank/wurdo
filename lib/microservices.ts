/* eslint-disable @typescript-eslint/no-explicit-any */
"use server";

import { getWordData, createWordEntry, updateWordData } from "./actions";
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
export async function RhymeMicro(word: string, wordToAdd: string) {
  const randomNum = Math.floor(Math.random() * 100);

  if (!word) return console.warn("No word provided");
  const check = await getWordData(word);
  const newWordToAdd = `${wordToAdd.toLowerCase()}`;
  if (check !== null) {
    const rhyme: PartialUpdateData = { rhyme: { [newWordToAdd]: randomNum } };
    const data = await updateWordData(word, rhyme);
    data;
  }
}

export async function oloMicro(word: string, wordToAdd: string) {
  const randomNum = Math.floor(Math.random() * 100);

  if (!word) return console.warn("No word provided");
  const check = await getWordData(word);
  const newWordToAdd = `${wordToAdd.toLowerCase()}`;
  if (check !== null) {
    const olo: PartialUpdateData = {
      oneLetterOff: { [newWordToAdd]: randomNum },
    };
    const data = await updateWordData(word, olo);
    data;
  }
}

export async function anaMicro(word: string, wordToAdd: string) {
  const randomNum = Math.floor(Math.random() * 100);

  if (!word) return console.warn("No word provided");
  const check = await getWordData(word);
  const newWordToAdd = `${wordToAdd.toLowerCase()}`;
  if (check !== null) {
    const ana: PartialUpdateData = { anagram: { [newWordToAdd]: randomNum } };
    const data = await updateWordData(word, ana);
    data;
  }
}

export async function RhymeMicroArray(word: string, wordsToAdd: string[]) {
  const randomNum = Math.floor(Math.random() * 100);

  if (!word) return console.warn("No word provided");
  const check = await getWordData(word);
  for (const word of wordsToAdd) {
    const newWordToAdd = `${word.toLowerCase()}`;
    if (check !== null) {
      const rhyme: PartialUpdateData = { rhyme: { [newWordToAdd]: randomNum } };
      const data = await updateWordData(word, rhyme);
      data;
    }
  }
}

export async function oloMicroArray(word: string, wordsToAdd: string[]) {
  const randomNum = Math.floor(Math.random() * 100);

  if (!word) return console.warn("No word provided");
  const check = await getWordData(word);
  for (const word of wordsToAdd) {
    const newWordToAdd = `${word.toLowerCase()}`;
    if (check !== null) {
      const olo: PartialUpdateData = {
        oneLetterOff: { [newWordToAdd]: randomNum },
      };
      const data = await updateWordData(word, olo);
      data;
    }
  }
}

export async function anaMicroArray(word: string, wordsToAdd: string[]) {
  const randomNum = Math.floor(Math.random() * 100);

  if (!word) return console.warn("No word provided");
  const check = await getWordData(word);
  for (const word of wordsToAdd) {
    const newWordToAdd = `${word.toLowerCase()}`;
    if (check !== null) {
      const ana: PartialUpdateData = { anagram: { [newWordToAdd]: randomNum } };
      const data = await updateWordData(word, ana);
      data;
    }
  }
}
