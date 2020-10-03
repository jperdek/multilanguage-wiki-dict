
import xml.sax
import json
import re


class XMLHandler(xml.sax.ContentHandler):
    def __init__(self, langlinks, forJSON, name_of_end_file, language_shortening):
        self.currentData = ""
        self.occurences = 0
        self.on_page_to_do = False
        self.page_data = None
        self.first_title_added = False
        self.langlinks = langlinks
        self.forJSON = forJSON
        self.name_of_end_file= name_of_end_file
        self.language_shortening = language_shortening

    def startElement(self, tag, attributes):
        self.currentData = tag
        if tag == 'page':
            self.occurences = self.occurences + 1
            self.on_page_to_do = True
            self.page_data = {}
            self.first_title_added = True

    def endElement(self, tag):
        if tag == 'page':
            self.on_page_to_do = False
            self.forJSON[self.language_shortening].append(self.page_data)

        self.currentData = ""

    def characters(self, content):
        if self.currentData == "title" and self.on_page_to_do and re.search("^MediaWiki:", content) == None:
            self.page_data['title'] = content
        elif self.currentData == "id" and self.first_title_added and 'title' in self.page_data:
            self.first_title_added = False
            self.page_data['id'] = content
            if self.page_data['id'] in self.langlinks:
                for record in self.langlinks[self.page_data['id']]:
                    self.page_data[record['ll_lang']] = record['ll_title']

    def endDocument(self):
        print("Occurences: "+str(self.occurences))
        #SAVE AS JSON FILE
        with open(self.name_of_end_file, "w") as f:
            f.write(json.dumps(self.forJSON))     #FINAL DUMPING


def load_records(langlinks_sql_dump_file, language_array_shortenings):
    page_data = {}

    lang_condition_string = language_array_shortenings[0]
    for i in range(1, len(language_array_shortenings)):
        lang_condition_string = language_array_shortenings[i] + "|" + lang_condition_string

    with open(langlinks_sql_dump_file, encoding="utf-8") as langlinks:
        texts = langlinks.read().split("INSERT INTO")

    for text in texts:
        text = text[text.find('VALUES') + 6:]

        found = re.findall("\((.+?)'\)[,;]", text)

        for insert in found:
            page_record = {}
            try:
                id_record = str(re.search('^([1-9][0-9]*),', insert).group(1))
                page_record['ll_lang'] = re.search("^[1-9][0-9]*,'(" + lang_condition_string + ")',", insert).group(1)
                page_record['ll_title'] = re.search("^[1-9][0-9]*,'(" + lang_condition_string + ")','(.+)$", insert)\
                    .group(2)

                if id_record not in page_data:
                    page_data[id_record] = []
                    page_data[id_record].append(page_record)
                else:
                    page_data[id_record].append(page_record)

            except AttributeError:

                try:
                    re.search("^[1-9][0-9]*,'([-a-z]+)','.*$", insert).group(1)
                except AttributeError:
                    print("BAD REGEX USED: " + insert)

                try:
                    re.search("^[1-9][0-9]*,'([-a-z]+)',", insert).group(1)
                except AttributeError:
                    print("BAD LANGUAGE STRING: " + insert)

    return page_data


def createJSON(langlinks_sql_dump, file, end_file, language_shortening, language_array_shortenings):
    langlinks =load_records(langlinks_sql_dump, language_array_shortenings)

    titles = dict()
    titles[language_shortening] = []
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    xml_handler = XMLHandler(langlinks, titles, end_file, language_shortening)
    parser.setContentHandler(xml_handler)

    parser.parse(file)


if __name__ == "__main__":
    end_file = 'end_regex.json'
    createJSON('D://wiki/skwiki-latest-langlinks1.sql', 'D://wiki/skwiki-20200901-pages-articles-multistream.xml',
               end_file, "sk", ["en", "cs"])

#mapTitlesToOtherLanguages(cursor, end_file, "sk", ["en", "cs"])
