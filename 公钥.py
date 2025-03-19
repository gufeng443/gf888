import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
import os

def read_file_as_binary(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            binary_content = ' '.join(f'{byte:08b}' for byte in content)
            return binary_content
    except Exception as e:
        return f"Error reading file: {e}"

def read_file_as_hex(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            hex_content = content.hex()
            return hex_content
    except Exception as e:
        return f"Error reading file: {e}"

def on_drop(event):
    file_path = event.data.strip('{}')
    if os.path.exists(file_path):
        if display_mode.get() == "hex":
            data = read_file_as_hex(file_path)
        else:
            data = read_file_as_binary(file_path)
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, data)
    else:
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, "File not found.")

def update_display_mode():
    # 当用户切换显示模式时，重新加载当前文件
    if file_path:
        on_drop(file_path)

root = TkinterDnD.Tk()
root.title("KEY 文件查看器")
root.geometry("600x400")

# 拖放区域
drop_frame = tk.Label(root, text="将 KEY 文件拖放到此处", bg="lightgray", font=("Arial", 14))
drop_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# 显示模式选择
display_mode = tk.StringVar(value="hex")
hex_radio = tk.Radiobutton(root, text="十六进制", variable=display_mode, value="hex", command=update_display_mode)
hex_radio.pack(pady=5)
binary_radio = tk.Radiobutton(root, text="二进制", variable=display_mode, value="binary", command=update_display_mode)
binary_radio.pack(pady=5)

# 文本框
text_box = tk.Text(root, wrap=tk.WORD, font=("Arial", 12))
text_box.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

# 绑定拖放事件
drop_frame.drop_target_register(DND_FILES)
drop_frame.dnd_bind('<<Drop>>', on_drop)

# 初始化文件路径
file_path = None

root.mainloop()