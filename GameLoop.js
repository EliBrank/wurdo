import * as readline from 'readline';
import { pathToFileURL } from 'url';
import GameState from './GameState';
import CommandHandler from './CommandHandler';

class GameLoop {
  constructor(initialWord) {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: '> '
    });

    this.gameState = new GameState(initialWord);
    this.commandHandler = new CommandHandler(this.gameState, this);
    this.isRunning = true

    this.setupEventHandlers();
  }

  setupEventHandlers() {
    // Logic for game loop
    this.rl.on('line', (input) => {
      const shouldContinue = this.commandHandler.handleCommand(input);
      if (shouldContinue) {
        this.gameLoop();
      } else {
        this.isRunning = false;
        this.rl.close();
      }
    });

    this.rl.on('close', () => {
      console.log('\nEnd game. Exiting...');
      process.exit(0);
    });

    process.on('SIGNINT', () => {
      console.log('\nGame interrupted. Exiting...');
      process.exit(0);
    });
  }

  start() {
    console.log('Welcome to Wurdo!');
    this.commandHandler.showGameState();
    this.gameLoop();
  }

}



const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

if (import.meta.url === pathToFileURL(process.argv[1].href)) {
  // module called directly
}

rl.question()
