from python import textPreprocessing
import math
import numpy as np
import json


# Indexing of words in text
# index                 - dictionary containing indexes
# check_duplicates      - dictionary for finding duplicates
# text                  - text which should be tokenized and indexed
# document_identifier   - identifier of certain documents associated with text
# dest_lang_shortening  - language used for access to index
def index_words(index, check_duplicates, text, document_identifier, dest_lang_shortening):
    for word in textPreprocessing.tokenize_text(text):
        word = str(word)
        if word in index[dest_lang_shortening]:

            if document_identifier not in check_duplicates[dest_lang_shortening][word]['doc']:
                index[dest_lang_shortening][str(word)]['doc'].append(document_identifier)
                index[dest_lang_shortening][word]['df'] = len(index[dest_lang_shortening][word]['doc'])
        else:
            index[dest_lang_shortening][word] = {}
            index[dest_lang_shortening][word]['doc'] = []
            index[dest_lang_shortening][word]['df'] = 1

            check_duplicates[dest_lang_shortening][word] = {}
            check_duplicates[dest_lang_shortening][word]['doc'] = set()
            check_duplicates[dest_lang_shortening][word]['doc'].add(document_identifier)
            index[dest_lang_shortening][word]['doc'].append(document_identifier)


# Indexing of words in text and prepare it for tf-idf
# index                 - dictionary containing indexes
# check_duplicates      - dictionary for finding duplicates
# text                  - text which should be tokenized and indexed
# document_identifier   - identifier of certain documents associated with text
# dest_lang_shortening  - language used for access to index
def index_words_term_freq_doc_freq(index, doc_freq_index, text, document_identifier, dest_lang_shortening):
    tokenized_text = textPreprocessing.tokenize_text(text)
    doc_freq_index[dest_lang_shortening][document_identifier] = len(tokenized_text)
    index[dest_lang_shortening + "_docs"] = index[dest_lang_shortening + "_docs"] + 0

    for word in tokenized_text:
        word = str(word)
        if word in index[dest_lang_shortening]:
            if document_identifier not in index[dest_lang_shortening][word]['doc']:
                index[dest_lang_shortening][word]['doc'][document_identifier] = 1
                index[dest_lang_shortening][word]['df'] = len(index[dest_lang_shortening][word]['doc'])
            else:
                index[dest_lang_shortening][word]['doc'][document_identifier] = \
                                                    index[dest_lang_shortening][word]['doc'][document_identifier] + 1
        else:
            index[dest_lang_shortening][word] = {}
            index[dest_lang_shortening][word]['doc'] = {}
            index[dest_lang_shortening][word]['df'] = 1
            index[dest_lang_shortening][word]['doc'][document_identifier] = 1


# Class which manages tf-idf operations
class TdIdfOperations:

    # Initialization of required data types
    def __init__(self):
        self.term_indexes = {}
        self.doc_indexes = {}
        self.number_of_docs = 0

    # Loads index file
    # index_file - json file with indexes
    @staticmethod
    def prepare_index_file(index_file):
        with open(index_file, encoding="utf-8") as index_file:
            return json.load(index_file)

    # Initialization of document indexes
    # doc_index_file        - file with document lengths
    # term_index_file       - file with frequencies of certain term in document
    # language_shortening   - language association with concrete language words
    def initialize(self, doc_index_file, term_indexes_file, language_shortening):
        self.initialize_indexes(self.prepare_index_file(doc_index_file), self.prepare_index_file(term_indexes_file),
                                language_shortening)

    # Initialization of indexes - loads indexes to class for its usage
    # doc_indexes           - length of doc in dictionary of docs
    # term_indexes          - term frequencies in certain document and number of unique documents
    # language_shortening   - language association with concrete language words
    def initialize_indexes(self, doc_indexes, term_indexes, language_shortening):
        self.term_indexes[language_shortening] = term_indexes[language_shortening]
        self.doc_indexes[language_shortening] = doc_indexes[language_shortening]
        self.number_of_docs = term_indexes[language_shortening + "_docs"]

    # Normalization of array by diving each part of vector size of this vector
    # array - array representing vector of values
    @staticmethod
    def normalize_array(array):
        sum_of_square_roots = 0.0
        for i in array:
            sum_of_square_roots = sum_of_square_roots + math.pow(i, 2)
        denominator = math.sqrt(sum_of_square_roots)

        for i in range(len(array)):
            array[i] = array[i] / denominator

        return array

    # Counts term frequency
    # term_frequency_in_doc     - frequency of term in doc
    # frequency_of_words_in_doc - frequency of term in doc
    @staticmethod
    def count_tf(term_frequency_in_doc, frequency_of_words_in_doc):
        return term_frequency_in_doc / frequency_of_words_in_doc

    # Counts inverse document frequency
    # number_of_docs            - number of documents
    # number_of_docs_with_terms - number of unique docs with reference for certain term
    @staticmethod
    def count_idf(number_of_docs, number_of_docs_with_term):
        return np.log((1.0 + number_of_docs) / (1.0 + number_of_docs_with_term))

    # Counts tf idf from term by multiplying tf and idf values
    # term-frequency_in_doc     - frequency of term in certain document
    # frequency_of_term_in_doc  - frequency of term in doc
    # number_of_docs            - number of documents
    # number_of_docs_with_term  - number of unique docs with reference for certain term
    def count_tf_idf_for_term(self, term_frequency_in_doc, frequency_of_terms_in_doc, number_of_docs,
                              number_of_docs_with_term):
        return self.count_tf(term_frequency_in_doc, frequency_of_terms_in_doc)\
               * self.count_idf(number_of_docs, number_of_docs_with_term)

    # Counts tf-idf using array of terms
    # array_of_terms        -
    # language_shortenings  -
    def count_tf_idf(self, array_of_terms, language_shortenings):
        doc_identifier = ""
        tf_idf_output = []
        for i in range(len(array_of_terms)):
            tf_idf_output.append([])

        for i in range(len(array_of_terms)):
            term = array_of_terms[i]
            for language_shortening in language_shortenings:
                if term in self.term_indexes[language_shortening]:
                    term_record = self.term_indexes[language_shortening][term]

                    for doc in term_record['doc']:
                        term_frequency_in_doc = self.doc_indexes[language_shortening][doc]
                        frequency_of_terms_in_doc = self.doc_indexes[language_shortening][doc_identifier]
                        number_of_docs = term_record[language_shortening + "_docs"]
                        number_of_docs_with_term = term_record['df']
                        if doc not in tf_idf_output[i]:
                            tf_idf_output[i][doc] = 0.0
                        tf_idf_output[i][doc] = tf_idf_output[i][doc] + self.count_tf_idf_for_term(
                            term_frequency_in_doc, frequency_of_terms_in_doc, number_of_docs, number_of_docs_with_term)

    # Counts TF-IDF indexes
    # language_shortening   - language association with concrete language words
    # end_index_file_tf_idf - destination file where TF-IDF indexes will be stored
    def count_tf_idf_from_indexes(self, language_shortening, end_index_file_tf_idf):
        tf_idf_output = {}
        terms = list(self.term_indexes[language_shortening].keys())

        for i in range(len(terms)):
            term = terms[i]
            if term in self.term_indexes[language_shortening]:
                term_record = self.term_indexes[language_shortening][term]

                for doc_identifier, term_frequency_in_doc in term_record['doc'].items():
                    frequency_of_terms_in_doc = self.doc_indexes[language_shortening][doc_identifier]
                    # number_of_docs = term_record[language_shortening + "_docs"]
                    number_of_docs_with_term = term_record['df']

                    if term not in tf_idf_output:
                        tf_idf_output[term] = {}
                    if doc_identifier not in tf_idf_output[term]:
                        tf_idf_output[term][doc_identifier] = 0

                    tf_idf_output[term][doc_identifier] = round(tf_idf_output[term][doc_identifier] +
                                                                self.count_tf_idf_for_term(term_frequency_in_doc,
                                                                frequency_of_terms_in_doc, self.number_of_docs,
                                                                                           number_of_docs_with_term), 6)

        with open(end_index_file_tf_idf, "w", encoding="utf-8") as f:
            f.write(json.dumps(tf_idf_output))

    # creation of tf-idf file
    # doc_index_file        -file with length of documents
    # term_indexes_file     -file with term indexes
    # language_shortening   -language association with concrete language words
    # end_index_file_tf_idf -destination file where TF-IDF indexes will be stored
    def make_tf_idf_file(self, doc_index_file, term_indexes_file, language_shortening, end_index_file_tf_idf):

        self.initialize(doc_index_file, term_indexes_file, language_shortening)
        self.count_tf_idf_from_indexes(language_shortening, end_index_file_tf_idf)


# Creation of TF-IDF file from document indexes (length of docuemnts) and term indexes (occurences of term in document)
if __name__ == "__main__":
    td_idf_operations = TdIdfOperations()
    td_idf_operations.make_tf_idf_file('cdDocIndexes.json', 'csIndexes.json', 'cs', 'cs_tf_idf_file.json')
    td_idf_operations.make_tf_idf_file('skDocIndexes.json', 'skIndexes.json', 'sk', 'sk_tf_idf_file.json')
    td_idf_operations.make_tf_idf_file('enDocIndexes.json', 'enIndexes.json', 'en', 'en_tf_idf_file.json')
