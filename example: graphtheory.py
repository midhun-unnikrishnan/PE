# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 06:52:56 2016

@author: midhununnikrishnan
"""


import graphtheory as gt
import numpy as np

A = gt.directed_graph()
M = np.matrix([[131,673,234,103,18],
[201,96,342,965,150],
[630,803,746,422,111],
[537,699,497,121,956],
[805,732,524,37,331]])
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        A.addnode((i,j),[])
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        if i<M.shape[0]-1:
            A.add_edge((i,j),(i+1,j),M[i+1,j])
        if j<M.shape[1]-1:
            A.add_edge((i,j),(i,j+1),M[i,j+1])
dist,path = A.shortest_path((0,0),(4,4))
