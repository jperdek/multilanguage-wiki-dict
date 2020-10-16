import json
from python import textPreprocessing
from python import langDictionary


class FindInDictionary:

    def __init__(self):
        self.character_trees = dict()
        self.majka_lemmatizers = dict()
        self.stop_words = dict()

    def init(self, array_character_file_trees, language_array_shortenings):
        for character_file_tree in array_character_file_trees:
            language_shortening = character_file_tree.split('_')[0]
            self.character_trees[language_shortening] = langDictionary.CharacterTree()
            self.character_trees[language_shortening].load_as_json(character_file_tree, language_shortening)

        self.majka_lemmatizers = self.initialize_majka_lemmatizers(language_array_shortenings)

        stop_words_files = self.load_json_file('stop_words/stopwords_file_paths.json')
        for language_shortening in language_array_shortenings:
            self.stop_words[language_shortening] = self.load_json_file(stop_words_files[language_shortening])

    @staticmethod
    def load_json_file(lang_connection_file):
        with open(lang_connection_file, "r", encoding='utf-8') as file:
            return json.load(file)

    def do_text_preprocessing(self, text, language_shortening):
        text = self.majka_lemmatizers[language_shortening].lemmatization_and_loaded_stop_words_removal_in_array(
            textPreprocessing.tokenize_text(text), self.stop_words[language_shortening])
        print(text)
        return textPreprocessing.tokenize_text(text)


    def find_foreign_equivalents(self, text, initial_language_shortening, dest_language_shortenings):
        results = dict()
        for language_shortening in dest_language_shortenings:
            results[language_shortening] = ""

        tokens = textPreprocessing.tokenize_text(text) # self.do_text_preprocessing(text, initial_language_shortening)

        for token in tokens:
            result_part_dict = self.character_trees[initial_language_shortening].find_word_more_languages(
                token, dest_language_shortenings)
            if result_part_dict is not None:
                for language_shortening, result_part in result_part_dict.items():
                    results[language_shortening] = results[language_shortening] + " " + result_part

        for language_shortening, result in results.items():
            if result != "":
                print(language_shortening + ": " + result)


    def initialize_majka_lemmatizers(self, languages_array_shortenings):
        majka_lemmatizers = dict()

        for language_shortening in languages_array_shortenings:
            majka_lemmatizer = textPreprocessing.Lemmatization()
            majka_lemmatizer.majka_init_for_lemmatization(language_shortening)
            majka_lemmatizers[language_shortening] = majka_lemmatizer
            majka_lemmatizers[language_shortening].lemmatization_and_stop_words_removal_in_array(
                "fegyegfye", ['sd', 'sdsds'])
        return majka_lemmatizers

if __name__ == "__main__" :
    find_in_dictionary = FindInDictionary()
    #find_in_dictionary.init(['sk_lang_char_tree.json', 'cs_lang_char_tree.json', 'en_lang_char_tree.json'],
    #                        ['sk', 'cs', 'en'])
    find_in_dictionary.init(['sk_lang_char_tree1.json', 'cs_lang_char_tree1.json', 'en_lang_char_tree1.json'],
                            ['sk', 'cs', 'en'])
    find_in_dictionary.find_foreign_equivalents("Newtonov zákon všade pôsobí", 'sk', ['cs', 'en'])
    find_in_dictionary.find_foreign_equivalents("Esperanto nie je jediný jazyk na svete", 'sk', ['cs', 'en'])