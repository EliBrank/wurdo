import words from './wordData.js';

const word = 'flare';
const currentWord = 'dare';
let scoreChange = 0;
let meter = 20;

console.log('objects for each match type:', Object.values(words[currentWord]));

for (const matches of Object.values(words[currentWord])) {
  if (word in matches) {
    scoreChange = matches[word];
    console.log('score change:', scoreChange);
    break;
  }
}
