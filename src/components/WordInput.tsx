type WordInputProps = {
  typedWord: string;
};

export const WordInput = ({
  typedWord
} : WordInputProps) => {
  return (
    <div className="flex justify-center items-end gap-2 mx-auto fit-content mb-4 px-8 max-w-100">
      <span className="border-b-2 border-primary-dark text-primary-dark text-xl flex flex-1 tracking-wider">
        {typedWord}
      </span>
      <button className="flex justify-center items-center h-8 w-8 rounded-full bg-primary-dark text-2xl text-default-light font-black">🡒</button>
    </div>
  );
}
