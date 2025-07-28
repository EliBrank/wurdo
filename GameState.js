export default class GameState {
  constructor(initialWord) {
    this.score = 0;
    this.meter = 20;
    this.currentWord = initialWord;
    this.wordHistory = [initialWord];
  }

  getStatus() {
    // const meterValue = Math.max(0, Math.min(20, this.meter));
    const meterBar = '#'.repeat(this.meter) + '_'.repeat(20 - this.meter);
    const recentWords = this.wordHistory.slice(0, 5).reverse();
    // console.log('TESTING - meterBar:', meterBar);
    return {
      score: this.score,
      meterBar: meterBar,
      recentWords: recentWords,
    };
  }
}
