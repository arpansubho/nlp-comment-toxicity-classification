import re # regular expression
import string
import spacy
from nltk.corpus import stopwords

# Precompile regex patterns
url_pattern = re.compile(r'https?://\S+|www\.\S+')
num_pattern = re.compile(r'\b\d+\b')
html_pattern = re.compile(r'<.*?>')
emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\u2600-\u26FF"          # misc symbols
    "\u2700-\u27BF"          # dingbats
    "]+", flags=re.UNICODE
)

# Load spaCy English model
nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])

# Stopwords
stop_words = set(stopwords.words('english'))

# Contraction map
contractions = {
    "isn't": "is not", "didn't": "did not", "he's": "he is", "wasn't": "was not",
    "there's": "there is", "couldn't": "could not", "won't": "will not",
    "they're": "they are", "she's": "she is", "wouldn't": "would not",
    "haven't": "have not", "that's": "that is", "you've": "you have",
    "what's": "what is", "weren't": "were not", "we're": "we are",
    "hasn't": "has not", "you'd": "you would", "shouldn't": "should not",
    "let's": "let us", "they've": "they have", "you'll": "you will",
    "i'm": "i am", "we've": "we have", "it's": "it is", "don't": "do not",
    "that´s": "that is", "i´m": "i am", "it’s": "it is", "she´s": "she is",
    "he’s": "he is", "i’m": "i am", "i’d": "i did"
}

def expand_contractions(text):
    for contraction, expanded in contractions.items():
        text = re.sub(contraction, expanded, text)
    return text

def preprocess_texts(texts):
    cleaned_texts = []
    for text in texts:
        # Lowercase
        text = text.lower()
        # Remove URLs, numbers, HTML, emojis
        text = re.sub(url_pattern, '', text)
        text = re.sub(num_pattern, '', text)
        text = re.sub(html_pattern, '', text)
        text = re.sub(emoji_pattern, '', text)
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        # Expand contractions
        text = expand_contractions(text)

        # Lemmatization
        doc = nlp(text)
        tokens = [
            token.lemma_.lower() for token in doc
            if token.is_alpha and not token.is_stop and len(token.text) > 2
        ]
        cleaned_texts.append(" ".join(tokens))
    return cleaned_texts