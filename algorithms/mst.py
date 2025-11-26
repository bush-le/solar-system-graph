# -*- coding: utf-8 -*-
# Module: mst.py
# Project: solar-system-graph
# Chức năng: Tìm Cây khung nhỏ nhất (MST) - Prim & Kruskal

import networkx as nx
import heapq

def prim_algorithm(G, start_node=None):
    """
    Thuật toán Prim: Phát triển cây khung từ một đỉnh ban đầu.
    """
    if start_node is None:
        start_node = list(G.nodes())[0]

    mst_edges = []
    visited = {start_node}
    
    # Priority Queue chứa (weight, u, v)
    # Lấy tất cả cạnh nối từ start_node ra ngoài
    edges_candidate = []
    for neighbor in G.neighbors(start_node):
        weight = G[start_node][neighbor].get('weight', 1.0)
        heapq.heappush(edges_candidate, (weight, start_node, neighbor))

    # Bắt đầu vòng lặp
    while edges_candidate:
        weight, u, v = heapq.heappop(edges_candidate)
        
        if v in visited:
            continue
            
        visited.add(v)
        mst_edges.append((u, v))
        
        # Yield trạng thái để vẽ: (Node hiện tại, Các node đã nối, Các cạnh MST)
        yield v, list(visited), mst_edges
        
        # Thêm các cạnh từ node mới (v) vào hàng đợi
        for next_node in G.neighbors(v):
            if next_node not in visited:
                new_weight = G[v][next_node].get('weight', 1.0)
                heapq.heappush(edges_candidate, (new_weight, v, next_node))

# --- Class hỗ trợ cho Kruskal ---
class UnionFind:
    def __init__(self, elements):
        self.parent = {e: e for e in elements}
    
    def find(self, item):
        if self.parent[item] == item:
            return item
        self.parent[item] = self.find(self.parent[item]) # Path compression
        return self.parent[item]
    
    def union(self, a, b):
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a != root_b:
            self.parent[root_a] = root_b
            return True
        return False

def kruskal_algorithm(G, start_node=None):
    """
    Thuật toán Kruskal: Sắp xếp cạnh và nối dần các thành phần liên thông.
    (start_node không dùng trong Kruskal nhưng giữ để đồng bộ tham số)
    """
    # 1. Lấy tất cả các cạnh và sắp xếp theo trọng số
    edges = []
    for u, v, data in G.edges(data=True):
        edges.append((data.get('weight', 1.0), u, v))
    
    edges.sort() # Sắp xếp tăng dần
    
    uf = UnionFind(list(G.nodes()))
    mst_edges = []
    visited_nodes_viz = set() # Chỉ dùng để hiển thị animation
    
    for weight, u, v in edges:
        # Nếu u và v chưa kết nối với nhau -> Chọn cạnh này
        if uf.union(u, v):
            mst_edges.append((u, v))
            visited_nodes_viz.add(u)
            visited_nodes_viz.add(v)
            
            # Yield trạng thái
            yield v, list(visited_nodes_viz), mst_edges
            
    # Yield lần cuối để đảm bảo vẽ đủ
    yield None, list(G.nodes()), mst_edges