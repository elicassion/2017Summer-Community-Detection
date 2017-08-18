import os
import json
import random
mode = 'test_title'
conferences = [
	# 'AAAI',
	# 'ACL',
	'SIGCOMM',
	# 'MIXED_100',
	# 'MIXED_1203'
]
sp_mode = 't_cite'


def load_edges(data_dir):
    edges = {}
    re_edges = {}
    aus = set()
    edges_count = 0
    for line in open(os.path.join(data_dir, 't_links.txt'), "r"):
        # line = [i for i in line.split() if i in predictor.uname2uid]
        # print(line)
        line = [i for i in line.split('\t')]
        doc_id = line[0]
        ref_id = line[1]
        aus.add(doc_id)
        aus.add(ref_id)
        if doc_id not in edges.keys():
        	edges[doc_id] = {}
        if ref_id not in edges[doc_id].keys():
        	edges[doc_id][ref_id] = []
        if ref_id not in re_edges.keys():
        	re_edges[ref_id] = {}
        if doc_id not in re_edges[ref_id].keys():
        	re_edges[ref_id][doc_id] = []
        for tpl in line[2:]:
            tp = tpl.split(' ')
            edges[doc_id][ref_id].append((int(tp[0]), int(tp[1]), tp[2], tp[3]))
            re_edges[ref_id][doc_id].append((int(tp[0]), int(tp[1]), tp[3], tp[2]))
            edges_count += 1
    return edges, re_edges, aus, edges_count

def export_t_link(filename, d):
	f = open(filename, "w")
	for dau in d.keys():
		for rau in d[dau].keys():
			if len(d[dau][rau]) == 0:
				continue
			f.write("%s\t%s\t" % (dau, rau))
			for t1, t2, p1, p2 in d[dau][rau]:
				f.write("%d %d %s %s\t" % (t1, t2, p1, p2))
			f.write('\n')

def export_link(filename, d):
	f = open(filename, "w")
	for dau in d.keys():
		for rau in d[dau].keys():
			if len(d[dau][rau]) == 0:
				continue
			f.write("%s\t%s\t" % (dau, rau))
			for t1, t2, p1, p2 in d[dau][rau]:
				f.write("%d %d\t" % (t1, t2))
			f.write('\n')

def export_sp_result(fdir, e, d_e):
	d_e_filename = os.path.join(fdir, 'del_links.txt')
	export_link(d_e_filename, d_e)
	e_filename = os.path.join(fdir, 'links.txt')
	export_link(e_filename, e)

	t_d_e_filename = os.path.join(fdir, 't_del_links.txt')
	export_t_link(t_d_e_filename, d_e)
	t_e_filename = os.path.join(fdir, 't_links.txt')
	export_t_link(t_e_filename, e)



for conference in conferences:
	print ("Deleting %s" % conference)
	data_dir = os.path.join('data', mode, conference)
	edges, re_edges, aus, edges_count = load_edges(data_dir)

	del_edges = {}
	del_edges_count = 0
	print ("all edges: %d" % edges_count)
	print ("all aus: %d" % len(aus))

	while del_edges_count < edges_count * 0.2:
		if del_edges_count and del_edges_count % int(edges_count * 0.02) == 0:
			print ("deleted edges: %d" % del_edges_count)

		dau = random.sample(edges.keys(), 1)[0]
		if len(edges[dau]) > 1:
			rau = random.sample(edges[dau].keys(), 1)[0]
			if rau in re_edges.keys() and len(re_edges[rau]) > 1:
				if dau not in del_edges.keys():
					del_edges[dau] = {}
				if rau not in del_edges[dau].keys():
					del_edges[dau][rau] = []
				for edge in edges[dau][rau]:
					del_edges[dau][rau].append(edge)
					del_edges_count += 1
				edges[dau].pop(rau)
				re_edges[rau].pop(dau)

			# if rau in edges.keys() and len(edges[rau]) > 1:
			# 	if dau in edges[rau].keys():
			# 		if rau not in del_edges.keys():
			# 			del_edges[rau] = {}
			# 		if dau not in del_edges[rau].keys():
			# 			del_edges[rau][dau] = []
			# 		for edge in edges[rau][dau]:
			# 			del_edges[rau][dau].append(edge)
			# 			del_edges_count += 1
			# 		edges[rau].pop(dau)

	sp_data_dir = os.path.join('data', sp_mode, conference)
	if not os.path.exists(sp_data_dir):
		os.makedirs(sp_data_dir)
	export_sp_result(sp_data_dir, edges, del_edges)