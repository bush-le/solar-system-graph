# -*- coding: utf-8 -*-
# Module: canvas_widget.py
# Project: solar-system-graph
# Chức năng: Widget hiển thị đồ thị hỗ trợ chuyển đổi linh hoạt 2D/3D và Smart Scaling

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QHBoxLayout, QRadioButton, QButtonGroup, QLabel
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

# Cấu hình Style tối
plt.style.use('dark_background')

class GraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # --- TOOLBAR AREA ---
        tool_layout = QHBoxLayout()
        
        # 1. Canvas
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.fig.patch.set_facecolor('#0b0f19')
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet("background-color: #ecf0f1; color: black;")
        
        # 2. Controls: Chế độ 2D/3D
        lbl_mode = QLabel("Mode:")
        lbl_mode.setStyleSheet("color: white; font-weight: bold; margin-left: 10px;")
        
        self.radio_3d = QRadioButton("3D Space")
        self.radio_2d = QRadioButton("2D Map")
        self.radio_3d.setChecked(True) # Mặc định 3D
        
        # Style cho Radio Button
        style_radio = "color: white; margin-left: 5px;"
        self.radio_3d.setStyleSheet(style_radio)
        self.radio_2d.setStyleSheet(style_radio)
        
        # Group để chỉ chọn 1 trong 2
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.radio_3d)
        self.mode_group.addButton(self.radio_2d)
        self.mode_group.buttonToggled.connect(self.refresh_view)

        # 3. Controls: Smart Scaling
        self.chk_log_scale = QCheckBox("Smart Scale")
        self.chk_log_scale.setChecked(True)
        self.chk_log_scale.setStyleSheet("color: #f1c40f; font-weight: bold; margin-left: 15px;")
        self.chk_log_scale.toggled.connect(self.refresh_view)

        # Add to layout
        tool_layout.addWidget(self.toolbar)
        tool_layout.addWidget(lbl_mode)
        tool_layout.addWidget(self.radio_3d)
        tool_layout.addWidget(self.radio_2d)
        tool_layout.addWidget(self.chk_log_scale)
        
        layout.addLayout(tool_layout)
        layout.addWidget(self.canvas)

        # Cache dữ liệu
        self.cached_G = None
        self.cached_pos = None
        self.cached_path = None
        self.cached_highlight = None
        self.axes = None

    def _transform_coords(self, pos_3d):
        """Co giãn không gian để dễ nhìn"""
        if not self.chk_log_scale.isChecked():
            return pos_3d

        new_pos = {}
        POWER_FACTOR = 0.45 # Căn chỉnh lại một chút cho 2D đẹp hơn
        
        for node, coord in pos_3d.items():
            arr = np.array(coord)
            dist = np.linalg.norm(arr)
            if dist == 0: 
                new_pos[node] = arr
            else:
                scale_len = dist ** POWER_FACTOR
                new_pos[node] = (arr / dist) * (scale_len * 6)
        return new_pos

    def refresh_view(self):
        """Vẽ lại khi thay đổi cấu hình"""
        if self.cached_G:
            self.plot_graph(self.cached_G, self.cached_pos, self.cached_path, self.cached_highlight)

    def plot_graph(self, G, pos_3d, path_edges=None, highlighted_nodes=None):
        self.cached_G = G
        self.cached_pos = pos_3d
        self.cached_path = path_edges
        self.cached_highlight = highlighted_nodes

        # Reset Figure để đổi Projection (2D <-> 3D)
        self.fig.clear()
        
        is_2d = self.radio_2d.isChecked()
        
        if is_2d:
            self.axes = self.fig.add_subplot(111) # 2D Plot
            self.axes.set_facecolor('#0b0f19')
            self.axes.set_title("Top-Down Orbital Map", color='white', fontsize=10)
        else:
            self.axes = self.fig.add_subplot(111, projection='3d') # 3D Plot
            self.axes.set_facecolor('#0b0f19')
            # 3D cần chỉnh pane color thành trong suốt
            self.axes.xaxis.set_pane_color((0,0,0,0))
            self.axes.yaxis.set_pane_color((0,0,0,0))
            self.axes.zaxis.set_pane_color((0,0,0,0))

        ax = self.axes
        display_pos = self._transform_coords(pos_3d)

        # --- VẼ ---
        # 1. Edges
        for u, v in G.edges():
            p1 = display_pos[u]
            p2 = display_pos[v]
            
            # Màu sắc cạnh
            color = '#34495e'
            width = 1.0 if is_2d else 0.8
            alpha = 0.5
            
            # Highlight đường đi
            if path_edges and ((u, v) in path_edges or (v, u) in path_edges):
                color = '#f1c40f' 
                width = 3.0
                alpha = 1.0
            
            if is_2d:
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=width, alpha=alpha)
            else:
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 
                        color=color, linewidth=width, alpha=alpha)

        # 2. Nodes
        xs = [display_pos[n][0] for n in G.nodes()]
        ys = [display_pos[n][1] for n in G.nodes()]
        zs = [display_pos[n][2] for n in G.nodes()] if not is_2d else None
        
        colors = []
        sizes = []
        for n in G.nodes():
            s = 60 if is_2d else 40 # 2D thì vẽ to hơn chút
            c = '#3498db'
            if n == 'Sun': 
                c = '#e67e22'; s = 120
            elif highlighted_nodes and n in highlighted_nodes:
                c = '#e74c3c'; s = 80
            colors.append(c)
            sizes.append(s)

        if is_2d:
            ax.scatter(xs, ys, s=sizes, c=colors, edgecolors='white', alpha=1.0, zorder=5)
        else:
            ax.scatter(xs, ys, zs, s=sizes, c=colors, edgecolors='white', alpha=1.0)

        # 3. Labels
        for node, p in display_pos.items():
            if node in G.nodes():
                if is_2d:
                    ax.text(p[0], p[1]+0.8, f"{node}", color='white', fontsize=9, 
                            ha='center', va='bottom', fontweight='bold')
                else:
                    offset = 0.5 if self.chk_log_scale.isChecked() else 1.0
                    ax.text(p[0] + offset, p[1], p[2], f"{node}", color='white', fontsize=8)

        # Tắt trục tọa độ cho đẹp
        ax.set_xticks([])
        ax.set_yticks([])
        if not is_2d: ax.set_zticks([])
        
        # Vẽ lại
        self.canvas.draw_idle()