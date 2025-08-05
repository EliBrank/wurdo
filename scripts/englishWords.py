import wordfreq
import re

# Get words from wordfreq
print("Loading wordfreq English word list...")
freq_dict = wordfreq.get_frequency_dict('en')
print(f"Loaded {len(freq_dict)} words from wordfreq")

# Debug: Show some sample words
sample_words = list(freq_dict.keys())[:20]
print(f"Sample words from wordfreq: {sample_words}")

# Check if 'gods' exists in the original data
print(f"Does 'gods' exist in wordfreq? {'gods' in freq_dict}")
print(f"Does 'cat' exist in wordfreq? {'cat' in freq_dict}")

# Filter words by length (3-7 characters), alphabetic only, and convert to lowercase
filtered_words = []
for word in freq_dict.keys():
    # Only include alphabetic words
    if re.match(r'^[a-zA-Z]+$', word):
        word_lower = word.lower()
        if 3 <= len(word_lower) <= 7:
            filtered_words.append(word_lower)

print(f"Filtered to {len(filtered_words)} alphabetic words with length 3-7 characters")

# Debug: Show some filtered words
if filtered_words:
    print(f"Sample filtered words: {filtered_words[:10]}")
    print(f"Does 'gods' exist in filtered words? {'gods' in filtered_words}")
else:
    print("No words passed the filter!")
    # Let's see what's happening with the regex
    test_words = ['gods', 'cat', 'dog', 'the', 'a', '123', 'abc', '🤷']
    for word in test_words:
        matches = re.match(r'^[a-zA-Z]+$', word)
        print(f"'{word}' matches regex: {matches is not None}")

# Sort words alphabetically
filtered_words.sort()

# Write to CSV (without pronunciation for now)
print("Writing words to data.csv...")
with open("data.csv", "w") as f:
    f.write("word,pronunciation\n")
    
    processed_count = 0
    for word in filtered_words:
        f.write(f"{word},\n")  # No pronunciation for now
        processed_count += 1
        
        # Progress indicator
        if processed_count % 1000 == 0:
            print(f"Processed {processed_count} words...")

print(f"✅ Successfully generated data.csv with {processed_count} words!")
print(f"📊 Word list now includes comprehensive English vocabulary from wordfreq")
print(f"🔍 This should now include words like 'gods', 'cats', 'dogs', etc.")
