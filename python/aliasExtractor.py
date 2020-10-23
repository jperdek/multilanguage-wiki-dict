
import xml.sax
import re
import json


# Parser used to find aliases in text
class XMLHandler(xml.sax.ContentHandler):

    # Initializes parser for finding aliases
    # mapping_file                      - file to connect languages
    # name_of_end_file                  - file where aliases should be stored
    # base_language_shortening          - shortening of base language used in connection_file
    # language_shortening               - language of wiki_file
    def __init__(self, mapping_file, name_of_end_file, base_lang_shortening, language_shortening):
        super().__init__()
        self.current_data = ""
        self.occurences = 0
        self.title = ""
        self.titles_aliases = dict()

        self.on_page_to_do = False
        self.first_title_added = False
        self.name_of_end_file = name_of_end_file
        self.language_shortening = language_shortening

        self.load_titles(mapping_file, base_lang_shortening, language_shortening)

    # Loads titles from connection file as keys of dict
    # mapping_file          - connection file amongst languages
    # base_lang_shortening  - base language used in mapping_file
    # language_shortening   - language_shortening of destination languages for which mapping is provided
    def load_titles(self, mapping_file, base_lang_shortening, language_shortening):
        load_json = self.load_as_json(mapping_file)
        if language_shortening == base_lang_shortening:
            for record in load_json[base_lang_shortening]:
                if 'title' in record:
                    self.titles_aliases[record['title']] = []
        else:
            for record in load_json[base_lang_shortening]:
                if language_shortening in record:
                    self.titles_aliases[record[language_shortening]] = []

    # Initializes variables on every start on element page
    # tag           - name of start tag
    # attributes    - attributes of tag
    def startElement(self, tag, attributes):
        self.current_data = tag
        if tag == 'page':
            self.occurences = self.occurences + 1
            self.on_page_to_do = True

    # Nulls content of data and informs about processed pages
    # tag       - name of end tag
    def endElement(self, tag):
        if tag == 'page':
            self.on_page_to_do = False
            if self.occurences % 1000 == 0:
                print(self.occurences)

        self.current_data = ""

    # Tries to find redirect which indicates occurrence of alias
    # if alias is found then is added to base title and removed from list of titles
    # content       - content between tags
    def characters(self, content):
        if self.current_data == "title" and self.on_page_to_do:
            self.title = content
        elif self.current_data == "text":
            content_to_find = content.lower()
            results = re.findall(r"^\s*#\s*redirect\s*\[\[(.*)\]\]\s*$", content_to_find)
            if len(results) > 0:
                if self.title in self.titles_aliases.keys():
                    # print("Removing " + self.title + " from titles - its alias")
                    del self.titles_aliases[self.title]

                if results[0] in self.titles_aliases.keys():
                    # print(self.title)
                    self.titles_aliases[results[0]].append(self.title)

    # Deletes empty field for objects not containing aliases
    def delete_empty_ones(self):
        remove = [key for key, aliases in self.titles_aliases.items() if len(aliases) == 0]
        for key in remove:
            del self.titles_aliases[key]

    # Saves obtained aliases to JSON file
    def endDocument(self):
        print("Occurences: "+str(self.occurences))

        self.delete_empty_ones()
        # SAVE AS JSON FILE
        self.save_as_json(self.name_of_end_file, self.titles_aliases)

    # Loads JSON file
    # file_name     - file name of JSON file
    @staticmethod
    def load_as_json(file_name):
        with open(file_name, "r", encoding='utf-8') as f:
            return json.load(f)

    # Stores dictionary as JSON file
    # file_name         - file name of resulting file
    # object_to_save    - dictionary which should be saved as JSON file
    @staticmethod
    def save_as_json(file_name, object_to_save):
        with open(file_name, "w", encoding='utf-8') as f:
            f.write(json.dumps(object_to_save))  # FINAL DUMPING


# Prepares parser to find aliases
# connection_file           - file to connect languages
# wiki_file                 - file of pages to find redirects
# end_file                  - file where aliases should be stored
# base_language_shortening  - shortening of base language used in connection_file
# language_shortening       - language of wiki_file
def find_lang_aliases(connection_file, wiki_file, end_file, base_language_shortening, language_shortening):

    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    xml_handler = XMLHandler(connection_file, end_file, base_language_shortening, language_shortening)
    parser.setContentHandler(xml_handler)

    parser.parse(wiki_file)


# Extracts aliases from page files
if __name__ == "__main__":
    # find_lang_aliases("end_regex.json", "D:/wiki/skwiki-20200901-pages-articles-multistream.xml",
    #                  "sk_aliases_wiki.json", 'sk', 'sk')
    # find_lang_aliases("end_regex.json", "D:/wiki/enwiki-20200901-pages-articles-multistream.xml",
    # "en_aliases_wiki.json", 'sk', 'en')
    find_lang_aliases("end_regex.json", "D:/wiki/cswiki-20200901-pages-articles-multistream.xml",
                      "cs_aliases_wiki.json", 'sk', 'cs')
