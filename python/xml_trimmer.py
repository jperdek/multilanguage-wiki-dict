import xml.sax
from xml.sax.saxutils import escape


# XML handler for SAX parser to trim large XML to small pieces
class XMLHandler(xml.sax.ContentHandler):

    # Initialize xml handler
    def __init__(self):
        super().__init__()
        self.occurences = 0
        self.stack = []
        self.number_occurences = 100000
        self.file = None
        self.file_number = 0
        self.open_file = True
        self.chosen_tag = ""
        self.path_to_dict = ""
        self.file_name = ""

    # inits processing of file
    # number_occurences         - number occurences after them new file should be created
    # chosen_tag                - chosen tag to be threated and in relation with of occurences
    # path_to_dict              - path to destination directory where trimmed files should be created
    # file_name                 - name of end file, without end type
    def init(self, number_occurences, chosen_tag, path_to_dict, file_name):
        self.number_occurences = number_occurences
        self.chosen_tag = chosen_tag
        self.path_to_dict = path_to_dict
        self.file_name = file_name

    # Opens file on the beginning of document
    def startDocument(self):
        if self.open_file:
            self.file = open(self.path_to_dict + self.file_name + str(self.file_number) + ".xml", "w", encoding="utf-8")
            self.file_number = self.file_number + 1
            self.file.write('<?xml version="1.0" encoding="utf-8"?>')
            self.file.write('<wiki>')
            for tag_stack, attributes in self.stack:
                self.file.write('<' + tag_stack + '>')
            self.open_file = False

    # Adds starting tag to xml file
    # Informs about number of processed chosen tags
    # It does not take care of attributes!!!!!!
    # tag           - name of start tag
    # attributes    - attributes of given tag
    def startElement(self, tag, attributes):
        self.stack.append([tag, attributes])

        if self.open_file:
            self.file = open(self.path_to_dict + self.file_name + str(self.file_number) + ".xml", "w", encoding="utf-8")
            self.file_number = self.file_number + 1
            self.file.write('<?xml version="1.0" encoding="utf-8"?>')
            self.file.write('<wiki>')
            for tag_stack, attributes in self.stack:
                self.file.write('<' + tag_stack + '>')
            self.open_file = False

        self.file.write('<' + tag + '>')

        if tag == self.chosen_tag:
            self.occurences = self.occurences + 1

            if self.occurences % 1000 == 0:
                print(self.occurences)

    # Adds all characters to whole content
    # it escapes all xml characters
    # content       - content between xml tags
    def characters(self, content):
        if self.open_file:
            self.file = open(self.path_to_dict + self.file_name + str(self.file_number) + ".xml", "w", encoding="utf-8")
            self.file_number = self.file_number + 1
            self.file.write('<?xml version="1.0" encoding="utf-8"?>')
            self.file.write('<wiki>')
            for tag_stack, attributes in self.stack:
                self.file.write('<' + tag_stack + '>')
            self.open_file = False

        self.file.write(escape(content))

    # On end element adds end element tag
    # If number occurences reached requested number it pops and adds whole content of LIFO and creates new file
    # tag       = name of end tag
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

    # On end of document id pops and adds remaining content of LIFO and closes a file
    def endDocument(self):
        print("Occurences: "+str(self.occurences))
        if not self.file.closed:
            for tag_stack, attributes in reversed(self.stack):
                self.file.write('</' + tag_stack + '>')
            self.file.write('</wiki>')
            self.file.close()


# Provides JSON files with indexes
# mapping_file          - file containing mapping amongst languages
# number_occurences     - number occurences of specific tag to create new document after
# chosen_tag            - chosen tag to trim whole document
# path_to_dict          - path to destination directory where files should be stored
# file_name             - name of destination file, it should be provided without ending
def prepare_json_for_indexing(mapping_file, number_occurences, chosen_tag, path_to_dict, file_name):

    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    xml_handler = XMLHandler()
    xml_handler.init(number_occurences, chosen_tag, path_to_dict, file_name)
    parser.setContentHandler(xml_handler)

    parser.parse(mapping_file)


# Trims XML file to smaller pieces
if __name__ == "__main__":
    prepare_json_for_indexing('D://wiki/skwiki-20200901-pages-articles-multistream.xml', 250000, 'page', 'D:/wiki/temp',
                              'sk_part_wiki')
