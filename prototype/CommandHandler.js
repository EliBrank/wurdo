import words from "./wordData.js";

export default class CommandHandler {
  constructor(gameState, gameInstance) {
    this.gameState = gameState;
    this.game = gameInstance;
  }

  handleInput(input) {
    const inputWord = input.trim().toLowerCase();

    if (!inputWord) return true;

    if (inputWord.includes(' ')) {
      console.log('Only single words may be submitted');
      return true;
    }

    if (!(inputWord in words)) {
      console.log('Invalid word');
      return true;
    }

    return this.evaluatePlay(inputWord);
  }

  evaluatePlay(word) {
    let scoreChange = 0;
    const currentWord = this.gameState.currentWord

    // Search through each match type in current word's scoring object
    // Score/Meter change depends on first match found
    //
    // e.g. currentWord object:
    // {
    //   "anagram": {...},
    //   "rhyme": {..."matchingWord": 15},
    //   "obo": {..."matchingWord": 20 },
    // }
    //
    // Score change is now 15, because rhyme was found first
    for (const matches of Object.values(words[currentWord])) {
      if (word in matches) {
        scoreChange = matches[word];
      }
    }

    const meterChange = Math.floor(((scoreChange - 50) / 10) - 1);

    this.gameState.score += scoreChange;
    this.gameState.meter += meterChange;
    this.gameState.currentWord = word;
    this.gameState.wordHistory.unshift(word);

    return true;
  }

  showGameState() {
    const status = this.gameState.getStatus();

    console.log();
    console.log('===================================');
    console.log(`Current Score: ${status.score}`);
    console.log(`Energy Meter: ${status.meterBar}`);
    console.log();
    // console.log('Available words:');;
    // console.log(Object.keys(words));
    console.log('===================================');
    console.log('Played Words:')
    console.log();
    status.recentWords.forEach((word) => {
      console.log('\t', word);
    });
    console.log();
  }
}
