import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import os


class WhatsAppManager:
    def __init__(self, profile_path=None):
        self.options = webdriver.ChromeOptions()
        if profile_path:
            self.options.add_argument(f"--user-data-dir={profile_path}")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get("https://web.whatsapp.com/")

    def create_community(self, name, description):
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//canvas[@aria-label="扫描二维码"]'))
            )
            # 等待用户手动扫码登录
            input("请扫码登录后按回车继续...")

            # 进入社群页面
            self.driver.find_element(By.XPATH, '//button[@aria-label="社群"]').click()

            # 创建新社群
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[text()="新建社群"]'))
            ).click()

            # 填写信息
            name_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//p[@class="selectable-text copyable-text"]'))
            )
            name_field.send_keys(name)

            desc_field = self.driver.find_element(By.XPATH, '//div[@contenteditable="true"]')
            desc_field.clear()
            desc_field.send_keys(description)

            # 提交创建
            self.driver.find_element(By.XPATH, '//div[@aria-label="创建社群"]').click()

            # 获取邀请链接
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="邀请"]'))
            ).click()

            link = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//span[@class="invite-link"]'))
            ).text

            return link
        except Exception as e:
            print(f"操作出错: {str(e)}")
            return None


class AutoCommunityApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WhatsApp社群创建工具")
        self.geometry("600x500")
        self.profiles = []
        self.create_widgets()

    def create_widgets(self):
        # 账号管理模块
        ttk.Label(self, text="账号配置:").grid(row=0, column=0, padx=5, pady=5)
        self.profile_list = tk.Listbox(self, width=50, height=5)
        self.profile_list.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

        ttk.Button(self, text="添加账号", command=self.add_profile).grid(row=1, column=1, pady=5)
        ttk.Button(self, text="移除账号", command=self.remove_profile).grid(row=1, column=2, pady=5)

        # 创建参数模块
        ttk.Label(self, text="基础名称:").grid(row=2, column=0, padx=5, pady=5)
        self.base_name = ttk.Entry(self)
        self.base_name.grid(row=2, column=1, columnspan=2, padx=5, pady=5)

        ttk.Label(self, text="起始编号:").grid(row=3, column=0, padx=5, pady=5)
        self.start_num = ttk.Entry(self)
        self.start_num.grid(row=3, column=1, columnspan=2, padx=5, pady=5)

        ttk.Label(self, text="创建数量:").grid(row=4, column=0, padx=5, pady=5)
        self.quantity = ttk.Entry(self)
        self.quantity.grid(row=4, column=1, columnspan=2, padx=5, pady=5)

        ttk.Label(self, text="群描述:").grid(row=5, column=0, padx=5, pady=5)
        self.description = tk.Text(self, height=4, width=40)
        self.description.grid(row=5, column=1, columnspan=2, padx=5, pady=5)

        # 控制按钮
        ttk.Button(self, text="开始创建", command=self.start_process).grid(row=6, column=1, pady=10)
        ttk.Button(self, text="退出程序", command=self.destroy).grid(row=6, column=2, pady=10)

    def add_profile(self):
        path = filedialog.askdirectory(title="选择Chrome用户数据目录")
        if path:
            self.profiles.append(path)
            self.profile_list.insert(tk.END, path)

    def remove_profile(self):
        selected = self.profile_list.curselection()
        if selected:
            self.profiles.pop(selected[0])
            self.profile_list.delete(selected[0])

    def start_process(self):
        try:
            base = self.base_name.get()
            start = int(self.start_num.get())
            count = int(self.quantity.get())
            desc = self.description.get("1.0", tk.END).strip()

            if not base or not desc:
                messagebox.showerror("错误", "请填写完整信息")
                return

            threading.Thread(
                target=self.run_creation,
                args=(base, start, count, desc),
                daemon=True
            ).start()
        except ValueError:
            messagebox.showerror("错误", "编号和数量必须为数字")

    def run_creation(self, base, start, count, desc):
        drivers = []
        try:
            # 初始化所有浏览器实例
            for profile in self.profiles:
                mgr = WhatsAppManager(profile)
                drivers.append(mgr.driver)
                # 等待扫码登录
                input("请为账号 {} 扫码登录...".format(profile))

            # 执行创建任务
            for i in range(count):
                current_name = f"{base}-{start + i}"
                for driver in drivers:
                    mgr = WhatsAppManager()
                    mgr.driver = driver
                    if link := mgr.create_community(current_name, desc):
                        self.log_result(f"{current_name}\n{link}\n")

        finally:
            for d in drivers:
                try:
                    d.quit()
                except:
                    pass

    def log_result(self, text):
        self.after(0, lambda: self.description.insert(tk.END, text))


if __name__ == "__main__":
    app = AutoCommunityApp()
    app.mainloop()