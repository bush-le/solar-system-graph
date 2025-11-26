import sys
import os

# Đảm bảo Python nhận diện được thư mục gốc để import module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    """
    Điểm nhập chính của ứng dụng AstroGraph.
    """
    # 1. Khởi tạo ứng dụng
    app = QApplication(sys.argv)
    
    # 2. Cấu hình High DPI cho màn hình độ phân giải cao
    # (Quan trọng để Matplotlib và Text không bị vỡ hạt)
    try:
        from PyQt6.QtGui import QHighDpiScaling
        # PyQt6 thường tự động xử lý, nhưng giữ đoạn này để debug nếu cần
        pass 
    except ImportError:
        pass

    # 3. Khởi tạo cửa sổ chính
    window = MainWindow()
    window.show()
    
    # 4. Chạy vòng lặp sự kiện (Event Loop)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()