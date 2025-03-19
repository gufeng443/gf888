import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QSpinBox, QLabel, QCheckBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt

class BrowserWindow(QThread):
    status_update = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.driver = None
        self.monitoring = False  # 控制监控是否开启

    def run(self):
        try:
            # 启动浏览器
            self.driver = webdriver.Chrome()
            self.driver.get(self.url)

            # 自动最小化窗口
            self.driver.minimize_window()

            while True:
                if self.monitoring:
                    try:
                        # 等待 <span>自动执行</span> 元素可点击
                        WebDriverWait(self.driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, "//span[text()='自动执行']"))
                        )

                        # 获取元素并滚动到视图中，确保元素可点击
                        auto_execute_element = self.driver.find_element(By.XPATH, "//span[text()='自动执行']")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", auto_execute_element)

                        # 等待元素可点击
                        WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//span[text()='自动执行']"))
                        )

                        # 再次确保元素可见且不被覆盖
                        if auto_execute_element.is_displayed() and auto_execute_element.is_enabled():
                            auto_execute_element.click()
                            self.status_update.emit("成功点击了'自动执行'按钮")
                        else:
                            self.status_update.emit("元素不可点击，正在重试...")
                            time.sleep(3)  # 调整为3秒
                    except Exception as e:
                        # 捕获并忽略底层 Selenium 错误，不让它们显示在用户界面
                        print(f"底层错误: {str(e)}")  # 仅打印到控制台
                        time.sleep(3)  # 调整为3秒
                else:
                    time.sleep(3)  # 如果监控未启动，每3秒钟检查一次

        except Exception as main_error:
            # 捕获浏览器启动或初始化错误，并只打印日志到控制台
            print(f"启动浏览器失败: {str(main_error)}")  # 不让此信息显示到用户界面
        finally:
            if self.driver:
                self.driver.quit()

    def stop(self):
        # 停止监控
        self.monitoring = False

    def start_monitoring(self):
        # 开始监控
        self.monitoring = True

    def stop_monitoring(self):
        # 停止监控
        self.monitoring = False


class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.browsers = []
        self.window_counter = 0  # 记录已经打开的浏览器窗口数量

        # 窗口设置
        self.setWindowTitle("云控监控系统")
        self.setGeometry(100, 100, 400, 400)

        # 主布局
        layout = QVBoxLayout()

        # 输入框和按钮布局
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit(self)
        self.url_input.setText("https://bss.gtws.cc/#/task/pullGroup")  # 默认网址
        self.url_input.setPlaceholderText("请输入网址")
        self.num_input = QSpinBox(self)
        self.num_input.setRange(1, 10)
        self.num_input.setValue(1)

        start_button = QPushButton("启动窗口", self)
        start_button.clicked.connect(self.start_browsers)

        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.num_input)
        layout.addLayout(url_layout)
        layout.addWidget(start_button)

        # 添加 "全部停止" 按钮
        stop_all_button = QPushButton("全部停止", self)
        stop_all_button.clicked.connect(self.stop_all_browsers)
        layout.addWidget(stop_all_button)

        # 监控状态
        self.status_label = QLabel("状态: 未启动", self)
        layout.addWidget(self.status_label)

        # 浏览器窗口列表
        self.browser_checkboxes = []

        # 添加布局
        self.setLayout(layout)

    def start_browsers(self):
        url = self.url_input.text()
        num_windows = self.num_input.value()

        # 启动浏览器线程
        for i in range(num_windows):
            browser_thread = BrowserWindow(url)
            browser_thread.status_update.connect(self.update_status)
            browser_thread.start()
            self.browsers.append(browser_thread)
            self.window_counter += 1  # 更新已打开窗口的数量

            # 为每个浏览器添加复选框和控制按钮
            checkbox = QCheckBox(f"窗口 {self.window_counter} 开始监控", self)
            checkbox.clicked.connect(lambda checked, i=self.window_counter-1: self.toggle_monitoring(i, checked))
            self.browser_checkboxes.append(checkbox)
            self.layout().addWidget(checkbox)

        self.status_label.setText("状态: 监控中")

    def update_status(self, status):
        self.status_label.setText(f"状态: {status}")

    def toggle_monitoring(self, index, checked):
        # 控制指定浏览器窗口的监控开始或停止
        if checked:
            self.browsers[index].start_monitoring()
        else:
            self.browsers[index].stop_monitoring()

    def stop_all_browsers(self):
        # 停止所有浏览器的监控操作，但不关闭浏览器窗口
        for browser in self.browsers:
            browser.stop_monitoring()

        # 取消所有复选框的勾选
        for checkbox in self.browser_checkboxes:
            checkbox.setChecked(False)

        self.status_label.setText("状态: 所有监控已停止")

    def closeEvent(self, event):
        # 仅停止监控，不关闭浏览器窗口
        for browser in self.browsers:
            browser.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = ControlPanel()
    panel.show()
    sys.exit(app.exec_())