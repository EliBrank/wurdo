export default class GameState {
  constructor(initialWord) {
    this.score = 0;
    this.meter = 20;
    this.currentWord = initialWord;
    this.wordHistory = [initialWord];
  }

  getStatus() {
    const meterBar = '#'.repeat(this.meter) + '_'.repeat(20 - this.meter);
    const recentWords = wordHistory.slice(0, 5).reverse();
    return {
      score: this.score,
      meter: meterBar,
      recentWords: recentWords,
    };
  }
}
