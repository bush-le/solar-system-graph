# -*- coding: utf-8 -*-
# Module: main_window.py
# Project: solar-system-graph
# Chức năng: Cửa sổ chính - Trung tâm điều khiển và tích hợp mọi module

from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QMessageBox, 
                             QStatusBar, QFileDialog)
from PyQt6.QtCore import QTimer

# --- IMPORT CÁC MODULE GIAO DIỆN ---
from ui.canvas_widget import GraphWidget
from ui.controls import ControlPanel
from ui.dialogs import DataViewDialog

# --- IMPORT CÁC MODULE XỬ LÝ DỮ LIỆU ---
from utils.astro_data import AstroDataFetcher
from algorithms.graph_base import SpaceGraph
import utils.file_io as file_io

# --- IMPORT CÁC THUẬT TOÁN ---
import algorithms.traversal as traversal
import algorithms.shortest_path as sp
import algorithms.mst as mst
import algorithms.flow as flow
import algorithms.eulerian as eulerian

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Interplanetary Traffic GEM - AstroGraph System")
        self.resize(1300, 850)
        
        # --- 1. CORE LOGIC ---
        self.graph_manager = SpaceGraph()
        
        # --- 2. GUI SETUP ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Panel Trái: Điều khiển
        self.control_panel = ControlPanel()
        
        # Panel Phải: Hiển thị đồ thị
        self.canvas_widget = GraphWidget()
        
        # Layout tỉ lệ 3:7
        self.main_layout.addWidget(self.control_panel, 3)
        self.main_layout.addWidget(self.canvas_widget, 7)
        
        # Thanh trạng thái
        self.setStatusBar(QStatusBar(self))
        
        # --- 3. KẾT NỐI TÍN HIỆU (WIRING) ---
        self._connect_signals()

        # --- 4. ANIMATION ENGINE ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_animation_step)
        self.current_algo_generator = None 
        self.is_running = False

    def _connect_signals(self):
        """Kết nối các nút bấm từ ControlPanel với các hàm xử lý tại đây"""
        # Nhóm Dữ liệu & File
        self.control_panel.signal_load_data.connect(self.start_loading_data)
        self.control_panel.signal_save_graph.connect(self.save_graph_file)
        self.control_panel.signal_load_graph.connect(self.load_graph_file)
        
        # Nhóm Công cụ
        self.control_panel.signal_graph_mode.connect(self.change_graph_mode)
        self.control_panel.signal_view_data.connect(self.show_data_dialog)
        self.control_panel.signal_clear_viz.connect(self.reset_visualization)
        
        # Nhóm Thuật toán
        self.control_panel.signal_run_algo.connect(self.execute_algorithm)

    # =========================================================================
    #  PHẦN 1: XỬ LÝ DỮ LIỆU & FILE IO
    # =========================================================================

    def start_loading_data(self):
        self.control_panel.btn_load.setEnabled(False)
        self.control_panel.log("Contacting JPL Horizons API...")
        self.statusBar().showMessage("Downloading NASA data...")
        
        self.fetcher = AstroDataFetcher(use_realtime=True)
        self.fetcher.data_ready.connect(self.on_data_loaded)
        self.fetcher.data_error.connect(self.on_data_error)
        self.fetcher.start()

    def on_data_loaded(self, planet_data):
        self.statusBar().showMessage(f"Data Loaded: {len(planet_data)} objects.")
        self.graph_manager.clear()
        
        # Thêm node
        for name, coords in planet_data.items():
            self.graph_manager.add_planet(name, coords[0], coords[1], coords[2])
        
        # Tạo kết nối ngẫu nhiên
        self.graph_manager.connect_randomly(probability=0.45)
        
        # Cập nhật UI
        self._refresh_ui_after_load()
        self.control_panel.log(f"Graph initialized with {self.graph_manager.G.number_of_edges()} routes.")

    def on_data_error(self, error_msg):
        self.control_panel.log(f"ERROR: {error_msg}")
        QMessageBox.critical(self, "Data Error", error_msg)
        self.control_panel.btn_load.setEnabled(True)

    def save_graph_file(self):
        """Lưu đồ thị ra file JSON"""
        filename, _ = QFileDialog.getSaveFileName(self, "Save Graph", "", "JSON Files (*.json)")
        if filename:
            success, msg = file_io.save_graph_to_json(
                self.graph_manager.G, 
                self.graph_manager.positions, 
                filename
            )
            if success:
                self.control_panel.log(f"💾 Saved successfully to {filename}")
                QMessageBox.information(self, "Saved", "File saved successfully!")
            else:
                QMessageBox.critical(self, "Error", msg)

    def load_graph_file(self):
        """Mở đồ thị từ file JSON"""
        filename, _ = QFileDialog.getOpenFileName(self, "Open Graph", "", "JSON Files (*.json)")
        if filename:
            success, G, positions = file_io.load_graph_from_json(filename)
            if success:
                self.graph_manager.G = G
                self.graph_manager.positions = positions
                self._refresh_ui_after_load()
                self.control_panel.log(f"📂 Loaded graph from {filename}")
            else:
                QMessageBox.critical(self, "Error", "Failed to load file.")

    def _refresh_ui_after_load(self):
        """Hàm phụ trợ để vẽ lại và cập nhật list sau khi Load Data/File"""
        self.canvas_widget.plot_graph(self.graph_manager.G, self.graph_manager.positions)
        self.control_panel.update_planet_list(list(self.graph_manager.G.nodes()))
        self.control_panel.btn_load.setEnabled(True)
        self.control_panel.btn_load.setText("♻ Reload Data")

    # =========================================================================
    #  PHẦN 2: CÔNG CỤ & VIEW
    # =========================================================================

    def change_graph_mode(self, is_directed):
        self.graph_manager.set_directed(is_directed)
        mode = "Directed" if is_directed else "Undirected"
        self.control_panel.log(f"Graph mode changed to: {mode}")
        self.canvas_widget.plot_graph(self.graph_manager.G, self.graph_manager.positions)

    def show_data_dialog(self):
        if self.graph_manager.G.number_of_nodes() == 0:
            QMessageBox.warning(self, "No Data", "Please load data first!")
            return
        dialog = DataViewDialog(self.graph_manager.G, self)
        dialog.exec()

    def reset_visualization(self):
        if self.is_running:
            self.timer.stop()
            self.is_running = False
        self.canvas_widget.plot_graph(self.graph_manager.G, self.graph_manager.positions)
        self.control_panel.log("Visualization reset.")

    # =========================================================================
    #  PHẦN 3: THUẬT TOÁN & ANIMATION (TRÁI TIM CỦA APP)
    # =========================================================================

    def execute_algorithm(self, algo_name, start_node, end_node):
        if self.is_running:
            self.control_panel.log("⚠️ An algorithm is already running. Please wait or reset.")
            return

        G = self.graph_manager.G
        if G.number_of_nodes() == 0:
            QMessageBox.warning(self, "No Data", "Graph is empty.")
            return

        self.control_panel.log(f"🚀 Initializing {algo_name}...")
        
        try:
            # 1. Traversal Algorithms
            if "BFS" in algo_name:
                self.control_panel.log(f"📍 Start: {start_node}")
                self.current_algo_generator = traversal.bfs_traversal(G, start_node)
            
            elif "DFS" in algo_name:
                self.control_panel.log(f"📍 Start: {start_node}")
                self.current_algo_generator = traversal.dfs_traversal(G, start_node)
            
            # 2. Pathfinding
            elif "Dijkstra" in algo_name:
                self.control_panel.log(f"📍 Route: {start_node} ➔ {end_node}")
                self.current_algo_generator = sp.dijkstra_algorithm(G, start_node, end_node)
            
            # 3. MST (Minimum Spanning Tree)
            elif "Prim" in algo_name:
                self.control_panel.log(f"⚡ Prim MST starting at {start_node}")
                self.current_algo_generator = mst.prim_algorithm(G, start_node)
            
            elif "Kruskal" in algo_name:
                self.control_panel.log("⚡ Kruskal MST (Global optimization)")
                self.current_algo_generator = mst.kruskal_algorithm(G)
            
            # 4. Max Flow
            elif "Flow" in algo_name:
                if not G.is_directed():
                    QMessageBox.warning(self, "Mode Error", "Max Flow requires a DIRECTED graph.\nPlease check 'Directed Graph' in Graph Tools.")
                    return
                self.control_panel.log(f"🌊 Max Flow: {start_node} ➔ {end_node}")
                self.current_algo_generator = flow.edmonds_karp(G, start_node, end_node)
            
            # 5. Eulerian Circuit
            elif "Euler" in algo_name:
                self.control_panel.log(f"∞ Eulerian Circuit starting at {start_node}")
                self.current_algo_generator = eulerian.find_eulerian_circuit(G, start_node)
            
            else:
                self.control_panel.log("⚠️ Algorithm logic not found!")
                return

        except Exception as e:
            self.control_panel.log(f"❌ Setup Error: {e}")
            return

        # Start Animation Loop
        self.is_running = True
        self.timer.start(150) # Tốc độ: 150ms/bước

    def run_animation_step(self):
        """Hàm được gọi liên tục bởi QTimer để vẽ từng bước"""
        try:
            # Lấy bước tiếp theo
            step_data = next(self.current_algo_generator)
            
            # Unpack dữ liệu: (Node đang xét, List node đã thăm, List cạnh đường đi)
            current_node, visited_nodes, path_edges = step_data
            
            # Cập nhật giao diện
            self.canvas_widget.plot_graph(
                self.graph_manager.G,
                self.graph_manager.positions,
                path_edges=path_edges,
                highlighted_nodes=visited_nodes
            )
            
        except StopIteration:
            # Khi thuật toán chạy xong
            self.timer.stop()
            self.is_running = False
            self.control_panel.log("✅ Algorithm Finished Successfully.")
            QMessageBox.information(self, "Done", "Mission Accomplished!")
            
        except Exception as e:
            self.timer.stop()
            self.is_running = False
            self.control_panel.log(f"❌ Runtime Error: {e}")