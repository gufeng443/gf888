import os
import tkinter as tk
from tkinter import filedialog

def get_directory_structure(rootdir):
    """获取目录结构"""
    structure = []
    for root, dirs, files in os.walk(rootdir):
        level = root.replace(rootdir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        structure.append('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            structure.append('{}├── {}'.format(subindent, f))
    return '\n'.join(structure)

def select_folder():
    """选择文件夹并显示目录结构"""
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        directory_structure = get_directory_structure(folder_selected)
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, directory_structure)

# 创建主窗口
root = tk.Tk()
root.title("文件夹结构查看器")

# 创建选择文件夹按钮
select_button = tk.Button(root, text="选择文件夹", command=select_folder)
select_button.pack(pady=10)

# 创建文本框用于显示目录结构
text_box = tk.Text(root, wrap=tk.NONE)
text_box.pack(fill=tk.BOTH, expand=True)

# 运行主循环
root.mainloop()