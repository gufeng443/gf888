import tkinter as tk
from tkinter import filedialog, messagebox
import os


def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        file_path_var.set(file_path)


def process_file():
    file_path = file_path_var.get()
    if not file_path:
        messagebox.showwarning("Warning", "Please select a TXT file.")
        return

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    folder_path = os.path.dirname(file_path)
    output_folder = os.path.join(folder_path, base_name)

    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # 创建一个字典来保存按开头数字分类的行
        grouped_lines = {str(i): [] for i in range(10, 20)}

        for line in lines:
            line = line.strip()
            if line and line.isdigit() and len(line) > 0:
                first_digit = line[:2]  # 取前两位进行分类
                if first_digit in grouped_lines:
                    grouped_lines[first_digit].append(line)

        for digit, lines in grouped_lines.items():
            if lines:
                output_file_name = os.path.join(output_folder, f"{base_name}_{digit}.txt")
                with open(output_file_name, 'w') as output_file:
                    output_file.write("\n".join(lines))

        messagebox.showinfo("Success", "Files have been processed and saved.")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# 创建主窗口
root = tk.Tk()
root.title("TXT File Splitter")

file_path_var = tk.StringVar()

# 创建界面组件
label = tk.Label(root, text="选择一个TXT文件:")
label.pack(pady=10)

file_entry = tk.Entry(root, textvariable=file_path_var, width=50)
file_entry.pack(pady=10)

browse_button = tk.Button(root, text="浏览", command=select_file)
browse_button.pack(pady=5)

process_button = tk.Button(root, text="开始执行", command=process_file)
process_button.pack(pady=20)

# 运行主循环
root.mainloop()
