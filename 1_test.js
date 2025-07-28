import words from './wordData.js';

const wordList = Object.keys(words);

console.log();
console.log('===================================');
console.log(`Current Score: 530`);
console.log(`Energy Meter: ##########__________`);
console.log();
wordList.slice(0, 6).forEach((word) => {
  console.log(word);
});
console.log('===================================');
console.log('Available words:');
console.log(Object.keys(words))
console.log();
