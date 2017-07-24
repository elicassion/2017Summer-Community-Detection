import os
import re
import copy
import json
import time
import numpy as np

dataset = 'data'
modes = [
	'cite',
	# 'coau'
]
conferences = [
	'AAAI',
	'ACL',
	'SIGCOMM'
]

root = os.path.abspath(os.path.join('..'))
data_dir = os.path.join(root, dataset)
for mode in modes:
	for conference in conferences:
		print (conference)
		fos_set_len = []
		for i in range(0, 4):
			fos_file = open(os.path.join(data_dir, mode, conference, 'fos_L%d.txt' % i), "r")
			fos_set = set()
			lines = fos_file.read()
			lines = lines.split('\n')
			for line in lines:
				line = line.split('\t')
				if len(line) == 1:
					continue
				foss = line[1].split(' ')
				for fos in foss:
					fos_set.add(fos)
			fos_set_len.append(len(fos_set))
			print (len(fos_set))
		resfile = open(os.path.join(data_dir, mode, conference, 'fos.stat'), "w")
		for res in fos_set_len:
			resfile.write(str(res)+'\n')
