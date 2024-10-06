from typing import Dict
from networkx import DiGraph
from pyvis.network import Network


def build_nx_graph(episodes_dict: Dict[int, Dict[str, str]]) -> DiGraph:
    '''
    Convert a dict of episodes into a networkx DiGraph.
    '''
    nodes = list(episodes_dict.keys())
    edges = [(i, j) for i, d in episodes_dict.items() for j in d['targets']]
    
    nx_graph = DiGraph()
    nx_graph.add_nodes_from(nodes)
    nx_graph.add_edges_from(edges)
    return nx_graph


def build_nt_graph(episodes_dict: Dict[int, Dict[str, str]], *args, **kwargs) -> Network:
    '''
    Convert a dict of episodes into a pyvis directed Network.
    '''
    nodes = list(episodes_dict.keys())
    edges = [(i, j) for i, d in episodes_dict.items() for j in d['targets']]
    
    nt_graph = Network(directed = True, *args, **kwargs)
    nt_graph.add_nodes(
        nodes = nodes,
        label = [str(i) for i in nodes],
        title = [str(i) for i in nodes],
        color = ['#e33030'] + ['#edc939'] * (len(nodes)-2) + ['#22e051'],
        value = [nodes[-1]] + [str(i) for i in nodes[1:]],
    )
    nt_graph.add_edges(edges)
    return nt_graph


def convert_nx_to_nt_graph(nx_graph: DiGraph, node_colors: Dict[int, str], *args, **kwargs) -> Network:
    '''
    Convert a networkx DiGraph into a pyvis directed Network.
    '''
    nodes = list(nx_graph.nodes())
    edges = list(nx_graph.edges())
    color = [(node_colors[n] if n in node_colors else '#edc939') for n in nodes]
    
    nt_graph = Network(directed = True, *args, **kwargs)
    nt_graph.add_nodes(
        nodes = nodes,
        label = [str(i) for i in nodes],
        title = [str(i) for i in nodes],
        color = color,
        value = [nodes[-1]] + [str(i) for i in nodes[1:]],
    )
    nt_graph.add_edges(edges)
    return nt_graph