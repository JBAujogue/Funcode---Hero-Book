
import sys
import os
from io import open, BytesIO, StringIO

# data
import pandas as pd

# graph
import networkx as nx
import pyvis.network as nt





#**********************************************************
#*                       content                          *
#**********************************************************

def build_nx_graph(episode_dict: dict):
    episode_ids = list(episode_dict.keys())
    edges = [(i, j[0]) for i, d in episode_dict.items() for j in d['targets']]
    
    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from(episode_ids)
    nx_graph.add_edges_from(edges)
    return nx_graph



def build_nt_graph(episode_dict: dict, height = 1200, width = 1980, notebook = False):
    episode_ids = list(episode_dict.keys())
    edges = [(i, j[0]) for i, d in episode_dict.items() for j in d['targets']]
    
    nt_graph = nt.Network(directed = True, height = height, width = width, notebook = notebook)
    nt_graph.add_nodes(
        nodes = episode_ids,
        label = [str(i) for i in episode_ids],
        title = [str(i) for i in episode_ids],
        color = ['#e33030'] + ['#edc939'] * (len(episode_ids)-2) + ['#22e051'],
        value = [episode_ids[-1]] + [str(i) for i in episode_ids[1:]],
    )
    nt_graph.add_edges(edges)
    return nt_graph



def convert_nx_to_nt_graph(nx_graph, node_colors = {}, height = 1200, width = 1980, notebook = False):
    nodes = list(nx_graph.nodes())
    edges = list(nx_graph.edges())
    color = [(node_colors[n] if n in node_colors else '#edc939') for n in nodes]
    
    nt_graph = nt.Network(directed = True, height = height, width = width, notebook = notebook)
    nt_graph.add_nodes(
        nodes = nodes,
        label = [str(i) for i in nodes],
        title = [str(i) for i in nodes],
        color = color, # (['#e33030'] + ['#edc939'] * (len(nodes)-2) + ['#22e051'])
        value = [nodes[-1]] + [str(i) for i in nodes[1:]],
    )
    nt_graph.add_edges(edges)
    return nt_graph