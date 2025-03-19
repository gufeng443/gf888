import sys
import os
import io
import re
import random
import string
from threading import Thread, Lock
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QCheckBox
from PyQt5.QtCore import Qt
from PIL import Image
import pytesseract

# 配置 Tesseract 的路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.monitored_windows = {}
        self.lock = Lock()

    def initUI(self):
        self.setWindowTitle('模拟器监控工具')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.label = QLabel('选择模拟器进行监控', self)
        layout.addWidget(self.label)

        self.readButton = QPushButton('读取模拟', self)
        self.readButton.clicked.connect(self.read_devices)
        layout.addWidget(self.readButton)

        self.setLayout(layout)

    def read_devices(self):
        # 获取连接的设备
        devices = subprocess.check_output('adb devices', shell=True).decode().strip().split('\n')[1:]
        self.checkboxes = []
        for device in devices:
            device_id = device.split()[0]
            checkbox = QCheckBox(device_id, self)

            # 设置复选框的固定大小
            checkbox.setFixedSize(200, 30)  # 宽度200，高度30（根据需要调整）

            # 使用CSS样式调整文字的大小
            checkbox.setStyleSheet("QCheckBox { font-size: 14px; }")  # 文字大小为14px
            checkbox.stateChanged.connect(self.on_checkbox_state_changed)
            self.checkboxes.append(checkbox)
            self.layout().addWidget(checkbox)

    def on_checkbox_state_changed(self, state):
        sender = self.sender()
        device_id = sender.text()

        if state == Qt.Checked:
            self.start_monitoring(device_id)
        elif state == Qt.Unchecked:
            self.stop_monitoring(device_id)
            sender.setChecked(False)

    def start_monitoring(self, device_id):
        with self.lock:
            if device_id not in self.monitored_windows:
                self.monitored_windows[device_id] = {
                    'thread': Thread(target=self.monitor_device, args=(device_id,)),
                    'max_members': 0,
                    'screenshot_path': None,
                    'monitoring': True
                }
                self.monitored_windows[device_id]['thread'].start()

    def stop_monitoring(self, device_id):
        with self.lock:
            if device_id in self.monitored_windows:
                self.monitored_windows[device_id]['monitoring'] = False
                # 不再删除截图文件，保留它
                self.monitored_windows.pop(device_id, None)

    def monitor_device(self, device_id):
        screenshot_folder = r'C:\Users\Administrator\Desktop\监测截图'
        while self.monitored_windows[device_id]['monitoring']:
            try:
                # 获取屏幕截图并处理
                screenshot_data = self.get_screenshot(device_id)
                if screenshot_data:
                    # 解析图像
                    members, contains_info = self.parse_members(screenshot_data)

                    with self.lock:
                        if contains_info:
                            if members > self.monitored_windows[device_id]['max_members']:
                                # 保存新截图并更新记录
                                screenshot_path = self.save_screenshot(screenshot_data, screenshot_folder, device_id)
                                self.monitored_windows[device_id]['max_members'] = members
                                if self.monitored_windows[device_id]['screenshot_path']:
                                    os.remove(self.monitored_windows[device_id]['screenshot_path'])
                                self.monitored_windows[device_id]['screenshot_path'] = screenshot_path

                        # 检测数据是否消失
                        if not contains_info:
                            # 保留截图文件，不再删除
                            self.monitored_windows[device_id]['screenshot_path'] = None
                            self.monitored_windows[device_id]['monitoring'] = False

            except Exception as e:
                print(f"Error during monitoring: {e}")
                break

    def get_screenshot(self, device_id):
        try:
            # 使用adb截图到内存
            result = subprocess.check_output(f'adb -s {device_id} exec-out screencap -p', shell=True)
            return io.BytesIO(result)
        except subprocess.CalledProcessError as e:
            print(f"Error taking screenshot: {e}")
            return None

    def parse_members(self, img_data):
        try:
            # 使用 PIL 打开图像
            img = Image.open(img_data)
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')

            # 解析图像中的数字和成员信息
            print(f"Extracted Text: {text}")

            # 提取成员数字和检测是否包含“？”位成员
            match = re.search(r'(\d+)\s*位成员', text)
            if match:
                return int(match.group(1)), True
            return 0, False
        except Exception as e:
            print(f"Error parsing members: {e}")
            return 0, False

    def save_screenshot(self, img_data, folder, device_id):
        try:
            # 确定文件名
            new_number = self.get_next_screenshot_number(folder, device_id)
            filename = f'{device_id}_screenshot_{new_number}.png'
            file_path = os.path.join(folder, filename)

            # 保存图像
            img = Image.open(img_data)
            img.save(file_path)

            return file_path
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            return None

    def get_next_screenshot_number(self, folder, device_id):
        files = [f for f in os.listdir(folder) if f.startswith(f'{device_id}_screenshot_')]
        if files:
            numbers = [int(f.split('_')[-1].split('.')[0]) for f in files]
            return max(numbers) + 1
        return 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
