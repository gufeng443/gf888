import tkinter as tk
from tkinter import ttk
import importlib
import json
import os


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("多功能工具--------孤风出品必属精品")
        self.geometry("850x700")

        # 配置文件路径，可以调整为相对路径或者动态获取
        config_path = 'config.json'
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件未找到: {config_path}")

        # 读取配置文件
        with open(config_path, 'r', encoding='utf-8') as file:
            self.config = json.load(file)

        # 创建样式
        self.style = ttk.Style()
        self.configure_styles()

        self.create_widgets()
        self.load_page('主页')

    def configure_styles(self):
        self.style.configure("NavButton.TButton",
                             background="lightblue",
                             foreground="black",
                             font=("Helvetica", 12),
                             padding=10)
        self.style.map("NavButton.TButton",
                       background=[('active', 'lightgreen'), ('pressed', 'lightcoral')],
                       foreground=[('pressed', 'white')],
                       relief=[('pressed', 'sunken')])

        self.style.configure("PageFrame.TFrame",
                             background="white",
                             borderwidth=2,
                             relief="solid")

    def create_widgets(self):
        self.nav_frame = tk.Frame(self, width=200, bg='lightgrey')
        self.nav_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.page_frame = ttk.Frame(self, style="PageFrame.TFrame")
        self.page_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.nav_buttons = {}
        for name, module_name in self.config.get('pages', {}).items():
            button = ttk.Button(self.nav_frame, text=name, style="NavButton.TButton",
                                command=lambda n=name: self.load_page(n))
            button.pack(fill=tk.X, pady=2)
            self.nav_buttons[name] = button

    def load_page(self, page_name):
        for widget in self.page_frame.winfo_children():
            widget.destroy()

        module_name = self.config['pages'].get(page_name)
        if not module_name:
            ttk.Label(self.page_frame, text=f"页面配置错误: {page_name} 不存在", foreground="red").pack(pady=20)
            return

        try:
            module = importlib.import_module(f'pages.{module_name}')
            print(f"加载模块: pages.{module_name}")

            # 创建页面实例
            page_class = next(
                (cls for cls in [getattr(module, 'EmulatorSelector', None),
                                 getattr(module, 'ZJ', None),
                                 getattr(module, 'HomePage', None),
                                 getattr(module, 'TranslationPage', None),
                                 getattr(module, 'CommonToolsPage', None),
                                 getattr(module, 'ToolsPage', None),
                                 getattr(module, 'CanvasFrame', None),
                                 getattr(module, 'MyApplication', None),
                                 getattr(module, 'AutoSplitPage', None)]
                 if cls is not None), None
            )
            if page_class:
                page = page_class(self.page_frame)
                page.pack(fill=tk.BOTH, expand=True)
            elif hasattr(module, 'create_page'):
                module.create_page(self.page_frame)
            else:
                raise AttributeError(f"模块 '{module_name}' 不含有效页面类.")

        except Exception as e:
            ttk.Label(self.page_frame, text=f"无法加载页面: {e}", foreground="red").pack(pady=20)


if __name__ == '__main__':
    app = Application()
    app.mainloop()
