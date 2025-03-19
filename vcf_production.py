# pages/vcf_production.py

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import re
import pandas as pd

def clean_number(number):
    cleaned = re.sub(r'[^0-9+]', '', number)
    return cleaned

def extract_number(line):
    if not isinstance(line, str):
        line = str(line)
    line = line.strip()
    number = ""
    found_number = False
    for char in line:
        if char.isdigit() or (char == '+' and not found_number):
            number += char
            found_number = True
        elif char.isalpha() and found_number:
            break
        elif found_number:
            number += char
    number = clean_number(number)
    return number

def convert_to_vcf(input_data):
    contacts = []
    for line in input_data:
        number = extract_number(line)
        if len(re.sub(r'\D', '', number)) >= 7:
            contacts.append(number)
    vcf_data = []
    for idx, number in enumerate(contacts, start=1):
        label = f"A{str(idx).zfill(4)}"
        vcf_record = (f"BEGIN:VCARD\nVERSION:3.0\nN:;{label};;;\nFN:{label}\n"
                      f"TEL;type=CELL;type=VOICE;type=pref:{number}\nEND:VCARD\n")
        vcf_data.append(vcf_record)
    return vcf_data

def write_vcf_files(input_file, vcf_data, split_files, split_size):
    base_name = os.path.splitext(os.path.basename(input_file))[0].strip()
    dir_name = os.path.join(os.path.dirname(input_file), f"{base_name}_vcf")
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    if split_files:
        split_data = split_vcf_data(vcf_data, split_size)
        for idx, data_chunk in enumerate(split_data, start=1):
            output_filename = os.path.join(dir_name, f"{base_name}-{idx}.vcf")
            try:
                with open(output_filename, 'w', encoding='utf-8') as vcf_file:
                    vcf_file.writelines(data_chunk)
                print(f"Split VCF file created: {output_filename}")
            except Exception as e:
                print(f"Error writing split VCF file {output_filename}: {e}")
    else:
        original_vcf_file = os.path.join(dir_name, f"{base_name}.vcf")
        with open(original_vcf_file, 'w', encoding='utf-8') as vcf_file:
            vcf_file.writelines(vcf_data)
        print(f"Original VCF file created: {original_vcf_file}")

def save_numbers_to_txt(input_file, numbers, split_files, split_size):
    base_name = os.path.splitext(os.path.basename(input_file))[0].strip()
    txt_dir = os.path.join(os.path.dirname(input_file), f"{base_name}_txt")
    if not os.path.exists(txt_dir):
        os.makedirs(txt_dir)
    if split_files:
        split_data = split_vcf_data(numbers, split_size)
        for idx, data_chunk in enumerate(split_data, start=1):
            # 在这里使用原始的电话号码，不带加号
            split_filename = os.path.join(txt_dir, f"{base_name}-{idx}.txt")
            try:
                with open(split_filename, 'w', encoding='utf-8') as txt_file:
                    txt_file.write('\n'.join(data_chunk))
                print(f"Split TXT file created: {split_filename}")
            except Exception as e:
                print(f"Error writing split TXT file {split_filename}: {e}")
    else:
        all_numbers_file = os.path.join(txt_dir, f"{base_name}.txt")
        with open(all_numbers_file, 'w', encoding='utf-8') as txt_file:
            txt_file.write('\n'.join(numbers))
        print(f"All numbers TXT file created: {all_numbers_file}")
def split_vcf_data(data, split_size):
    split_files = []
    for i in range(0, len(data), split_size):
        split_files.append(data[i:i + split_size])
    return split_files

def process_txt_file(input_file, generate_vcf, generate_txt, split_files, split_size):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        numbers = [extract_number(line) for line in lines if len(re.sub(r'\D', '', extract_number(line))) >= 7]
        if generate_vcf:
            vcf_data = convert_to_vcf(numbers)
            write_vcf_files(input_file, vcf_data, split_files, split_size)
        if generate_txt:
            save_numbers_to_txt(input_file, numbers, split_files, split_size)
        messagebox.showinfo("Success", "数据处理完成!")
    except Exception as e:
        messagebox.showerror("Error", f"Error processing text file {input_file}: {e}")

def process_excel_file(input_file, generate_vcf, generate_txt, split_files, split_size):
    try:
        df = pd.read_excel(input_file, engine='openpyxl')
        numbers = [extract_number(str(cell)) for cell in df.values.flatten() if
                   len(re.sub(r'\D', '', extract_number(str(cell)))) >= 7]
        if generate_vcf:
            vcf_data = convert_to_vcf(numbers)
            write_vcf_files(input_file, vcf_data, split_files, split_size)
        if generate_txt:
            save_numbers_to_txt(input_file, numbers, split_files, split_size)
        messagebox.showinfo("Success", "数据处理完成!")
    except Exception as e:
        messagebox.showerror("Error", f"Error processing Excel file {input_file}: {e}")

def process_files(input_dir, generate_vcf, generate_txt, split_files, split_size):
    try:
        for filename in os.listdir(input_dir):
            input_file = os.path.join(input_dir, filename)
            if filename.endswith(".txt"):
                process_txt_file(input_file, generate_vcf, generate_txt, split_files, split_size)
            elif filename.endswith(".xls") or filename.endswith(".xlsx"):
                process_excel_file(input_file, generate_vcf, generate_txt, split_files, split_size)
            else:
                print(f"Unsupported file format: {filename}")
        messagebox.showinfo("Success", "拆分完成")
    except Exception as e:
        messagebox.showerror("Error", f"Error processing files: {e}")

def create_page(parent_frame):
    def select_input_directory():
        dir_path = filedialog.askdirectory()
        if dir_path:
            input_dir_var.set(dir_path)

    def start_processing():
        input_dir = input_dir_var.get()
        generate_vcf = vcf_var.get()
        generate_txt = txt_var.get()
        split_files = split_var.get()
        split_size = int(split_size_var.get())

        if not os.path.exists(input_dir):
            messagebox.showwarning("Warning", "Input directory does not exist!")
            return

        if split_size <= 0:
            messagebox.showwarning("Warning", "Split size must be a positive integer!")
            return

        process_files(input_dir, generate_vcf, generate_txt, split_files, split_size)

    input_dir_var = tk.StringVar()
    vcf_var = tk.BooleanVar(value=False)
    txt_var = tk.BooleanVar(value=True)
    split_var = tk.BooleanVar(value=True)
    split_size_var = tk.StringVar(value="30")

    ttk.Label(parent_frame, text="选择料子文件夹：").grid(row=0, column=0, padx=10, pady=10, sticky="W")
    ttk.Entry(parent_frame, textvariable=input_dir_var, width=50).grid(row=0, column=1, padx=10, pady=10)
    ttk.Button(parent_frame, text="打开", command=select_input_directory).grid(row=0, column=2, padx=10, pady=10)

    ttk.Checkbutton(parent_frame, text="数据转换为VCF", variable=vcf_var).grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="W")
    ttk.Checkbutton(parent_frame, text="数据转换为TXT", variable=txt_var).grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="W")
    ttk.Checkbutton(parent_frame, text="拆分数据", variable=split_var).grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky="W")

    ttk.Label(parent_frame, text="拆分后每个文件的数据数量:").grid(row=4, column=0, padx=10, pady=5, sticky="W")
    ttk.Entry(parent_frame, textvariable=split_size_var, width=10).grid(row=4, column=1, padx=10, pady=5)

    ttk.Button(parent_frame, text="开始处理", command=start_processing).grid(row=5, column=0, columnspan=3, padx=10, pady=10)

