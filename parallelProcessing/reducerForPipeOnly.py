#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fileinput
import io
import json
import sys
print (sys.version)
	
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

    # Adds word pairs in dict to character tree
    #
    def add_words_pairs_extended(self, dict_word_pairs, dest_language):
        for word, destination_words in dict_word_pairs.items():
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
                    if dest_language not in previous_node[character].keys():
                        previous_node[character][dest_language] = dict()
                    for destination_word in destination_words:
                        if destination_word not in previous_node[character][dest_language].keys():
                            previous_node[character][dest_language][destination_word] = 1
                        else:
                            previous_node[character][dest_language][destination_word] = \
                                previous_node[character][dest_language][destination_word] + 1

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

    # finds word
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

    # starts test to load words and confirm thier next finding in three
    def test(self):
        failed = False
        self.init('sk')
        self.add_words_pairs({"name": "blame"}, 'en')
        self.add_words_pairs({"nama": "lama"}, 'en')
        self.add_words_pairs({"nail": "ame"}, 'en')
        self.add_words_pairs({"kraľovať": "king"}, 'en')
        if self.find_word('name', 'en') != 'blame':
            print("Error test failed on word blame!")
            failed = True
        if self.find_word('nail', 'en') != 'ame':
            print("Error test failed on word nail!")
            failed = True
        if self.find_word('nama', 'en') != 'lama':
            print("Error test failed on word nama!")
            failed = True
        if self.find_word('kraľovať', 'en') != 'king':
            print("Error test failed on word nama!")
            failed = True

        if not failed:
            print("Test succeed!")

    def save_as_json(self, file_name):
        with io.open(file_name, "w") as f:
            f.write(json.dumps(self.root_node))  # FINAL DUMPING

    def load_as_json(self, file_name, language_shortening):
        self.tree_language_shortening = language_shortening
        with io.open(file_name, "r", encoding='utf-8') as f:
            self.root_node = json.load(f)
			
			
sk_tree = CharacterTree()
sk_tree.init('sk')
	
for line in fileinput.input():
	data = line.split(",")
	if len(data) != 2:
		# Something has gone wrong. Skip this line.
		print("Something has gone wrong. Skip this line")
		continue
	word, translation_language = data
	translation, language_shortening = translation_language.split(';')
	#dictionary = {}
	#dictionary[word] = translation;
	language_shortening = language_shortening.replace('\n','')
	sk_tree.add_words_pairs({word: translation}, language_shortening)

sk_tree.save_as_json('sk_test_character_tree.json')
