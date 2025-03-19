import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
import binascii
import threading

class EXEToBinaryEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("EXE to Binary Editor")
        self.root.geometry("600x400")

        # 创建文本编辑器
        self.text_editor = tk.Text(self.root, wrap=tk.NONE)
        self.text_editor.pack(fill=tk.BOTH, expand=True)

        # 创建一键复制按钮
        self.copy_button = tk.Button(self.root, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.pack()

        # 启用拖放功能
        self.text_editor.drop_target_register(DND_FILES)
        self.text_editor.dnd_bind('<<Drop>>', self.handle_drop)

    def handle_drop(self, event):
        # 获取拖放的文件路径
        file_path = event.data.strip('{}')
        if file_path.lower().endswith('.exe'):
            # 使用多线程处理文件读取和二进制转换
            threading.Thread(target=self.load_exe_file, args=(file_path,), daemon=True).start()
        else:
            self.text_editor.insert(tk.END, "Please drop a valid .EXE file.\n")

    def load_exe_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                binary_data = file.read()
                # 将二进制数据转换为十六进制字符串
                hex_data = binascii.hexlify(binary_data).decode('utf-8')
                # 在主线程中更新编辑器内容
                self.root.after(0, self.update_editor, hex_data)
        except Exception as e:
            self.root.after(0, self.text_editor.insert, tk.END, f"Error loading file: {e}\n")

    def update_editor(self, content):
        # 清空编辑器并插入新内容
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.insert(tk.END, content)

    def copy_to_clipboard(self):
        # 获取编辑器中的内容
        content = self.text_editor.get(1.0, tk.END)
        # 复制到剪贴板
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = EXEToBinaryEditor(root)
    root.mainloop()