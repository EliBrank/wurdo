type WordInputProps = {
  typedWord: string;
  onSubmit: () => void;
};

export const WordInput = ({ typedWord, onSubmit }: WordInputProps) => {
  return (
    <div className="fit-content mx-auto mt-24 mb-4 flex max-w-100 items-end justify-center gap-2 px-8">
      <span className="flex flex-1 border-b-2 border-primary-dark text-xl tracking-wider text-primary-dark">
        {typedWord}
      </span>
      <button
        className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-dark text-2xl font-black text-default-light"
        onClick={onSubmit}
      >
        🡒
      </button>
    </div>
  );
};
