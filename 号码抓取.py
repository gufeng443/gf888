import tkinter as tk
from tkinter import ttk, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from collections import defaultdict
import threading
import time

# 用户界面
class WebScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("网页数据抓取工具")

        # 启动浏览器按钮
        self.start_browser_button = tk.Button(root, text="启动浏览器", command=self.start_browser)
        self.start_browser_button.pack(pady=10)

        # 开始抓取按钮
        self.start_scraping_button = tk.Button(root, text="开始抓取", command=self.start_scraping_thread)
        self.start_scraping_button.pack(pady=10)

        # 实时数据显示框
        self.real_time_data_label = tk.Label(root, text="实时抓取的号码：")
        self.real_time_data_label.pack(pady=5)
        self.real_time_data_display = scrolledtext.ScrolledText(root, width=80, height=10)
        self.real_time_data_display.pack(pady=10)

        # 统计数据显示框
        self.statistics_label = tk.Label(root, text="号码统计结果：")
        self.statistics_label.pack(pady=5)
        self.statistics_display = scrolledtext.ScrolledText(root, width=80, height=10)
        self.statistics_display.pack(pady=10)

        # 进度条
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # 浏览器驱动
        self.driver = None

        # 多线程控制
        self.scraping_thread = None
        self.stop_event = threading.Event()

    def start_browser(self):
        """启动浏览器"""
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=Service('E:\GP\chromedriver-win64\chromedriver-win64\chromedriver.exe'), options=chrome_options)
        self.driver.get("https://818ws-pull.com/#/admin/channel")

    def start_scraping_thread(self):
        """启动抓取任务线程"""
        if not self.driver:
            self.real_time_data_display.insert(tk.END, "请先启动浏览器！\n")
            return

        # 重置进度条和数据框
        self.progress["value"] = 0
        self.real_time_data_display.delete(1.0, tk.END)
        self.statistics_display.delete(1.0, tk.END)

        # 启动抓取任务线程
        self.stop_event.clear()
        self.scraping_thread = threading.Thread(target=self.start_scraping)
        self.scraping_thread.start()

    def start_scraping(self):
        """抓取任务"""
        try:
            # 等待页面加载
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "el-scrollbar__view"))
            )

            # 找到所有 <span class="">查人员</span> 元素
            check_buttons = self.driver.find_elements(By.CSS_SELECTOR, "span")

            # 统计号码
            number_count = defaultdict(int)

            # 更新进度条最大值
            self.progress["maximum"] = len(check_buttons)

            for index, button in enumerate(check_buttons):
                if self.stop_event.is_set():  # 检查是否停止任务
                    break

                if button.text.strip() == "查人员":  # 确保是“查人员”按钮
                    try:
                        # 滚动到元素可见位置
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(0.5)  # 等待滚动完成

                        # 使用 ActionChains 点击元素
                        actions = ActionChains(self.driver)
                        actions.move_to_element(button).click().perform()
                        time.sleep(0.4)  # 等待页面更新

                        # 获取群组成员信息
                        member_list = self.driver.find_element(By.CSS_SELECTOR, ".member-list-card")
                        number_elements = member_list.find_elements(
                            By.CSS_SELECTOR, "span[data-v-7be24a59][style*='color: rgb(112, 95, 237)']"
                        )

                        # 获取第二个元素的号码数据
                        if len(number_elements) >= 2:
                            number = number_elements[1].text
                            number_count[number] += 1

                            # 实时显示抓取的号码
                            self.real_time_data_display.insert(tk.END, f"{number}\n")
                            self.real_time_data_display.see(tk.END)  # 滚动到最新数据

                        # 更新进度条
                        self.progress["value"] = index + 1
                        self.root.update_idletasks()

                    except Exception as e:
                        self.real_time_data_display.insert(tk.END, f"抓取过程中出现错误: {e}\n")
                        continue

            # 显示统计结果
            self.statistics_display.insert(tk.END, "号码统计结果：\n")
            for number, count in number_count.items():
                self.statistics_display.insert(tk.END, f"出现{count}次的号码有: {number}\n")

        except Exception as e:
            self.real_time_data_display.insert(tk.END, f"抓取过程中出现错误: {e}\n")

        self.real_time_data_display.insert(tk.END, "抓取完成！\n")

    def stop_scraping(self):
        """停止抓取任务"""
        self.stop_event.set()
        if self.scraping_thread:
            self.scraping_thread.join()

# 运行程序
if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()