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
nodes = []
edges = []
cf = open(comm_filename, "r")
maxn = 0
for cid, line in enumerate(cf.read().split('\n')[:-1]):
	members = line.split(' ')[:-1]
	for mem in members:
		mem = int(mem)
		if mem > maxn:
			maxn = mem
for i in range(1, maxn+1):
	node = {}
	node['attributes'] = {'modualrity_class': cid}
	node['catagory'] = cid
	node['id'] = str(i)
	node['itemStyle'] = {'label':{'normal':{'show':False}}}
	node['name'] = str(i)
	node['symbolSize'] = 20
	node['value'] = 20
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
