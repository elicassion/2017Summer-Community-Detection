import json
import os
import codecs
# *.timeline format:
# comm_line_number: exist_time_step=real_comm_id

# so birthdeath and mergesplit remain to do
gen_data_path = os.path.join('..', '..', 'gen_data')
cvt_data_path = os.path.join('..', '..', 'data', 'gen')
if not os.path.exists(cvt_data_path):
	os.mkdirs(cvt_data_path)
prefixs = ["switch", "birthdeath", "expand", "hide", "mergesplit"]
t_steps = 20
baseyear = 1989
for prefix in prefixs:
	# comms_years derive format:
	# year comm_number
	# comm_id \t au au au...
	# ...
	# \n
	# year comm_number

	# au_comm_years derive format:
	# au \t comm,year,year,year,... comm,year,year,year,...
	# ...
	# comm_au_years = []
	au_comm_years = []
	cvt_file_dir = os.path.join(cvt_data_path, prefix)
	if not os.path.exists(cvt_file_dir):
		os.mkdirs(cvt_file_dir)
	comm_au_years_file = open(os.path.join(cvt_file_dir, "comm_au.txt"), "w")
	au_comm_years_file = open(os.path.join(cvt_file_dir, "au_comm.txt"), "w")
	for t_step in range(1, t_steps+1):
		comm_filename = os.path.join(gen_data_path, "%s.t%02d.comm" % (prefix, t_step))
		edges_filename = os.path.join(gen_data_path, "%s.t%02d.edges" % (prefix, t_step))

		# convert comms

		# comm_au = []
		au_comm = {}
		cf = open(comm_filename, "r")
		lines = cf.read().split('\n')[:-1]
		comm_au_years_file.write("%d %d\n" % (baseyear+t_step, len(lines)))
		for cid, line in enumerate(lines):
			members = line.split(' ')[:-1]
			comm_au_years_file.write("%d\t" % cid)
			for mem in members[:-1]:
				comm_au_years_file.write("%s " % mem)
				if mem not in au_comm.keys():
					au_comm[mem] = {}
				if cid not in au_comm[mem].keys():
					au_comm[mem][cid] = set()
				au_comm[mem][cid].add(baseyear+t_step)
			comm_au_years_file.write("%s\n" % members[-1])
		comm_au_years_file.write("\n")
		au_comm_years.append(au_comm)
		cf.close()


		# convert links
		edges = []
		ef = open(edges_filename, "r")
		for link in ef.read().split('\n')[:-1]:
			tpl = link.split(' ')
			edge = {}
			edge['id'] = ""
			edge['lineStyle'] = {'normal':{}}
			edge['name'] = ""
			edge['source'] = tpl[0]
			edge['target'] = tpl[1]
			edges.append(edge)
		ef.close()
		graph = {'nodes': nodes, 'links': edges}
		graph_dumpfile = open(os.path.join('..', 'data', '%s.t%02d.json' % (prefix, t_step)), "w")
		json.dump(graph, graph_dumpfile)
		graph_dumpfile.close()