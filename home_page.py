import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class HomePage(tk.Frame):
    def __init__(self, parent_frame):
        super().__init__(parent_frame)
        self.create_page()

    def create_page(self):
        # 设置淡蓝色背景
        self.configure(bg="#e0f7fa")  # 淡蓝色背景

        # 创建 Canvas 作为背景图层
        self.canvas = tk.Canvas(self, bg="#e0f7fa", bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 添加背景图片
        self.load_background_image()

        # 创建一个透明的 Frame 用于放置其他内容
        self.content_frame = tk.Frame(self.canvas, bg="#e0f7fa", bd=0)
        self.content_frame.place(relwidth=1, relheight=1)

        # 添加欢迎标题
        ttk.Label(self.content_frame, text="欢迎使用多功能工具", font=("Helvetica", 32, "bold"), background="#FFFFE0").pack(pady=20)

        # 添加中心图像
        self.load_center_image()

        # 添加功能简介
        self.create_info_cards()

        # 添加额外信息
        ttk.Label(self.content_frame, text="应用版本: 1.0.0", font=("Helvetica", 12), background="#e0f7fa").pack(pady=5, side=tk.LEFT, anchor='sw')
        ttk.Label(self.content_frame, text="电报Telegram: +44 7498 148126", font=("Helvetica", 12), background="#e0f7fa").pack(pady=5, side=tk.RIGHT, anchor='se')

    def load_background_image(self):
        image_path = "im00ge.png"  # 修改为实际背景图片路径

        if not os.path.isfile(image_path):
            print(f"Error: Background image file not found at {image_path}")
            return

        try:
            # 加载背景图片
            image = Image.open(image_path)
            image = image.resize((self.winfo_width(), self.winfo_height()), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)
        except Exception as e:
            print(f"Error loading background image: {e}")

    def load_center_image(self):
        image_path = "center_image.png"  # 修改为实际中心图像路径

        if not os.path.isfile(image_path):
            print(f"Error: Center image file not found at {image_path}")
            return

        try:
            # 加载中心图像
            image = Image.open(image_path)
            image = image.resize((400, 250), Image.Resampling.LANCZOS)
            self.center_image = ImageTk.PhotoImage(image)
            image_label = ttk.Label(self.content_frame, image=self.center_image, background="#E0F7FA")
            image_label.pack(pady=20)
        except Exception as e:
            print(f"Error loading center image: {e}")

    def create_info_cards(self):
        # 创建信息卡片容器
        card_frame = tk.Frame(self.content_frame, bg="#B2DFDB", bd=2, relief="flat")
        card_frame.pack(pady=25, padx=10, fill=tk.BOTH, expand=True)

        # 卡片样式
        card_style = ttk.Style()
        card_style.configure("Card.TFrame", background="#E0F7FA", borderwidth=2, relief="flat")

        # 卡片内容
        card_content = [
            {"title": "翻译功能", "description": "快速翻译多种语言的文本。"},
            {"title": "VCF制作", "description": "从文本或Excel中生成VCF文件。"},
            {"title": "云控数据分包", "description": "对数据进行多种分析和处理。"},
            {"title": "模拟器设管理", "description": "进入群组搜寻页，根据输入的管理号快速自动添加。"},
            {"title": "0VCF制作", "description": "0从文本或Excel中生成VCF文件。"},
            {"title": "0数据分析", "description": "0对数据进行多种分析和处理。"}
        ]

        # 每行显示的卡片数量
        cards_per_row = 3

        # 创建卡片
        for index, content in enumerate(card_content):
            row = index // cards_per_row
            column = index % cards_per_row

            card = ttk.Frame(card_frame, padding="10", style="Card.TFrame")
            card.grid(row=row, column=column, padx=10, pady=10, sticky=tk.NSEW)

            ttk.Label(card, text=content["title"], font=("Helvetica", 16, "bold")).pack(pady=5)
            ttk.Label(card, text=content["description"], font=("Helvetica", 12), wraplength=180).pack()

        # 调整卡片布局，使其在 Grid 布局中填充整个可用空间
        for i in range(cards_per_row):
            card_frame.grid_columnconfigure(i, weight=1)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("多功能工具")
    root.geometry("800x600")
    home_page = HomePage(root)
    home_page.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
