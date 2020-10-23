from sklearn.feature_extraction.text import TfidfVectorizer

from collections import defaultdict
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk import word_tokenize
import pickle
import json
from majka import Majka
import sys


# Separate array with spaces
def separate_with_space(array):
    return ' '.join(array)


# Converts string to lower case
def to_lower_case(string):
    return string.lower()


# Tokenize text to tokens (strings divided by white character)
def tokenize_text(string):
    return word_tokenize(string)


# Lemmatizer class to provide lemmatization base on Czech project Majka
class Lemmatization:

    # Initialization of lemmatizer
    def __init__(self):
        self.tag_map = defaultdict(lambda: wordnet.NOUN)
        self.tag_map['J'] = wordnet.ADJ
        self.tag_map['V'] = wordnet.VERB
        self.tag_map['R'] = wordnet.ADV
        self.chosen_majkas = []
        self.majka = None

    # Initializes majka for lemmatization
    # language_shortening       - base language in which lemmatization should be provided
    def majka_init_for_lemmatization(self, language_shortening):
        majka_paths = self.load_majka_paths('./majka/majka_file_paths.json')

        if language_shortening not in majka_paths.keys():
            print("Unrecognized language for Majka! "+str(majka_paths))
            sys.exit(2)

        self.majka = Majka(majka_paths[language_shortening])
        self.majka.first_only = True
        self.majka.tags = False

    # Initializes array of majka instances for given languages
    # language_shortenings      - languages to be lammatized by majka
    def all_chosen_majkas_init_for_lemmatization(self, language_shortenings):
        majka_paths = self.load_majka_paths('./majka/majka_file_paths.json')

        for language_shortening in language_shortenings:
            if language_shortening not in majka_paths.keys():
                print("Unrecognized language for Majka! " + str(majka_paths))
                sys.exit(2)

            majka = Majka(majka_paths[language_shortening])
            majka.first_only = True
            majka.tags = False
            self.chosen_majkas.append(majka)

    # Loads majka configuration JSON file
    # file      - file to be loaded
    @staticmethod
    def load_majka_paths(file):
        with open(file, encoding='utf-8') as majka_paths:
            return json.load(majka_paths)

    # Lemmatize given data, use WordNetLemmatizer - NOT USED because of language restrictions of WordNetLemmatizer
    # data_to_lemmatize         - data which should be lemmatized
    def lemmatization_and_stop_words_removal_from_documents(self, data_to_lemmatize):
        lemmatized_data = []
        for sentence in data_to_lemmatize:
            lemmatized_words = []
            word_lemmatized = WordNetLemmatizer()
            tokenized = word_tokenize(sentence.lower())

            for word, tag in pos_tag(tokenized):

                if word not in stopwords.words('english') and len(word) > 2 and word.isalpha():
                    word_final = word_lemmatized.lemmatize(word, self.tag_map[tag[0]])
                    lemmatized_words.append(word_final)
            lemmatized_data.append(separate_with_space(lemmatized_words))

    # Lemmatization using WordNet lemmatizer - not used because of language restrictions
    def lemmatization_and_stop_words_removal(self, tokenized_text, stop_words_language):
        lemmatized_data = []
        lemmatized_words = []
        word_lemmatized = WordNetLemmatizer()

        for word, tag in pos_tag(tokenized_text):
            # print(word)
            if word not in stopwords.words(stop_words_language) and len(word) > 2 and word.isalpha():
                word_final = word_lemmatized.lemmatize(word, self.tag_map[tag[0]])
                lemmatized_words.append(word_final)
        lemmatized_data.append(separate_with_space(lemmatized_words))
        # print(lemmatized_data)
        return lemmatized_data

    # Lemmatization with loading stop words from file before lemmatization
    # tokenized_text            - text which is tokenize and prepared for lemmatization
    # stop_words_language_file  - file name which contains  stop words
    def lemmatization_and_stop_words_removal_not_included(self, tokenized_text, stop_words_language_file):

        with open(stop_words_language_file, encoding='utf-8') as stop_words_file:
            stop_words_from_file = json.load(stop_words_file)

        return self.lemmatization_and_stop_words_removal_in_array(tokenized_text, stop_words_from_file)

    # tokenized_text            - text which is tokenize and prepared for lemmatization
    # stop_words_language_file  - file name which contains  stop words
    def lemmatization_and_stop_words_removal_in_array(self, tokenized_text, stop_words_from_file):
        lemmatized_words = []

        for word, tag in pos_tag(tokenized_text):
            # print(word)
            if word not in stop_words_from_file and len(word) > 2 and word.isalpha():
                word_final = self.majka.find(word)  # word_Lemmatized.lemmatize(word, self.tag_map[tag[0]])
                if len(word_final) > 0:
                    lemmatized_words.append(word_final[0]['lemma'])

        return separate_with_space(lemmatized_words)

    # tokenized_text            - text which is tokenize and prepared for lemmatization
    # stop_words_language_file  - file name which contains  stop words
    def lemmatization_and_stop_words_removal_in_array_all_majka(self, tokenized_text, stop_words_from_file):
        lemmatized_words = []

        for word, tag in pos_tag(tokenized_text):
            # print(word)
            if word not in stop_words_from_file and len(word) > 2 and word.isalpha():
                for majka in self.chosen_majkas:
                    word_final = majka.find(word)  # word_Lemmatized.lemmatize(word, self.tag_map[tag[0]])
                    if len(word_final) > 0:
                        lemmatized_words.append(word_final[0]['lemma'])

        return separate_with_space(lemmatized_words)

    # tokenized_text            - text which is tokenize and prepared for lemmatization
    # stop_words                - stop words array in language of tokenized text
    def lemmatization_and_loaded_stop_words_removal_in_array(self, tokenized_text, stop_words):
        lemmatized_words = []

        for word, tag in pos_tag(tokenized_text):
            if word not in stop_words and len(word) > 2 and word.isalpha():
                word_final = self.majka.find(word)  # word_Lemmatized.lemmatize(word, self.tag_map[tag[0]])

                if len(word_final) > 0:
                    lemmatized_words.append(word_final[0]['lemma'])

        return separate_with_space(lemmatized_words)


# Creates tfidf vectorized - NOT USED METHOD
# file_name             - file name to store tfidf vectorized instance
# stop_words_language   - language containing stop words
def create_tfidf_vectorizer(file_name, stop_words_language):
    tf_idf_vectorizer = TfidfVectorizer(stop_words=stop_words_language, max_df=0.7)
    with open(file_name, 'wb') as tf_idf_vectorizer_file:
        pickle.dump(tf_idf_vectorizer, tf_idf_vectorizer_file, protocol=pickle.HIGHEST_PROTOCOL)
    return tf_idf_vectorizer


# Vectorizes using tf idf
# tfidf_vectorizer      - instance of tf-idf vectorizer
# data_for_tfidf        - data which should be vectorized by tf-idf
def vectorize_ti_idf(tfidf_vectiorizer, data_for_tfidf):
    return tfidf_vectiorizer.fit_transform(data_for_tfidf)
