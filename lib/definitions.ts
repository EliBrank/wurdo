export interface WordScore {
    word: string;
    score: number;
}
export interface BatchWordUpdate {
    word: string;
    data: PartialUpdateData
}

export interface FullWordData {
    pronunciation: string;
    olo: Record<string, number>;
    ana: Record<string, number>;
    rhy:Record<string, number>;
}

// You can pass this for the scoring system. 
// Something like updateWordData(word="word", partialData= "oneLetterOff: {"word": "score"}" )
export interface PartialUpdateData {
    pronunciation?: string;
    oneLetterOff?: Record<string, number>;
    anagram?: Record<string, number>;
    rhyme?: Record<string, number>;
  
}