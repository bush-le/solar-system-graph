# -*- coding: utf-8 -*-
# Module: eulerian.py
# Project: solar-system-graph
# Chức năng: Tìm chu trình Euler (Hierholzer's Algorithm)

import networkx as nx

def find_eulerian_circuit(G, start_node=None):
    """
    Tìm chu trình Euler.
    Nếu đồ thị chưa Euler, sẽ tự động thêm cạnh (Eulerize) trên bản sao để chạy demo.
    """
    # 1. Tạo bản sao để không làm hỏng đồ thị gốc
    H = G.copy()
    if start_node is None:
        start_node = list(H.nodes())[0]

    # 2. Kiểm tra điều kiện Euler
    if nx.is_directed(H):
        if not nx.is_eulerian(H):
            # Với đồ thị có hướng, việc Eulerize phức tạp hơn, ta chỉ cảnh báo
            # Hoặc chuyển sang vô hướng để demo
            H = H.to_undirected()
            
    # 3. Biến đổi thành đồ thị Euler (Eulerize) nếu cần
    if not nx.is_eulerian(H):
        # Thêm các cạnh giả vào các đỉnh bậc lẻ để chúng thành bậc chẵn
        H = nx.eulerize(H)

    # 4. Tìm chu trình (Hierholzer's algorithm được tích hợp trong nx)
    # eulerian_circuit trả về generator các cạnh (u, v)
    try:
        circuit = list(nx.eulerian_circuit(H, source=start_node))
    except Exception:
        # Fallback nếu vẫn lỗi (ví dụ đồ thị không liên thông)
        return

    # 5. Yield từng bước để Animation
    visited_edges = []
    visited_nodes = {start_node}
    
    current_path_viz = []
    
    for u, v in circuit:
        visited_nodes.add(u)
        visited_nodes.add(v)
        current_path_viz.append((u, v))
        
        # Yield trạng thái: (Node hiện tại, Nodes đã thăm, Đường đi Euler)
        yield v, list(visited_nodes), current_path_viz