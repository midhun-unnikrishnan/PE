# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 21:46:22 2016

@author: midhununnikrishnan
"""

from numbers import Number
import numpy as np

class undirected_graph:
    '''Undirected finite graph represented as an adjacency list.
    Node names are not permitted to be tuples, as this interferes with 
    the internal representation of the Adjacency list.
    '''
    nodes = []
    nodetoN = dict()
    __accepted_leaftypes = [Number] # consider including lists
    # multiple-edges between two nodes are currently represented using weightings
    # on edges, viz. the leaf n represents n edges. The class currently does
    # not support multiple, weighted edges - not that I can conceive of an application
    # for these
    
    def __init__(self,node2N:dict={}):
        '''warning: constructor takes argument by reference, and may
        modify it into a standard input format - send explicit object
        by using dict.copy() if this is to be avoided.
        '''
        self.addnodes(node2N)
        
    def addnodes(self,node2N:dict={}):
        '''add multiple new nodes and connections. 
        If a graph is being defined without edge-weights (i.e. weight = 1),
        then a dictionary of the form {node1:[neigh1,neigh2,...],key2:...}
        is supplied, where neigh1 etc are nodes themselves.
        If edge-weights are specified, then nested dictionaries of the form 
        {node1:{neigh1:weight1,neigh2:weight2,...},...}
        need to be supplied instead.
        Note that in either case the entire input must be consistent in format.
        '''
        for key,val in node2N.items():
            if key in self.nodetoN.keys():
                raise Exception('Error: trying to add a node that exists - ' + \
                ' use append')
            if isinstance(val,list):
                self.nodetoN[key] = dict()
                for val2 in val:
                    self.nodetoN[key][val2] = 1                
            elif isinstance(val,dict):
                #.copy() safeguards against graph-devalidation
                #if node2N is changed in the parent function
                self.nodetoN[key] = val.copy() 
            else:
                raise Exception('Invalid dictionary used to define graph')
        try:
            for key in node2N.keys():
                for key2,val2 in self.nodetoN[key].items():
                    self.nodetoN[key2][key] = val2
        except KeyError:
            raise Exception('Invalid dictionary used to define/modify graph')
            
        self.nodes = self.nodetoN.keys()
        self.validate()
        
    def add_edge(self,node1,node2,weight=1):
        self.nodetoN[node1][node2] = weight + self.nodetoN[node1].get(node2,0)
        self.nodetoN[node2][node1] = self.nodetoN[node1][node2]
        
    def delete_edge(self,node1,node2,weight=1):
        self.nodetoN[node1][node2] = -weight + self.nodetoN[node1].get(node2,0)
        self.nodetoN[node2][node1] = self.nodetoN[node1][node2]
        if abs(self.nodetoN[node2][node1]) < 1e-12:
            del self.nodetoN[node2][node1]
            del self.nodetoN[node1][node2]
            
    def validate(self):
        for key,val in self.nodetoN.items():
            if not isinstance(val,dict):
                raise Exception('Invalid input used to define/modify graph')
            for key2,val2 in val.items():
                if key2 == key:
                    continue # self-loops are ignored
                if key2 not in self.nodes or not isinstance(val2,Number):
                    raise Exception('Invalid dictionary used to define graph')
                elif self.nodetoN[key2][key] != val2:
                    raise Exception('Node neighbours are not defined symmetrically')
        
    @classmethod
    def fromAM(cls,AdjMatrix:np.matrix):
        '''constructer using adjacency matrix. 
           Does not support multiple edges - use the primitive constructor if
           this feature is required, or represent these as numbers other than
           1 in the adjacency matrix
        '''
        if len(AdjMatrix) != len(AdjMatrix[1]):
            raise(Exception('invalid adjacency matrix'))
        nodetoN = {k: {} for k in range(len(AdjMatrix))}
        for i,x in enumerate(AdjMatrix):
            for j,y in enumerate(x):
                if abs(y) > 1e-12:
                    nodetoN[i][j] = y
                    if AdjMatrix[j][i] != y:
                        raise Exception('Adjacency matrix for an undirected' + \
                        'graph is symmetric')
        return cls(nodetoN)
        
    def copy(self):
        return type(self)(self.nodetoN.copy())
    
    def addnode(self,node,connections):
        ''' adds a node and connections - beware, argument connections passed by
        reference
        '''
        self.addnodes({node:connections})
        
    def delnodes(self,nodesD,forcevalidate=False):
        ''' delete a node and its connections
        '''
        for node in nodesD:
            del self.nodetoN[node]
        self.nodes = self.nodetoN.keys()
        for key in self.nodes:
            self.nodetoN[key] = {x:y for x,y in self.nodetoN[key].items() if \
            x not in nodesD}
        if forcevalidate: # for debugging if required
            self.validate()
    
    def delnode(self,node,forcevalidate=False):
        self.delnodes([node],forcevalidate)
        
    def contractnodes(self,node1,node2,resultname=None):
        ''' glue together two nodes, by default the glued node will have
            the name of the first specified node.
            Note that double edges will be represented by adding the two
            leaf numbers (edge weights)
        '''
        if resultname == None:
            resultname = node1
        for key,val in self.nodetoN.items():
            if node2 in val.keys():
                val[node1] = val.get(node1,0) + val[node2]
                self.nodetoN[node1][key] = val[node1]
                del val[node2]
        if resultname != node1:
            self.nodetoN[resultname] = self.nodetoN[node1]
            del self.nodetoN[node1]
        del self.nodetoN[node2]
        
        
        
            