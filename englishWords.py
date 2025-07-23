from english_words import get_english_words_set

word_set = get_english_words_set(['web2'], lower=True)

sorted_wordSet = sorted(word_set)

with open("data.json", "w") as f:
    for word in sorted_wordSet:
        if len(word) >= 3 & len(word) <= 7:
            f.writelines(f"{word}\n")
        else:
            break
