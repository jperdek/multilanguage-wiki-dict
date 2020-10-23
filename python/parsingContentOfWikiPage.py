import xml.sax
import json
import re
from python import textPreprocessing, token_indexing
import copy


# Class used to parse content of wiki pages using SAX parser
class XMLHandler(xml.sax.ContentHandler):

    # Initialization of parsing of wiki page
    def __init__(self):
        super().__init__()
        self.currentData = ""
        self.occurences = 0
        self.on_page_to_do = False
        self.prepared_for_indexing = False
        self.lemmatizer = textPreprocessing.Lemmatization()
        self.page_content = ""
        self.docs_set = set()
        self.document_identifier = ""
        self.lang_document_identifier = ""
        self.text_content = ""
        self.indexes = None
        self.doc_freq_index = None
        self.language_indexes = {}
        self.language_shortening = "sk"
        self.term_end_file = None
        self.doc_end_file = None
        self.titles_indexes = None

    # Sets indexes to class content
    # indexes       - indexes to set
    def set_indexes(self, indexes):
        self.indexes = indexes
        self.doc_freq_index = copy.deepcopy(indexes)

    # Sets JSON file
    # titles_indexes            - indexes of titles, connection file
    # language_shortening       - base language for language connection
    # term_end_file             - end file for storing indexes from terms
    # doc_end_file              - end file for storing documents length
    def set_json(self, titles_indexes, language_shortening, term_end_file, doc_end_file):
        self.titles_indexes = titles_indexes
        self.language_shortening = language_shortening
        self.language_indexes = []
        self.term_end_file = term_end_file
        self.doc_end_file = doc_end_file
        self.lemmatizer.majka_init_for_lemmatization(language_shortening)

    # Initializes or nulls variables when new page is accessed
    # tag           - start tag name
    # attributes    - attributes of element
    def startElement(self, tag, attributes):
        self.currentData = tag
        if tag == 'page':
            self.occurences = self.occurences + 1
            self.on_page_to_do = True
            self.text_content = ""

            # if self.occurences == 200:
            #    self.indexes[self.language_shortening + "_docs"] = len(self.docs_set)
            #    with open(self.term_end_file, "w") as f:
            #        f.write(json.dumps(self.indexes))  # FINAL DUMPING
            #    with open(self.doc_end_file, "w") as f:
            #        f.write(json.dumps(self.doc_freq_index))  # FINAL DUMPING
            #        sys.exit(0)

            if self.occurences % 100 == 0:
                print(self.occurences)

    # If end element is page than it preprocessed text if any and adds it to indexes
    # tag       - end tag name
    def endElement(self, tag):
        if tag == 'page':
            self.prepared_for_indexing = False
            if self.text_content != "":
                self.docs_set.add(self.document_identifier)
                token_indexing.index_words_term_freq_doc_freq(self.indexes, self.doc_freq_index, self.text_content,
                                                              self.document_identifier, self.language_shortening)
        self.currentData = ""

    # Preprocessing of page content of connected pages
    # Can be called multiple times on one tag content!!!
    # content       - content between tags
    def characters(self, content):
        if self.currentData == "title" and self.on_page_to_do and re.search(r"^MediaWiki:", content) is None:
            if content in self.titles_indexes[self.language_shortening]:
                self.document_identifier = str(self.titles_indexes[self.language_shortening][content])
                self.lang_document_identifier = self.language_shortening + "-" + self.document_identifier
                self.prepared_for_indexing = True

        if self.currentData == 'text' and self.prepared_for_indexing:
            self.page_content = self.lemmatizer.lemmatization_and_stop_words_removal_not_included(
                textPreprocessing.tokenize_text(content), 'stop_words/en_stop_words.json')
            # print(self.document_identifier+ "< >"+str(len(content)))
            if self.page_content != "":
                self.text_content = self.text_content + self.page_content

    # Saves indexes content to separate JSON files
    def endDocument(self):
        print("Occurences: "+str(self.occurences))

        self.indexes[self.language_shortening + "_docs"] = len(self.docs_set)

        # SAVE AS JSON FILE
        with open(self.term_end_file, "w") as f:
            f.write(json.dumps(self.indexes))     # FINAL DUMPING
        with open(self.doc_end_file, "w") as f:
            f.write(json.dumps(self.doc_freq_index))     # FINAL DUMPING


# Prepares a title dict for specific language
#    - obtained titles in next xml processing can be compared to find out if mapping exists for them
#    mapping file - name of file with language mappings
#    file_language_shortening - language shortening for origin language for which mapping is originated
#    dest_language_shortening - array of other languages - only one language shortening should be provided
#                             - this language must be same as language provided in language_file
def prepare_titles(mapping_file, file_language_shortening, dest_language_shortenings):
    title_indexes = {}
    for dest_language_shortening in dest_language_shortenings:
        title_indexes[dest_language_shortening] = {}

    with open(mapping_file, encoding='utf-8') as indexing_file:
        json_file = json.load(indexing_file)

        for record in json_file[file_language_shortening]:
            for dest_language_shortening in dest_language_shortenings:
                if dest_language_shortening == file_language_shortening and 'id' in record:
                    title_indexes[dest_language_shortening][record['title']] = record['id']
                elif dest_language_shortening in record:
                    title_indexes[dest_language_shortening][record[dest_language_shortening]] = record['id']

    return title_indexes


# Starts parsing xml file
#    mapping file - name of file with language mappings
#    language file - file which should be processed - in certain language
#                   -mappings must be created for it first!!!
#    mapping_file_language_shortening - language shortening for origin language for which mapping is originated
#    language_array_shortenings - array of other languages - only one language shortening should be provided
#                               - this language must be same as language provided in language_file
#    term_end_file - title for end file for tokens including associated docs with frequency for them
#    doc_end_file  - title for end file for doc length
def prepare_json_for_indexing(mapping_file, language_file, mapping_file_language_shortening, language_array_shortenings,
                              term_end_file, doc_end_file):
    titles_indexes = prepare_titles(mapping_file, mapping_file_language_shortening, language_array_shortenings)

    indexes = {}
    for dest_language_shortening in language_array_shortenings:
        indexes[dest_language_shortening] = {}
        indexes[dest_language_shortening + "_docs"] = 0

    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    xml_handler = XMLHandler()
    xml_handler.set_json(titles_indexes, language_array_shortenings[0], term_end_file, doc_end_file)
    xml_handler.set_indexes(indexes)

    parser.setContentHandler(xml_handler)

    parser.parse(language_file)


# loads partially divided files
def partial_load(start_index, end_index, source_language_shortening, language_shortening, language_file):

    for number in range(start_index, end_index + 1):
        addition = ""
        addition = addition + str(number)
        prepare_json_for_indexing('end_regex.json', language_file + '' + addition + '.xml', source_language_shortening,
                                  [language_shortening],
                                  'partial/' + addition + '_' + language_shortening + 'Indexes.json', 'partial/' +
                                  addition + '_' + language_shortening + 'DocIndexes.json')


# Creates indexes which can be used for tf-idf score creation
if __name__ == "__main__":
    # PROCESSING OF EACH LANGUAGE WIKIPEDIA FILE
    # prepare_json_for_indexing('end_regex.json', 'D://wiki/cswiki-20200901-pages-articles-multistream.xml', "sk",
    # ["cs"], 'csIndexes.json', 'csDocIndexes.json')
    prepare_json_for_indexing('end_regex.json', 'D://wiki/skwiki-20200901-pages-articles-multistream.xml', "sk",
                              ["sk"], 'skIndexes.json', 'skDocIndexes.json')
    # prepare_json_for_indexing('end_regex.json', 'D://wiki/enwiki-20200901-pages-articles-multistream.xml', "sk",
    # ["en"], 'enIndexes.json', 'enDocIndexes.json')

    # PARTIAL PROCESSING OF FILE - FILE MUST BE TRIMMED
    # partial_load(0, 206,'sk', 'en', 'D:/wiki/tempexamples')
    # partial_load(43, 206, 'sk', 'en', 'D:/wiki/tempexamples')
