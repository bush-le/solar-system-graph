# -*- coding: utf-8 -*-
# Module: file_io.py
# Project: solar-system-graph
# Chức năng: Đọc/Ghi dữ liệu đồ thị ra file JSON

import json
import networkx as nx
import numpy as np

def save_graph_to_json(G, positions, filepath):
    """Lưu đồ thị và tọa độ ra file JSON"""
    data = {
        "nodes": [],
        "links": []
    }
    
    # 1. Lưu Nodes và Tọa độ
    for node in G.nodes():
        pos = positions.get(node, np.array([0,0,0]))
        data["nodes"].append({
            "id": node,
            "x": float(pos[0]),
            "y": float(pos[1]),
            "z": float(pos[2])
        })
        
    # 2. Lưu Edges (Links)
    for u, v, dat in G.edges(data=True):
        data["links"].append({
            "source": u,
            "target": v,
            "weight": dat.get('weight', 1.0)
        })
        
    # Ghi file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True, "File saved successfully."
    except Exception as e:
        return False, str(e)

def load_graph_from_json(filepath):
    """Đọc file JSON và tái tạo đồ thị"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        G = nx.Graph() # Mặc định load ra vô hướng, user có thể chuyển mode sau
        positions = {}
        
        # Tái tạo Nodes
        for node_data in data["nodes"]:
            nid = node_data["id"]
            G.add_node(nid)
            positions[nid] = np.array([
                node_data["x"], 
                node_data["y"], 
                node_data["z"]
            ])
            
        # Tái tạo Edges
        for link in data["links"]:
            G.add_edge(link["source"], link["target"], weight=link["weight"])
            
        return True, G, positions
    except Exception as e:
        return False, None, None