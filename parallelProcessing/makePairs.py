#!/usr/bin/python
# -*- coding: utf-8 -*-
		
@outputSchema("words:{(word:chararray)}")
def createPairs(sentence1, sentence2, language):
	length = 0
	if len(sentence1) < len(sentence2):
		length = len(sentence1);
	else:
		length = len(sentence2);
	array = []
	for i in range(0,length):
		array.append(sentence1[i][0] +","+ sentence2[i][0] +";"+ language)
	return array
	