# -*- coding: utf-8 -*-
# Module: canvas_widget.py
# Project: solar-system-graph
# Chức năng: Widget hiển thị đồ thị 3D nhúng trong PyQt6

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Cấu hình Style cho Matplotlib đẹp hơn
plt.style.use('dark_background')

class MplCanvas(FigureCanvas):
    """Lớp Canvas cơ bản của Matplotlib"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # Tạo Figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#0b0f19') # Màu nền vũ trụ (Xanh đen thẫm)
        
        # Tạo Axes 3D
        self.axes = self.fig.add_subplot(111, projection='3d')
        self.axes.set_facecolor('#0b0f19')
        
        super().__init__(self.fig)

class GraphWidget(QWidget):
    """Widget hoàn chỉnh bao gồm Canvas và Thanh công cụ (Toolbar)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Khởi tạo Canvas
        self.canvas = MplCanvas(self, width=8, height=6, dpi=100)
        
        # Thanh công cụ (Zoom, Pan, Save)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet("background-color: #ecf0f1; color: black;")
        
        # Thêm vào layout
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
    def plot_graph(self, G, pos_3d, path_edges=None, highlighted_nodes=None):
        """
        Hàm vẽ đồ thị chính.
        :param G: NetworkX graph object
        :param pos_3d: Dict {node: (x, y, z)}
        :param path_edges: List các cạnh cần tô sáng (VD: đường đi ngắn nhất)
        :param highlighted_nodes: List các node đang được duyệt (Animation)
        """
        self.canvas.axes.clear()
        ax = self.canvas.axes
        
        # 1. Vẽ các Cạnh (Edges)
        for u, v in G.edges():
            x = [pos_3d[u][0], pos_3d[v][0]]
            y = [pos_3d[u][1], pos_3d[v][1]]
            z = [pos_3d[u][2], pos_3d[v][2]]
            
            # Màu cạnh: Xám nhạt
            color = '#34495e'
            width = 1.0
            
            # Nếu cạnh nằm trong đường đi ngắn nhất/MST -> Màu Vàng
            if path_edges and ((u, v) in path_edges or (v, u) in path_edges):
                color = '#f1c40f' # Yellow
                width = 3.0
                
            ax.plot(x, y, z, color=color, linewidth=width, alpha=0.6)

        # 2. Vẽ các Nút (Nodes/Planets)
        xs = [pos_3d[n][0] for n in G.nodes()]
        ys = [pos_3d[n][1] for n in G.nodes()]
        zs = [pos_3d[n][2] for n in G.nodes()]
        
        # Kích thước nút dựa trên bậc (degree) hoặc cố định
        sizes = [30 + 10 * G.degree(n) for n in G.nodes()]
        
        # Màu nút: Mặc định là xanh dương
        node_colors = ['#3498db'] * len(G.nodes())
        
        # Xử lý màu cho node đang highlight (Animation)
        if highlighted_nodes:
            node_list = list(G.nodes())
            for i, node in enumerate(node_list):
                if node in highlighted_nodes:
                    node_colors[i] = '#e74c3c' # Red
        
        ax.scatter(xs, ys, zs, s=sizes, c=node_colors, edgecolors='white', alpha=1.0)

        # 3. Vẽ Nhãn (Label) tên hành tinh
        for node, (x, y, z) in pos_3d.items():
            if node in G.nodes():
                ax.text(x, y, z, f"  {node}", color='white', fontsize=9)

        # Cấu hình trục
        ax.set_xlabel('X (AU)')
        ax.set_ylabel('Y (AU)')
        ax.set_zlabel('Z (AU)')
        ax.grid(False) # Tắt lưới mặc định cho đẹp
        
        # Vẽ lại
        self.canvas.draw_idle()