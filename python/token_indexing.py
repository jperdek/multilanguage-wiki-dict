from python import textPreprocessing
import math
import numpy as np
import json

def index_words(index, check_duplicates, text, document_identifier, langDocumentIdentifier, dest_lang_shortening):
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


def index_words_term_freq_doc_freq(index, doc_freq_index, text, document_identifier, lang_document_identifier, dest_lang_shortening):
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


class TdIdfOperations:

    def __init__(self):
        self.term_indexes = {}
        self.doc_indexes = {}
        self.number_of_docs = 0

    def prepare_index_file(self, index_file):
        with open(index_file, encoding="utf-8") as index_file:
            return json.load(index_file)

    def initialize(self, doc_index_file, term_indexes_file, language_shortening):
        self.initialize_indexes(self.prepare_index_file(doc_index_file), self.prepare_index_file(term_indexes_file),
                                language_shortening)

    def initialize_indexes(self, doc_indexes, term_indexes, language_shortening):
        self.term_indexes[language_shortening] = term_indexes[language_shortening]
        self.doc_indexes[language_shortening] = doc_indexes[language_shortening]
        self.number_of_docs = term_indexes[language_shortening + "_docs"]

    def normalize_array(self, array):
        sum_of_square_roots = 0.0
        for i in array:
            sum_of_square_roots = sum_of_square_roots + math.pow(i, 2)
        denominator = math.sqrt(sum_of_square_roots)

        for i in range(len(array)):
            array[i] = array[i] / denominator

        return array

    def count_TF(self, term_frequency_in_doc, frequency_of_words_in_doc):
        return term_frequency_in_doc / frequency_of_words_in_doc

    def count_IDF(self, number_of_docs, number_of_docs_with_term):
        return np.log((1.0 + number_of_docs) / (1.0 + number_of_docs_with_term))

    def count_TF_IDF_for_term(self, term_frequency_in_doc, frequency_of_terms_in_doc, number_of_docs, number_of_docs_with_term):
        return self.count_TF(term_frequency_in_doc, frequency_of_terms_in_doc) * self.count_IDF(number_of_docs, number_of_docs_with_term)

    def count_TF_IDF(self, array_of_terms, language_shortenings):
        term = ""
        term_record = ""
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
                        tf_idf_output[i][doc] = tf_idf_output[i][doc] + self.count_TF_IDF_for_term(term_frequency_in_doc, frequency_of_terms_in_doc, number_of_docs, number_of_docs_with_term)

    def count_TF_IDF_from_indexes(self, language_shortening, end_index_file_tf_idf):
        tf_idf_output = {}
        terms = list(self.term_indexes[language_shortening].keys())

        for i in range(len(terms)):
            term = terms[i]
            if term in self.term_indexes[language_shortening]:
                term_record = self.term_indexes[language_shortening][term]

                for doc_identifier, term_frequency_in_doc in term_record['doc'].items():
                    frequency_of_terms_in_doc = self.doc_indexes[language_shortening][doc_identifier]
                    #number_of_docs = term_record[language_shortening + "_docs"]
                    number_of_docs_with_term = term_record['df']

                    if term not in tf_idf_output:
                        tf_idf_output[term] = {}
                    if doc_identifier not in tf_idf_output[term]:
                        tf_idf_output[term][doc_identifier] = 0

                    tf_idf_output[term][doc_identifier] = round(tf_idf_output[term][doc_identifier]
                           + self.count_TF_IDF_for_term(term_frequency_in_doc, frequency_of_terms_in_doc,
                                                self.number_of_docs, number_of_docs_with_term), 6)

        with open(end_index_file_tf_idf, "w", encoding="utf-8") as f:
            f.write(json.dumps(tf_idf_output))

    def make_tf_idf_file(self, doc_index_file, term_indexes_file, language_shortening, end_index_file_tf_idf):

        self.initialize(doc_index_file, term_indexes_file, language_shortening)
        self.count_TF_IDF_from_indexes(language_shortening, end_index_file_tf_idf)


if __name__ == "__main__":
    td_idf_operations = TdIdfOperations()
    td_idf_operations.make_tf_idf_file('cdDocIndexes.json', 'csIndexes.json', 'cs', 'cs_tf_idf_file.json')
    td_idf_operations.make_tf_idf_file('skDocIndexes.json', 'skIndexes.json', 'sk', 'sk_tf_idf_file.json')