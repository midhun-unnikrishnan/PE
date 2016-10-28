# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 21:46:22 2016

@author: midhununnikrishnan
"""

from numbers import Number
import numpy as np
import copy as copy

class directed_graph:
    '''Undirected finite graph represented as an adjacency list.
    Node names can be any dictionary key type, and the entire information
    is represented as a two-level nested dictionary.
    '''
    __nodes = []
    __nodetoN = dict()
    __accepted_leaftypes = [Number] # consider including lists
    __isdag = None # is the graph acyclic
    __istree = None # is the graph a tree
    __ispositive = None # are all edge weights positive
    __istopsorted = False # if the graph is acyclic, is self.__nodes in
                         # topological order
    __dfslog = {}
    
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
        
    def empty(self):
        self.__init__({})
        
    def addnodes(self,node2N:dict={},validate = False):
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
            if key in self.__nodetoN.keys():
                raise Exception('Error: trying to add a node that exists - ' + \
                ' use append')
            if isinstance(val,list):
                self.__nodetoN[key] = dict()
                for val2 in val:
                    self.__nodetoN[key][val2] = 1                
            elif isinstance(val,dict):
                #.copy() safeguards against graph-devalidation
                #if node2N is changed in the parent function
                self.__nodetoN[key] = val.copy() 
            else:
                raise Exception('Invalid dictionary used to define graph')
            
        self.__nodes.extend(node2N.keys())
        if validate:
            self.validate()
            
        # now that the graph structure has changed, the following must be recomputed
        # on demand
        self.__isdag = None
        self.__istopsorted = False
        self.__istree = None
        self.__ispositive = None
        self.__dfslog = {}

        #symmetrize
#        try:
#            for key in node2N.keys():
#                for key2,val2 in self.__nodetoN[key].items():
#                    self.__nodetoN[key2][key] = val2
#        except KeyError:
#            raise Exception('Invalid dictionary used to define/modify graph')

    def add_edge(self,node1,node2,weight=1):
        self.__nodetoN[node1][node2] = weight + self.__nodetoN[node1].get(node2,0)
        # now that the graph structure has changed, the following must be recomputed
        # on demand
        self.__isdag = None
        self.__istopsorted = False
        self.__istree = None
        if weight < 0 and self.__ispositive: 
            self.__ispositive = False  # not anymore
        self.__dfslog = {}
        # self.__nodetoN[node2][node1] = self.__nodetoN[node1][node2]
        
    def delete_edge(self,node1,node2,weight=1):
        try:
            self.__nodetoN[node1][node2] = -weight + self.__nodetoN[node1][node2]
        except KeyError:
            raise Exception('Cannot delete a non-existent edge')
        # self.__nodetoN[node2][node1] = self.__nodetoN[node1][node2]
        if abs(self.__nodetoN[node2][node1]) < 1e-12:
            del self.__nodetoN[node2][node1]
            # del self.__nodetoN[node1][node2]
        # now that the graph structure has changed, the following must be recomputed
        # on demand
        self.__isdag = None # <--- in case graph has one cycle which is broken
        # self.__istopsorted = False <-- top sorting remains valid 
        self.__istree = None # <--- 
        if weight < 0 and self.__ispositive: 
            self.__ispositive = False  # not anymore
        self.__dfslog = {}
            
    def validate(self):
        for key,val in self.__nodetoN.items():
            if not isinstance(val,dict):
                raise Exception('Invalid input used to define/modify graph')
            if key in val.keys():
                del val[key] # self-loops are removed
            for key2,val2 in val.items():
                if key2 not in self.__nodes or not isinstance(val2,Number):
                    raise Exception('Invalid dictionary used to define graph') 
        if set(self.__nodetoN.keys()) != set(self.__nodes):
            raise Exception('Internal mismatch between node and neighbour lists')    
#                elif self.__nodetoN[key2][key] != val2:
#                    raise Exception('Node neighbours are not defined symmetrically')
        
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
#                    if AdjMatrix[j][i] != y:
#                        raise Exception('Adjacency matrix for an undirected' + \
#                        'graph is symmetric')
        return cls(nodetoN)
       
    def copy(self):
        cpy = copy.copy(self)
        return cpy
    
    def addnode(self,node,connections):
        ''' adds a node and connections - beware, argument connections passed by
        reference
        '''
        self.addnodes({node:connections})
        
    def delnodes(self,nodesD,forcevalidate=False):
        ''' delete a node and its connections
        '''
        for node in nodesD:
            del self.__nodetoN[node]
            self.__nodes.remove(node)
            
        for key in self.__nodes:
            self.__nodetoN[key] = {x:y for x,y in self.__nodetoN[key].items() if \
            x not in nodesD}
        if forcevalidate: # for debugging if required
            self.validate()
        
        # now that the graph structure has changed, the following must be recomputed
        # on demand
        self.__isdag = None
        self.__istopsorted = False 
        self.__istree = None
        self.__ispositive = None
        self.__dfslog = {}
    
    def delnode(self,node,forcevalidate=False):
        self.delnodes([node],forcevalidate)
        
    def size(self):
        n = len(self.__nodes)
        m = sum([sum(x.values()) for x in self.__nodetoN.values()])//2
        return (n,m)
    
    def DFS(self,force_eval=False):
        ''' performs depth-first search on the graph. Outputs a dictionary
            with in and out times of the search at each node
        '''
        if len(self.__dfslog) and not force_eval:
            return self.__dfslog
            
        done = {x:False for x in self.__nodes}
        logs = {x:[None,None] for x in self.__nodes}
        
        counter = 0
        
        def iterate(node):
            nonlocal self,done,logs,counter
            if done[node]:
                return
            done[node] = True
            counter += 1
            logs[node][0] = counter
            for neighbor in self.__nodetoN[node].keys():
                iterate(neighbor)
            counter += 1
            logs[node][1] = counter
            
        for node in self.__nodes:
            iterate(node)    
            
        return logs
    
    def Topsort(self,force_eval=False):
        if not self.isdag():
            raise Exception('Graph should be acyclic to allow linearization')
        if self.__istopsorted and not force_eval:
            return
        logs = self.DFS()
        self.__nodes = sorted(self.nodes(),key=lambda x:logs[x][1],reverse=True)
        self.__istopsorted = True
                    
    def dagpath(self,node_start,node_fin):
        self.Topsort()
        istart = self.__nodes.index(node_start)
        iend = self.__nodes.index(node_fin)
        nodeslice = self.__nodes[istart:iend+1]
        dist = {x:np.inf for x in nodeslice}
        pred = {x:None for x in nodeslice}
        dist[node_start] = 0
        for x in nodeslice:
            for nei,length in self.__nodetoN[x].items():
                if dist[x]+length < dist[nei]:
                    dist[nei] = dist[x]+length
                    pred[nei] = x
        stack = [node_fin]
        while stack[-1] != node_start:
            temp = pred[stack[-1]]
            stack.append(temp)
        stack.reverse()
        return (dist[node_fin],stack)
            
    def ford_fulkerson(self,node_start,node_fin):
        raise Exception('FF not implemented')
        
    def shortest_path(self,node_start,node_fin):
        if self.isdag():
            return self.dagpath(node_start,node_fin) # dfs shortest path O(|V|)
        else:
            return self.ford_fulkerson(node_start,node_fin) # dijkstra algorithm is O(|V||E|)
    
    def nodes(self):
        return self.__nodes.copy()
        
    def neighbours(self,node):
        return self.__nodetoN[node].copy()
        
    def isdag(self,force_eval=False):
        if self.__isdag == None or force_eval:
            flag = True
            logs = self.DFS()
            for node in self.__nodes:
                for k in self.__nodetoN[node].keys():
                    if logs[k][0]<logs[node][0] and logs[k][1]>logs[node][1]:
                        flag = False # found a back edge
                        break
                else:
                    continue
                break
            self.__isdag = flag
            
        return self.__isdag
    
    def ispositive(self,force_eval=False):
        if self.__ispositive == None or force_eval:
            self.__ispositive = True
            for node in self.__nodes:
                for v in self.__nodetoN[node].values():
                    if v<0:
                        self.__ispositive = False
                        break
                else:
                    continue
                break 
        return self.__ispositive
        
    def istree(self,force_eval=False):
        if self.__istree == None or force_eval:
            raise Exception('istree unimplemented')
        else:
            return self.__istree    
#        
#    def rand_edge(self,useweights=True):
#        ''' choose a random edge from the graph. If useweights = True
#        then the probability of an edge being chosen is proportional to its
#        weight.
#        '''
#        rnode = self.rand_node(useweights,True)
#        if not useweights:
#            p = [1 for x in self.__nodetoN[rnode].keys()]
#        else:
#            p = [y for x,y in self.__nodetoN[rnode].items()]
#        p = [x/sum(p) for x in p]
#        options = [x for x in self.__nodetoN[rnode].keys()]
#        #typecasting to list because dict_keys dont support indexing 
#        rn2 = rnd.choice(len(options),p=p)
#        rnode2 = options[rn2]
#        if rnode not in self.__nodes or rnode2 not in self.__nodes:
#            flag = [False]
#        return [rnode,rnode2,self.__nodetoN[rnode][rnode2]]
#        
#    def rand_node(self,useedges=False,useweights=False):
#        '''choose a random node from the graph.
#        If useedges == False then a node is chosen uniformly randomly
#        
#        If useedges,useweights == True,False then the probability of choosing a
#        node is proportional to the number of neighbours to it
#        
#        If useedges,useweights == True,True the probability of choosing a node is
#        proportional to the total weight of edges it has connected to it.
#        '''
#        if not useedges:
#            rn = rnd.choice(len(self.__nodes))
#            return self.__nodes[rn]
#            # as to why choice isnt applied directly on the nodes, try evaluating
#            # rnd.choice([1,'2']) a few times
#        elif not useweights:
#            p = [len(self.__nodetoN[x]) for x in self.__nodes]
#        else: 
#            p = [sum(self.__nodetoN[x].values()) for x in self.__nodes]
#        p = [x/sum(p) for x in p]
#        rn = rnd.choice(len(self.__nodes),p=p)
#        return self.__nodes[rn]
#        
#    def contractnodes(self,node1,node2,resultname=None):
#        ''' glue together two nodes, by default the glued node will have
#            the list of glued node-names as its own 'name'.
#            Note that double edges will be represented by adding the two
#            leaf numbers (edge weights)
#        '''
#        flag = []
#        if node1 not in self.__nodes or node2 not in self.__nodes:
#            flag = [False]
#
#        for x in self.__nodetoN.keys():
#            if x not in self.__nodes:
#                pass
#        if resultname == None:
#            resultname = node1
#        for key,val in self.__nodetoN.items():
#            if node2 in val.keys():
#                val[node1] = val.get(node1,0) + val[node2]
#                self.__nodetoN[node1][key] = val[node1]
#                del val[node2]
#                
#        if resultname != node1:
#            self.__nodetoN[resultname] = self.__nodetoN[node1]
#            del self.__nodetoN[node1]
#        try:
#            del self.__nodetoN[node2]
#        except:
#            if node1 not in self.__nodes or node2 not in self.__nodes:
#                flag.append(True)            
#            pass
#        
#        self.__nodes = [x for x in self.__nodetoN.keys()]
        
