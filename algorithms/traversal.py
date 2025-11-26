# -*- coding: utf-8 -*-
# Module: traversal.py
# Project: solar-system-graph
# Chức năng: Các thuật toán duyệt đồ thị (BFS, DFS) hỗ trợ Animation

import networkx as nx
from collections import deque

def bfs_traversal(G, start_node):
    """
    Thuật toán duyệt theo chiều rộng (BFS).
    Yield: (current_node, visited_nodes, edges_traversed)
    """
    visited = set()
    queue = deque([start_node])
    visited.add(start_node)
    
    # Danh sách cạnh đã duyệt để vẽ
    path_edges = []
    
    while queue:
        current = queue.popleft()
        
        # Trả về trạng thái hiện tại để vẽ UI
        yield current, list(visited), path_edges
        
        # Duyệt các hàng xóm
        neighbors = sorted(list(G.neighbors(current))) # Sort để thứ tự ổn định
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                path_edges.append((current, neighbor))
                # Yield ngay khi tìm thấy cạnh mới
                yield neighbor, list(visited), path_edges

def dfs_traversal(G, start_node):
    """
    Thuật toán duyệt theo chiều sâu (DFS).
    """
    visited = set()
    stack = [start_node]
    path_edges = []
    
    while stack:
        current = stack.pop()
        
        if current not in visited:
            visited.add(current)
            yield current, list(visited), path_edges
            
            neighbors = sorted(list(G.neighbors(current)), reverse=True)
            for neighbor in neighbors:
                if neighbor not in visited:
                    stack.append(neighbor)
                    path_edges.append((current, neighbor))