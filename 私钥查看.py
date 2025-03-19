import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
import os

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
        hex_data = read_file_as_hex(file_path)
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, hex_data)
    else:
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, "File not found.")

root = TkinterDnD.Tk()
root.title("KEY 文件十六进制查看器")
root.geometry("600x400")

drop_frame = tk.Label(root, text="将 KEY 文件拖放到此处", bg="lightgray", font=("Arial", 14))
drop_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

text_box = tk.Text(root, wrap=tk.WORD, font=("Arial", 12))
text_box.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

drop_frame.drop_target_register(DND_FILES)
drop_frame.dnd_bind('<<Drop>>', on_drop)

root.mainloop()