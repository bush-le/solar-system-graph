# -*- coding: utf-8 -*-
# Module: converters.py
# Project: solar-system-graph
# Chức năng: Chuyển đổi định dạng dữ liệu

import networkx as nx
import numpy as np

def graph_to_adj_matrix_text(G):
    """Chuyển ma trận kề thành String đẹp"""
    nodes = list(G.nodes())
    matrix = nx.to_numpy_array(G, nodelist=nodes)
    
    text = "   " + "  ".join([f"{n[:3]:>4}" for n in nodes]) + "\n"
    for i, row in enumerate(matrix):
        row_str = "  ".join([f"{val:4.1f}" if val > 0 else "   ." for val in row])
        text += f"{nodes[i][:3]:>3} {row_str}\n"
    return text

def graph_to_edge_list_text(G):
    """Chuyển danh sách cạnh thành String"""
    text = f"{'Source':<15} | {'Target':<15} | {'Weight'}\n"
    text += "-"*45 + "\n"
    
    for u, v, data in G.edges(data=True):
        w = data.get('weight', 1.0)
        text += f"{u:<15} | {v:<15} | {w:.2f}\n"
    return text