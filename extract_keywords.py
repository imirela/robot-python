import re
from collections import Counter

# Citim conținutul din data.txt
with open("data.txt", "r", encoding="utf-8") as file:
    text = file.read().lower()

# Eliminăm semnele de punctuație și împărțim textul în cuvinte
words = re.findall(r'\b\w+\b', text)

# Numărăm aparițiile fiecărui cuvânt
word_counts = Counter(words)

# Filtrăm doar cuvintele care apar de cel puțin 2 ori
common_words = {word for word, count in word_counts.items() if count >= 2}

# Salvăm lista de cuvinte într-un fișier
with open("excluded_keywords.txt", "w", encoding="utf-8") as file:
    file.write("\n".join(sorted(common_words)))

print(f"Am salvat {len(common_words)} cuvinte în excluded_keywords.txt")
