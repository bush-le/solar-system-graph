# -*- coding: utf-8 -*-
# Module: dialogs.py
# Project: solar-system-graph
# Chức năng: Các cửa sổ phụ (Hiển thị ma trận, thông tin)

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QTabWidget, QTextEdit, QPushButton)
import networkx as nx
import numpy as np

class DataViewDialog(QDialog):
    def __init__(self, G, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Graph Data Inspector")
        self.resize(800, 600)
        self.G = G
        
        layout = QVBoxLayout(self)
        
        # Tạo Tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Adjacency Matrix
        self.tab_matrix = QTableWidget()
        self._setup_matrix_tab()
        self.tabs.addTab(self.tab_matrix, "Adjacency Matrix (Ma trận kề)")
        
        # Tab 2: Adjacency List
        self.txt_adj_list = QTextEdit()
        self.txt_adj_list.setReadOnly(True)
        self.txt_adj_list.setStyleSheet("font-family: Consolas; font-size: 14px;")
        self._setup_adj_list_tab()
        self.tabs.addTab(self.txt_adj_list, "Adjacency List (DS Kề)")
        
        # Tab 3: Edge List
        self.tab_edges = QTableWidget()
        self._setup_edge_list_tab()
        self.tabs.addTab(self.tab_edges, "Edge List (DS Cạnh)")
        
        layout.addWidget(self.tabs)
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _setup_matrix_tab(self):
        nodes = list(self.G.nodes())
        n = len(nodes)
        
        # Cấu hình bảng
        self.tab_matrix.setRowCount(n)
        self.tab_matrix.setColumnCount(n)
        self.tab_matrix.setHorizontalHeaderLabels(nodes)
        self.tab_matrix.setVerticalHeaderLabels(nodes)
        
        # Lấy ma trận từ NetworkX
        matrix = nx.to_numpy_array(self.G, nodelist=nodes)
        
        for r in range(n):
            for c in range(n):
                val = matrix[r][c]
                # Nếu val > 0 thì hiển thị trọng số, 0 thì để trống cho dễ nhìn
                text = f"{val:.1f}" if val > 0 else "0"
                item = QTableWidgetItem(text)
                
                # Tô màu nhẹ cho các ô có giá trị
                if val > 0:
                    item.setBackground(util_color(200, 255, 200)) # Xanh nhạt
                    
                self.tab_matrix.setItem(r, c, item)

    def _setup_adj_list_tab(self):
        text = ""
        for node in self.G.nodes():
            neighbors = []
            for nbr, dat in self.G[node].items():
                w = dat.get('weight', 0)
                neighbors.append(f"{nbr}(w={w:.1f})")
            
            line = f"🪐 {node:<10} ➔  {', '.join(neighbors)}\n"
            text += line
            text += "-"*60 + "\n"
        self.txt_adj_list.setText(text)

    def _setup_edge_list_tab(self):
        edges = list(self.G.edges(data=True))
        self.tab_edges.setRowCount(len(edges))
        self.tab_edges.setColumnCount(3)
        self.tab_edges.setHorizontalHeaderLabels(["Start Node", "End Node", "Weight"])
        
        for i, (u, v, data) in enumerate(edges):
            w = data.get('weight', 1.0)
            self.tab_edges.setItem(i, 0, QTableWidgetItem(str(u)))
            self.tab_edges.setItem(i, 1, QTableWidgetItem(str(v)))
            self.tab_edges.setItem(i, 2, QTableWidgetItem(f"{w:.2f}"))

def util_color(r, g, b):
    from PyQt6.QtGui import QColor, QBrush
    return QBrush(QColor(r, g, b))