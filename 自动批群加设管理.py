import tkinter as tk
from tkinter import messagebox
import pygetwindow as gw
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class WhatsAppBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web版WhatsApp 自动群准群组申请与批量管理员设置")

        # 下拉框标签
        self.browser_label = tk.Label(root, text="选择浏览器窗口:")
        self.browser_label.pack()

        # 绑定变量
        self.selected_window = tk.StringVar()
        self.selected_window.set("请选择浏览器窗口")  # 设置默认值

        # 下拉框，初始为空
        self.browser_dropdown = tk.OptionMenu(root, self.selected_window, "请选择浏览器窗口")
        self.browser_dropdown.pack()

        # 获取已打开浏览器按钮
        self.get_browser_button = tk.Button(root, text="获取已打开的浏览器窗口", command=self.get_open_browsers)
        self.get_browser_button.pack()

        # 管理员号码输入框
        self.admin_numbers_label = tk.Label(root, text="输入管理员号码（每行一个）:")
        self.admin_numbers_label.pack()

        self.admin_numbers_text = tk.Text(root, height=10, width=30)
        self.admin_numbers_text.pack()

        # 设置管理员按钮
        self.set_admin_button = tk.Button(root, text="设置管理员", command=self.set_admin)
        self.set_admin_button.pack()

        # WebDriver配置（使用现有浏览器窗口进行操作）
        self.driver = None

    def get_open_browsers(self):
        """获取所有已打开的浏览器窗口，并填充下拉菜单"""
        open_windows = self.get_browser_windows()
        if open_windows:
            # 清空当前菜单
            self.browser_dropdown['menu'].delete(0, 'end')
            for window_title in open_windows:
                # 在下拉菜单中添加窗口标题
                self.browser_dropdown['menu'].add_command(label=window_title,
                                                          command=tk._setit(self.selected_window, window_title))
        else:
            messagebox.showwarning("警告", "没有检测到打开的浏览器窗口。")

    def get_browser_windows(self):
        """获取所有打开的浏览器窗口标题"""
        try:
            browser_windows = []
            # 获取所有活动窗口
            windows = gw.getWindowsWithTitle('')
            for window in windows:
                if 'Chrome' in window.title or 'Edge' in window.title:  # 过滤出浏览器窗口
                    browser_windows.append(window.title)  # 只保留窗口标题
            return browser_windows
        except Exception as e:
            print(f"获取浏览器窗口失败: {e}")
            return []

    def set_admin(self):
        """在选定的浏览器中执行设置管理员操作"""
        selected_window_title = self.selected_window.get()
        if selected_window_title == "请选择浏览器窗口":
            messagebox.showwarning("警告", "请先选择一个浏览器窗口。")
            return

        admin_numbers = self.admin_numbers_text.get("1.0", tk.END).splitlines()
        if not admin_numbers:
            messagebox.showwarning("警告", "请输入管理员号码。")
            return

        # 通过窗口标题获取对应的浏览器窗口并执行操作
        open_windows = gw.getWindowsWithTitle('')
        selected_window = None
        for window in open_windows:
            if window.title == selected_window_title:
                selected_window = window
                break

        if not selected_window:
            messagebox.showwarning("警告", "没有找到匹配的浏览器窗口。")
            return

        # 激活并最小化其他窗口
        selected_window.activate()

        # 获取已打开的浏览器窗口句柄
        try:
            # 启动 Chrome 远程调试服务并通过 Selenium 连接
            options = Options()
            options.add_argument("--remote-debugging-port=9222")  # 启动Chrome的远程调试

            # 如果浏览器已经打开并启用了远程调试端口，我们将连接到该窗口
            self.driver = webdriver.Chrome(options=options)
            self.driver.get("https://web.whatsapp.com")
        except Exception as e:
            messagebox.showerror("错误", f"无法连接到浏览器：{e}")
            return

        # 在选定的浏览器窗口中执行管理员设置操作
        for number in admin_numbers:
            try:
                # 找到搜索框并输入号码
                search_box = self.driver.find_element(By.CSS_SELECTOR,
                                                      "div[class='x1n2onr6 x1n2onr6 xyw6214 x78zum5 x1r8uery x1iyjqo2 xdt5ytf x6ikm8r x1odjw0f x1hc1fzr']")
                search_box.send_keys(number)
                time.sleep(2)  # 等待搜索结果显示

                # 找到“设为管理员”按钮并点击
                admin_button = self.driver.find_element(By.XPATH, "//div[@aria-label='设为管理员']")
                admin_button.click()
                time.sleep(1)  # 等待操作完成
            except Exception as e:
                print(f"设置管理员失败: {e}")
                continue

        messagebox.showinfo("操作完成", "管理员设置成功！")


# 创建应用程序实例
if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppBotApp(root)
    root.mainloop()