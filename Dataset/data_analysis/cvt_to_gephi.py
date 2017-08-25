import os
import sys
import codecs
data_dir = os.path.join('..', 'data', 't_cite', 'AAAI')
res_dir = os.path.join('..', 'res', '')
exnid_uid_filename = os.path.join(data_dir, 'nid_uid.csv')
exlink_filename = os.path.join(data_dir, 'nid_links.csv')
exlink_time_filename = os.path.join(data_dir, 'nid_time_links.csv')
uname2uid = {}
exlink_file = open(exlink_filename, 'w')
exlink_file.write('Source\tTarget\n')
exlink_time_file = open(exlink_time_filename, 'w')
exlink_time_file.write('Source\tTarget\tWeight\n')
for line in open(os.path.join(data_dir, 'links.txt')):
    line = line.split('\t')
    if line[0] not in uname2uid:
        uname2uid[line[0]] = len(uname2uid)
    if line[1] not in uname2uid:
        uname2uid[line[1]] = len(uname2uid)
    doc_id = uname2uid[line[0]]
    ref_id = uname2uid[line[1]]
    for tpl in line[2:-1]:
        tp = tpl.split(' ')
        t1 = int(tp[0])
        t2 = int(tp[1])
        exlink_file.write('%d\t%d\n' % (doc_id, ref_id))
        exlink_time_file.write('%d\t%d\t%d\n' % (doc_id, ref_id, t2))

for line in open(os.path.join(data_dir, 'del_links.txt')):
    line = line.split('\t')
    if line[0] not in uname2uid:
        uname2uid[line[0]] = len(uname2uid)
    if line[1] not in uname2uid:
        uname2uid[line[1]] = len(uname2uid)
    doc_id = uname2uid[line[0]]
    ref_id = uname2uid[line[1]]
    for tpl in line[2:-1]:
        tp = tpl.split(' ')
        t1 = int(tp[0])
        t2 = int(tp[1])
        exlink_file.write('%d\t%d\n' % (doc_id, ref_id))
        exlink_time_file.write('%d\t%d\t%d\n' % (doc_id, ref_id, t2))
exlink_file.close()
exlink_time_file.close()


exnid_uid_file = open(exnid_uid_filename, 'w')
exnid_uid_file.write('Id\tLabel\n')
for uname, uid in uname2uid.items():
	exnid_uid_file.write('%s\t%s\n' % (uid, uname))
exnid_uid_file.close()