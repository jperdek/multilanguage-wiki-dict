from googletrans import Translator
from python import textPreprocessing
import json

# Parse character tree to obtain words and their translation
# Some statistics then will be count
class CharacterTreeTranslator:

    # Initialisation of character tree translator
    # sets base language and character tree
    # character_tree_json_file -   character tree json file
    # base_language -              base language of character tree
    def __init__(self, character_tree_json_file, base_language):
        self.tree_language_shortening = "sk"
        self.root_node = None
        self.translator = Translator()
        self.base_language = base_language
        self.statistics = dict()
        self.load_as_json(character_tree_json_file, base_language)
        self.stop_words = dict()
        self.majka_lemmatizers = dict()

    # Initialize majka lemmatizers
    # language_array_shortenings -   array with language shortenings which are suitable for translation
    @staticmethod
    def initialize_majka_lemmatizers(languages_array_shortenings):
        majka_lemmatizers = dict()

        for language_shortening in languages_array_shortenings:
            majka_lemmatizer = textPreprocessing.Lemmatization()
            majka_lemmatizer.majka_init_for_lemmatization(language_shortening)
            majka_lemmatizers[language_shortening] = majka_lemmatizer

        return majka_lemmatizers

    # Initialises structures for collecting statistic information
    # language_array_shortenings -   array with language shortenings which are suitable for translation
    def prepare_statistic_structures(self, language_array_shortenings):
        self.statistics = dict()
        self.statistics['positive'] = dict()
        self.statistics['negative'] = dict()
        self.statistics['missed'] = dict()

        for language_shortening in language_array_shortenings:
            self.statistics['positive'][language_shortening] = 0
            self.statistics['negative'][language_shortening] = 0
            self.statistics['missed'][language_shortening] = 0

        return self.statistics

    # Print all collected statistical information
    # language_array_shortenings -   array with language shortenings which are suitable for translation
    def print_statistics(self, language_array_shortenings):
        for language_shortening in language_array_shortenings:
            print("Number good for " + language_shortening + " is: " +
                  str(self.statistics['positive'][language_shortening]))
            print("Number bad for " + language_shortening + " is: " +
                  str(self.statistics['negative'][language_shortening]))
            print("Accuracy: " + str(self.statistics['positive'][language_shortening] /
                  (self.statistics['positive'][language_shortening]
                   + self.statistics['negative'][language_shortening])))
            print("Missed: " + str(self.statistics['missed'][language_shortening]))

    # Manages parsing and collecting of statistical data
    # language_array_shortenings -   array with language shortenings which are suitable for translation
    def get_translation_and_statistics_parse(self, language_array_shortenings):
        lifo_stack = []
        self.prepare_statistic_structures(language_array_shortenings)

        self.parse(lifo_stack, self.root_node, language_array_shortenings)

        self.print_statistics(language_array_shortenings)

    # Loads stop words
    # language_array_shortenings -   array with language shortenings which are suitable for translation
    def load_stop_words(self, language_array_shortenings):
        stop_words_files = self.load_json_file('stop_words/stopwords_file_paths.json')
        for language_shortening in language_array_shortenings:
            self.stop_words[language_shortening] = self.load_json_file(stop_words_files[language_shortening])

    # Manages parsing and collecting of statistical data - uese lemmatizer
    # language_array_shortenings -   array with language shortenings which are suitable for translation
    def get_translation_and_statistics_parse_lemmatizer(self, language_array_shortenings):
        lifo_stack = []
        self.majka_lemmatizers = self.initialize_majka_lemmatizers(language_array_shortenings)
        self.load_stop_words(language_array_shortenings)
        self.prepare_statistic_structures(language_array_shortenings)

        self.parse_lemmatizer(lifo_stack, self.root_node, language_array_shortenings)

        self.print_statistics(language_array_shortenings)

    # Parsing of character tree
    # lifo_stack -        lifo stack which should be used for character retrieval
    # dictionary_base -   dictionary with characters - child node of some node
    # language_array_shortenings -   array with language shortenings which are suitable for translation
    def parse(self, lifo_stack, dictionary_base, language_array_shortenings):

        for character, dictionary in dictionary_base.items():
            if character in language_array_shortenings:
                # print("lang: " + character + " " + dictionary )
                word = ''.join(lifo_stack)
                translation = self.translator.translate(dictionary, src=character, dest=self.base_language)
                # print(translation.text + " " + word)

                if translation.text.lower() != word.lower():
                    self.statistics['negative'][character] = self.statistics['negative'][character] + 1
                else:
                    self.statistics['positive'][character] = self.statistics['positive'][character] + 1
                # print(word + " " + dictionary)
            else:
                lifo_stack.append(character)
                self.parse(lifo_stack, dictionary, language_array_shortenings)
                lifo_stack.pop()

    # Parsing of character tree with use of lemmatizer
    # lifo_stack -        lifo stack which should be used for character retrieval
    # dictionary_base -   dictionary with characters - child node of some node
    # language_array_shortenings -   array with language shortenings which are suitable for translation
    def parse_lemmatizer(self, lifo_stack, dictionary_base, language_array_shortenings):

        for character, dictionary in dictionary_base.items():
            if character in language_array_shortenings:
                # print("lang: " + character + " " + dictionary )
                word = ''.join(lifo_stack)

                translation = self.translator.translate(dictionary, src=character, dest=self.base_language)
                # print(translation.text + " " + word)
                translation_text = self.majka_lemmatizers[character].\
                    lemmatization_and_loaded_stop_words_removal_in_array(
                    textPreprocessing.tokenize_text(translation.text), self.stop_words[character]).lower()
                word_text = self.majka_lemmatizers[
                    character].lemmatization_and_loaded_stop_words_removal_in_array(
                    textPreprocessing.tokenize_text(word), self.stop_words[character]).lower()

                if translation_text == "" or word_text == "":
                    self.statistics['missed'][character] = self.statistics['missed'][character] + 1
                    continue

                print(translation_text + " " + word_text)

                if translation_text != word_text:
                    self.statistics['negative'][character] = self.statistics['negative'][character] + 1
                else:
                    self.statistics['positive'][character] = self.statistics['positive'][character] + 1
                # print(word + " " + dictionary)
            else:
                lifo_stack.append(character)
                self.parse_lemmatizer(lifo_stack, dictionary, language_array_shortenings)
                lifo_stack.pop()

    # Parsing of character tree with use of lemmatizer
        # lifo_stack -        lifo stack which should be used for character retrieval
    # dictionary_base -   dictionary with characters - child node of some node
    # language_array_shortenings -   array with language shortenings which are suitable for translation
    def parse_lemmatizer_ext(self, lifo_stack, dictionary_base, language_array_shortenings):

        for character, dictionary in dictionary_base.items():
            if character in language_array_shortenings:
                # print("lang: " + character + " " + dictionary )
                word = ''.join(lifo_stack)
                word_text = self.majka_lemmatizers[
                    character].lemmatization_and_loaded_stop_words_removal_in_array(
                    textPreprocessing.tokenize_text(word), self.stop_words[character]).lower()

                if word_text == "":
                    self.statistics['missed'][character] = self.statistics['missed'][character] + 1
                    continue

                max = 0
                array_of_equal = list()
                for foreign_word, frequency in dictionary.items():
                    if frequency > max:
                        max = frequency
                        array_of_equal = list()
                        array_of_equal.append(foreign_word)
                    elif frequency == max:
                        array_of_equal.append(foreign_word)

                missed = True
                translation_text = ""
                if array_of_equal is not None:
                    for found_word in array_of_equal:
                        if found_word is None:
                            continue
                        # print(character)
                        # print(str(frequency) + " " + str(found_word))

                        translation = self.translator.translate(found_word, src=character, dest=self.base_language)
                        # print(translation.text + " " + word)
                        translation_text = self.majka_lemmatizers[character]. \
                            lemmatization_and_loaded_stop_words_removal_in_array(
                            textPreprocessing.tokenize_text(translation.text), self.stop_words[character]).lower()
                        if missed and (translation_text == "" or word_text == ""):
                            continue
                        if translation_text == word_text:
                            break
                        else:
                            missed = False

                if missed and (translation_text == "" or word_text == ""):
                    self.statistics['missed'][character] = self.statistics['missed'][character] + 1
                    continue

                print(translation_text + " " + word_text)

                if translation_text != word_text:
                    self.statistics['negative'][character] = self.statistics['negative'][character] + 1
                else:
                    self.statistics['positive'][character] = self.statistics['positive'][character] + 1
                    # print(word + " " + dictionary)
            else:
                lifo_stack.append(character)
                self.parse_lemmatizer_ext(lifo_stack, dictionary, language_array_shortenings)
                lifo_stack.pop()

    # Parsing of character tree with use of lemmatizer
    # lifo_stack -        lifo stack which should be used for character retrieval
    # dictionary_base -   dictionary with characters - child node of some node
    # language_array_shortenings -   array with language shortenings which are suitable for translation
    # min_frequency -       minimal frequency of translation
    def parse_lemmatizer_ext_min(self, lifo_stack, dictionary_base, language_array_shortenings, min_frequency):

        for character, dictionary in dictionary_base.items():
            if character in language_array_shortenings:
                # print("lang: " + character + " " + dictionary )
                word = ''.join(lifo_stack)
                word_text = self.majka_lemmatizers[
                    character].lemmatization_and_loaded_stop_words_removal_in_array(
                    textPreprocessing.tokenize_text(word), self.stop_words[character]).lower()

                if word_text == "":
                    self.statistics['missed'][character] = self.statistics['missed'][character] + 1
                    continue

                max = 0
                array_of_equal = list()
                for foreign_word, frequency in dictionary.items():
                    if frequency > max:
                        max = frequency
                        array_of_equal = list()
                        array_of_equal.append(foreign_word)
                    elif frequency == max:
                        array_of_equal.append(foreign_word)

                if frequency < min_frequency:
                    self.statistics['missed'][character] = self.statistics['missed'][character] + 1
                    continue

                missed = True
                translation_text = ""
                if len(array_of_equal) > 1:
                    self.statistics['negative'][character] = self.statistics['negative'][character] + 1
                    continue

                translation = self.translator.translate(array_of_equal[0], src=character, dest=self.base_language)
                # print(translation.text + " " + word)
                translation_text = self.majka_lemmatizers[character]. \
                    lemmatization_and_loaded_stop_words_removal_in_array(
                    textPreprocessing.tokenize_text(translation.text), self.stop_words[character]).lower()

                if missed and (translation_text == "" or word_text == ""):
                    self.statistics['missed'][character] = self.statistics['missed'][character] + 1
                    continue

                print(translation_text + " " + word_text)

                if translation_text != word_text:
                    self.statistics['negative'][character] = self.statistics['negative'][character] + 1
                else:
                    self.statistics['positive'][character] = self.statistics['positive'][character] + 1
                    # print(word + " " + dictionary)
            else:
                lifo_stack.append(character)
                self.parse_lemmatizer_ext_min(lifo_stack, dictionary, language_array_shortenings, min_frequency)
                lifo_stack.pop()

    # Manages parsing and collecting of statistical data - extended (contains frequences of translated words)
    # language_array_shortenings -   array with language shortenings which are suitable for translation
    def get_translation_and_statistics_parse_ext(self, language_array_shortenings, min_occurences=0):
        lifo_stack = []
        self.majka_lemmatizers = self.initialize_majka_lemmatizers(language_array_shortenings)

        self.load_stop_words(language_array_shortenings)
        self.prepare_statistic_structures(language_array_shortenings)

        if min_occurences < 2:
            self.parse_lemmatizer_ext(lifo_stack, self.root_node, language_array_shortenings)
        else:
            print("SUCCESS")
            self.parse_lemmatizer_ext_min(lifo_stack, self.root_node, language_array_shortenings, min_occurences)

        self.print_statistics(language_array_shortenings)

    # Parsing of character tree - extended (with frequences of other potential candidates)
    # lifo_stack -        lifo stack which should be used for character retrieval
    # dictionary_base -   dictionary with characters - child node of some node
    # language_array_shortenings -   array with language shortenings which are suitable for translation
    def parse_ext(self, lifo_stack, dictionary_base, language_array_shortenings):

        for character, dictionary in dictionary_base.items():
            if character in language_array_shortenings:
                probable_words = self.get_probable_words(dictionary)
                word = ''.join(lifo_stack)
                # print(word)
                visited = False

                for probable_word in probable_words:
                    # print("lang1: " + character + " " + probable_word)

                    translation = self.translator.translate(probable_word, src=character, dest=self.base_language)

                    if translation.text != word:
                        self.statistics['positive'][character] = self.statistics['positive'][character] + 1
                        break

                if not visited:
                    self.statistics['negative'][character] = self.statistics['negative'][character] + 1
            elif character is not None:
                lifo_stack.append(character)
                self.parse_ext(lifo_stack, dictionary, language_array_shortenings)
                lifo_stack.pop()

    # Obtains those words with maximal frequency of translated words
    # word_freq_dict -    dictionary with words as keys and their frequencies as values
    @staticmethod
    def get_probable_words(word_freq_dict):
        max_freq = 0
        preferable_word = list()

        if not isinstance(word_freq_dict, dict):
            return ""

        for word, freq in word_freq_dict.items():
            if freq > max_freq:
                preferable_word = list()
                preferable_word.append(word)
                max_freq = freq
            elif freq == max:
                preferable_word.append(word)

        return preferable_word

    # Loads JSON file and sets language of a tree
    # file_name -             name of file containing character tree
    # language_shortening -   shortening of base language of character tree
    def load_as_json(self, file_name, language_shortening):
        self.tree_language_shortening = language_shortening
        with open(file_name, "r", encoding='utf-8') as f:
            self.root_node = json.load(f)

    # Loads JSON file
    # json_file -   json file path and file name
    @staticmethod
    def load_json_file(json_file):
        with open(json_file, "r", encoding='utf-8') as file:
            return json.load(file)


# Collects statistic information about character tree
if __name__ == "__main__":
     # character_tree = CharacterTreeTranslator('sk_lang_char_tree.json', 'sk')
     # character_tree.get_translation_and_statistics_parse(['en', 'cs'])
     # character_tree.get_translation_and_statistics_parse_lemmatizer(['en', 'cs'])

     character_tree = CharacterTreeTranslator('sk_lang_char_tree_ext.json', 'sk')
     # character_tree.get_translation_and_statistics_parse_ext(['en', 'cs'])
     character_tree.get_translation_and_statistics_parse_ext(['en', 'cs'], 3)
     # character_tree.get_translation_and_statistics_parse_ext(['en', 'cs'], 5)
     # character_tree.get_translation_and_statistics_parse_ext(['en', 'cs'], 7)

