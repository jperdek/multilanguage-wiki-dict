import json
from python import textPreprocessing
from python import langDictionary


# Enables searching using given word pairs obtained in Wikipedia
class FindInDictionary:

    # prepares dictionaries to use
    def __init__(self):
        self.character_trees = dict()
        self.majka_lemmatizers = dict()
        self.stop_words = dict()

    # Initialization for searching
    # array_character_file_trees    -array of character threes one for each language
    # 
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

    def get_probable_words(self, word_freq_dict):
        max = 0
        preferable_word = ""
        more_words = False

        if not isinstance(word_freq_dict, dict):
            return ""

        for word, freq in word_freq_dict.items():
            if freq > max:
                preferable_word = word
                max = freq
                more_words = False
            elif freq == max:
                more_words = True
                preferable_word = preferable_word + ", " + word

        if more_words:
            return "[ " + preferable_word + " ]"
        else:
            return preferable_word

    def find_foreign_equivalents(self, text, initial_language_shortening, dest_language_shortenings):
        results = dict()
        for language_shortening in dest_language_shortenings:
            results[language_shortening] = ""

        tokens = textPreprocessing.tokenize_text(text)
        # self.do_text_preprocessing(text, initial_language_shortening)

        for token in tokens:
            result_part_dict = self.character_trees[initial_language_shortening].find_word_more_languages(
                token, dest_language_shortenings)
            if result_part_dict is not None:
                for language_shortening, result_part in result_part_dict.items():
                    results[language_shortening] = results[language_shortening] + " " + result_part

        for language_shortening, result in results.items():
            if result != "":
                print(language_shortening + ": " + result)

    def find_foreign_equivalents_ext(self, text, initial_language_shortening, dest_language_shortenings):
        results = dict()
        for language_shortening in dest_language_shortenings:
            results[language_shortening] = ""

        tokens = textPreprocessing.tokenize_text(text)
        # self.do_text_preprocessing(text, initial_language_shortening)

        for token in tokens:
            result_part_dict = self.character_trees[initial_language_shortening].find_word_more_languages(
                token, dest_language_shortenings)
            if result_part_dict is not None:
                for language_shortening, result_parts in result_part_dict.items():
                    results[language_shortening] = results[language_shortening] + " " + \
                                                   self.get_probable_words(result_parts)

        for language_shortening, result in results.items():
            if result != "":
                print(language_shortening + ": " + result)

    def initialize_majka_lemmatizers(self, languages_array_shortenings):
        majka_lemmatizers = dict()

        for language_shortening in languages_array_shortenings:
            majka_lemmatizer = textPreprocessing.Lemmatization()
            majka_lemmatizer.majka_init_for_lemmatization(language_shortening)
            majka_lemmatizers[language_shortening] = majka_lemmatizer

        return majka_lemmatizers


if __name__ == "__main__" :
    find_in_dictionary = FindInDictionary()
    # find_in_dictionary.init(['sk_lang_char_tree.json', 'cs_lang_char_tree.json', 'en_lang_char_tree.json'],
    #                        ['sk', 'cs', 'en'])
    find_in_dictionary.init(['sk_lang_char_tree_ext.json', 'cs_lang_char_tree_ext.json', 'en_lang_char_tree_ext.json'],
                            ['sk', 'cs', 'en'])
    find_in_dictionary.find_foreign_equivalents_ext("Filozof vie vysvetliť metafyziku", 'sk', ['cs', 'en'])
    find_in_dictionary.find_foreign_equivalents_ext("Esperanto nie je jediný jazyk na svete", 'sk', ['cs', 'en'])
    find_in_dictionary.find_foreign_equivalents_ext("Metaphysics changes not only in past years", 'en', ['sk', 'cs'])
