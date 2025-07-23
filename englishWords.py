from english_words import get_english_words_set
from phonimize import phonimize


word_set = get_english_words_set(['web2'], lower=True)

sorted_wordSet = sorted(word_set)

with open("data.csv", "w") as f:
    f.write("word,\n")
    for word in sorted_wordSet:
        if 3 <= len(word) <= 7:
            f.writelines(f"{word},\n")

with open("data.csv", "r") as baseFile, open("append.txt") as appendFile:
    baseLines = baseFile.readlines()
    appendLines = appendFile.readlines()