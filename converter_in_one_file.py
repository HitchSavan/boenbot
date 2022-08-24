#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np, os

from numpy.core.defchararray import array

cache_path = os.getcwd()+'/casch/2000000002'
files = os.listdir(path = cache_path)
cumout = np.zeros((1, 1, 1))
i = j = 0

for pic in files:
	if 'diff.npz' not in pic:
		continue
	data = np.load(cache_path+'/'+pic)
	notBase = data['arr_0']
	data.close()
	cumout = np.append(cumout, [notBase, [pic]])
np.savez_compressed(cache_path+'/big_pic', cumout)

data = np.load(cache_path+'/big_pic.npz', allow_pickle=True)
testAll = data['arr_0']
data.close()

for item in testAll:
	if type(item) == np.ndarray:
		i += 1
	elif type(item) == list:
		print(item[0])
	j += 1

print(testAll)
print(i)
print(j)