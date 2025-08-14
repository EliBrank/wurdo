import { motion, AnimatePresence } from "motion/react";
import { WordHistoryTile } from "./WordHistoryTile";

type WordHistoryProps = {
  words: string[];
};

export const WordHistory = ({ words }: WordHistoryProps) => {
  const wordStrings = words.map((word) => {
    return word.split("");
  });

  return (
    <div className="relative h-150">
      <div className="flex max-h-[90vh] min-h-24 flex-col-reverse overflow-y-auto border px-16 py-2">
        <AnimatePresence initial={false}>
          {[...wordStrings].reverse().map((letters, index) => {
            const isNewest = index === 0;

            return (
              <motion.div
                key={letters.join("")}
                initial={{ y: 50, opacity: 0 }}
                animate={{ y: 0, opacity: isNewest ? 1 : 0.4 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.4 }}
                className="my-2 grid w-full grid-cols-7 gap-1"
              >
                {letters.map((letter, i) => (
                  <div
                    key={i}
                    className="flex flex-1 items-center justify-center"
                  >
                    <WordHistoryTile label={letter} />
                  </div>
                ))}
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      <div className="absolute top-0 left-0 h-4 w-full bg-gradient-to-b from-primary-light to-transparent"></div>
      <div className="absolute bottom-0 left-0 h-4 w-full bg-gradient-to-t from-primary-light to-transparent"></div>
    </div>
  );
};
