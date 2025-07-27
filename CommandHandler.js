import words from "./wordData";

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
  }

  showGameState() {
    const status = this.gameState.getStatus();

    console.log();
    console.log('===================================');
    console.log(`Current Score: ${status.score}`);
    console.log(`Energy Meter: ${status.meterBar}`);
    console.log();
    status.recentWords.forEach((word) => {
      console.log(word);
    });
    console.log('===================================');
    console.log(Object.keys(words));
    console.log();
  }
}
