import tkinter as tk
from tkinter import ttk
import webbrowser

class page005(tk.Frame):
    def __init__(self, parent_frame):
        super().__init__(parent_frame)
        self.create_page()

    def create_page(self):
        # 设置背景颜色
        self.configure(bg="#f5f5f5")  # 淡灰色背景

        # 创建一个 Frame 用于放置工具卡片
        self.tools_frame = tk.Frame(self, bg="#f5f5f5")
        self.tools_frame.pack(pady=20, padx=10, fill=tk.BOTH, expand=True)

        # 工具网址列表
        self.tools_list = [
            {"name": "Google", "url": "https://www.google.com"},
            {"name": "GitHub", "url": "https://www.github.com"},
            {"name": "Stack Overflow", "url": "https://stackoverflow.com"},
            {"name": "Python Documentation", "url": "https://docs.python.org"},
            {"name": "PIL Documentation", "url": "https://pillow.readthedocs.io"},
            {"name": "Tkinter Documentation", "url": "https://docs.python.org/3/library/tkinter.html"}
        ]

        # 创建工具卡片
        self.create_tool_cards()

    def create_tool_cards(self):
        # 每行显示的工具数量
        tools_per_row = 3

        # 创建卡片
        for index, tool in enumerate(self.tools_list):
            row = index // tools_per_row
            column = index % tools_per_row

            card = ttk.Frame(self.tools_frame, padding="10", style="ToolCard.TFrame")
            card.grid(row=row, column=column, padx=10, pady=10, sticky=tk.NSEW)

            # 工具名称和链接
            link = tk.Label(card, text=tool["name"], font=("Helvetica", 14, "bold"), fg="#1E88E5", cursor="hand2", bg="#f5f5f5")
            link.pack()
            link.bind("<Button-1>", lambda e, url=tool["url"]: self.open_url(url))

            # 添加描述
            ttk.Label(card, text=tool["url"], font=("Helvetica", 12), wraplength=180).pack()

        # 调整卡片布局
        for i in range(tools_per_row):
            self.tools_frame.grid_columnconfigure(i, weight=1)

    def open_url(self, url):
        webbrowser.open(url)

if __name__ == '__main__':
    root = tk.Tk()
    root.title("常用工具网址")
    root.geometry("800x600")
    tools_page = page005(root)
    tools_page.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
