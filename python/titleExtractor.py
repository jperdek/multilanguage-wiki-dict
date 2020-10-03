
import xml.sax
import json
import re
import urllib.request
import urllib.parse
import mariadb
import sys


class XMLHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.currentData = ""
        self.occurences = 0
        self.on_page_to_do = False
        self.page_data = None
        self.first_title_added = False

    def setJSON(self, cursor, forJSON, name_of_end_file, language_shortening, language_array_shortenings):
        self.cursor = cursor
        self.forJSON = forJSON
        self.name_of_end_file= name_of_end_file
        self.language_shortening = language_shortening
        self.language_array_conditions = create_language_conditions(language_array_shortenings)

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
            self.page_data = get_other_titles(self.page_data, self.language_array_conditions)


    def endDocument(self):
        print("Occurences: "+str(self.occurences))
        #SAVE AS JSON FILE
        with open(self.name_of_end_file, "w") as f:
            f.write(json.dumps(self.forJSON))     #FINAL DUMPING


def create_language_conditions(language_array_shortenings):
    languages = " ( ll_lang = '" + language_array_shortenings[0] +"'"
    for i in range(1, len(language_array_shortenings)):
        languages = languages + " OR ll_lang = '" +language_array_shortenings[i] +"'"

    languages = languages + " ) "
    return languages


def get_other_titles(page_data, language_conditions):
    cursor.execute(
        "SELECT ll_lang, ll_title FROM langlinks WHERE ll_from=? AND " +language_conditions,
        (page_data['id'],))
    for (ll_lang, ll_title) in cursor:
        page_data[ll_lang.decode('utf-8')] = ll_title.decode('utf-8')

    return page_data


def createJSON(cursor, file, end_file, language_shortening, language_array_shortenings):
    titles = {}
    titles[language_shortening] = []
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    xmlHandler = XMLHandler()
    xmlHandler.setJSON(cursor, titles, end_file, language_shortening, language_array_shortenings)
    parser.setContentHandler(xmlHandler)

    parser.parse(file)


def connectToMariaDB():
    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user="root",
            password="postgres",
            host="127.0.0.1",
            port=3306,
            database="postgres"
        )
    except mariadb.Error as e:
        print("Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    cursor = conn.cursor()
    return cursor


def mapTitlesToOtherLanguagesHTTP(json_titles, language_shortening, language_array_shortenings):
    url1 = "https://sk.wikipedia.org/w/api.php?action=query&titles="
    url2 = "&prop=langlinks&lllang="
    url3 = "&format=json&lllimit=500"

    with open(json_titles) as json_file:
        titles = json.load(json_file)['titles']
        chosen = "Metafyzika" #titles[0] #str(titles[0].encode('utf-8'))#replace(' ','_')

        response = urllib.request.urlopen(url1 + urllib.parse.quote(chosen) + url2 + language_array_shortenings[0] + url3)
        #print(response.read())
        #r = json.loads(response.read(), encoding='utf-8')
        #print(r)
        data = json.loads(response.read().decode(response.info().get_param('charset') or 'utf-8'))
        print(data)
        half_result = data['query']['pages'][next(iter(data['query']['pages']))]
        print(half_result)
        if 'langlinks' in half_result:
            print(data['query']['pages'][next(iter(data['query']['pages']))]['langlinks'][0]['*'])
        #for title in titles:
        #    print(title)

end_file = 'end.json'
cursor = connectToMariaDB()
createJSON(cursor, 'D://wiki/skwiki-20200901-pages-articles-multistream.xml', end_file, "sk", ["en", "cs"])

#mapTitlesToOtherLanguages(cursor, end_file, "sk", ["en", "cs"])
