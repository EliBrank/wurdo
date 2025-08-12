/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useState } from "react";
import { getWordData, updateWordData, createWordEntry } from "@/lib/actions";
import { FullWordData, PartialUpdateData } from "@/lib/definitions";
import { RhymeMicro } from "@/lib/microservices";

export default function WordEditor() {
  // State for the search input field
  const [word, setWord] = useState<string>("");

  // State to hold the word currently being displayed or edited
  const [activeWord, setActiveWord] = useState<string>("");

  // State for the fetched data from the database. `null` indicates it doesn't exist.
  const [data, setData] = useState<FullWordData | null>(null);

  // A single state object to manage all form fields for simplicity
  const [formData, setFormData] = useState({
    pronunciation: "",
    newOloWord: "",
    newAnagramWord: "",
    newRhymeWord: "",
  });

  // UI state for loading, errors, and success messages
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  /**
   * Handles changes for all form inputs to update the `formData` state.
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  /**
   * Fetches word data when the user clicks the "Search" button.
   */
  const handleSearch = async () => {
    if (!word.trim()) {
      setError("Please enter a word to search.");
      return;
    }
    setIsLoading(true);
    setError(null);
    setMessage(null);
    setData(null); // Clear previous results before new search

    try {
      const result = await getWordData(word);
      setActiveWord(word); // Lock in the word being edited

      if (result) {
        // Word was found
        setData(result);
        setFormData({
          pronunciation: result.pronunciation || "",
          newOloWord: "",
          newAnagramWord: "",
          newRhymeWord: "",
        });
        setMessage(`Data loaded for "${word}". You can now edit it.`);
      } else {
        // Word was not found, prepare for creation
        setData(null);
        setFormData({
          pronunciation: "",
          newOloWord: "",
          newAnagramWord: "",
          newRhymeWord: "",
        });
        setMessage(`Word "${word}" not found. Fill out the form to create it.`);
      }
    } catch (e) {
      console.error("Error fetching word:", e);
      const error = e as Error;
      setError(`Failed to fetch data: ${error.message || "Unknown error"}`);
      setActiveWord(""); // Reset on error
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Saves changes. Handles both creating a new word and updating an existing one.
   */
  const handleSave = async () => {
    if (!activeWord) {
      setError("Please search for a word before saving.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setMessage(null);

    // Prepare the data payload for the backend
    const updateData: PartialUpdateData = {};
    if (formData.pronunciation.trim()) {
      updateData.pronunciation = formData.pronunciation.trim();
    }
    if (formData.newOloWord.trim()) {
      updateData.oneLetterOff = { [formData.newOloWord.trim()]: 1 };
    }
    if (formData.newAnagramWord.trim()) {
      updateData.anagram = { [formData.newAnagramWord.trim()]: 1 };
    }
    if (formData.newRhymeWord.trim()) {
      updateData.rhyme = { [formData.newRhymeWord.trim()]: 1 };
    }

    if (Object.keys(updateData).length === 0) {
      setMessage("No new data to save.");
      setIsLoading(false);
      return;
    }

    try {
      let success = false;
      const isCreating = data === null;

      if (isCreating) {
        // --- CREATE LOGIC ---
        success = await createWordEntry(activeWord);
        const remainingUpdates = { ...updateData };
        delete remainingUpdates.pronunciation;
        if (success && Object.keys(remainingUpdates).length > 0) {
          success = await updateWordData(activeWord, remainingUpdates);
        }
      } else {
        // --- UPDATE LOGIC ---
        success = await updateWordData(activeWord, updateData);
      }

      if (success) {
        setMessage(`Successfully saved changes for "${activeWord}"!`);
        // Re-run search with the original word to refresh data and clear form
        await handleSearch();
      } else {
        setError(`Failed to save changes for "${activeWord}".`);
      }
    } catch (e) {
      console.error("Error saving word:", e);
      const error = e as Error;
      setError(`Failed to save data: ${error.message || "Unknown error"}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto mt-8 max-w-xl rounded-lg bg-white p-4 shadow-md">
      <h2 className="mb-4 text-center text-2xl font-bold text-gray-800">
        Word Data Manager
      </h2>

      {/* --- 1. Search Section --- */}
      <div className="mb-4">
        <label
          htmlFor="wordInput"
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          Search for a Word
        </label>
        <div className="flex items-center space-x-2">
          <input
            id="wordInput"
            className="w-full rounded-md border border-gray-300 p-2 focus:border-blue-500 focus:ring-blue-500"
            placeholder="e.g., 'apple', 'tiger'"
            value={word}
            onChange={(e) => setWord(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <button
            className="flex-shrink-0 rounded-md bg-blue-600 px-4 py-2 text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
            onClick={handleSearch}
            disabled={isLoading || !word.trim()}
          >
            {isLoading ? "Searching..." : "Search"}
          </button>
        </div>
      </div>

      {/* --- Status Messages --- */}
      <div className="mb-4 min-h-[24px] text-center">
        {isLoading && !message && (
          <p className="text-gray-500">Processing...</p>
        )}
        {error && <p className="text-red-600">{error}</p>}
        {message && !error && (
          <div>
            <p className="text-green-600">{message}</p>
            <span>{JSON.stringify(data)}</span>
          </div>
        )}
      </div>

      {/* --- 2. Editor Form (shows after search) --- */}
      {activeWord && !isLoading && (
        <div className="mt-4 border-t border-gray-200 pt-4">
          <h3 className="mb-3 text-lg font-semibold">
            {data
              ? `Editing Data for "${activeWord}"`
              : `Create New Entry for "${activeWord}"`}
          </h3>

          <button
            className="mb-4 w-full rounded-md bg-green-600 px-4 py-2 text-white transition-colors hover:bg-green-700 disabled:opacity-50"
            onClick={handleSave}
            disabled={isLoading}
          >
            {data ? "Save Changes" : "Create Word"}
          </button>

          <div className="space-y-4">
            {/* Pronunciation */}
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Pronunciation
              </label>
              <input
                name="pronunciation"
                type="text"
                className="mt-1 w-full rounded-md border p-2"
                placeholder="Enter ARPABET pronunciation"
                value={formData.pronunciation}
                onChange={handleInputChange}
              />
            </div>

            {/* One Letter Off (OLO) */}
            <div>
              <label className="block text-sm font-medium text-gray-700">
                One Letter Off (OLO)
              </label>
              {data?.olo && Object.keys(data.olo).length > 0 && (
                <ul className="mt-1 list-inside list-disc rounded bg-gray-50 p-2 text-sm text-gray-600">
                  {Object.entries(data.olo).map(([w, s]) => (
                    <li key={w}>
                      {w} (Score: {s})
                    </li>
                  ))}
                </ul>
              )}
              <input
                name="newOloWord"
                className="mt-2 w-full rounded-md border p-2"
                placeholder="Add new OLO word"
                value={formData.newOloWord}
                onChange={handleInputChange}
              />
            </div>

            {/* Anagrams */}
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Anagrams
              </label>
              {data?.ana && Object.keys(data.ana).length > 0 && (
                <ul className="mt-1 list-inside list-disc rounded bg-gray-50 p-2 text-sm text-gray-600">
                  {Object.entries(data.ana).map(([w, s]) => (
                    <li key={w}>
                      {w} (Score: {s})
                    </li>
                  ))}
                </ul>
              )}
              <input
                name="newAnagramWord"
                className="mt-2 w-full rounded-md border p-2"
                placeholder="Add new Anagram"
                value={formData.newAnagramWord}
                onChange={handleInputChange}
              />
            </div>

            {/* Rhymes */}
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Rhymes
              </label>
              <form action={RhymeMicro}>
                <input
                  name="newRhymeWord"
                  className="mt-2 w-full rounded-md border p-2"
                  placeholder="Add new Rhyme"
                  value={formData.newRhymeWord}
                  onChange={handleInputChange}
                />
                <input
                  name="word"
                  type="hidden"
                  className="mt-2 w-full rounded-md border p-2"
                  placeholder="Add new Rhyme"
                  value={activeWord}
                />
                <button type="submit">Click here to test</button>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
