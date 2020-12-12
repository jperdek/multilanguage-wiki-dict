#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import string
import fileinput
import sys

def func():
	return 0;

for line in open(0, mode='r', encoding="utf-8").readlines():
	try:
		print(str(line[1:-2]))
	except:
		func()
