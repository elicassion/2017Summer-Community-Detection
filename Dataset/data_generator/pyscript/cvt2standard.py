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
	# comm comm comm...
	# ...
	# \n
	# year comm_number

	# au_comm_years derive format:
	# au \t comm,year,year,year,... comm,year,year,year,...
	# ...
	comms_years = []
	for t_step in range(1, t_steps+1):
		comm_filename = os.path.join(gen_data_path, "%s.t%02d.comm" % (prefix, t_step))
		edges_filename = os.path.join(gen_data_path, "%s.t%02d.edges" % (prefix, t_step))
		cvt_file_dir = os.path.join(cvt_data_path, prefix)
		if not os.path.exists(cvt_file_dir):
			os.mkdirs(cvt_file_dir)
		node_set = set()
		nodes = []
		edges = []
		cf = open(comm_filename, "r")
		maxn = 0
		for cid, line in enumerate(cf.read().split('\n')[:-1]):
			members = line.split(' ')[:-1]
			for mem in members:
				if int(mem) not in node_set:
					node_set.add(int(mem))
					
			
		cf.close()
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