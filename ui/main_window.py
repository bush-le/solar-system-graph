# -*- coding: utf-8 -*-
# Module: main_window.py
# Project: solar-system-graph
# Chức năng: Cửa sổ chính, tích hợp Controls, Canvas và Animation Engine

from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QMessageBox, QStatusBar)
from PyQt6.QtCore import QTimer

# Import module nội bộ
from ui.canvas_widget import GraphWidget
from ui.controls import ControlPanel
from utils.astro_data import AstroDataFetcher
from algorithms.graph_base import SpaceGraph
# Import mới
import algorithms.mst as mst
from ui.dialogs import DataViewDialog   

# Import thuật toán
import algorithms.traversal as traversal
import algorithms.shortest_path as sp
import algorithms.flow as flow

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
        
        self.control_panel = ControlPanel()
        self.canvas_widget = GraphWidget()
        
        self.main_layout.addWidget(self.control_panel, 3)
        self.main_layout.addWidget(self.canvas_widget, 7)
        self.setStatusBar(QStatusBar(self))
        
        self._connect_signals()

        # --- 3. ANIMATION ENGINE ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_animation_step)
        self.current_algo_generator = None # Biến chứa thuật toán đang chạy
        self.is_running = False

    def _connect_signals(self):
        self.control_panel.signal_load_data.connect(self.start_loading_data)
        self.control_panel.signal_run_algo.connect(self.execute_algorithm)
        self.control_panel.signal_graph_mode.connect(self.change_graph_mode)
        self.control_panel.signal_clear_viz.connect(self.reset_visualization)
        self.control_panel.signal_view_data.connect(self.show_data_dialog) # <--- Mới

    # --- DATA LOADING ---
    def start_loading_data(self):
        self.control_panel.btn_load.setEnabled(False)
        self.control_panel.log("Contacting JPL Horizons API...")
        self.statusBar().showMessage("Downloading data...")
        self.fetcher = AstroDataFetcher(use_realtime=True)
        self.fetcher.data_ready.connect(self.on_data_loaded)
        self.fetcher.data_error.connect(self.on_data_error)
        self.fetcher.start()

    def on_data_loaded(self, planet_data):
        self.statusBar().showMessage(f"Loaded {len(planet_data)} objects.")
        self.graph_manager.clear()
        for name, coords in planet_data.items():
            self.graph_manager.add_planet(name, coords[0], coords[1], coords[2])
        
        # Kết nối ngẫu nhiên để tạo thành mạng lưới
        self.graph_manager.connect_randomly(probability=0.4)
        
        self.control_panel.update_planet_list(list(planet_data.keys()))
        self.control_panel.btn_load.setEnabled(True)
        self.control_panel.btn_load.setText("♻ Reload Data")
        self.canvas_widget.plot_graph(self.graph_manager.G, self.graph_manager.positions)
        self.control_panel.log(f"Graph initialized with {self.graph_manager.G.number_of_edges()} routes.")

    def on_data_error(self, error_msg):
        self.control_panel.log(f"ERROR: {error_msg}")
        QMessageBox.critical(self, "Data Error", error_msg)
        self.control_panel.btn_load.setEnabled(True)

    def show_data_dialog(self):
        if self.graph_manager.G.number_of_nodes() == 0:
            QMessageBox.warning(self, "No Data", "Please load NASA data first!")
            return
            
        dialog = DataViewDialog(self.graph_manager.G, self)
        dialog.exec()

    # --- GRAPH UTILS ---
    def change_graph_mode(self, is_directed):
        self.graph_manager.set_directed(is_directed)
        mode = "Directed" if is_directed else "Undirected"
        self.control_panel.log(f"Mode: {mode}")
        self.canvas_widget.plot_graph(self.graph_manager.G, self.graph_manager.positions)

    def reset_visualization(self):
        if self.is_running:
            self.timer.stop()
            self.is_running = False
        self.canvas_widget.plot_graph(self.graph_manager.G, self.graph_manager.positions)
        self.control_panel.log("Visualization reset.")

    # --- ALGORITHM EXECUTION (TRÁI TIM CỦA APP) ---
    def execute_algorithm(self, algo_name, start_node, end_node):
        if self.is_running:
            self.control_panel.log("⚠️ An algorithm is already running. Please wait or reset.")
            return

        self.control_panel.log(f"🚀 Initializing {algo_name}...")
        
        G = self.graph_manager.G

        # 1. Chọn Generator phù hợp
        try:
            if "BFS" in algo_name:
                self.control_panel.log(f"📍 Start Node: {start_node}")
                self.current_algo_generator = traversal.bfs_traversal(G, start_node)
            elif "DFS" in algo_name:
                self.control_panel.log(f"📍 Start Node: {start_node}")
                self.current_algo_generator = traversal.dfs_traversal(G, start_node)
            elif "Dijkstra" in algo_name:
                self.control_panel.log(f"📍 From {start_node} ➔ {end_node}")
                self.current_algo_generator = sp.dijkstra_algorithm(G, start_node, end_node)
            
            # --- PHẦN MỚI THÊM CHO MST ---
            elif "Prim" in algo_name:
                self.control_panel.log(f"📍 Start Node for Prim: {start_node}")
                self.current_algo_generator = mst.prim_algorithm(G, start_node)
            elif "Kruskal" in algo_name:
                self.current_algo_generator = mst.kruskal_algorithm(G)
            # -----------------------------
            elif "Flow" in algo_name: # Max Flow
                if not G.is_directed():
                    QMessageBox.warning(self, "Warning", "Max Flow requires a Directed Graph!\nPlease switch mode in Graph Tools.")
                    self.control_panel.log("⚠️ Max Flow requires a Directed Graph.")
                    return
                self.control_panel.log(f"🌊 Computing Max Flow: {start_node} ➔ {end_node}")
                self.current_algo_generator = flow.edmonds_karp(G, start_node, end_node)
            
            else:
                self.control_panel.log("⚠️ Algorithm not implemented yet.")
                return
        except Exception as e:
            self.control_panel.log(f"❌ Setup Error: {e}")
            return

        # 2. Bắt đầu Timer Animation
        self.is_running = True
        self.timer.start(100)

    def run_animation_step(self):
        """Hàm này được gọi liên tục bởi QTimer"""
        try:
            # Lấy bước tiếp theo từ thuật toán
            step_data = next(self.current_algo_generator)
            
            # Unpack dữ liệu (Mỗi thuật toán trả về format hơi khác nhau nhưng cơ bản là giống)
            current_node, visited_nodes, path_edges = step_data
            
            # Vẽ lại đồ thị với trạng thái mới
            self.canvas_widget.plot_graph(
                self.graph_manager.G,
                self.graph_manager.positions,
                path_edges=path_edges,       # Các cạnh đang xét/đường đi
                highlighted_nodes=visited_nodes # Các nút đã duyệt
            )
            
        except StopIteration:
            # Thuật toán chạy xong
            self.timer.stop()
            self.is_running = False
            self.control_panel.log("✅ Mission Complete!")
            QMessageBox.information(self, "Success", "Algorithm Execution Finished!")
            
        except Exception as e:
            self.timer.stop()
            self.is_running = False
            self.control_panel.log(f"❌ Runtime Error: {e}")

            