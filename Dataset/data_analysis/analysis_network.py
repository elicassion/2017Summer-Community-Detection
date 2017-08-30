import os
import codecs
data_dir = os.path.join('..', 'data', 'test_fos', 'big_data')

lf = open(os.path.join(data_dir, 'links.txt'))
count = 0
uname2uid = {}
linkyear = set()
for line in lf:
	line = line.strip()
	tps = line.split('\t')
	if tps[0] not in uname2uid:
		uname2uid[tps[0]] = len(uname2uid)
	if tps[1] not in uname2uid:
		uname2uid[tps[1]] = len(uname2uid)
	count += len(tps) - 2
	for tpl in tps[2:]:
		tp = tpl.split(' ')
		t1 = int(tp[0])
		t2 = int(tp[1])
		linkyear.add(t1)
		linkyear.add(t2)
print ("Link Num: %d" % count)
# print (uname2uid['61F1FBBD'])
print (linkyear)