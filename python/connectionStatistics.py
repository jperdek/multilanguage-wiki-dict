import json
from python import textPreprocessing


# Saves dictionary as JSON file
# file_name     - name of JSON file to save
# content_dict  - dictionary with content to save
def save_as_json(file_name, content_dict):
    with open(file_name, "w", encoding='utf-8') as f:
        f.write(json.dumps(content_dict))  # FINAL DUMPING


# Loads JSON file
# file_name     - name of JSON file to load
def load_as_json(file_name):
    with open(file_name, "r", encoding='utf-8') as f:
        return json.load(f)


# Finds statistic information using conection file
# connection_file           - file with language connections
# base_language_shortening  - language used to connect other titles in connection file
# language_array_shortening - array of used languages shortenings
def find_statistics_information_connection(connection_file, base_language_shortening,
                                           language_array_shortenings):
    connection_data = load_as_json(connection_file)

    max_tokens = 25
    number_records = 0
    statistic_for_languages = dict()

    for language_shortening in language_array_shortenings:
        statistic_for_languages[language_shortening] = dict()

    for language_shortening in language_array_shortenings:
        statistic_for_languages[language_shortening]['records'] = 0
        statistic_for_languages[language_shortening]['tokens'] = dict()
        for i in range(1, max_tokens):
            statistic_for_languages[language_shortening]['tokens'][str(i)] = 0

    for record in connection_data[base_language_shortening]:
        if 'title' in record and record['title'] != "":
            number_records = number_records + 1

            for language_shortening in language_array_shortenings:
                if language_shortening in record and record[language_shortening] != "":
                    statistic_for_languages[language_shortening]['records'] = \
                        statistic_for_languages[language_shortening]['records'] + 1
                    number_tokens = len(textPreprocessing.tokenize_text(record[language_shortening]))

                    if number_tokens < max_tokens:
                        statistic_for_languages[language_shortening]['tokens'][str(number_tokens)] = \
                            statistic_for_languages[language_shortening]['tokens'][str(number_tokens)] + 1
                    else:
                        print('Number tokens for ' + language_shortening + 'exceeds: ' + str(number_tokens))

    print("Number records: " + str(number_records))
    for language_shortening in language_array_shortenings:
        print("Number connections in " + language_shortening + " is: " +
              str(statistic_for_languages[language_shortening]['records']))
        for i in range(1, max_tokens):
            print(str(i) + " token frequencies is: " + str(statistic_for_languages[language_shortening]['tokens']
                                                           [str(i)]))


# Finds out statistic information from alias file
# alias_files - files with aliases (every language has language shortening in title separated with _ symbol
def find_statistics_information_from_alias_files_extended(alias_files):
    statistic_for_language = dict()
    max_tokens_base = 10
    max_tokens_aliases = 20
    max_number_aliases = 40

    for alias_file in alias_files:
        language_shortening = alias_file.split('_')[0]
        alias_data = load_as_json(alias_file)

        statistic_for_language[language_shortening] = dict()
        statistic_for_language[language_shortening]['records'] = 0
        statistic_for_language[language_shortening]['tokens_base'] = dict()
        statistic_for_language[language_shortening]['tokens_aliases'] = dict()
        statistic_for_language[language_shortening]['number_aliases'] = dict()

        for i in range(1, max_tokens_base):
            statistic_for_language[language_shortening]['tokens_base'][str(i)] = 0

        for i in range(1, max_tokens_aliases):
            statistic_for_language[language_shortening]['tokens_aliases'][str(i)] = 0

        for i in range(1, max_number_aliases):
            statistic_for_language[language_shortening]['number_aliases'][str(i)] = 0

        for base_name, array_aliases in alias_data.items():
            if base_name != "":
                if len(array_aliases) < max_number_aliases:
                    statistic_for_language[language_shortening]['number_aliases'][str(len(array_aliases))] =\
                        statistic_for_language[language_shortening]['number_aliases'][str(len(array_aliases))] + 1
                else:
                    print("Number of aliases for " + language_shortening + " exceeds: " + str(len(array_aliases)))

                statistic_for_language[language_shortening]['records'] = \
                    statistic_for_language[language_shortening]['records'] + 1
                base_tokens = len(textPreprocessing.tokenize_text(base_name))
                if base_tokens < max_tokens_base:
                    statistic_for_language[language_shortening]['tokens_base'][str(base_tokens)] = \
                        statistic_for_language[language_shortening]['tokens_base'][str(base_tokens)] + 1
                else:
                    print("Number base tokens for " + language_shortening + " exceeds: " + base_tokens)

                for alias in array_aliases:
                    alias_tokens = len(textPreprocessing.tokenize_text(alias))
                    if alias_tokens < max_tokens_aliases:
                        statistic_for_language[language_shortening]['tokens_aliases'][str(alias_tokens)] = \
                            statistic_for_language[language_shortening]['tokens_aliases'][str(alias_tokens)] + 1
                    else:
                        print("Number alias tokens for " + language_shortening + " exceeds: " + alias_tokens)

    for language_shortening in statistic_for_language.keys():
        print('\n')
        print("Number records for " + language_shortening + " containing aliases: " +
              str(statistic_for_language[language_shortening]['records']))

        for i in range(1, max_tokens_base):
            print(str(i) + " base token frequencies are: " +
                  str(statistic_for_language[language_shortening]['tokens_base'][str(i)]))

        for i in range(1, max_tokens_aliases):
            print(str(i) + " token of aliases frequencies are: " +
                  str(statistic_for_language[language_shortening]['tokens_aliases'][str(i)]))

        for i in range(1, max_number_aliases):
            print(str(i) + " aliases have frequency of: " +
                  str(statistic_for_language[language_shortening]['number_aliases'][str(i)]))


# Finds out statistic information from connection file and file with aliases
if __name__ == "__main__":
    find_statistics_information_connection('end_regex.json', 'sk', ['cs', 'en'])
    find_statistics_information_from_alias_files_extended(['sk_aliases_wiki.json', 'cs_aliases_wiki.json',
                                                           'en_aliases_wiki.json'])
