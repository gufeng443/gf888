import os
import re
import tkinter as tk
from tkinter import filedialog


def convert_to_vcf(input_data):
    vcard_counter = 1
    vcf_data = ""
    for data in input_data:
        # 清理数据中的电话号码（根据实际情况可以自定义这个函数）
        cleaned_data = clean_number(str(data))
        # 查找10位或更多位的数字（在这里可以对实际数据进行调整）
        numbers = re.findall(r'\b\d{10,}\b', cleaned_data)
        for number in numbers:
            vcf_data += f"BEGIN:VCARD\nVERSION:3.0\nN:;A{str(vcard_counter).zfill(4)};;;\nFN:A{str(vcard_counter).zfill(4)}\nTEL;type=CELL;type=VOICE;type=pref:+{number}\nEND:VCARD\n"
            vcard_counter += 1

    return vcf_data


def clean_number(number):
    # 这个函数可以根据实际需要来清理号码
    # 示例清理：去除非数字字符
    return re.sub(r'\D', '', number)


def main():
    # 创建一个简单的图形用户界面（GUI）用于选择文件夹
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 选择文件夹
    folder_path = filedialog.askdirectory(title="选择文件夹")

    if not folder_path:
        print("未选择任何文件夹。")
        return

    # 获取所有子文件夹名称
    subfolders = [f.name for f in os.scandir(folder_path) if f.is_dir()]

    # 保存文件夹名称到“互粉.txt”
    txt_file_path = os.path.join(folder_path, "互粉.txt")
    with open(txt_file_path, "w", encoding="utf-8") as txt_file:
        for folder in subfolders:
            txt_file.write(folder + "\n")

    print(f"文件夹名称已保存到 {txt_file_path}")

    # 从“互粉.txt”读取数据
    with open(txt_file_path, "r", encoding="utf-8") as txt_file:
        input_data = txt_file.readlines()

    # 转换为VCF格式
    vcf_data = convert_to_vcf(input_data)

    # 保存VCF数据到“01.VCF”
    vcf_file_path = os.path.join(folder_path, "01.VCF")
    with open(vcf_file_path, "w", encoding="utf-8") as vcf_file:
        vcf_file.write(vcf_data)

    print(f"VCF文件已保存到 {vcf_file_path}")


if __name__ == "__main__":
    main()
