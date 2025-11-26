# -*- coding: utf-8 -*-
# Module: astro_data.py
# Project: solar-system-graph
# Chức năng: Lấy dữ liệu tọa độ hành tinh từ NASA Horizons (Chạy đa luồng)

import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from datetime import datetime
import warnings

# Tắt cảnh báo không cần thiết từ astropy
warnings.filterwarnings('ignore')

try:
    from astroquery.jplhorizons import Horizons
    HAS_ASTROQUERY = True
except ImportError:
    HAS_ASTROQUERY = False

# Danh sách ID các hành tinh theo chuẩn NASA JPL
# 199: Mercury, 299: Venus, 399: Earth, 499: Mars, etc.
# Sun được đặt cố định tại tâm (0,0,0)
PLANET_IDS = {
    'Mercury': '199',
    'Venus':   '299',
    'Earth':   '399',
    'Mars':    '499',
    'Jupiter': '599',
    'Saturn':  '699',
    'Uranus':  '799',
    'Neptune': '899'
}

class AstroDataFetcher(QThread):
    """
    Class xử lý việc tải dữ liệu từ NASA trên luồng riêng (Background Thread).
    Không làm treo giao diện chính.
    """
    # Signal bắn dữ liệu về UI khi tải xong: trả về dict {tên: (x, y, z)}
    data_ready = pyqtSignal(dict)
    
    # Signal báo lỗi nếu mất mạng hoặc API lỗi
    data_error = pyqtSignal(str)

    def __init__(self, use_realtime=True):
        super().__init__()
        self.use_realtime = use_realtime
        self.current_date = datetime.now().strftime("%Y-%m-%d")

    def run(self):
        """Hàm này sẽ tự động chạy khi gọi .start()"""
        
        # Dữ liệu chứa Sun ở tâm
        solar_system_data = {
            'Sun': np.array([0.0, 0.0, 0.0])
        }

        if self.use_realtime and HAS_ASTROQUERY:
            try:
                # Gửi request lấy dữ liệu cho từng hành tinh
                # location='@sun' nghĩa là lấy tọa độ tương đối so với Mặt Trời
                for name, pid in PLANET_IDS.items():
                    obj = Horizons(id=pid, location='@sun', epochs=self.current_date)
                    vectors = obj.vectors()
                    
                    # Lấy tọa độ x, y, z (đơn vị AU)
                    x = float(vectors['x'][0])
                    y = float(vectors['y'][0])
                    z = float(vectors['z'][0])
                    
                    solar_system_data[name] = np.array([x, y, z])
                
                # Hoàn thành, bắn tín hiệu về
                self.data_ready.emit(solar_system_data)

            except Exception as e:
                # Lỗi mạng hoặc API, chuyển sang chế độ Mock
                print(f"Error fetching NASA data: {e}. Switching to offline mode.")
                self._load_mock_data()
        else:
            # Chạy chế độ offline ngay từ đầu
            self._load_mock_data()

    def _load_mock_data(self):
        """Dữ liệu giả lập (Offline) dùng khi mất mạng hoặc test nhanh"""
        # Tọa độ xấp xỉ (AU) để test đồ thị
        mock_data = {
            'Sun':     np.array([0.0, 0.0, 0.0]),
            'Mercury': np.array([0.3, 0.1, 0.0]),
            'Venus':   np.array([0.7, -0.2, 0.05]),
            'Earth':   np.array([-1.0, 0.1, 0.0]),
            'Mars':    np.array([-1.5, -0.5, 0.1]),
            'Jupiter': np.array([5.0, 1.0, -0.2]),
            'Saturn':  np.array([9.0, -2.0, 0.3]),
            'Uranus':  np.array([-18.0, 3.0, 0.5]),
            'Neptune': np.array([28.0, -5.0, -0.5])
        }
        # Nếu dùng mock thì delay 1 chút để mô phỏng việc loading
        self.msleep(500) 
        self.data_ready.emit(mock_data)