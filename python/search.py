import json
import python.textPreprocessing as textPreprocessing


# Search based on TF-IDF order
class SearchTFIDF:

    # Initialization of TF-IDF search
    def __init__(self):
        self.tf_idf_scores = []
        self.lemmatizer = textPreprocessing.Lemmatization()
        self.titles = dict()
        self.stopwords = []

    # Loads tf-idf scores for each language
    # array_of_tf_idf_language_files    - fie containing tf-idf scores to tokens
    def load_language_files(self, array_of_tf_idf_language_files):
        for language_tf_idf_file in array_of_tf_idf_language_files:
            self.tf_idf_scores.append(self.load_json_file(language_tf_idf_file))

    # Loads JSON file
    # file      - file which should be loaded
    @staticmethod
    def load_json_file(file):
        with open(file, encoding='utf-8') as loaded_file:
            return json.load(loaded_file)

    # Loads all language stopwords
    # language_array_shortenings    - shortenings of connected languages
    def load_all_language_stopwords(self, language_array_shortenings):
        stopwords = []
        stopwords_file_names_dict = self.load_json_file('stop_words/stopwords_file_paths.json')

        for language_array_shortening in stopwords_file_names_dict:
            if language_array_shortening in language_array_shortenings:
                stopwords = stopwords + self.load_json_file(stopwords_file_names_dict[language_array_shortening])

        self.stopwords = stopwords

    # Loads titles according id
    # Loads array of dicts from connection file based on base language - language_shortening
    # titles_file           - connection file with titles used as reference during search
    # language_shortening   - base language shortening in connetion file
    def load_titles_according_id(self, titles_file, language_shortening):
        titles = dict()
        array_of_dicts = self.load_json_file(titles_file)[language_shortening]

        for dictionary in array_of_dicts:
            if 'id' in dictionary and 'title' in dictionary:
                titles[str(dictionary['id'])] = dictionary['title']

        return titles

    # initialization of search based on tf-idf
    # titles_file                       - file containing titles, connection file
    # array_of_tf_idf_language_files    - array of file containing tf-idf score
    # language_array_shortenings        - array of language shortenings which are connected in titles_file
    # base_language_shortening          - base language in titles_file used to connect languages
    def initialize(self, titles_file, array_of_tf_idf_language_files, language_array_shortenings,
                   base_language_shortening):
        self.load_language_files(array_of_tf_idf_language_files)
        self.load_all_language_stopwords(language_array_shortenings)
        self.lemmatizer.all_chosen_majkas_init_for_lemmatization(language_array_shortenings)
        self.titles = self.load_titles_according_id(titles_file, base_language_shortening)

    # Does text processing
    # text          - text which should be processed
    # stopwords     - stopwords to remove from text
    def text_preprocessing(self, text, stopwords):
        return self.lemmatizer.lemmatization_and_stop_words_removal_in_array_all_majka(
            textPreprocessing.tokenize_text(text), stopwords)

    # Makes intersection between found documents
    # Only documents containing all tokens should be chosen
    # order will be given according tf-idf index descending
    # preprocessed_text     - text which was preprocessed
    def find_dictionary_docs(self, preprocessed_text):
        found_dictionary_docs = None

        for token in textPreprocessing.tokenize_text(preprocessed_text):
            help_dictionary_docs = dict()
            for score in self.tf_idf_scores:
                if token in score:
                    for doc, score_value in score[token].items():
                        if doc not in help_dictionary_docs:
                            help_dictionary_docs[doc] = score_value
                        else:
                            help_dictionary_docs[doc] = help_dictionary_docs[doc] + score_value

            if found_dictionary_docs is None:
                found_dictionary_docs = help_dictionary_docs.copy()
            else:
                found_dictionary_docs = {key: value for key, value in found_dictionary_docs.items() if
                                         key in help_dictionary_docs.keys()}

        sorted_dictionary = {key: value for key, value in
                             sorted(found_dictionary_docs.items(), key=lambda item: item[1], reverse=True)}
        return sorted_dictionary

    # Prints found titles
    # sorted_dictionary     - sorted dictionary according tf-idf value
    # mapped_titles         - mapped titles according id in base language
    # value_enable          - enables to print tf_idf value
    @staticmethod
    def print_titles(sorted_dictionary, mapped_titles, value_enable):

        for order, (record_id, score) in enumerate(sorted_dictionary.items()):
            if value_enable:
                print(str(order) + "#: " + mapped_titles[str(record_id)] + "    VALUE: " + str(score))
            else:
                print(str(order) + "#: " + mapped_titles[record_id])

    # Initializes search
    # text  - text which should be used for searching
    def search(self, text):
        preprocessed_text = self.text_preprocessing(text, self.stopwords)
        sorted_dictionaty = self.find_dictionary_docs(preprocessed_text)
        self.print_titles(sorted_dictionaty, self.titles, True)


# Provides search in content of connected language files  - it not depends on used languages
if __name__ == "__main__":
    search_tf_idf = SearchTFIDF()
    search_tf_idf.initialize('end_regex.json', ['sk_tf_idf_file.json', 'cs_tf_idf_file.json', 'en_tf_idf_file.json'],
                             ['cs', 'sk', 'en'], 'sk')
    search_tf_idf.search("Metafyzika rozumom")
    print("\nAnother 2:")
    search_tf_idf.search("clever substance causa sui")
    print("\nAnother 3:")
    search_tf_idf.search("causa sui")
    print("\nAnother 4:")
    search_tf_idf.search("zajímavá metaphysics")
