import json


def load_json(file):
    with open(file, encoding='utf-8') as file_json:
        return json.load(file_json)

def merge_term_indexes(start, end, path_to_file, filename, language_shortening, term_end_file):
    first_json = load_json(path_to_file + '' + str(start) + '_' + filename + ".json")
    unique_docs = set()
    for term in first_json[language_shortening]:
        for doc in first_json[language_shortening][term]['doc'].keys():
            unique_docs.add(doc)


    for i in range(start + 1, end + 1):
        json_to_merge = load_json(path_to_file +''+ str(i) + '_' + filename + '.json')
        print("i "+ str(i))
        for term in json_to_merge[language_shortening]:
            if term not in first_json[language_shortening]:
                for doc in json_to_merge[language_shortening][term]['doc'].keys():
                    unique_docs.add(doc)
                first_json[language_shortening][term] = json_to_merge[language_shortening][term].copy()
            else:
                for document in json_to_merge[language_shortening][term]['doc'].keys():
                    if document in first_json[language_shortening][term]['doc']:
                        first_json[language_shortening][term]['doc'][document] = \
                            first_json[language_shortening][term]['doc'][document] + \
                            json_to_merge[language_shortening][term]['doc'][document]
                        if document == '603' and term == 'symbol':
                            print(json_to_merge[language_shortening][term]['doc'][document])
                    else:
                        first_json[language_shortening][term]['doc'][document] = \
                            json_to_merge[language_shortening][term]['doc'][document]
                        first_json[language_shortening][term]['df'] = first_json[language_shortening][term]['df'] + 1
                        unique_docs.add(document)

    first_json[language_shortening +'_docs'] = len(unique_docs)


    with open(term_end_file, "w") as f:
        f.write(json.dumps(first_json))  # FINAL DUMPING



def merge_doc_indexes(start, end, path_to_file, filename, language_shortening, term_end_file):
    first_json = load_json(path_to_file + '' + str(start) + '_' + filename + ".json")

    for i in range(start + 1, end + 1):
        json_to_merge = load_json(path_to_file +''+ str(i) + '_' + filename + '.json')
        print("i " + str(i))
        for docs, frequency in json_to_merge[language_shortening].items():
            if docs in first_json[language_shortening].keys():
                first_json[language_shortening][docs] = first_json[language_shortening][docs] + \
                                                        json_to_merge[language_shortening][docs]
            else:
                first_json[language_shortening][docs] = json_to_merge[language_shortening][docs]

    with open(term_end_file, "w") as f:
        f.write(json.dumps(first_json))  # FINAL DUMPING


if __name__ == "__main__" :
    merge_term_indexes(0, 205, 'partial/', 'enIndexes', 'en', 'enIndexes.json')
    merge_doc_indexes(0,205, 'partial/', 'enDocIndexes', 'en', 'enDocIndexes.json')

