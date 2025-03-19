import tkinter as tk
from tkinter import scrolledtext

class page004(tk.Frame):
    def __init__(self, parent_frame):
        super().__init__(parent_frame)
        self.create_page()

        # 创建界面元素
        self.frame_novel = tk.Frame(self)
        self.frame_novel.pack(pady=10)

        self.label_novel = tk.Label(self.frame_novel, text="小说文本框")
        self.label_novel.grid(row=0, column=0, padx=10, pady=5)

        self.text_novel = scrolledtext.ScrolledText(self.frame_novel, width=80, height=10)
        self.text_novel.grid(row=1, column=0, padx=10, pady=5)

        self.btn_clear_blank_lines = tk.Button(self.frame_novel, text="清除空白行", command=self.clear_blank_lines)
        self.btn_clear_blank_lines.grid(row=2, column=0, padx=10, pady=5)

        self.btn_import_data = tk.Button(self.frame_novel, text="分次导入", command=self.import_data)
        self.btn_import_data.grid(row=3, column=0, padx=10, pady=5)

        self.frame_data = tk.Frame(self)
        self.frame_data.pack(pady=10)

        self.label_imported_data = tk.Label(self.frame_data, text="导入数据文本框")
        self.label_imported_data.grid(row=0, column=0, padx=10, pady=5)

        self.text_imported_data = scrolledtext.ScrolledText(self.frame_data, width=80, height=40)
        self.text_imported_data.grid(row=1, column=0, padx=10, pady=5)

        self.btn_clear_data = tk.Button(self.frame_data, text="清空数据", command=self.clear_data)
        self.btn_clear_data.grid(row=2, column=0, padx=10, pady=5)

        # 记录导入的数据块
        self.data_chunks = []

    def create_page(self):
        # 这是一个空方法，目前没有用到
        pass

    def clear_blank_lines(self):
        # 清除空白行
        novel_text = self.text_novel.get("1.0", tk.END)
        clean_text = "\n".join(line for line in novel_text.splitlines() if line.strip())
        self.text_novel.delete("1.0", tk.END)
        self.text_novel.insert("1.0", clean_text)

    def import_data(self):
        # 分次导入数据
        novel_text = self.text_novel.get("1.0", tk.END)
        chunks = self.chunk_text(novel_text, 1500)
        self.data_chunks = chunks

        # 更新导入数据显示
        self.text_imported_data.delete("1.0", tk.END)
        for i, chunk in enumerate(chunks):
            self.text_imported_data.insert(tk.END, f"第{i+1}部分:\n{chunk}\n\n")

    def chunk_text(self, text, chunk_size):
        # 将文本按指定大小分块
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i+chunk_size])
        return chunks

    def clear_data(self):
        # 清空导入的数据和重置分次导入状态
        self.data_chunks = []
        self.text_imported_data.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Page 004")
    root.geometry("800x600")
    app = page004(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
