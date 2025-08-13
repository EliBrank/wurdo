import { motion, AnimatePresence } from "motion/react";

type WordHistoryProps = {
  wordStrings: string[][];
};

export const WordHistory = ({ wordStrings }: WordHistoryProps) => {
  return (
    <div
      className="flex min-h-48 flex-col-reverse overflow-y-auto border bg-green-500 p-2"
    >
      <AnimatePresence initial={false}>
        {[...wordStrings].reverse().map((letters) => (
          <motion.div
            key={letters.join('')}
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
            className="flex gap-1"
          >
            {letters.map((letter, i) => (
              <div key={i} className="border px-2 py-1 text-black">
                {letter}
              </div>
            ))}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};
