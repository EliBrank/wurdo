from english_words import get_english_words_set
from g2p_en import G2p

# Get and sort words
word_set = get_english_words_set(['web2'], lower=True)
filtered_words = [word for word in sorted(word_set) if 3 <= len(word) <= 7]

# Initialize G2P converter
g2p = G2p()

# Write to a single CSV
with open("data.csv", "w") as f:
    f.write("word,pronunciation\n")
    for word in filtered_words:
        phonemes = g2p(word)
        phoneme_str = " ".join(phonemes)  # Convert list to space-separated string
        f.write(f"{word},{phoneme_str}\n")
