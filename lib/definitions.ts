export interface WordScore {
    word: string;
    score: number;
}
  
export interface PartialData extends Record<string, any> {
    pronunciation?: string;
    oneLetterOff?: WordScore[];
    anagram?: WordScore[];
    rhyme?: WordScore[];
  
}