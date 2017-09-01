import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import os
import random
import time
import sys

R = 1000
CC = 6
PI = np.pi
RR = 0.03 # Random Rate

COLORS = [
	'#e60012',
	'#eb6100', 
	'#f39800',
	'#fcc800',
	'#fff100',
	'#cfdb00',
	'#8fc31f',
	'#22ac38',
	'#009944',
	'#009b6b',
	'#009e96',
	'#00a0c1',
	'#00a0e9',
	'#0086d1',
	'#0068b7',
	'#00479d',
	'#1d2088',
	'#601986',
	'#920783',
	'#be0081',
	'#e4007f',
	'#e5006a',
	'#e5004f',
	'#e60033',
	'#303030',
	'#101010'
]

CCMAP = {
	0:5, 1:5, 2:5, 3:5, 4:5, 
	5:5, 6:5, 7:5, 8:0, 9:5, 
	10:5, 11:5, 12:5, 13:5, 14:5, 
	15:1, 16:2, 17:3, 18:5, 19:5, 
	20:5, 21:5, 22:5, 23:4, 24:5
}

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


def hex_to_int(hxs):
	s = hxs[1:]
	r = int(s[:2], 16)
	g = int(s[2:4], 16)
	b = int(s[4:6], 16)
	return r, g, b

def int_to_hex(r, g, b):
	return "#%02x%02x%02x" % (r, g, b)

def ratio_split(v1, v2, lmd):
	return (v1+lmd*v2)/(1+lmd)

def get_node_xyc(au):
	c1, v1 = au[0]
	c2, v2 = au[1]
	cx1 = np.cos(c1/CC*PI*2)*R
	cy1 = np.sin(c1/CC*PI*2)*R
	cx2 = np.cos(c2/CC*PI*2)*R
	cy2 = np.sin(c2/CC*PI*2)*R
	MAXSIZE = 10
	if v1 < 1e-10:
		x = cx2 + random.uniform(-RR*cx2, RR*cx2)
		y = cy2 + random.uniform(-RR*cy2, RR*cy2)
		color = COLORS[c2*round(len(COLORS)/CC)]
		size = MAXSIZE
	else:
		lmd = v2/v1
		size = MAXSIZE * max(v2, v1) / 2.5
		x = ratio_split(cx1, cx2, lmd)
		y = ratio_split(cy1, cy2, lmd)
		xr = random.uniform(-RR, RR)
		# yr = random.uniform(-RR, RR)
		if abs(cx1 - cx2) < 1e-5:
			y = y + y*xr
		else:
			k = (cy1-cy2)/(cx1-cx2)
			b = (cx1*cy2-cx2*cy1)/(cx1-cx2)
			x = x + xr*R
			y = k*x + b
		r1, g1, b1 = hex_to_int(COLORS[c1*round(len(COLORS)/CC)])
		r2, g2, b2 = hex_to_int(COLORS[c2*round(len(COLORS)/CC)])
		r = round(ratio_split(r1, r2, lmd))
		g = round(ratio_split(g1, g2, lmd))
		b = round(ratio_split(b1, b2, lmd))
		color = int_to_hex(r, g, b)

	return x, y, size, color

def load_data(dir, t):
	aus = []
	f = open(os.path.join(dir, "comm_vis_%d.txt" % t), "r")
	# %d %.3f\t%d %.3f\n
	for line in f:
		line = line.strip().split('\t')
		c1, v1 = line[0].split()
		c2, v2 = line[1].split()
		c1 = int(c1)
		c2 = int(c2)
		v1 = float(v1)
		v2 = float(v2)
		c1 = CCMAP[c1]
		c2 = CCMAP[c2]
		if c1 == c2:
			continue
		aus.append([(c1, v1), (c2, v2)])
	return aus

set_type = 'new_big_data'
data_dir = os.path.join('..', 'data', 'test_fos', set_type)
result_dir = os.path.join('..', 'res', 'cdot', 'test_fos', set_type, 'bd_083100')
vis_dir = os.path.join('res', set_type)
save_dir = os.path.join(vis_dir, 'comm_fig')
comm_vis_dir = os.path.join(vis_dir, 'draw_comm_data')
if not os.path.exists(save_dir):
	os.makedirs(save_dir)


draw_year = [2016, 1987]
for t in draw_year:
	t = 2016
	aus = load_data(comm_vis_dir, t)
	pbar = ProgressBar(name="Calc Coordinate Year %d" % t, total=len(aus))
	pbar.start()
	# Xs = [[] for i in range(CC)]
	# Ys = [[] for i in range(CC)]
	ct = 0
	for au in aus:
		x, y, s, c= get_node_xyc(au)
		plt.scatter(x, y, s=s, c=c)
		pbar.move()
		ct += 1
		# if ct == 10000:
		# 	break
	plt.draw()
	plt.savefig(os.path.join(save_dir, 'fig_%d.png' % t), dpi=600)
	# break
