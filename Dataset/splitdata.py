import os
import json
import random
mode = 'cite'
conferences = [
	'AAAI',
	'ACL',
	'SIGCOMM'
]
sp_mode = 's_' + mode


def load_edges(data_dir):
    edges = {}
    aus = set()
    edges_count = 0
    for line in open(os.path.join(data_dir, 'link.txt'), "r"):
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
        for tpl in line[2:-1]:
            tp = tpl.split(' ')
            edges[doc_id][ref_id].append((int(tp[0]), int(tp[1])))
            edges_count += 1
    return edges, aus, edges_count

def export_link(filename, d):
	f = open(filename, "w")
	for dau in d.keys():
		for rau in d[dau].keys():
			if len(d[dau][rau]) == 0:
				continue
			f.write("%s\t%s\t" % (dau, rau))
			for t1, t2 in d[dau][rau]:
				f.write("%d %d\t" % (t1, t2))
			f.write('\n')

def export_sp_result(fdir, d_e, e):
	d_e_filename = os.path.join(fdir, 'del_link.txt')
	export_link(d_e_filename, d_e)
	e_filename = os.path.join(fdir, 'link.txt')
	export_link(e_filename, e)



for conference in conferences:
	print ("Deleting %s" % conference)
	data_dir = os.path.join('data', mode, conference)
	edges, aus, edges_count = load_edges(data_dir)

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
			if dau not in del_edges.keys():
				del_edges[dau] = {}
			if rau not in del_edges[dau].keys():
				del_edges[dau][rau] = []
			for edge in edges[dau][rau]:
				del_edges[dau][rau].append(edge)
				del_edges_count += 1
			edges[dau].pop(rau)

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