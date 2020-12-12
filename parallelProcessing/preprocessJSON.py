#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import io

def save_to_line(json_array, file_name):
	with io.open(file_name, "w", encoding='utf-8') as f:
		for field in json_array:
			dictionary = {}
				
			if 'title' in field:
				dictionary['title']= field['title'].replace(',',' ').replace(';',' ')
			else:
				dictionary['title']= ''
				
			if 'id' in field:
				dictionary['id']= field['id'].replace(',',' ').replace(';',' ')
			else:
				dictionary['id']= 0
				
			if 'cs' in field:
				dictionary['cs']= field['cs'].replace(',',' ').replace(';',' ')
			else:
				dictionary['cs']= ''
				
			if 'en' in field:
				dictionary['en']= field['en'].replace(',',' ').replace(';',' ')
			else:
				dictionary['en']= ''
				
			f.write(str(json.dumps(dictionary))+"\n")
				
def load_as_json(file_name, language_shortening):
	with io.open(file_name, "r", encoding='utf-8') as f:
		return json.load(f)[language_shortening]
		
		
save_to_line(load_as_json('end_regex.json', 'sk'), 'simpleData.txt')