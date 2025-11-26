# -*- coding: utf-8 -*-
# Module: flow.py
# Project: solar-system-graph
# Chức năng: Tìm luồng cực đại (Max Flow) dùng thuật toán Edmonds-Karp (cải tiến của Ford-Fulkerson)

import networkx as nx
from collections import deque

def edmonds_karp(G, source, sink):
    """
    Tìm luồng cực đại từ source đến sink.
    Yield: (current_node, visited_nodes, flow_edges)
    """
    # Tạo đồ thị thặng dư (Residual Graph)
    # Copy đồ thị gốc để không làm hỏng dữ liệu chính
    R = G.copy() if G.is_directed() else G.to_directed()
    
    max_flow = 0
    path_edges_viz = []
    
    while True:
        # 1. Tìm đường tăng luồng bằng BFS
        parent = {node: None for node in R.nodes()}
        queue = deque([source])
        path_found = False
        
        # BFS tìm đường đi ngắn nhất trong đồ thị thặng dư
        while queue:
            u = queue.popleft()
            if u == sink:
                path_found = True
                break
            
            for v in R.neighbors(u):
                # Chỉ đi qua cạnh còn sức chứa (capacity > 0) và chưa duyệt
                capacity = R[u][v].get('weight', 0) # Coi weight là capacity
                if parent[v] is None and capacity > 0:
                    parent[v] = u
                    queue.append(v)
        
        # Nếu không còn đường tăng luồng -> Dừng
        if not path_found:
            yield sink, list(R.nodes()), path_edges_viz
            break

        # 2. Tính bottleneck (dung lượng nhỏ nhất trên đường đi tìm được)
        path_flow = float('inf')
        v = sink
        current_path = [] # Để vẽ
        
        while v != source:
            u = parent[v]
            current_path.append((u, v))
            capacity = R[u][v].get('weight', 0)
            path_flow = min(path_flow, capacity)
            v = u
            
        max_flow += path_flow
        path_edges_viz.extend(current_path)

        # 3. Cập nhật đồ thị thặng dư & Yield animation
        v = sink
        visited_nodes = set()
        while v != source:
            u = parent[v]
            visited_nodes.add(u)
            visited_nodes.add(v)
            
            # Giảm capacity cạnh xuôi
            R[u][v]['weight'] -= path_flow
            
            # Tăng capacity cạnh ngược (nếu chưa có thì tạo)
            if R.has_edge(v, u):
                R[v][u]['weight'] += path_flow
            else:
                R.add_edge(v, u, weight=path_flow)
                
            v = u
            
        # Yield trạng thái để vẽ đường vừa tăng luồng
        yield source, list(visited_nodes), current_path