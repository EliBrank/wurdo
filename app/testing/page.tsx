"use client";

import { useState } from "react";
import { getWordData, updateWordData } from "@/lib/actions"; // your server actions
import { WordScore } from "@/lib/definitions";

export default function WordEditor() {
  const [word, setWord] = useState("");
  const [data, setData] = useState<any>(null);
  const [form, setForm] = useState({
    oneLetterOff: "",
    anagram: "",
    rhyme: "",
  });

  const fetch = async () => {
    const result = await getWordData(word);
    setData(result);
  };

  const update = async () => {
    const updateData = {
      pronunciation: "", // Optional, fallback to ARPAbet in server
      oneLetterOff: form.oneLetterOff
        ? [{ word: form.oneLetterOff, score: 1 }]
        : [],
      anagram: form.anagram ? [{ word: form.anagram, score: 1 }] : [],
      rhyme: form.rhyme ? [{ word: form.rhyme, score: 1 }] : [],
    };

    await updateWordData(word, updateData);
    setForm({ oneLetterOff: "", anagram: "", rhyme: "" });
    fetch(); // Refresh data after update
  };

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h2 className="text-xl font-bold mb-4">Word Lookup / Update</h2>

      <input
        className="border p-2 mb-2 w-full"
        placeholder="Enter a word"
        value={word}
        onChange={(e) => setWord(e.target.value)}
      />
      <div className="flex gap-2 mb-4">
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded"
          onClick={fetch}
        >
          Fetch
        </button>
        <button
          className="bg-green-600 text-white px-4 py-2 rounded"
          onClick={update}
        >
          Update
        </button>
      </div>

      {/* Update form */}
      <div className="space-y-2">
        <input
          className="border p-2 w-full"
          placeholder="Add to oneLetterOff"
          value={form.oneLetterOff}
          onChange={(e) => setForm({ ...form, oneLetterOff: e.target.value })}
        />
        <input
          className="border p-2 w-full"
          placeholder="Add to anagram"
          value={form.anagram}
          onChange={(e) => setForm({ ...form, anagram: e.target.value })}
        />
        <input
          className="border p-2 w-full"
          placeholder="Add to rhyme"
          value={form.rhyme}
          onChange={(e) => setForm({ ...form, rhyme: e.target.value })}
        />
      </div>

      {/* Show results */}
      {data && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-2">Word Data</h3>
          <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
