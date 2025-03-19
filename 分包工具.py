import os
import tkinter as tk
from tkinter import filedialog


def get_folder_path():
    """打开文件夹选择对话框，并返回选择的文件夹路径。"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    folder_path = filedialog.askdirectory(title="选择要处理的文件夹")
    return folder_path


def process_files(folder_path):
    """处理文件夹中的所有txt文件，合并数据，并分割成多个文件。"""
    all_lines = []

    # 遍历文件夹中的所有txt文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                all_lines.extend(lines)

    # 分割数据并保存到新文件中
    lines_per_file = 2000
    total_lines = len(all_lines)
    num_files = (total_lines + lines_per_file - 1) // lines_per_file  # 向上取整

    for i in range(num_files):
        start_index = i * lines_per_file
        end_index = min((i + 1) * lines_per_file, total_lines)
        chunk = all_lines[start_index:end_index]

        output_file_path = os.path.join(folder_path, f'output_part_{i + 1}.txt')
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.writelines(chunk)

    print(f"处理完成，共生成 {num_files} 个文件。")


if __name__ == "__main__":
    folder_path = get_folder_path()
    if folder_path:
        process_files(folder_path)
    else:
        print("未选择文件夹。")
