import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QFileDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal

class DeviceListThread(QThread):
    devices_fetched = pyqtSignal(list)

    def run(self):
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        devices = [line.split()[0] for line in result.stdout.splitlines() if '\tdevice' in line]
        self.devices_fetched.emit(devices)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('模拟器管理')
        layout = QVBoxLayout()

        self.device_label = QLabel('选择模拟器:')
        layout.addWidget(self.device_label)

        self.device_combo = QComboBox()
        layout.addWidget(self.device_combo)

        self.load_devices_button = QPushButton('读取模拟器')
        self.load_devices_button.clicked.connect(self.loadDevices)
        layout.addWidget(self.load_devices_button)

        self.extract_button = QPushButton('提取页面元素')
        self.extract_button.clicked.connect(self.extractElements)
        layout.addWidget(self.extract_button)

        self.setLayout(layout)

    def loadDevices(self):
        self.thread = DeviceListThread()
        self.thread.devices_fetched.connect(self.updateDeviceList)
        self.thread.start()

    def updateDeviceList(self, devices):
        self.device_combo.clear()
        self.device_combo.addItems(devices)

    def extractElements(self):
        device = self.device_combo.currentText()
        if not device:
            QMessageBox.warning(self, "警告", "请先选择一个模拟器")
            return

        folder = QFileDialog.getExistingDirectory(self, "选择保存文件夹", "C:\\Users\\Administrator\\Desktop\\000")
        if folder:
            try:
                # 执行提取元素的ADB命令
                subprocess.run(['adb', '-s', device, 'shell', 'uiautomator', 'dump'], check=True)

                # 将UI dump文件从设备拉取到本地
                local_file = f"{folder}/uiautomator_dump.xml"
                subprocess.run(['adb', '-s', device, 'pull', '/sdcard/window_dump.xml', local_file], check=True)

                QMessageBox.information(self, "成功", f"页面元素已保存到 {local_file}")

            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "错误", f"提取页面元素时出错: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
