# -*- coding: utf-8 -*-
# Module: shortest_path.py
# Project: solar-system-graph
# Chức năng: Thuật toán tìm đường ngắn nhất (Dijkstra)

import networkx as nx
import heapq

def dijkstra_algorithm(G, start, end):
    """
    Tìm đường ngắn nhất dùng Dijkstra.
    Yield: (current_node, visited_nodes, path_edges)
    """
    # Priority Queue: (khoảng_cách, node_hiện_tại)
    pq = [(0, start)]
    
    distances = {node: float('inf') for node in G.nodes()}
    distances[start] = 0
    
    previous = {node: None for node in G.nodes()}
    visited = set()
    path_edges_viz = [] # Chỉ dùng để hiển thị quá trình duyệt
    
    while pq:
        current_dist, current_node = heapq.heappop(pq)
        
        if current_node in visited:
            continue
        visited.add(current_node)
        
        # Nếu đã đến đích -> Dừng và Reconstruct path
        if current_node == end:
            final_path = []
            curr = end
            while curr is not None:
                prev = previous[curr]
                if prev is not None:
                    final_path.append((prev, curr))
                curr = prev
            
            # Yield lần cuối cùng với đường đi hoàn chỉnh
            yield current_node, list(visited), final_path
            return

        # Yield trạng thái đang tìm kiếm
        yield current_node, list(visited), path_edges_viz
        
        for neighbor in G.neighbors(current_node):
            weight = G[current_node][neighbor].get('weight', 1.0)
            distance = current_dist + weight
            
            # Chỉ thêm vào visual nếu chưa duyệt
            if neighbor not in visited:
                path_edges_viz.append((current_node, neighbor))
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))