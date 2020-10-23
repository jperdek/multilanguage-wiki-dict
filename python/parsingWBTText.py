import re

def parse_wiki_data_to_wiki_page_mapping(props_text_file):
    mapping_relations = dict()
    with open(props_text_file, "r", encoding='utf-8') as file:
        for line in file:
            mapping_items = re.findall(r"\(([1-9][0-9]*),'wikibase_item',(Q[1-9][0-9]*),[^\)]+\)", line)

            for mapping_item in mapping_items:
                mapping_relations[mapping_item[0]] = mapping_item[1]

