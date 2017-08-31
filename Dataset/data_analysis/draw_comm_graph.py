import numpy as np
import matplotlib.plot as plt
import os
import random

R = 300
CC = 34
PI = np.pi
def get_node_xy(au):
	c1, v1 = au[0]
	c2, v2 = au[1]
	cx1 = np.cos(c1/CC*PI)*R
	cy1 = np.sin(c1/CC*PI)*R
	cx2 = np.cos(c2/CC*PI)*R
	cy2 = np.sin(c2/CC*PI)*R
	if v1 < 1e-10:
		x = cx2 + random.random(-0.05*cx2, 0.05*cx2)
		y = cy2 + random.random(-0.05*cy2, 0.05*cy2)
	else:
		lbd = v2/v1
		x = (cx1+lbd*cx2)/(1+lbd)
		x = (cy1+lbd*cy2)/(1+lbd)
		x = x + random.random(-0.05*x, 0.05*x)
		y = y + random.random(-0.05*y, 0.05*y)
	return x, y
