import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/mnt/c/Users/LENOVO/OneDrive/Desktop/ros2_ws/install/patrol_detection'
