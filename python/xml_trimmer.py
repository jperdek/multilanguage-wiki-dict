import xml.sax
from xml.sax.saxutils import escape
import json
import re
import copy
import sys

class XMLHandler(xml.sax.ContentHandler):

    def __init__(self):
        self.occurences = 0
        self.stack = []
        self.number_occurences = 100000
        self.file = None
        self.file_number = 0
        self.open_file = True
        self.chosen_tag = ""

    def init(self, number_occurences, chosen_tag, path_to_dict, file_name):
        self.number_occurences = number_occurences
        self.chosen_tag = chosen_tag
        self.path_to_dict = path_to_dict
        self.file_name = file_name

    def startDocument(self):
        if self.open_file:
            self.file = open(self.path_to_dict + self.file_name + str(self.file_number) + ".xml", "w", encoding="utf-8")
            self.file_number = self.file_number + 1
            self.file.write('<?xml version="1.0" encoding="utf-8"?>')
            self.file.write('<wiki>')
            for tag_stack, attributes in self.stack:
                self.file.write('<'+ tag_stack +'>')
            self.open_file = False

    def startElement(self, tag, attributes):
        self.stack.append([tag, attributes])

        if self.open_file:
            self.file = open(self.path_to_dict + self.file_name + str(self.file_number) + ".xml", "w", encoding="utf-8")
            self.file_number = self.file_number + 1
            self.file.write('<?xml version="1.0" encoding="utf-8"?>')
            self.file.write('<wiki>')
            for tag_stack, attributes in self.stack:
                self.file.write('<'+ tag_stack +'>')
            self.open_file = False

        self.file.write('<' + tag + '>')

        if tag == self.chosen_tag:
            self.occurences = self.occurences + 1

            if self.occurences % 1000 == 0:
                print(self.occurences)


    def characters(self, content):
        if self.open_file:
            self.file = open(self.path_to_dict + self.file_name + str(self.file_number) + ".xml", "w", encoding="utf-8")
            self.file_number = self.file_number + 1
            self.file.write('<?xml version="1.0" encoding="utf-8"?>')
            self.file.write('<wiki>')
            for tag_stack, attributes in self.stack:
                self.file.write('<'+ tag_stack +'>')
            self.open_file = False
        #content.replace('<', '&lt;')
        #content.replace('>', '&gt;')
       # content.replace('&', '&amp;')
        #content.replace('"', '&quot;')
        #content.replace("'", '&apos;')
        #content.replace("-", '')

        self.file.write(escape(content))

    def endElement(self, tag):
        self.stack.pop()

        self.file.write('</' + tag + '>')

        if self.occurences >= self.number_occurences:
            self.occurences = 0
            self.open_file = True
            for tag_stack, attributes in reversed(self.stack):
                self.file.write('</' + tag_stack + '>')
            self.file.write('</wiki>')
            self.file.close()

    def endDocument(self):
        print("Occurences: "+str(self.occurences))
        if self.file.closed == False:
            for tag_stack, attributes in reversed(self.stack):
                self.file.write('</' + tag_stack + '>')
            self.file.write('</wiki>')
            self.file.close()


def prepare_json_for_indexing(mapping_file, number_occurences, chosen_tag, path_to_dict, file_name):

    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    xmlHandler = XMLHandler()
    xmlHandler.init(number_occurences, chosen_tag, path_to_dict, file_name)
    parser.setContentHandler(xmlHandler)

    parser.parse(mapping_file)

if __name__ == "__main__" :
    #prepare_json_for_indexing('end_regex.json', 'D://wiki/cswiki-20200901-pages-articles-multistream.xml', "sk", ["cs"], 'csIndexes.json', 'csDocIndexes.json')
    #prepare_json_for_indexing('end_regex.json', 'D://wiki/skwiki-20200901-pages-articles-multistream.xml', "sk", ["sk"], 'skIndexes.json', 'skDocIndexes.json')
    prepare_json_for_indexing('D://wiki/enwiki-20200901-pages-articles-multistream.xml', 100000, 'page', 'D:/wiki/temp', 'examples')