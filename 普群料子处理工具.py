import os
import re
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
from tkinter import font
import subprocess
#水军可是是交单员的账号
src_path = "C:/Users/Administrator/Desktop/料子"  #下载的料子应该保存的位置
process_path = "C:/Users/Administrator/Desktop/LZ"  #处理后的料子自动保存的位置
export_dir = "C:/Users/Administrator/Desktop/交单"  #料子信息保存的位置
export_links_path = "C:/Users/Administrator/Desktop/小群链接.txt"  #提取的链接保存的位置


def adjust_links(line):
    """检查并调整超链接到下一行"""
    hyperlink_pattern = r"https?://[^\s]+"
    matches = re.findall(hyperlink_pattern, line)
    for match in matches:
        if line.strip() != match:  # 如果超链接前面有其他数据
            line = line.replace(match, f'\t\n{match}')   #可以在n后添加“人字，为后续手动填写成群人数方便，如果需要成群截图管理器的配合就不要添加。
    return line


def extract_data():
    text_area.delete('1.0', tk.END)  # 清空文本框旧数据
    for filename in os.listdir(src_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(src_path, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                # 获取前三行并显示到文本框
                for line in lines[:1]:
                    adjusted_line = adjust_links(line)
                    text_area.insert(tk.END, adjusted_line)
                text_area.insert(tk.END, '\n\n')  # 加3个空白行


def process_files():   #处理料子指定的规则
    if not os.path.exists(process_path):
        os.makedirs(process_path)

    for filename in os.listdir(src_path):
        if filename.endswith(".txt"):
            in_filepath = os.path.join(src_path, filename)
            out_filepath = os.path.join(process_path, filename)
            with open(in_filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            processed_lines = []
            for line in lines:
                # 清除行内空格和符号，只保留字母和数字
                clean_line = re.sub(r'\W', '', line).replace(" ", "")
                # 只保留行内包含10位以上数字的行
                numeric_match = re.search(r'\d{10,}', clean_line)
                if numeric_match:
                    # 获取10位以上的数字
                    number = numeric_match.group()
                    # 检查此数字是否后面有字母，如果有字母只保留字母前的部分
                    alpha_index = re.search(r'[A-Za-z]', number)
                    if alpha_index:
                        number = number[:alpha_index.start()]
                    processed_lines.append(number + '\n')

            # 将处理后的数据保存到目标文件
            with open(out_filepath, 'w', encoding='utf-8') as f:
                f.writelines(processed_lines)

    # 显示处理完毕的消息
    messagebox.showinfo("孤峰出品必属精品", f"文件已处理，并保存到 {process_path}")


def export_and_clear():   #保存料子信息是指定的规则
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H-%M-%S")

    todays_export_dir = os.path.join(export_dir, current_date)
    # 确保当前日期的目录存在
    os.makedirs(todays_export_dir, exist_ok=True)

    export_filepath = os.path.join(todays_export_dir, f"{current_time}.txt")

    with open(export_filepath, 'w', encoding='utf-8') as f:
        f.write(text_area.get('1.0', tk.END))

    # 清空文本框
    text_area.delete('1.0', tk.END)
    messagebox.showinfo("孤峰出品必属精品", f"数据已保存到 {export_filepath}")


def add_management():
    try:
        lines_count = int(entry_lines.get())
    except ValueError:
        messagebox.showerror("输入错误", "请输入一个有效的正整数")
        return

    if lines_count <= 0:
        messagebox.showerror("输入错误", "请输入一个正整数")
        return

    for filename in os.listdir(process_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(process_path, filename)
            with open(file_path, 'r+', encoding='utf-8') as file:
                lines = file.readlines()
                max_line = min(lines_count, len(lines))

                for i in range(max_line):
                    lines[i] = lines[i].strip() + 'x\n'

                # 将文件指针移动到文件开头并写入修改后的内容
                file.seek(0)
                file.writelines(lines)

    messagebox.showinfo("操作完成", "数据已更新并保存")


def export_links():
    content = text_area.get('1.0', tk.END)
    hyperlink_pattern = r"https?://[^\s]+"
    matches = re.findall(hyperlink_pattern, content)

    with open(export_links_path, 'w', encoding='utf-8') as file:
        for match in matches:
            file.write(match + '\n')

    messagebox.showinfo("导出完成", f"超链接数据已导出到 {export_links_path}")


def add_water_army():
    number = entry_number.get().strip()
    if not number:
        messagebox.showerror("输入错误", "请输入一个有效的号码")
        return

    for filename in os.listdir(process_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(process_path, filename)
            with open(file_path, 'r+', encoding='utf-8') as file:
                lines = file.readlines()

                # 找到最后一行包含字母的行的索引
                last_letter_line_index = None
                for i in range(len(lines) - 1, -1, -1):
                    if any(char.isalpha() for char in lines[i]):
                        last_letter_line_index = i
                        break

                if last_letter_line_index is not None:
                    # 在最后一行包含字母的行后面插入号码数据
                    lines.insert(last_letter_line_index + 1, number + '\n')

                    # 将文件指针移动到文件开头并写入修改后的内容
                    file.seek(0)
                    file.writelines(lines)

    messagebox.showinfo("操作完成", "号码已成功添加到所有文件的最后一行包含字母的行后面")


def append_numbers():
    for filename in os.listdir(process_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(process_path, filename)
            with open(file_path, 'r+', encoding='utf-8') as file:
                lines = file.readlines()

                # 找到最后一行包含字母的行的索引
                last_letter_line_index = None
                for i in range(len(lines) - 1, -1, -1):
                    if any(char.isalpha() for char in lines[i]):
                        last_letter_line_index = i
                        break

                if last_letter_line_index is not None:
                    # 复制包含字母的行
                    letter_lines = [line for line in lines if any(char.isalpha() for char in line)]

                    # 去除字母数据,只保留字母前的数据
                    processed_lines = []
                    for line in letter_lines:
                        processed_line = line.split(next(char for char in line if char.isalpha()))[0]
                        processed_lines.append(processed_line + '\n')

                    # 将处理后的数据插入到最后一行包含字母的行后面
                    lines[last_letter_line_index + 1:last_letter_line_index + 1] = processed_lines

                # 将文件指针移动到文件开头并写入修改后的内容
                file.seek(0)
                file.writelines(lines)

    messagebox.showinfo("操作完成", "数据已追加并保存")

def run_vcf_script():
    try:
        subprocess.run(["python", "E:/MNQ/ZH/VCF.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"运行 VCF.py 失败: {e}")

def run_script():
    script_path = "E:/MNQ/ZH/VCF.py"
    subprocess.Popen(["python", script_path])

# 创建主窗口
root = tk.Tk()
root.title("懒人专属         孤风出品--必属精品")
root.geometry("500x500")

# 创建字体对象
font_style = font.Font(family="Arial", size=12)

# 创建一个带滚动条的文本框
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=font_style)
text_area.pack(fill=tk.BOTH, expand=True)

# 创建一个框架，用于放置按钮
button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, pady=10)

# 创建按钮并添加到框架中
extract_button = tk.Button(button_frame, text="提取数据", command=extract_data, font=font_style)
extract_button.grid(row=0, column=0, padx=10, pady=5)

process_button = tk.Button(button_frame, text="数据处理", command=process_files, font=font_style)
process_button.grid(row=0, column=1, padx=10, pady=5)

export_button = tk.Button(button_frame, text="导出数据并清除", command=export_and_clear, font=font_style)
export_button.grid(row=0, column=2, padx=10, pady=5)

export_links_button = tk.Button(button_frame, text="导出链接", command=export_links, font=font_style)
export_links_button.grid(row=0, column=3, padx=10, pady=5)

# 创建一个框架，用于放置管理按钮和输入框
management_frame = tk.Frame(button_frame)
management_frame.grid(row=1, column=0, columnspan=4, pady=5)

entry_lines = tk.Entry(management_frame, width=21, font=font_style)
entry_lines.pack(side=tk.LEFT, padx=5)
entry_lines.insert(0, "1")  # 设置默认值为1
add_management_button = tk.Button(management_frame, text="添加管理", command=add_management, font=font_style)
add_management_button.pack(side=tk.LEFT)

append_button = tk.Button(management_frame, text="追加", command=append_numbers, font=font_style, bg="#f7c6c7")
append_button.pack(side=tk.LEFT, padx=10)
# 创建一个框架，用于放置水军按钮和输入框
water_army_frame = tk.Frame(button_frame)
water_army_frame.grid(row=2, column=0, columnspan=4, pady=5)

entry_number = tk.Entry(water_army_frame, width=15, font=font_style)
entry_number.pack(side=tk.LEFT, padx=5)

add_water_army_button = tk.Button(water_army_frame, text="添加水军", command=add_water_army, font=font_style)
add_water_army_button.pack(side=tk.LEFT)

run_script_button = tk.Button(water_army_frame, text="带编号VCF转换", command=run_script, font=font_style)
run_script_button.pack(side=tk.LEFT)



# 运行主循环
root.mainloop()