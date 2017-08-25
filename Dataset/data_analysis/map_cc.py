import os
import codecs
import pymysql

connection = pymysql.connect(host='127.0.0.1',
                             user='data',
                             password='data',
                             db='mag-new-160205',
                             charset='utf8mb4',
                             port=3306,
                             cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()

data_dir = os.path.join('..', 'data', 't_cite', 'AAAI')
cc_lv = 'L1'
cfile = open(os.path.join(data_dir, 'c_fos_%s.txt' % cc_lv), 'r')
cid_dict = {}
if not os.path.exists(os.path.join(data_dir, 'fos_id_name_%s.txt' % cc_lv)):
	exfile = open(os.path.join(data_dir, 'fos_id_name_%s.txt' % cc_lv), 'w')
	for line in cfile:
		cid = line.split('\t')[0]
		# print (cid)
		cursor.execute("SELECT FieldsOfStudyName FROM FieldsOfStudy WHERE FieldsOfStudyID = '%s'" % cid)
		name = cursor.fetchall()[0]['FieldsOfStudyName']
		# print (name)
		exfile.write("%s\t%s\n" % (cid, name))
		cid_dict[cid] = name
	exfile.close()
else:
	for line in open(os.path.join(data_dir, 'fos_id_name_%s.txt' % cc_lv), 'r'):
		cid, name = line.strip().split('\t')
		cid_dict[cid] = name

fcfile = open(os.path.join(data_dir, 'fos_%s.txt' % cc_lv), 'r')
trans_fcfile = open(os.path.join(data_dir, 'fos_%s_name.txt') % cc_lv, 'w')
for line in fcfile:
	tp = line.strip().split('\t')
	if len(tp) == 1:
		trans_fcfile.write("%s\n" % tp[0])
		continue
	auid = tp[0]
	aufoss = tp[1]
	trans_fcfile.write("%s\t" % auid)
	for fos in aufoss.split():
		trans_fcfile.write("%s\t" % cid_dict[fos])
	trans_fcfile.write('\n')
trans_fcfile.close()