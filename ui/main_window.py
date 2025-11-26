# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QMessageBox, QPushButton, QStatusBar)
from PyQt6.QtCore import Qt

# Import module nội bộ
from ui.canvas_widget import GraphWidget
from utils.astro_data import AstroDataFetcher
from algorithms.graph_base import SpaceGraph

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Interplanetary Traffic GEM - AstroGraph System")
        self.resize(1200, 800)
        
        # --- 1. CORE LOGIC ---
        self.graph_manager = SpaceGraph()
        
        # --- 2. GUI SETUP ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget) # Chia trái/phải
        
        # Panel Trái (Controls - Sẽ làm kỹ ở bước sau)
        self.left_panel = QVBoxLayout()
        self.btn_load_data = QPushButton("📡 Load NASA Data")
        self.btn_load_data.setMinimumHeight(50)
        self.btn_load_data.clicked.connect(self.start_loading_data)
        
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setStyleSheet("color: gray; font-style: italic;")
        
        self.left_panel.addWidget(self.btn_load_data)
        self.left_panel.addWidget(self.lbl_status)
        self.left_panel.addStretch() # Đẩy lên trên
        
        # Panel Phải (Visualization)
        self.canvas_widget = GraphWidget()
        
        # Thêm vào layout chính (Trái: 2 phần, Phải: 8 phần)
        self.main_layout.addLayout(self.left_panel, 2)
        self.main_layout.addWidget(self.canvas_widget, 8)
        
        # Status Bar
        self.setStatusBar(QStatusBar(self))

    def start_loading_data(self):
        """Bắt đầu thread tải dữ liệu"""
        self.btn_load_data.setEnabled(False)
        self.btn_load_data.setText("Loading coordinates...")
        self.statusBar().showMessage("Contacting JPL Horizons API...")
        
        # Khởi tạo và chạy Thread
        self.fetcher = AstroDataFetcher(use_realtime=True)
        self.fetcher.data_ready.connect(self.on_data_loaded)
        self.fetcher.data_error.connect(self.on_data_error)
        self.fetcher.start()

    def on_data_loaded(self, planet_data):
        """Callback khi tải xong dữ liệu"""
        self.statusBar().showMessage(f"Loaded {len(planet_data)} celestial objects.")
        
        # 1. Reset đồ thị
        self.graph_manager.clear()
        
        # 2. Thêm Node (Hành tinh)
        for name, coords in planet_data.items():
            # coords là (x, y, z)
            self.graph_manager.add_planet(name, coords[0], coords[1], coords[2])
            
        # 3. Tạo kết nối ngẫu nhiên (Demo)
        self.graph_manager.connect_randomly(probability=0.5)
        
        # 4. Vẽ lên Canvas
        self.canvas_widget.plot_graph(
            self.graph_manager.G, 
            self.graph_manager.positions
        )
        
        # Reset UI state
        self.btn_load_data.setText("📡 Reload Data")
        self.btn_load_data.setEnabled(True)
        self.lbl_status.setText(f"Graph Order: {self.graph_manager.G.number_of_nodes()} nodes")

    def on_data_error(self, error_msg):
        QMessageBox.critical(self, "Data Error", error_msg)
        self.btn_load_data.setEnabled(True)
        self.btn_load_data.setText("Retry Data Load")