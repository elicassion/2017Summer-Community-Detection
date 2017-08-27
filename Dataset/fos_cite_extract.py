# 0482DB7F Big Data

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
import sys



connection = pymysql.connect(host='127.0.0.1',
                             user='data',
                             password='data',
                             db='mag-new-160205',
                             charset='utf8mb4',
                             port=3306,
                             cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()

class ProgressBar:
	def __init__(self, name = '', total = 0, width = 20):
		self.total = total
		self.width = width
		self.count = 0
		self.name = name
		self.start_time = 0

	def start(self):
		self.start_time = time.time()

	def move(self):
		self.count += 1
		self.showProgress()

	def showProgress(self):
		progress = self.width * self.count / self.total
		elapsed = time.time() - self.start_time
		eta = elapsed * (self.total / self.count - 1)
		sys.stdout.write('%s: [%d/%d] ' % (self.name, self.count, self.total))
		sys.stdout.write('[' + '=' * round(progress) + '>' + '-' * round(self.width - progress) + '] ')
		sys.stdout.write('Elapsed: %ds/ETA: %ds\r' % (round(elapsed), round(eta)))
		if progress == self.width:
			sys.stdout.write('\n')
		sys.stdout.flush()



def load_result(cursor, container, name):
    for row in cursor.fetchall():
        container.append(row[name])
    return container

def load_results(cursor, containers, names):
	for row in cursor.fetchall():
		for container, name in zip(containers, names):
			container.append(row[name])
	return containers

def export_fos(fos_dicts, exdir):
    if not os.path.exists(exdir):
        os.makedirs(exdir)
    filename = os.path.join(exdir, 'fos_L3.txt')
    f = open(filename, 'w')
    count = 0
    for au in fos_dicts.keys():
        if len(fos_dicts[au]) == 0:
            f.write(au+'\n')
            continue
        f.write(au+'\t')
        for j in range(len(fos_dicts[au])-1):
            f.write(fos_dicts[au][j]+' ')
        f.write(fos_dicts[au][-1]+'\n')
        count += len(fos_dicts[au])
    f.close()
    print ("Export %s: %d fos" % (filename, count))


FosName = 'Big data'
cursor.execute("SELECT FieldsOfStudyID FROM FieldsOfStudy WHERE FieldsOfStudyName = '%s'" % FosName)
FosID = cursor.fetchall()[0]['FieldsOfStudyID']
print (FosID)


def export_sonFos(sonfos, sonfosname, exdir):
	sonfos_filename = os.path.join(exdir, "sonfos.txt")
	if not os.path.exists(exdir):
		os.makedirs(exdir)
	sonfos_file = open(sonfos_filename, "w")
	for fosid, fosname in zip(sonfos, sonfosname):
		sonfos_file.write("%s\t%s\n" % (fosid, fosname))
	sonfos_file.close()
	print ("Export %s" % sonfos_filename)

cursor.execute("SELECT FieldsOfStudyID, FieldsOfStudyName From FieldsOfStudy WHERE FieldsOfStudyID IN (SELECT ChildFieldOfStudyID FROM FieldOfStudyHierarchy WHERE ParentFieldOfStudyID='%s')" % FosID)
sonFos = []
sonFosName = []
for row in cursor.fetchall():
	sonFos.append(row['FieldsOfStudyID'])
	sonFosName.append(row['FieldsOfStudyName'])
export_sonFos(sonFos, sonFosName, 'data/test_fos/%s' % FosName)

cursor.execute("SELECT PaperID FROM PaperRefKeywords WHERE FieldOfStudyIDMappedToKeyword = '%s'" % FosID)
pid = set()
for row in cursor.fetchall():
    pid.add(row['PaperID'])
print ("Paper Num: %d" % len(pid))


ref = set()
st_ref = time.time()
# cursor.execute("SELECT PaperID, PaperReferenceID FROM PaperReferences WHERE PaperID IN (SELECT PaperID FROM PaperRefKeywords WHERE FieldOfStudyIDMappedToKeyword = '%s') AND PaperReferenceID IN (SELECT PaperID FROM PaperRefKeywords WHERE FieldOfStudyIDMappedToKeyword = '%s')" % (FosID, FosID))
search_pbar = ProgressBar(name="Searching Ref", total=len(pid))
search_pbar.start()
for paperid in pid:
	# st_sg = time.time()
	cursor.execute("SELECT PaperID, PaperReferenceID FROM PaperReferences WHERE PaperID='%s'" % paperid)
	ref_res = cursor.fetchall()
	for row in ref_res:
		if row['PaperReferenceID'] not in pid:
			continue
		ref.add((row['PaperID'], row['PaperReferenceID']))

	cursor.execute("SELECT PaperID, PaperReferenceID FROM PaperReferences WHERE PaperReferenceID='%s'" % paperid)
	ref_res = cursor.fetchall()
	for row in ref_res:
		if row['PaperID'] not in pid:
			continue
		ref.add((row['PaperID'], row['PaperReferenceID']))
	search_pbar.move()
	
print ("Searching All Time: %.3f" % (time.time() - st_ref))
print (len(ref_res))

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
print ("Build Time: %.3f" % (time.time() - st_build))
print ("Link Count: %d" % link_count)

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
    print ("Export %s" % filename)
    print ("Export %s" % gilename)

export_link(auid_link_dict, 'data/test_fos/%s' % FosName)

def export_title(au_title_dict, exdir):
    # format: auid \t paperid \t year \t title
	if not os.path.exists(exdir):
		os.makedirs(exdir)
	filename = os.path.join(exdir, 'docs.txt')
	f = open(filename, 'w')
	for au in au_title_dict.keys():
		for time, title in au_title_dict[au]:
			f.write(au+'\t'+str(time)+'\t'+title+'\n')
	print ("Export %s" % filename)

def export_pid_title(pid_title_dict, exdir):
    if not os.path.exists(exdir):
        os.makedirs(exdir)
    filename = os.path.join(exdir, 'pid_title.txt')
    f = open(filename, "w")
    for pid in pid_title_dict.keys():
        f.write("%s\t%s\n" % (pid, pid_title_dict[pid]))
    print ("Export %s" % filename)
    f.close()
	
export_title(au_time_title, 'data/test_fos/%s' % FosName)
export_pid_title(p_time_title, 'data/test_fos/%s' % FosName)

au_set = set()
for au in auid_link_dict.keys():
    au_set.add(au)
    for rau in auid_link_dict[au].keys():
        au_set.add(rau)
print ("Author number: %d" % len(au_set))

au_fos_all = {}
au_fos_count = []
for au in au_set:
    cursor.execute("SELECT AuthorFOS.FieldOfStudyIDMappedToKeyword FROM AuthorFOS, FieldsOfStudy WHERE AuthorFOS.AuthorID = '%s' and FieldsOfStudy.FieldsOfStudyID = AuthorFOS.FieldOfStudyIDMappedToKeyword and FieldsOfStudy.FieldsOfStudyLevel = 'L3' ")
    fos = []
    for row in cursor.fetchall():
    	if row['FieldOfStudyIDMappedToKeyword'] in sonFos:
        	fos.append(row[name])
    au_fos_all[au] = fos
    au_fos_count.append(len(fos))

export_fos(au_fos_all, 'data/test_fos/%s' % FosName)

fos_au_all = {}
fos_au_count = []
for au in au_fos_all.keys():
    for fos in au_fos_all[au]:
        if (fos not in fos_au_all.keys()):
            fos_au_all[fos] = set()
        fos_au_all[fos].add(au)
for fos in fos_au_all.keys():
    setlen = len(fos_au_all[fos])
    fos_au_count.append(setlen)

def com_export_fos(fos_au_dicts, exdir):
    if not os.path.exists(exdir):
        os.makedirs(exdir)
    filename = os.path.join(exdir, 'c_fos_L3.txt')
    f = open(filename, 'w')
    for fos in fos_au_dicts.keys():
        setlen = len(fos_au_dicts[fos])
        if  setlen == 0:
            f.write(fos+'\n')
            continue
        f.write(fos+'\t')
        for j, au in enumerate(fos_au_dicts[fos]):
            f.write(au)
            if (j < setlen - 1):
                f.write(' ')
        f.write('\n')
    f.close()
    print ("Export %s %d communities" % (filename, len(fos_au_dicts)))

com_export_fos(fos_au_all, 'data/test_fos/%s' % FosName)
