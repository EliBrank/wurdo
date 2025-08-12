import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "motion/react";

type WordInputProps = {
  typedWord: string;
  animWord: string | null;
  animDelay: number;
  onSubmit: () => void;
};

export const WordInput = ({
  typedWord,
  animWord,
  animDelay,
  onSubmit
} : WordInputProps) => {
  const [flyWord, setFlyWord] = useState<string | null>(null);

  // This activates animation whenever animWord (submitted word) changes
  useEffect(() => {
    if (animWord) {
      setFlyWord(animWord);
      const timer = setTimeout(() => setFlyWord(null), animDelay);
      return () => clearTimeout(timer);
    }
  }, [animWord, animDelay]);

  return (
    <div className="fit-content mx-auto mb-4 flex max-w-100 items-end justify-center gap-2 px-8">
      <span className="flex flex-1 border-b-2 border-primary-dark text-xl tracking-wider text-primary-dark">
        {typedWord}
      </span>
      <button className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-dark text-2xl font-black text-default-light">🡒</button>
    </div>
  );
}
