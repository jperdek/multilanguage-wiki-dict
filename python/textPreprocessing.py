from sklearn.feature_extraction.text import TfidfVectorizer

from collections import defaultdict
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk import word_tokenize
import pickle
import json
from majka import Majka
import sys



def separate_with_space(array):
    return ' '.join(array)


def to_lower_case(string):
    return string.lower()


def tokenize_text(string):
    return word_tokenize(string)


class Lemmatization():
    def __init__(self):
        self.tag_map = defaultdict(lambda: wordnet.NOUN)
        self.tag_map['J'] = wordnet.ADJ
        self.tag_map['V'] = wordnet.VERB
        self.tag_map['R'] = wordnet.ADV
        self.chosen_majkas = []

    def majka_init_for_lemmatization(self, language_shortening):
         majka_paths = self.load_majka_paths('./majka/majka_file_paths.json')

         if language_shortening not in majka_paths.keys():
             print("Unrecognized language for Majka! "+str(majka_paths))
             sys.exit(2)

         self.majka = Majka(majka_paths[language_shortening])
         self.majka.first_only = True
         self.majka.tags = False
         # self.majka.compact_tag = False

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



    def load_majka_paths(self, file):
        with open(file, encoding='utf-8') as majka_paths:
            return json.load(majka_paths)


    def lemmatization_and_stop_words_removal_from_documents(self, data_to_lemmatize, stop_words_language):
        lemmatized_data = []
        for sentence in data_to_lemmatize:
            lemmatized_words = []
            word_Lemmatized = WordNetLemmatizer()
            tokenized = word_tokenize(sentence.lower())
            # print(tokenized)
            for word, tag in pos_tag(tokenized):
                # print(word)
                if word not in stopwords.words('english') and len(word) > 2 and word.isalpha():
                    word_Final = word_Lemmatized.lemmatize(word, self.tag_map[tag[0]])
                    lemmatized_words.append(word_Final)
            lemmatized_data.append(separate_with_space(lemmatized_words))


    def lemmatization_and_stop_words_removal(self, tokenized_text, stop_words_language):
        lemmatized_data = []
        lemmatized_words = []
        word_Lemmatized = WordNetLemmatizer()

        for word, tag in pos_tag(tokenized_text):
            # print(word)
            if word not in stopwords.words(stop_words_language) and len(word) > 2 and word.isalpha():
                word_Final = word_Lemmatized.lemmatize(word, self.tag_map[tag[0]])
                lemmatized_words.append(word_Final)
        lemmatized_data.append(separate_with_space(lemmatized_words))
        #print(lemmatized_data)
        return lemmatized_data

    def lemmatization_and_stop_words_removal_not_included(self, tokenized_text, stop_words_language_file):

        with open(stop_words_language_file, encoding='utf-8') as stop_words_file:
            stop_words_from_file = json.load(stop_words_file)

        return self.lemmatization_and_stop_words_removal_in_array(tokenized_text, stop_words_from_file)

    def lemmatization_and_stop_words_removal_in_array(self, tokenized_text, stop_words_from_file):
        lemmatized_words = []

        for word, tag in pos_tag(tokenized_text):
            # print(word)
            if word not in stop_words_from_file and len(word) > 2 and word.isalpha():
                word_Final = self.majka.find(word)#word_Lemmatized.lemmatize(word, self.tag_map[tag[0]])
                if len(word_Final) > 0 :
                    lemmatized_words.append(word_Final[0]['lemma'])

        return separate_with_space(lemmatized_words)

    def lemmatization_and_stop_words_removal_in_array_all_majka(self, tokenized_text, stop_words_from_file):
        lemmatized_words = []

        for word, tag in pos_tag(tokenized_text):
            # print(word)
            if word not in stop_words_from_file and len(word) > 2 and word.isalpha():
                for majka in self.chosen_majkas:
                    word_Final = majka.find(word)#word_Lemmatized.lemmatize(word, self.tag_map[tag[0]])
                    if len(word_Final) > 0 :
                        lemmatized_words.append(word_Final[0]['lemma'])

        return separate_with_space(lemmatized_words)


def create_tfidf_vectorizer(file_name, stop_words_language):
    tf_idf_vectorizer = TfidfVectorizer(stop_words=stop_words_language, max_df=0.7)
    with open(file_name, 'wb') as tf_idf_vectorizer_file:
        pickle.dump(tf_idf_vectorizer, tf_idf_vectorizer_file, protocol=pickle.HIGHEST_PROTOCOL)
    return tf_idf_vectorizer


def vectorize_ti_idf(tfidf_vectiorizer, data_for_tfidf):
    return tfidf_vectiorizer.fit_transform(data_for_tfidf)


