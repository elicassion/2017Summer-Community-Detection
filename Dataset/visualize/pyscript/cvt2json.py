# link file ".edges" format:
# 	from to[no space]
#	[last one more empty line]


# comm file ".comm" format:
#	[linenumber=commid]
#	member1 member2 [has space]
#	[last one more empty line]
import json
import os
import codecs
gen_data_path = os.path.join('..', '..', 'gen_data')
prefix = "birthdeath"
t_step = 5
comm_filename = os.path.join(gen_data_path, "%s.t%02d.comm" % (prefix, t_step))
edges_filename = os.path.join(gen_data_path, "%s.t%02d.edges" % (prefix, t_step))
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
			node = {}
			node['attributes'] = {'modularity_class': cid}
			node['category'] = cid
			node['id'] = mem
			node['itemStyle'] = {'label':{'normal':{'show':False}}}
			node['name'] = mem
			node['symbolSize'] = 5
			node['value'] = 20
			node['x'] = None
			node['y'] = None
			nodes.append(node)
	
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
