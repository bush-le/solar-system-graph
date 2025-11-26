# -*- coding: utf-8 -*-
# Module: controls.py
# Project: solar-system-graph
# Chức năng: Panel điều khiển bên trái (Chọn thuật toán, Nút bấm, Console log)

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QComboBox, 
                             QPushButton, QLabel, QCheckBox, QTextEdit, QFormLayout)
from PyQt6.QtCore import pyqtSignal

class ControlPanel(QWidget):
    # Định nghĩa các Tín hiệu (Signals) để giao tiếp với Main Window
    signal_load_data = pyqtSignal()            # Yêu cầu tải dữ liệu
    signal_run_algo = pyqtSignal(str, str, str) # (Tên thuật toán, Start Node, End Node)
    signal_graph_mode = pyqtSignal(bool)       # True = Có hướng, False = Vô hướng
    signal_clear_viz = pyqtSignal()            # Xóa màu vẽ cũ
    signal_view_data = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        
        # --- GROUP 1: DỮ LIỆU ---
        grp_data = QGroupBox("1. System Data")
        layout_data = QVBoxLayout()
        
        self.btn_load = QPushButton("📡 Connect NASA API")
        self.btn_load.clicked.connect(self.signal_load_data.emit)
        self.btn_load.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 8px;")
        
        layout_data.addWidget(self.btn_load)
        grp_data.setLayout(layout_data)
        
        # --- GROUP 2: CẤU HÌNH ĐỒ THỊ ---
        grp_config = QGroupBox("2. Graph Tools")
        layout_config = QVBoxLayout()
        
        self.chk_directed = QCheckBox("Directed Graph (Có hướng)")
        self.chk_directed.toggled.connect(self.signal_graph_mode.emit)
        
        # Nút Mới: Xem dữ liệu
        self.btn_view_data = QPushButton("📊 View Matrices & Lists")
        self.btn_view_data.setStyleSheet("background-color: #8e44ad; color: white;")
        # Chúng ta cần thêm signal cho nút này, nhưng để đơn giản 
        # ta sẽ connect trực tiếp trong main_window sau, 
        # hoặc khai báo signal mới ở đầu class.
        
        layout_config.addWidget(self.chk_directed)
        layout_config.addWidget(self.btn_view_data) # <--- Thêm vào layout
        grp_config.setLayout(layout_config)

        # --- GROUP 3: THUẬT TOÁN ---
        grp_algo = QGroupBox("3. Algorithms & Navigation")
        layout_algo = QVBoxLayout()
        form_layout = QFormLayout()

        # Chọn thuật toán
        self.combo_algo = QComboBox()
        self.combo_algo.addItems([
            "BFS (Breadth-First Search)", 
            "DFS (Depth-First Search)",
            "Dijkstra (Shortest Path)",
            "MST (Prim Algorithm)",
            "MST (Kruskal Algorithm)"
        ])
        
        # Chọn điểm đầu - cuối
        self.combo_start = QComboBox()
        self.combo_end = QComboBox()
        
        form_layout.addRow("Algorithm:", self.combo_algo)
        form_layout.addRow("Start Node:", self.combo_start)
        form_layout.addRow("Target Node:", self.combo_end)
        
        # Nút chạy
        self.btn_run = QPushButton("🚀 EXECUTE MISSION")
        self.btn_run.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        self.btn_run.clicked.connect(self._on_run_clicked)
        
        # Nút Reset màu
        self.btn_clear = QPushButton("Reset Visualization")
        self.btn_clear.clicked.connect(self.signal_clear_viz.emit)

        layout_algo.addLayout(form_layout)
        layout_algo.addWidget(self.btn_run)
        layout_algo.addWidget(self.btn_clear)
        grp_algo.setLayout(layout_algo)

        # --- GROUP 4: LOG HỆ THỐNG ---
        grp_log = QGroupBox("4. Mission Log")
        layout_log = QVBoxLayout()
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("background-color: #2c3e50; color: #00ff00; font-family: Consolas;")
        layout_log.addWidget(self.txt_log)
        grp_log.setLayout(layout_log)

        # Thêm tất cả vào layout chính
        layout.addWidget(grp_data)
        layout.addWidget(grp_config)
        layout.addWidget(grp_algo)
        layout.addWidget(grp_log)
        layout.addStretch()

    def update_planet_list(self, planets):
        """Cập nhật danh sách hành tinh vào ComboBox sau khi tải dữ liệu"""
        self.combo_start.clear()
        self.combo_end.clear()
        
        self.combo_start.addItems(planets)
        self.combo_end.addItems(planets)
        
        # Mặc định chọn Earth -> Mars
        if "Earth" in planets: self.combo_start.setCurrentText("Earth")
        if "Mars" in planets: self.combo_end.setCurrentText("Mars")
        
        self.log(f"System updated: Found {len(planets)} celestial objects.")

    def log(self, message):
        """Ghi log ra màn hình"""
        self.txt_log.append(f">> {message}")
        # Tự động cuộn xuống dưới cùng
        self.txt_log.verticalScrollBar().setValue(self.txt_log.verticalScrollBar().maximum())

    def _on_run_clicked(self):
        """Xử lý sự kiện bấm nút chạy"""
        algo = self.combo_algo.currentText()
        start = self.combo_start.currentText()
        end = self.combo_end.currentText()
        
        if not start or not end:
            self.log("ERROR: Data not loaded properly.")
            return

        self.signal_run_algo.emit(algo, start, end)