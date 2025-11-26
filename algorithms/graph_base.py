# -*- coding: utf-8 -*-
# Module: graph_base.py
# Project: solar-system-graph
# Chức năng: Quản lý cấu trúc dữ liệu đồ thị (NetworkX wrapper)

import networkx as nx
import numpy as np

class SpaceGraph:
    def __init__(self):
        # Mặc định là đồ thị Vô hướng
        self.G = nx.Graph()
        self.is_directed = False
        
        # Lưu trữ tọa độ hiển thị {tên_node: (x, y, z)}
        self.positions = {}

    def set_directed(self, directed: bool):
        """Chuyển đổi kiểu đồ thị (Yêu cầu A.4)"""
        self.is_directed = directed
        if directed:
            self.G = self.G.to_directed()
        else:
            self.G = self.G.to_undirected()

    def add_planet(self, name, x, y, z):
        """Thêm một nút (Hành tinh)"""
        self.G.add_node(name)
        self.positions[name] = np.array([x, y, z])

    def add_route(self, u, v, weight=1.0):
        """Thêm một cạnh (Tuyến đường)"""
        # Nếu đã có cạnh, cập nhật trọng số
        self.G.add_edge(u, v, weight=weight)

    def calculate_distance(self, u, v):
        """Tính khoảng cách Euclidean giữa 2 hành tinh"""
        if u in self.positions and v in self.positions:
            p1 = self.positions[u]
            p2 = self.positions[v]
            return np.linalg.norm(p1 - p2)
        return 0.0

    def connect_randomly(self, probability=0.4):
        """
        Tạo các cạnh ngẫu nhiên để test.
        Trọng số = Khoảng cách thực tế.
        """
        nodes = list(self.G.nodes())
        import random
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if random.random() < probability:
                    u, v = nodes[i], nodes[j]
                    dist = self.calculate_distance(u, v)
                    self.add_route(u, v, weight=round(dist, 2))

    def get_adjacency_matrix(self):
        """Trả về ma trận kề (NumPy array) và danh sách node"""
        nodes = list(self.G.nodes())
        matrix = nx.to_numpy_array(self.G, nodelist=nodes)
        return nodes, matrix
    
    def clear(self):
        self.G.clear()
        self.positions.clear()