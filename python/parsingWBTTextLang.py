import re
import json


def parse_wbt_text(wbt_text_file, text_mappings):
    text_mapping_new = dict()
    with open(wbt_text_file, "r", encoding='utf-8') as file:

        for line in file:
            inserts = re.findall(r"\(([1-9][0-9]*),'([^']+)'\)[,;]", line)

            for insert in inserts:
                # print(">" + insert[0] + "<___>" + insert[1] + "<")
                if insert[0] in text_mappings.keys():
                    text_mapping_new[text_mappings[insert[0]]] = insert[1]
    return text_mapping_new


def parse_wbt_text_with_file_save(wbt_text_file, text_mappings, language_aliases, language_shortening, file_name):
    text_mapping_new = dict()
    with open(wbt_text_file, "r", encoding='utf-8') as file:

        for line in file:
            inserts = re.findall(r"\(([1-9][0-9]*),'([^']+)'\)[,;]", line)

            for insert in inserts:
                # print(">" + insert[0] + "<___>" + insert[1] + "<")
                if insert[0] in text_mappings.keys():
                    text_mapping_new[text_mappings[insert[0]]] = insert[1]

    save_partial_file(language_aliases, text_mapping_new, language_shortening, file_name)


def save_partial_file(language_aliases, text_mappings_new, language_shortening, dest_file_lang_connections):

    for id_language_text in language_aliases[language_shortening].keys():

        if id_language_text not in text_mappings_new:
            print("Error text not found")
        else:
            language_aliases[language_shortening][id_language_text] = text_mappings_new[id_language_text]

    save_as_json(language_shortening + "_" + dest_file_lang_connections, language_aliases[language_shortening])


def create_language_string(language_array_shortenings):
    language_string = ""
    for i in range(0, len(language_array_shortenings) - 1):
        language_string = language_string + language_array_shortenings[i] + "|"

    language_string = language_string + language_array_shortenings[len(language_array_shortenings) - 1]

    print(language_string)
    return language_string


def parse_wbt_text_lang_file(wbt_text_lang_file, language_array_shortenings, text_mappings, language_aliases):
    language_string = create_language_string(language_array_shortenings)
    with open(wbt_text_lang_file, "r", encoding='utf-8') as file:
        for line in file:
            inserts = re.findall(r"\(([1-9][0-9]*),'(" + language_string + r")',([1-9][0-9]*)\)[,;]", line)

            for insert in inserts:
                # print(">" + insert[0] + "<___>" + insert[1] + "<___>"+ insert[2] + "<")
                text_mappings[insert[2]] = insert[0]
                language_aliases[insert[1]][insert[0]] = ""


def parse_wbt_text_lang_file_with_text(wbt_text_lang_file, language_array_shortenings, language_shortening,
                                       wbt_text_file, file_name, parts):
    language_aliases = dict()
    language_aliases[language_shortening] = dict()
    text_mappings = dict()
    number_parts = 0

    language_string = create_language_string(language_array_shortenings)
    counter = 0
    with open(wbt_text_lang_file, "r", encoding='utf-8') as file:
        for line in file:
            inserts = re.findall(r"\(([1-9][0-9]*),'(" + language_string + r")',([1-9][0-9]*)\)[,;]", line)

            for insert in inserts:
                counter = counter + 1
                # print(">" + insert[0] + "<___>" + insert[1] + "<___>"+ insert[2] + "<")
                text_mappings[insert[2]] = insert[0]
                language_aliases[insert[1]][insert[0]] = ""

                if counter > parts:
                    parse_wbt_text_with_file_save(wbt_text_file, text_mappings, language_aliases, language_shortening,
                                                  str(number_parts) + "_" + file_name)
                    counter = 0
                    number_parts = number_parts + 1

                    text_mappings = dict()
                    language_aliases[language_shortening] = dict()


def parse_wbt_text_langs(wbt_text_lang_file, wbt_text_file, language_array_shortenings, dest_file_lang_connections):
    language_aliases = dict()
    for language_shortening in language_array_shortenings:
        language_aliases[language_shortening] = dict()
    text_mappings = dict()

    # parse_wbt_text_lang_file(wbt_text_lang_file, language_array_shortenings, text_mappings, language_aliases)
    with open(wbt_text_lang_file, "r", encoding='utf-8') as file:
        for line in file:
            inserts = re.findall(r"(\([1-9][0-9]*,'[^']+',[1-9][0-9]*\))[,;]", line)

            for insert in inserts:
                input_group = re.findall(r"\(([1-9][0-9]*),'([^']+)',([1-9][0-9]*)\)", insert)

                if input_group[0][1] in language_array_shortenings:
                    text_mappings[input_group[0][2]] = input_group[0][0]
                    language_aliases[input_group[0][1]][input_group[0][2]] = ""
                # print(str(input_group[0][0]) + " " + str(input_group[0][1]) + " " + str(input_group[0][2]))
    print('here')
    text_mappings_new = parse_wbt_text(wbt_text_file, text_mappings)
    print('there')

    for language_shortening in language_aliases.keys():
        for id_language_text in language_aliases[language_shortening].keys():
            language_aliases[language_shortening][id_language_text] = text_mappings_new[text_mappings[id_language_text]]

    for language_shortening in language_array_shortenings:
        save_as_json(language_shortening + "_" + dest_file_lang_connections, language_aliases[language_shortening])


def parse_wbt_text_lang(wbt_text_lang_file, wbt_text_file, language_shortening, dest_file_lang_connections):
    language_aliases = dict()
    language_aliases[language_shortening] = dict()
    text_mappings = dict()

    parse_wbt_text_lang_file(wbt_text_lang_file, [language_shortening], text_mappings, language_aliases)
    print('here ' + str(len(text_mappings)))

    text_mappings_new = parse_wbt_text(wbt_text_file, text_mappings)
    print('there ' + str(len(text_mappings_new)))

    for id_language_text in language_aliases[language_shortening].keys():
        if id_language_text not in text_mappings_new:
            print("Error text not found")
        else:
            language_aliases[language_shortening][id_language_text] = text_mappings_new[id_language_text]

    save_as_json(language_shortening + "_" + dest_file_lang_connections, language_aliases[language_shortening])


def save_as_json(file_name, object_to_save):
    with open(file_name, "w", encoding='utf-8') as f:
        f.write(json.dumps(object_to_save))  # FINAL DUMPING


if __name__ == "__main__":
    # VERY LONG TO RUN
    # parse_wbt_text_langs('D:/wiki/wikidatawiki-20200901-wbt_text_in_lang.sql',
    #                    'D:/wiki/wikidatawiki-20200901-wbt_text.sql', ['sk', 'en', 'cs'], "aliases.json")

    # parse_wbt_text_lang('D:/wiki/wikidatawiki-20200901-wbt_text_in_lang.sql',
    #                     'D:/wiki/wikidatawiki-20200901-wbt_text.sql', 'sk', "aliases.json")
    # parse_wbt_text_lang('D:/wiki/wikidatawiki-20200901-wbt_text_in_lang.sql',
    #                    'D:/wiki/wikidatawiki-20200901-wbt_text.sql', 'cs', "aliases.json")
    # parse_wbt_text_lang('D:/wiki/wikidatawiki-20200901-wbt_text_in_lang.sql',
    #                    'D:/wiki/wikidatawiki-20200901-wbt_text.sql', 'en', "aliases.json")
    # print(u'obchodn\u00e1 div\u00edzia'.encode('iso-8859-1').decode('utf-8'))

    parse_wbt_text_lang_file_with_text('D:/wiki/wikidatawiki-20200901-wbt_text_in_lang.sql', ['sk'], 'sk',
                                       'D:/wiki/wikidatawiki-20200901-wbt_text.sql', "aliases.json", 5)
