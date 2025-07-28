export default class GameState {
  constructor(initialWord) {
    this.score = 0;
    this.meter = 40;
    this.currentWord = initialWord;
    this.wordHistory = [initialWord];
  }

  getStatus() {
    const meterBar = '#'.repeat(this.meter / 2) + '_'.repeat(((40 - this.meter) / 2));
    const recentWords = this.wordHistory.slice(0, 5).reverse();

    return {
      score: this.score,
      meterBar: meterBar,
      recentWords: recentWords,
    };
  }
}
