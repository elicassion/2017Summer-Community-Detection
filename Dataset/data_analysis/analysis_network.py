import os
import codecs
data_dir = os.path.join('..', 'data', 'test_fos', 'big_data')

lf = open(os.path.join(data_dir, 'links.txt'))
count = 0
for line in lf:
	line = line.strip()
	tps = line.split('\t')
	count += len(tps) - 2
print ("Link Num: %d" % count)