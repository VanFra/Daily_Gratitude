import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# Make sure you have these dependencies
nltk.download('punkt')
# Original gratitude list
gratitude_words = [
    "thankfulness", "appreciation", "recognition", "gratefulness", "obligation", 
    "indebtedness", "praise", "acknowledgment", "respect", "thanksgiving", 
    "gratitude", "homage", "admiration", "debt of gratitude", "thanks",
    "thankful", "appreciative", "obliged", "indebted", "beholden", "pleased", 
    "thanking", "acknowledging", "grateful-hearted", "appreciating", "touched", 
    "obligated", "in debt", "honored", "grateful-minded",
    "value", "acknowledge", "respect", "admire", "esteem", "recognize", 
    "be grateful for", "be thankful for", "cherish", "reverence", "prize", 
    "treasure", "savor", "delight in", "be conscious of",
    "feel obliged", "be thankful for", "feel indebted", "give thanks", "express gratitude", 
    "owe thanks", "be in one's debt", "owe a debt of gratitude", "count one's blessings", 
    "show appreciation", "extend gratitude", "pay tribute", "feel indebted to", 
    "gratefully accept", "thank someone profusely"
]

# Initialize the stemmer
stemmer = PorterStemmer()

# Tokenize and stem the words
tokenized_stemmed_words = []

for phrase in gratitude_words:
    # Tokenize the phrase (handle multi-word phrases)
    tokens = word_tokenize(phrase)
    # Stem each token and add to the list
    for token in tokens:
        stemmed_token = stemmer.stem(token.lower())  # Convert to lower case and stem
        tokenized_stemmed_words.append(stemmed_token)

# Remove duplicates (if you don't want repeated tokens)
tokenized_stemmed_words = list(set(tokenized_stemmed_words))

# Print the result
print(tokenized_stemmed_words)