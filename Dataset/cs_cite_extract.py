import pymysql
import os
import re
import copy
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from lxml import etree
import json
import time
import numpy as np
import random
connection = pymysql.connect(host='127.0.0.1',
                             user='data',
                             password='data',
                             db='mag-new-160205',
                             charset='utf8mb4',
                             port=3306,
                             cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()

conference_num = 100
Ctype = 'MIXED_%d' % conference_num
random.seed(20170725)
exdir = 'data/test_title/%s' % Ctype
# conferenceIDs = []

# def load_cids(exdir):
# 	cids = []
# 	cidfile = open(os.path.join(exdir, 'cids.txt'), 'r')
# 	for line in cidfile:
# 		if line is not '':
# 			cids.append(line.strip())
# 	cidfile.close()
# 	return cids

# def export_cids(exdir, cids):
# 	if not os.path.exists(exdir):
#         os.makedirs(exdir)
# 	cidfile = open(os.path.join(exdir, 'cids.txt'), 'w')
# 	for item in cids:
# 		cidfile.write("%s\n" % item)
# 	cidfile.close()

# if os.path.exists(os.path.join(exdir, 'cids.txt')):
# 	conferenceIDs = load_cids(exdir)
# else:
# 	cursor.execute("SELECT ConferenceSeriesID FROM ConferenceSeries WHERE UnderCS = 1")
# 	all_conferenceIDs = []
# 	for row in cursor.fetchall():
# 	    all_conferenceIDs.append(row['ConferenceSeriesID'])
# 	print (len(all_conferenceIDs))
# 	# conference_num = len(all_conferenceIDs)
# 	# conferenceIDs = all_conferenceIDs
# 	conferenceIDs = random.sample(all_conferenceIDs, conference_num)
# 	export_cids(exdir, conferenceIDs)
# 	# print (conferenceIDs)




pid = []
ref = []

def load_ref(exdir):
	reffile = open(os.path.join(exdir, 'refs.txt'))
	refs = []
	for line in reffile:
		if line is not '':
			items = line.strip().split()
			refs.append((items[0], items[1]))
			# print (items[0], items[1])
	reffile.close()
	return refs

if os.path.exists(os.path.join(exdir, 'refs.txt')):
	ref = load_ref(exdir)
else:
	
	st_ref = time.time()
	# for conferenceID in conferenceIDs:
	cursor.execute("SELECT PaperID FROM Papers WHERE ConferenceSeriesIDMappedToVenueName IN (SELECT t.ConferenceSeriesID FROM (SELECT ConferenceSeriesID FROM ConferenceSeries WHERE UnderCS = 1 LIMIT %d) AS t)" % conference_num)
	for row in cursor.fetchall():
	    pid.append(row['PaperID'])
	print (len(pid))

	cursor.execute("SELECT PaperID, PaperReferenceID FROM PaperReferences WHERE PaperID IN (SELECT PaperID FROM Papers WHERE ConferenceSeriesIDMappedToVenueName IN (SELECT t.ConferenceSeriesID FROM (SELECT ConferenceSeriesID FROM ConferenceSeries WHERE UnderCS = 1 LIMIT %d) AS t)) AND PaperReferenceID IN (SELECT PaperID FROM Papers WHERE ConferenceSeriesIDMappedToVenueName IN (SELECT t.ConferenceSeriesID FROM (SELECT ConferenceSeriesID FROM ConferenceSeries WHERE UnderCS = 1 LIMIT %d) AS t))" % (conference_num, conference_num))
	ref_res = cursor.fetchall()
	print ("Ref Num: %d" % len(ref_res))
	print ("Searching Time Elapsed: %.3f" % (time.time() - st_ref))

	os.makedirs(exdir)
	reffile = open(os.path.join(exdir, 'refs.txt'), "w")
	for row in ref_res:
		ref.append((row['PaperID'], row['PaperReferenceID']))
		reffile.write("%s\t%s\n" % (row['PaperID'], row['PaperReferenceID']))
	reffile.close()


def load_result(cursor, container, name):
    for row in cursor.fetchall():
        container.append(row[name])
    return container

def load_results(cursor, containers, names):
	for row in cursor.fetchall():
		for container, name in zip(containers, names):
			container.append(row[name])
	return containers

auid_link_dict = {}
# add title
au_time_title = {}
p_time_title = {}           # format: p_time_title[pid]=title
link_count = 1
st_build = time.time()
for refp, orip in ref:
    oriau = []
    refau = []
    oriyear = []
    refyear = []
    orititle = []
    reftitle = []
    cursor.execute("SELECT AuthorID FROM PaperAuthorAffiliations WHERE PaperID = '%s' "% refp)
    load_result(cursor, refau, 'AuthorID')
    cursor.execute("SELECT PaperPublishYear, NormalizedPaperTitle FROM Papers WHERE PaperID = '%s'" % refp)
    load_results(cursor, [refyear, reftitle], ['PaperPublishYear', 'NormalizedPaperTitle'])
        
    cursor.execute("SELECT AuthorID FROM PaperAuthorAffiliations WHERE PaperID = '%s' "% orip)
    load_result(cursor, oriau, 'AuthorID')
    cursor.execute("SELECT PaperPublishYear, NormalizedPaperTitle FROM Papers WHERE PaperID = '%s'" % orip)
    load_results(cursor, [oriyear, orititle], ['PaperPublishYear', 'NormalizedPaperTitle'])

    if orip not in p_time_title.keys():
        p_time_title[orip] = orititle[0]
    if refp not in p_time_title.keys():
        p_time_title[refp] = reftitle[0]

    for au in oriau:
        if au not in auid_link_dict.keys():
            auid_link_dict[au] = {}
        if au not in au_time_title.keys():
            au_time_title[au] = set()
        au_time_title[au].add((oriyear[0], orititle[0]))
        for rau in refau:
            if rau not in auid_link_dict[au].keys():
                auid_link_dict[au][rau] = []
            if rau not in au_time_title.keys():
                au_time_title[rau] = set()
            auid_link_dict[au][rau].append((oriyear[0], refyear[0], orip, refp))
            au_time_title[rau].add((refyear[0], reftitle[0]))
            link_count += 1
build_time = time.time() - st_build
print ("build link time: %.3f" % build_time)
print ("link count: %d" % link_count)


def export_link(link_dict, exdir):    
    if not os.path.exists(exdir):
        os.makedirs(exdir)
    filename = os.path.join(exdir, 't_links.txt')
    gilename = os.path.join(exdir, 'links.txt')
    f = open(filename, 'w')
    g = open(gilename, 'w')
    for au in link_dict.keys():
        for rau in link_dict[au].keys():
            f.write(au+'\t'+rau+'\t')
            g.write(au+'\t'+rau+'\t')
            ylen = len(link_dict[au][rau])
            for i in range(ylen-1):
                f.write(str(link_dict[au][rau][i][0])+' '+str(link_dict[au][rau][i][1])+' '+\
                        str(link_dict[au][rau][i][2])+' '+str(link_dict[au][rau][i][3])+'\t')
                g.write(str(link_dict[au][rau][i][0])+' '+str(link_dict[au][rau][i][1])+'\t')
            f.write(str(link_dict[au][rau][ylen-1][0])+' '+str(link_dict[au][rau][ylen-1][1])+' '+\
                    str(link_dict[au][rau][ylen-1][2])+' '+str(link_dict[au][rau][ylen-1][3])+'\n')
            g.write(str(link_dict[au][rau][ylen-1][0])+' '+str(link_dict[au][rau][ylen-1][1])+'\n')
    f.close()
    g.close()
    print ("export %s" % filename)
    print ("export %s" % gilename)

export_link(auid_link_dict, exdir)


def export_title(au_title_dict, exdir):
    # format: auid \t paperid \t year \t title
    if not os.path.exists(exdir):
        os.makedirs(exdir)
    filename = os.path.join(exdir, 'docs.txt')
    f = open(filename, 'w')
    for au in au_title_dict.keys():
        for time, title in au_title_dict[au]:
            f.write(au+'\t'+str(time)+'\t'+title+'\n')
    print ("export %s" % filename)

def export_pid_title(pid_title_dict, exdir):
    if not os.path.exists(exdir):
        os.makedirs(exdir)
    filename = os.path.join(exdir, 'pid_title.txt')
    f = open(filename, "w")
    for pid in pid_title_dict.keys():
        f.write("%s\t%s\n" % (pid, pid_title_dict[pid]))
    print ("export %s" % filename)
    f.close()
    
export_title(au_time_title, exdir)
export_pid_title(p_time_title, exdir)

au_set = set()
for au in auid_link_dict.keys():
    au_set.add(au)
    for rau in auid_link_dict[au].keys():
        au_set.add(rau)
print ("author number: %d" % len(au_set))

au_fos_all = [{}, {}, {}, {}]
au_fos_count = [[],[],[],[]]
for i in range(4):
    for au in au_set:
        cursor.execute("SELECT AuthorFOS.FieldOfStudyIDMappedToKeyword FROM AuthorFOS, FieldsOfStudy WHERE AuthorFOS.AuthorID = '%s' and FieldsOfStudy.FieldsOfStudyID = AuthorFOS.FieldOfStudyIDMappedToKeyword and FieldsOfStudy.FieldsOfStudyLevel = 'L%d' " % (au, i))
        fos = []
        load_result(cursor, fos, 'FieldOfStudyIDMappedToKeyword')
        au_fos_all[i][au]  = fos
        au_fos_count[i].append(len(fos))

def export_fos(fos_dicts, exdir):
    if not os.path.exists(exdir):
        os.makedirs(exdir)
    fos_set_len = []
    for i in range(4):
        fos_set = set()
        filename = os.path.join(exdir, 'fos_L%d.txt' % i)
        f = open(filename, 'w')
        count = 0
        for au in fos_dicts[i].keys():
            if len(fos_dicts[i][au]) == 0:
                f.write(au+'\n')
                continue
            f.write(au+'\t')
            for j in range(len(fos_dicts[i][au])-1):
                f.write(fos_dicts[i][au][j]+' ')
                fos_set.add(fos_dicts[i][au][j])
            f.write(fos_dicts[i][au][-1]+'\n')
            fos_set.add(fos_dicts[i][au][-1])
            count += len(fos_dicts[i][au])
        fos_set_len.append(len(fos_set))
        f.close()
        print ("export %s: %d fos" % (filename, count))
    resfile = open(os.path.join(exdir, 'fos.stat'), "w")
    for res in fos_set_len:
        resfile.write(str(res)+'\n')
    resfile.close()

export_fos(au_fos_all, exdir)

fos_au_all = [{}, {}, {}, {}]
fos_au_count = [[], [], [], []]
for i in range(4):
    for au in au_fos_all[i].keys():
        for fos in au_fos_all[i][au]:
            if (fos not in fos_au_all[i].keys()):
                fos_au_all[i][fos] = set()
            fos_au_all[i][fos].add(au)
    for fos in fos_au_all[i].keys():
            setlen = len(fos_au_all[i][fos])
            fos_au_count[i].append(setlen)

def com_export_fos(fos_au_dicts, exdir):
    if not os.path.exists(exdir):
        os.makedirs(exdir)
    for i in range(4):
        filename = os.path.join(exdir, 'c_fos_L%d.txt' % i)
        f = open(filename, 'w')
        for fos in fos_au_dicts[i].keys():
            setlen = len(fos_au_dicts[i][fos])
            if  setlen == 0:
                f.write(fos+'\n')
                continue
            f.write(fos+'\t')
            for j, au in enumerate(fos_au_dicts[i][fos]):
                f.write(au)
                if (j < setlen - 1):
                    f.write(' ')
            f.write('\n')
        f.close()
        print ("export %s %d communities" % (filename, len(fos_au_dicts[i])))

com_export_fos(fos_au_all, exdir)

def export_log(exdir):
	logfile = open(os.path.join(exdir, 'log.txt'), "w")
	# logfile.write("Allconference Num: %d\n" % len(all_conferenceIDs))
	for item in conferenceIDs:
		logfile.write("%s\t" % item)
	logfile.write('\n')
	logfile.write("In Selected %d Conferences:\n" % conference_num)
	logfile.write("Paper Num: %d\n" %  len(pid))
	logfile.write("Link Num: %d\n" % link_count)
	logfile.write("Author Num: %d\n" % len(au_set))
	logfile.write("Build Link Time: %.3f\n" % build_time)


export_log(exdir)