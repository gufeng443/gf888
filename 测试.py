import re

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BrowserAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("浏览器自动化工具")

        self.browser_windows = []  # 用于存储已打开的浏览器窗口
        self.checkbuttons = []  # 用于存储每个浏览器窗口对应的复选框
        self.window_count = 0  # 用于跟踪窗口的数量
        self.selected_folder = ""  # 存储选中的文件夹路径
        self.txt_files = []  # 存储文件夹中的txt文件列表

        self.create_widgets()  # 创建 GUI 控件

    def create_widgets(self):
        # 创建浏览器操作相关的控件
        self.browser_frame = ttk.LabelFrame(self.root, text="浏览器操作", padding=10)
        self.browser_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.automation_frame = ttk.LabelFrame(self.root, text="自动化操作", padding=10)
        self.automation_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # 浏览器操作部分：URL 输入框、浏览器数量选择框
        self.url_label = ttk.Label(self.browser_frame, text="网址:")
        self.url_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.url_entry = ttk.Entry(self.browser_frame, width=40)
        self.url_entry.insert(0, "https://bss.gtws.cc/#/task/pullGroup")
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)

        self.num_label = ttk.Label(self.browser_frame, text="浏览器数量:")
        self.num_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.num_browser = ttk.Combobox(self.browser_frame, values=[i for i in range(1, 11)], width=5)
        self.num_browser.set(5)
        self.num_browser.grid(row=1, column=1, padx=5, pady=5)

        # 打开浏览器按钮
        self.open_browser_button = ttk.Button(self.browser_frame, text="打开浏览器", command=self.open_browser)
        self.open_browser_button.grid(row=2, column=0, columnspan=2, pady=10)

        # 自动化操作部分
        self.start_button = ttk.Button(self.automation_frame, text="自动启动", command=self.auto_start)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        self.restart_button = ttk.Button(self.automation_frame, text="中断重启", command=self.restart)
        self.restart_button.grid(row=0, column=1, padx=5, pady=5)

        # 导入链接部分
        self.link_label = ttk.Label(self.automation_frame, text="输入链接:")
        self.link_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.link_entry = ttk.Entry(self.automation_frame, width=40)
        self.link_entry.grid(row=1, column=1, padx=5, pady=5)

        self.import_link_button = ttk.Button(self.automation_frame, text="导入链接", command=self.import_link)
        self.import_link_button.grid(row=2, column=0, columnspan=2, pady=5)

        # 一键清除上传的文件按钮
        self.clear_upload_button = ttk.Button(self.automation_frame, text="清除上传文件", command=self.clear_uploaded_files)
        self.clear_upload_button.grid(row=3, column=0, columnspan=2, pady=5)

        # 平分TXT文件按钮
        self.split_txt_button = ttk.Button(self.automation_frame, text="平分TXT文件", command=self.split_txt)
        self.split_txt_button.grid(row=4, column=0, padx=5, pady=5)

        # 显示选择的文件夹路径
        self.folder_label = ttk.Label(self.automation_frame, text="未选择文件夹")
        self.folder_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # 显示txt文件数量
        self.txt_count_label = ttk.Label(self.automation_frame, text="txt 文件数量: 0")
        self.txt_count_label.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

        # 浏览器窗口控制部分：全选和全不选按钮
        self.all_select_button = ttk.Button(self.browser_frame, text="全选", command=self.select_all)
        self.all_select_button.grid(row=3, column=0, padx=5, pady=5)

        self.all_deselect_button = ttk.Button(self.browser_frame, text="全不选", command=self.deselect_all)
        self.all_deselect_button.grid(row=3, column=1, padx=5, pady=5)

    def clear_uploaded_files(self):
        try:
            # 遍历已勾选的浏览器窗口
            for i, driver in enumerate(self.browser_windows):
                if self.checkbuttons[i].get():
                    print(f"正在浏览器 {i + 1} 中执行清除操作")

                    try:
                        # 查找并点击清除按钮
                        clear_button = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, "//span[text()='清 除']"))
                        )
                        clear_button.click()
                        print(f"浏览器 {i + 1} 中的文件已清除")
                    except Exception as e:
                        print(f"在浏览器 {i + 1} 中执行清除操作时出错: {e}")
                        continue
        except Exception as e:
            print(f"清除上传文件时出错: {e}")
            messagebox.showerror("错误", f"清除上传文件时出错: {e}")
    def open_browser(self):
        try:
            num_browsers = int(self.num_browser.get())
            url = self.url_entry.get()

            for i in range(num_browsers):
                driver = webdriver.Chrome()
                driver.get(url)
                self.browser_windows.append(driver)

                self.login_to_page(driver)

                row_position = 4 + self.window_count
                var = tk.BooleanVar()
                self.checkbuttons.append(var)

                checkbox = ttk.Checkbutton(self.browser_frame, text=f"浏览器 {self.window_count + 1}", variable=var)
                checkbox.grid(row=row_position, column=0, sticky="w")

                pop_button = ttk.Button(self.browser_frame, text=f"弹起 {self.window_count + 1}",
                                        command=lambda i=self.window_count, d=driver: self.restore_window(i, d))
                pop_button.grid(row=row_position, column=1, padx=5, pady=5)

                min_button = ttk.Button(self.browser_frame, text=f"最小化 {self.window_count + 1}",
                                        command=lambda d=driver: d.minimize_window())
                min_button.grid(row=row_position, column=2, padx=5, pady=5)

                self.window_count += 1

        except Exception as e:
            messagebox.showerror("错误", f"打开浏览器时出错: {str(e)}")

    def login_to_page(self, driver):
        try:
            username_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='用户名' and @id='username']"))
            )
            username_field.clear()
            username_field.send_keys("gbs232")

            password_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='密码' and @id='password']"))
            )
            password_field.clear()
            password_field.send_keys("7kNQoZ")

            print("用户名和密码已成功输入！")

        except Exception as e:
            print(f"在登录时出错: {e}")

    def restore_window(self, i, driver):
        window_rect = driver.get_window_rect()
        x = window_rect['x']
        y = window_rect['y']
        width = window_rect['width']
        height = window_rect['height']

        driver.set_window_position(x, y)
        driver.set_window_size(width, height)

    def auto_start(self):
        try:
            for i, driver in enumerate(self.browser_windows):
                if self.checkbuttons[i].get():
                    print(f"正在浏览器 {i + 1} 中执行自动启动操作")

                    try:
                        auto_button = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, "//span[text()='自动执行']"))
                        )
                        auto_button.click()

                        confirm_button = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, "//span[text()='确定']"))
                        )
                        confirm_button.click()

                    except Exception as e:
                        print(f"在浏览器 {i + 1} 中执行自动启动时出错: {e}")
                        continue

        except Exception as e:
            print(f"执行自动启动时出错: {e}")
            messagebox.showerror("错误", f"自动启动时出错: {str(e)}")

    def restart(self):
        try:
            for i, driver in enumerate(self.browser_windows):
                if self.checkbuttons[i].get():
                    print(f"正在浏览器 {i + 1} 中执行中断重启操作")

                    try:
                        continue_button = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, "//span[text()='继续执行']"))
                        )
                        continue_button.click()
                    except Exception as e:
                        print(f"在浏览器 {i + 1} 中执行中断重启时出错: {e}")
                        continue

        except Exception as e:
            print(f"执行中断重启时出错: {e}")
            messagebox.showerror("错误", f"中断重启时出错: {str(e)}")

    def import_link(self):
        try:
            link = self.link_entry.get().strip()
            if not link:
                messagebox.showerror("错误", "请输入有效的链接")
                return

            for i, driver in enumerate(self.browser_windows):
                if self.checkbuttons[i].get():
                    print(f"正在浏览器 {i + 1} 中导入链接 {link}")

                    try:
                        link_input = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='请输入社群链接']"))
                        )
                        link_input.clear()
                        link_input.send_keys(link)
                        link_input.send_keys(Keys.RETURN)

                    except Exception as e:
                        print(f"在浏览器 {i + 1} 中导入链接时出错: {e}")
                        continue

        except Exception as e:
            print(f"导入链接时出错: {e}")
            messagebox.showerror("错误", f"导入链接时出错: {str(e)}")

    import re

    def split_txt(self):
        try:
            folder_path = filedialog.askdirectory(title="选择TXT文件夹")
            if not folder_path:
                messagebox.showerror("错误", "请选择文件夹")
                return

            self.selected_folder = folder_path
            self.folder_label.config(text=f"文件夹: {os.path.basename(folder_path)}")

            # 获取所有txt文件并按数字排序
            self.txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

            # 按照文件名中的最后一个数字进行排序
            self.txt_files.sort(key=lambda f: int(re.search(r'-(\d+)\.TXT$', f, re.IGNORECASE).group(1)))

            self.txt_count_label.config(text=f"txt 文件数量: {len(self.txt_files)}")

            # 获取用户勾选的浏览器数量
            selected_browsers = [i for i, cb in enumerate(self.checkbuttons) if cb.get()]
            num_browsers = len(selected_browsers)

            total_files = len(self.txt_files)

            if total_files == 0:
                messagebox.showerror("错误", "文件夹中没有txt文件")
                return

            if num_browsers == 0:
                messagebox.showerror("错误", "请至少选择一个浏览器窗口")
                return

            # 按照用户勾选的浏览器数量平分文件
            files_per_browser = total_files // num_browsers
            remaining_files = total_files % num_browsers

            for i, browser_idx in enumerate(selected_browsers):
                start_idx = i * files_per_browser
                end_idx = (
                                      i + 1) * files_per_browser if i < num_browsers - 1 else start_idx + files_per_browser + remaining_files
                files_to_upload = self.txt_files[start_idx:end_idx]

                driver = self.browser_windows[browser_idx]
                self.upload_files_to_browser(driver, files_to_upload)

            messagebox.showinfo("成功", f"成功将文件分配并上传到 {num_browsers} 个浏览器窗口")

        except Exception as e:
            messagebox.showerror("错误", f"平分TXT文件时出错: {e}")

    def upload_files_to_browser(self, driver, files):
        try:
            # 等待上传控件加载
            upload_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'ant-upload-btn')]"))
            )

            # 找到上传控件
            upload_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')

            # 构建文件路径列表，以换行符分隔
            file_paths = []
            for file in files:
                file_path = os.path.join(self.selected_folder, file)
                file_path = file_path.replace("\\", "/")  # 确保路径分隔符一致
                file_paths.append(file_path)

            # 将所有文件路径连接为一个字符串，用换行符分隔
            file_paths_str = "\n".join(file_paths)

            # 发送文件路径字符串，一次上传多个文件
            upload_input.send_keys(file_paths_str)
            print(f"已上传文件: {file_paths_str}")



            time.sleep(2)  # 等待文件上传完成

        except Exception as e:
            print(f"在浏览器中上传文件时出错: {e}")
            print("错误", f"上传文件时出错: {e}")

    def select_all(self):
        for button in self.checkbuttons:
            button.set(True)

    def deselect_all(self):
        for button in self.checkbuttons:
            button.set(False)


# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = BrowserAutomationApp(root)
    root.mainloop()
