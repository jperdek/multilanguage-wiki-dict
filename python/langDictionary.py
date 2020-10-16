
import json
from python import textPreprocessing


# Character tree for fast search of tokens
# complexity should be linear to number of characters of searched token
class CharacterTree:

    # initializes empty dict for root node
    # adds slovak language shortening as tree language shortening
    def __init__(self):
        self.root_node = dict()
        self.tree_language_shortening = 'sk'

    # Initialization with possibility to set own language shortening
    # language_shortening - new language shortening of character tree
    def init(self, language_shortening):
        self.root_node = dict()
        self.tree_language_shortening = language_shortening

    # Enables process array of dict with words
    # array_word_pairs  - array of word pairs dicts
    # dest_language     - destination language of processed words
    def add_word_pairs_array(self, array_word_pairs, dest_language):
        for word_pair in array_word_pairs:
            self.add_words_pairs(word_pair, dest_language)

    # Adds word pairs in dict to character tree
    #
    def add_words_pairs(self, dict_word_pairs, dest_language):
        for word, destination_word in dict_word_pairs.items():
            actual_node = self.root_node
            for i in range(0, len(word)):
                character = word[i]
                if character in actual_node.keys():
                    previous_node = actual_node
                    actual_node = actual_node[character]
                else:
                    actual_node[character] = dict()
                    previous_node = actual_node
                    actual_node = actual_node[character]

                if i == len(word) - 1:
                    previous_node[character][dest_language] = destination_word

    def find_word(self, word, dest_language):
        actual_node = self.root_node
        for i in range(0, len(word)):
            character = word[i]
            if character in actual_node.keys():
                previous_node = actual_node
                actual_node = actual_node[character]
            else:
                return None

            if i == len(word) - 1:
                if dest_language in previous_node[character]:
                    return previous_node[character][dest_language]
                else:
                    return None

    def find_word_more_languages(self, word, dest_languages):
        actual_node = self.root_node
        all_language_connections = dict()
        for i in range(0, len(word)):
            character = word[i]
            if character in actual_node.keys():
                previous_node = actual_node
                actual_node = actual_node[character]
            else:
                return None

            if i == len(word) - 1:
                for dest_language in dest_languages:
                    if dest_language in previous_node[character]:
                        all_language_connections[dest_language] = previous_node[character][dest_language]
                    else:
                        all_language_connections[dest_language] = ""
                return all_language_connections

    def test(self):
        failed = False
        self.init('sk')
        self.add_words_pairs({"name": "blame"}, 'en')
        self.add_words_pairs({"nama": "lama"}, 'en')
        self.add_words_pairs({"nail": "ame"}, 'en')
        if self.find_word('name', 'en') != 'blame':
            print("Error test failed on word blame!")
            failed = True
        if self.find_word('nail', 'en') != 'ame':
            print("Error test failed on word nail!")
            failed = True
        if self.find_word('nama', 'en') != 'lama':
            print("Error test failed on word nama!")
            failed = True

        if not failed:
            print("Test succeed!")

    def save_as_json(self, file_name):
        with open(file_name, "w") as f:
            f.write(json.dumps(self.root_node))  # FINAL DUMPING

    def load_as_json(self, file_name, language_shortening):
        self.tree_language_shortening = language_shortening
        with open(file_name, "r") as f:
            self.root_node = json.load(f)


def load_json_file(lang_connection_file):
    with open(lang_connection_file, "r") as file:
        return json.load(file)


def initialize_majka_lemmatizers(languages_array_shortenings, base_language_shortening):
    majka_lemmatizers = dict()

    for language_shortening in languages_array_shortenings:
        majka_lemmatizer = textPreprocessing.Lemmatization()
        majka_lemmatizer.majka_init_for_lemmatization(language_shortening)
        majka_lemmatizers[language_shortening] = majka_lemmatizer

    if base_language_shortening is not None:
        majka_lemmatizer = textPreprocessing.Lemmatization()
        majka_lemmatizer.majka_init_for_lemmatization(base_language_shortening)
        majka_lemmatizers[base_language_shortening] = majka_lemmatizer

    return majka_lemmatizers


# Finds pair of words from both titles and do some text preprocessing on them
# text1                     - title 1
# text2                     - title 2
# majka_lemmatizer_text1    - for lemmatization of text1 according initialized language
# majka_lemmatizer_text2    - for lemmatization of text2 according initialized language
# stop_words_file1           - stop words file for removing stop words in text1 according language of text1
# stop_words_file2           - stop words file for removing stop words in text2 according language of text2
def find_word_pairs(text1, text2, majka_lemmatizer_text1, majka_lammatizer_text2, stop_words_file1, stop_words_file2):
    #text1 = majka_lemmatizer_text1.lemmatization_and_stop_words_removal_not_included(
    #    textPreprocessing.tokenize_text(text1), stop_words_file1)
    #text2 = majka_lammatizer_text2.lemmatization_and_stop_words_removal_not_included(
    #    textPreprocessing.tokenize_text(text2), stop_words_file2)

    array1 = textPreprocessing.tokenize_text(text1)
    array2 = textPreprocessing.tokenize_text(text2)

    word_pairs = dict()
    if len(array1) > len(array2):
        min_length = len(array2)
    else:
        min_length = len(array1)

    for i in range(0, min_length):
        word_pairs[array1[i]] = array2[i]

    return word_pairs


# Creates dictionary consisting of various languages
# lang_connection_file          - file contains title connections bind for certain language title
# language_shortening           - shortening of language used for binding other titles
# language_array_shortenings    - array of language shortening which are mapped in bind file
# character_tree                - instance of character tree to load other words
# dest_lang_file                - file used to stored content of character tree as json
def create_dictionary(lang_connection_file, language_shortening, language_array_shortenings, character_tree,
                      dest_lang_file):
    lang_connections = load_json_file(lang_connection_file)
    majka_lemmatizers = initialize_majka_lemmatizers(language_array_shortenings, language_shortening)
    stop_words_files = load_json_file('stop_words/stopwords_file_paths.json')

    for record in lang_connections[language_shortening]:
        for dest_language_shortening in language_array_shortenings:
            if dest_language_shortening in record and record[dest_language_shortening] != "":
                word_pairs = find_word_pairs(record['title'], record[dest_language_shortening],
                                             majka_lemmatizers[language_shortening],
                                             majka_lemmatizers[dest_language_shortening],
                                             stop_words_files[language_shortening],
                                             stop_words_files[dest_language_shortening])
                character_tree.add_words_pairs(word_pairs, dest_language_shortening)

    character_tree.save_as_json(dest_lang_file)


# Creates dictionary consisting of various languages
# lang_connection_file           - file contains title connections bind for certain language title
# language_shortening           - shortening of language used for binding other titles
# language_array_shortenings    - array of language shortening which are mapped in bind file
# character_tree                - instance of character tree to load other words
# dest_lang_file                - file used to stored content of character tree as json
def create_dictionary_more(lang_connection_file, connection_file_lang_shortening, language_shortening,
                           language_array_shortenings, character_tree, dest_lang_file):
    lang_connections = load_json_file(lang_connection_file)
    majka_lemmatizers = initialize_majka_lemmatizers(language_array_shortenings, language_shortening)
    stop_words_files = load_json_file('stop_words/stopwords_file_paths.json')
    word_pairs = dict()

    for record in lang_connections[connection_file_lang_shortening]:
        for dest_language_shortening in language_array_shortenings:
            if dest_language_shortening in record and record[dest_language_shortening] != "":
                if connection_file_lang_shortening == language_shortening:
                    word_pairs = find_word_pairs(record['title'], record[dest_language_shortening],
                                                 majka_lemmatizers[language_shortening],
                                                 majka_lemmatizers[dest_language_shortening],
                                                 stop_words_files[language_shortening],
                                                 stop_words_files[dest_language_shortening])

                    character_tree.add_words_pairs(word_pairs, dest_language_shortening)

                elif dest_language_shortening != connection_file_lang_shortening:
                    if language_shortening in record and record[language_shortening] != "":
                        word_pairs = find_word_pairs(record[language_shortening], record[dest_language_shortening],
                                                     majka_lemmatizers[language_shortening],
                                                     majka_lemmatizers[dest_language_shortening],
                                                     stop_words_files[language_shortening],
                                                     stop_words_files[dest_language_shortening])

                        character_tree.add_words_pairs(word_pairs, dest_language_shortening)

            elif language_shortening in record and record[language_shortening] != "":
                word_pairs = find_word_pairs(record[language_shortening], record['title'],
                                             majka_lemmatizers[language_shortening],
                                             majka_lemmatizers[connection_file_lang_shortening],
                                             stop_words_files[language_shortening],
                                             stop_words_files[connection_file_lang_shortening])

                character_tree.add_words_pairs(word_pairs, dest_language_shortening)

    character_tree.save_as_json(dest_lang_file)


# tests character tree
def test_character_tree():
    character_tree_test = CharacterTree()
    character_tree_test.test()
    character_tree_test.save_as_json('sk_test_character_tree.json')


def create_dictionaries(lang_connection_file, connection_file_lang_shortening, all_language_shortenings):
    for language_shortening in all_language_shortenings:
        array_lang_shortenings = [lang_shortening for lang_shortening in all_language_shortenings if
                                  language_shortening != lang_shortening]
        tree = CharacterTree()
        tree.init(language_shortening)
        print(array_lang_shortenings)
        create_dictionary_more(lang_connection_file, connection_file_lang_shortening, language_shortening,
                               array_lang_shortenings, tree, language_shortening + '_lang_char_tree1.json')


def create_sk_lang_character_tree(lang_connection_file):
    array_lang_shortenings = ['cs', 'en']
    sk_tree = CharacterTree()
    sk_tree.init('sk')
    create_dictionary(lang_connection_file, 'sk', array_lang_shortenings, sk_tree, 'sk_lang_char_tree.json')


# creates character tree for various languages and tokens
if __name__ == "__main__":
    # test_character_tree()
    # create_sk_lang_character_tree('end_regex.json')
    create_dictionaries('end_regex.json', 'sk', ['en', 'sk', 'cs'])

