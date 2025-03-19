import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from selenium import webdriver


class BrowserAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("浏览器自动化工具")

        # 存储浏览器窗口和复选框的列表
        self.browser_windows = []
        self.checkbuttons = []
        self.window_count = 0  # 用于管理窗口的顺序

        self.create_widgets()

    def create_widgets(self):
        # 创建框架
        self.browser_frame = ttk.LabelFrame(self.root, text="浏览器操作", padding=10)
        self.browser_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.automation_frame = ttk.LabelFrame(self.root, text="自动化操作", padding=10)
        self.automation_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # 浏览器操作部分：网址输入框，浏览器数量选择框，打开浏览器按钮
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

        self.open_browser_button = ttk.Button(self.browser_frame, text="打开浏览器", command=self.open_browser)
        self.open_browser_button.grid(row=2, column=0, columnspan=2, pady=10)

        # 自动化操作部分：自动启动、中断重启、导入链接、平分txt文件等
        self.start_button = ttk.Button(self.automation_frame, text="自动启动", command=self.auto_start)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        self.restart_button = ttk.Button(self.automation_frame, text="中断重启", command=self.restart)
        self.restart_button.grid(row=0, column=1, padx=5, pady=5)

        self.link_label = ttk.Label(self.automation_frame, text="输入链接:")
        self.link_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.link_entry = ttk.Entry(self.automation_frame, width=40)
        self.link_entry.grid(row=1, column=1, padx=5, pady=5)

        self.import_link_button = ttk.Button(self.automation_frame, text="导入链接", command=self.import_link)
        self.import_link_button.grid(row=2, column=0, columnspan=2, pady=5)

        self.folder_button = ttk.Button(self.automation_frame, text="选择文件夹", command=self.select_folder)
        self.folder_button.grid(row=3, column=0, padx=5, pady=5)

        self.split_txt_button = ttk.Button(self.automation_frame, text="平分TXT文件", command=self.split_txt)
        self.split_txt_button.grid(row=3, column=1, padx=5, pady=5)

        # 浏览器窗口控制部分
        self.all_select_button = ttk.Button(self.browser_frame, text="全选", command=self.select_all)
        self.all_select_button.grid(row=3, column=0, padx=5, pady=5)

        self.all_deselect_button = ttk.Button(self.browser_frame, text="全不选", command=self.deselect_all)
        self.all_deselect_button.grid(row=3, column=1, padx=5, pady=5)

    def open_browser(self):
        try:
            num_browsers = int(self.num_browser.get())
            url = self.url_entry.get()

            # 打开浏览器并保存窗口
            for i in range(num_browsers):
                driver = webdriver.Chrome()  # 这里可以换成其他浏览器驱动
                driver.get(url)
                self.browser_windows.append(driver)

                # 为新打开的浏览器窗口增加UI控件（复选框、按钮）
                row_position = 4 + self.window_count  # 控件位置，根据已经打开的窗口数量来设置
                var = tk.BooleanVar()
                self.checkbuttons.append(var)

                checkbox = ttk.Checkbutton(self.browser_frame, text=f"浏览器 {self.window_count + 1}", variable=var)
                checkbox.grid(row=row_position, column=0, sticky="w")

                # 弹起按钮，保持原始窗口位置
                pop_button = ttk.Button(self.browser_frame, text=f"弹起 {self.window_count + 1}",
                                        command=lambda i=self.window_count, d=driver: self.restore_window(i, d))
                pop_button.grid(row=row_position, column=1, padx=5, pady=5)

                # 最小化按钮
                min_button = ttk.Button(self.browser_frame, text=f"最小化 {self.window_count + 1}",
                                        command=lambda d=driver: d.minimize_window())
                min_button.grid(row=row_position, column=2, padx=5, pady=5)

                self.window_count += 1  # 每次打开新的浏览器窗口时，增加计数器

        except Exception as e:
            messagebox.showerror("错误", f"打开浏览器时出错: {str(e)}")

    def restore_window(self, i, driver):
        # 获取并恢复浏览器窗口的原始位置和大小
        window_rect = driver.get_window_rect()
        x = window_rect['x']
        y = window_rect['y']
        width = window_rect['width']
        height = window_rect['height']

        # 设置窗口位置和大小
        driver.set_window_position(x, y)
        driver.set_window_size(width, height)

    def auto_start(self):
        # 这里的逻辑会根据第二部分的功能进行填写
        print("自动启动逻辑执行")

    def restart(self):
        # 这里的逻辑会根据第二部分的功能进行填写
        print("中断重启逻辑执行")

    def import_link(self):
        # 这里的逻辑会根据第三部分的功能进行填写
        print("导入链接逻辑执行")

    def split_txt(self):
        # 这里的逻辑会根据第四部分的功能进行填写
        print("平分TXT文件逻辑执行")

    def select_folder(self):
        # 选择文件夹对话框
        folder_path = filedialog.askdirectory(title="选择TXT文件夹")
        if folder_path:
            print(f"选择的文件夹路径：{folder_path}")
            # 可以将选择的路径保存并用于后续平分txt文件的操作
        else:
            messagebox.showwarning("警告", "未选择文件夹")

    def select_all(self):
        for var in self.checkbuttons:
            var.set(True)

    def deselect_all(self):
        for var in self.checkbuttons:
            var.set(False)


if __name__ == "__main__":
    root = tk.Tk()
    app = BrowserAutomationApp(root)
    root.mainloop()
