const scoreIdeas = [
  [10, Math.floor(((10 - 50) / 10))],
  [15, Math.floor(((15 - 50) / 10))],
  [20, Math.floor(((20 - 50) / 10))],
  [25, Math.floor(((25 - 50) / 10))],
  [30, Math.floor(((30 - 50) / 10))],
  [35, Math.floor(((35 - 50) / 10))],
  [40, Math.floor(((40 - 50) / 10))],
  [45, Math.floor(((45 - 50) / 10))],
  [50, Math.floor(((50 - 50) / 10))],
]

scoreIdeas.forEach(([scoreChange, meterChange]) => {
  console.log('score change', scoreChange);
  console.log('meter change:', meterChange);
  console.log();
});
