import os
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
import chardet  # 导入chardet库


# 查找指定文件夹中所有txt文件，并在文件中查找指定的数据
def search_files(folder_path, search_term):
    matched_files = []  # 存储符合条件的文件路径
    # 遍历文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 只考虑txt文件
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                # 打开文件并查找内容
                try:
                    # 使用 chardet 检测文件编码
                    with open(file_path, "rb") as f:
                        raw_data = f.read()
                        result = chardet.detect(raw_data)
                        encoding = result['encoding']

                    # 使用检测到的编码打开文件
                    with open(file_path, "r", encoding=encoding) as f:
                        content = f.read()
                        if search_term in content:
                            matched_files.append(file_path)
                except Exception as e:
                    print(f"读取文件 {file_path} 时出错: {e}")
    return matched_files


# 选择文件夹
def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_label.config(text=folder_path)


# 开始查找
def start_search():
    folder_path = folder_label.cget("text")
    search_term = search_entry.get()

    if not folder_path:
        messagebox.showwarning("警告", "请先选择一个文件夹")
        return

    if not search_term:
        messagebox.showwarning("警告", "请输入搜索内容")
        return

    # 执行查找操作
    matched_files = search_files(folder_path, search_term)

    if matched_files:
        # 显示找到的文件并打开第一个匹配的文件
        result_text = "\n".join(matched_files)
        result_label.config(text=result_text)

        # 打开第一个匹配的文件
        webbrowser.open(f"file:///{matched_files[0]}")
    else:
        messagebox.showinfo("提示", "没有找到匹配的文件")


# 创建GUI界面
root = tk.Tk()
root.title("文件搜索工具")

# 文件夹选择部分
folder_button = tk.Button(root, text="选择文件夹", command=select_folder)
folder_button.pack(pady=10)

folder_label = tk.Label(root, text="未选择文件夹", width=50, anchor='w')
folder_label.pack(pady=5)

# 数据输入部分
search_label = tk.Label(root, text="请输入查找的数据:")
search_label.pack(pady=5)

search_entry = tk.Entry(root, width=50)
search_entry.pack(pady=5)

# 开始查找按钮
start_button = tk.Button(root, text="开始查找", command=start_search)
start_button.pack(pady=10)

# 显示搜索结果的标签
result_label = tk.Label(root, text="", width=50, height=10, anchor='w', justify='left', padx=10, pady=10)
result_label.pack(pady=10)

# 运行主循环
root.mainloop()
