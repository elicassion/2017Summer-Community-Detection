import os
import codecs

# doc.txt format:
# auid \t year \t title

# export: 	id_year_title.txt
#				format: {id \t year \t title}
#			trans_doc.txt
#				format: {auid \t year \t doc_id}

conferences = ['AAAI', 'SIGCOMM']
for conference in conferences:
	indir = 'data/test_title/%s' % conference
	# title_set = set()
	id_title = {} 		# id_title[id] = title
	title_id = {}		# title_id[title] = id
	au_title_dict = {} 	# au_title_dict[auid][time] = docid
	infilename = os.path.join(indir, 'docs.txt')
	inff = open(infilename, 'r')
	otfilename = os.path.join(indir, 'trans_docs.txt')
	otff = open(otfilename, 'w')
	count = 0
	for line in inff:
		if line == '\n':
			continue
		item = line.strip().split("\t")
		auid = item[0]
		time = int(item[1])
		title = item[2]
		if auid not in au_title_dict.keys():
			au_title_dict[auid] = {}
		if time not in au_title_dict[auid].keys():
			au_title_dict[auid][time] = set()
		if title not in title_id.keys():
			au_title_dict[auid][time].add(title)
			id_title[count] = (time, title) # for sake, use time and title
			title_id[title] = count
			this_id = count
			count += 1
		else:
			this_id = title_id[title]
		otff.write("%s\t%s\t%s\n" % (auid, str(time), str(this_id)))

	id_title_filename = os.path.join(indir, 'id_year_title.txt')
	idtfff = open(id_title_filename, "w")
	for i in range(count):
		idtfff.write("%s\t%s\t%s\n" % (str(i), str(id_title[i][0]), str(id_title[i][1])))