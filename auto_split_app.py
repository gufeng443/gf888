import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import re
from tkinter import ttk
import chardet


class AutoSplitPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.root = parent
        self.image_path = None
        self.save_directory = None
        self.create_widgets()

    def create_widgets(self):
        # 添加样式
        style = ttk.Style()
        style.configure("RedBold.TButton", foreground="red", font=("黑体", 12, "bold"))
        style.configure("BlackRed.TButton", background="black", foreground="black", font=("黑体", 12, "bold"))

        # 使用 LabelFrame 将界面分块
        file_frame = ttk.LabelFrame(self.root, text="文件信息", padding=(10, 10))
        file_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        tk.Label(file_frame, text="文件名前缀:", font=("黑体", 12), fg='red').grid(row=0, column=0, padx=10, pady=5,
                                                                                   sticky='e')
        self.filename_entry = tk.Entry(file_frame, width=20)
        self.filename_entry.grid(row=0, column=1, padx=10, pady=5, columnspan=3, sticky='w')

        tk.Label(file_frame, text="群名称:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.group_name_entry = tk.Entry(file_frame, width=20)
        self.group_name_entry.grid(row=1, column=1, padx=10, pady=5, columnspan=3, sticky='w')

        self.sequence_var = tk.BooleanVar()
        ttk.Checkbutton(file_frame, text="启用序列号", variable=self.sequence_var).grid(row=2, column=1, padx=10,
                                                                                        pady=5, sticky='w')

        tk.Label(file_frame, text="开始序号:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.start_sequence_entry = tk.Entry(file_frame, width=10)
        self.start_sequence_entry.insert(0, "1")
        self.start_sequence_entry.grid(row=3, column=1, padx=10, pady=5, sticky='w')

        tk.Label(file_frame, text="分包数量:", font=("黑体", 12), fg='red').grid(row=3, column=2, padx=15, pady=10,
                                                                                 sticky='e')
        self.package_count_entry = tk.Entry(file_frame, width=10)
        self.package_count_entry.insert(0, "3")
        self.package_count_entry.grid(row=3, column=3, padx=15, pady=10, sticky='w')

        tk.Label(file_frame, text="第一个分包文件值:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        self.first_package_value_entry = tk.Entry(file_frame, width=10)
        self.first_package_value_entry.insert(0, "1000")
        self.first_package_value_entry.grid(row=4, column=1, padx=10, pady=5, sticky='w')

        self.use_first_package_var = tk.BooleanVar()
        ttk.Checkbutton(file_frame, text="启用第一个数值", variable=self.use_first_package_var).grid(row=4, column=2,
                                                                                                     padx=10, pady=5,
                                                                                                     columnspan=2,
                                                                                                     sticky='w')

        # 描述信息分组
        desc_frame = ttk.LabelFrame(self.root, text="群信息", padding=(10, 10))
        desc_frame.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        tk.Label(desc_frame, text="群描述:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.group_description_entry = tk.Entry(desc_frame, width=60)
        self.group_description_entry.grid(row=0, column=1, padx=10, pady=5, columnspan=3, sticky='w')

        tk.Label(desc_frame, text="管理号:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.manager_text = tk.Text(desc_frame, height=5, width=20)
        self.manager_text.grid(row=1, column=1, padx=10, pady=5, sticky='w')

        tk.Label(desc_frame, text="水军:").grid(row=1, column=2, padx=10, pady=5, sticky='e')
        self.soldiers_text = tk.Text(desc_frame, height=5, width=20)
        self.soldiers_text.grid(row=1, column=3, padx=10, pady=5, sticky='w')

        tk.Label(desc_frame, text="粉丝资源:").grid(row=2, column=0, padx=10, pady=5, sticky='ne')
        self.resources_text = tk.Text(desc_frame, height=10, width=62)
        self.resources_text.grid(row=2, column=1, padx=10, pady=5, columnspan=3, sticky='w')

        self.resource_count_label = tk.Label(desc_frame, text="资源条数: 0")
        self.resource_count_label.grid(row=3, column=1, padx=10, pady=5, sticky='w')
        # 功能按钮部分
        action_frame = ttk.LabelFrame(self.root, text="操作", padding=(10, 10))
        action_frame.grid(row=2, column=0, padx=10, pady=10, sticky='ew')

        ttk.Button(action_frame, text="合并数据", command=self.merge_data).grid(row=0, column=0, padx=10, pady=5,
                                                                                sticky='w')
        ttk.Button(action_frame, text="Excel 转 TXT", command=self.convert_excel_to_txt).grid(row=0, column=1, padx=10,
                                                                                              pady=5, sticky='w')
        ttk.Button(action_frame, text="TXT 转 Excel", command=self.convert_txt_to_excel).grid(row=0, column=2, padx=10,
                                                                                              pady=5, sticky='w')

        tk.Label(action_frame, text="区号:").grid(row=0, column=3, padx=10, pady=5, sticky='e')
        self.area_code_entry = tk.Entry(action_frame, width=10)
        self.area_code_entry.grid(row=0, column=4, padx=10, pady=5, sticky='w')

        # 修改后的按钮，字体加粗并变红色
        ttk.Button(action_frame, text="上传料子数据自动过滤", command=self.upload_resources,
                   style="RedBold.TButton").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        ttk.Button(action_frame, text="上传群头像", command=self.upload_image).grid(row=1, column=2, padx=10, pady=5,
                                                                                    sticky='e')

        self.generate_txt_var = tk.BooleanVar(value=True)   #True
        ttk.Checkbutton(action_frame, text="生成TXT文件", variable=self.generate_txt_var).grid(row=1, column=1, padx=10,
                                                                                               pady=5, sticky='w')


        ttk.Button(self.root, text="开始执行", command=self.process_data, style="BlackRed.TButton").grid(row=3,
                                                                                                         column=0,
                                                                                                         padx=10,
                                                                                                         pady=20,
                                                                                                         sticky='ew')

    def upload_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.bmp")])
        if self.image_path:
            messagebox.showinfo("信息", "头像已上传")

    def upload_resources(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return

        file_name = os.path.basename(file_path).split('.')[0]
        self.filename_entry.delete(0, tk.END)
        self.filename_entry.insert(0, file_name)

        import chardet

        # 读取文件内容，自动检测编码
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

        # 使用检测到的编码读取文件
        with open(file_path, 'r', encoding=encoding) as file:
            lines = file.readlines()

        # 清除每一行中的中文文字，符号，字母和空格，只保留数字
        cleaned_lines = []
        for line in lines:
            cleaned_line = re.sub(r'[^0-9]', '', line).strip()  # 保留数字
            if cleaned_line:  # 确保不为空
                cleaned_lines.append(cleaned_line)

        # 过滤数据：只保留包含至少10位数的行
        filtered_lines = [line for line in cleaned_lines if len(line) >= 10]

        manager_numbers = set(line.strip() for line in self.manager_text.get("1.0", tk.END).strip().splitlines())
        soldiers = set(line.strip() for line in self.soldiers_text.get("1.0", tk.END).strip().splitlines())
        all_excluded_numbers = manager_numbers.union(soldiers)

        filtered_lines = [line for line in filtered_lines if line not in all_excluded_numbers]

        area_code = self.area_code_entry.get().strip()
        if area_code:
            filtered_lines = [f"{area_code}{line}" for line in filtered_lines]

        self.resources_text.delete("1.0", tk.END)
        self.resources_text.insert("1.0", '\n'.join(filtered_lines))
        self.resource_count_label.config(text=f"资源条数: {len(filtered_lines)}")

    def merge_data(self):
        folder_path = filedialog.askdirectory(title="选择包含 TXT 文件的文件夹")
        if not folder_path:
            return

        all_lines = []

        for file_name in os.listdir(folder_path):
            if file_name.endswith('.txt'):
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    all_lines.extend(line.strip() for line in lines if line.strip())

        output_file_path = os.path.join(folder_path, '补.txt')
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write('\n'.join(all_lines))

        self.resources_text.delete("1.0", tk.END)
        self.resources_text.insert("1.0", '\n'.join(all_lines))
        self.filename_entry.delete(0, tk.END)
        self.filename_entry.insert(0, '补')

        messagebox.showinfo("信息", f"数据已合并到 '{output_file_path}'")

    def convert_excel_to_txt(self):
        folder_path = filedialog.askdirectory(title="选择文件夹")
        if not folder_path:
            return

        for file_name in os.listdir(folder_path):
                if file_name.endswith('.xls') or file_name.endswith('.xlsx') or file_name.endswith('.xlsm'):
                              file_path = os.path.join(folder_path, file_name)
                txt_file_path = os.path.join(folder_path, os.path.splitext(file_name)[0] + '.txt')

                try:
                    if file_name.endswith('.xls'):
                        df = pd.read_excel(file_path, header=None, engine='xlrd')
                    else:
                        df = pd.read_excel(file_path, header=None, engine='openpyxl')

                    with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
                        for index, row in df.iterrows():
                            for cell in row:
                                if pd.isna(cell):  # 检查是否为 NaN
                                    continue

                                if isinstance(cell, str):
                                    numbers = re.findall(r'\d+', cell)
                                    long_numbers = [num for num in numbers if len(num) >= 4]
                                    if long_numbers:
                                        txt_file.write(' '.join(long_numbers) + '\n')
                                elif isinstance(cell, (int, float)):
                                    cell_str = str(int(cell))  # 转换为整数字符串
                                    if len(cell_str) >= 4:
                                        txt_file.write(cell_str + '\n')
                    print(f"文件 '{txt_file_path}' 已保存")
                except Exception as e:
                    messagebox.showerror("错误", f"转换文件 '{file_name}' 时出错: {e}")

        messagebox.showinfo("信息", "Excel 文件已转换为 TXT 文件")

    def convert_txt_to_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return

        data = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # 按空格分隔数据
                row_data = line.strip().split()
                if row_data:
                    data.append(row_data)

        # 将数据转换为 DataFrame
        df = pd.DataFrame(data)

        excel_file_path = os.path.splitext(file_path)[0] + '.xlsx'
        try:
            df.to_excel(excel_file_path, index=False, header=False)
            messagebox.showinfo("信息", f"TXT 文件已转换为 Excel 文件 '{excel_file_path}'")
        except PermissionError:
            messagebox.showerror("错误",
                                 f"权限被拒绝，无法写入文件 '{excel_file_path}'. 请检查文件是否被占用或路径是否存在.")
        except Exception as e:
            messagebox.showerror("错误", f"转换文件 '{file_path}' 时出错: {e}")

    def process_data(self):
        if self.save_directory is None:
            self.save_directory = filedialog.askdirectory(title="选择保存位置")
            if not self.save_directory:
                messagebox.showwarning("警告", "未选择保存位置")
                return

        filename = self.filename_entry.get().strip()
        group_name = self.group_name_entry.get().strip() or "无群名"
        use_sequence = self.sequence_var.get()
        start_sequence = self.start_sequence_entry.get().strip()
        package_count = self.package_count_entry.get().strip()
        first_package_value = self.first_package_value_entry.get().strip()
        group_description = self.group_description_entry.get().strip()
        manager_numbers = set(line.strip() for line in self.manager_text.get("1.0", tk.END).strip().splitlines())
        soldiers = set(line.strip() for line in self.soldiers_text.get("1.0", tk.END).strip().splitlines())
        resources = self.resources_text.get("1.0", tk.END).strip().splitlines()

        if not filename:
            messagebox.showwarning("警告", "文件名不能为空")
            return

        if not resources:
            messagebox.showwarning("警告", "粉丝资源不能为空")
            return

        package_count = int(package_count) if package_count.isdigit() else 6

        if not package_count or package_count <= 0:
            messagebox.showwarning("警告", "分包数量必须为正整数")
            return

        use_first_package_value = self.use_first_package_var.get()
        first_package_value = int(first_package_value) if first_package_value.isdigit() else 1000

        chunks = []
        if use_first_package_value:
            total_resources = len(resources)
            if len(resources) > first_package_value:
                first_chunk = resources[:first_package_value]
                remaining_resources = resources[first_package_value:]
                chunk_size = len(remaining_resources) // (package_count - 1)
                if len(remaining_resources) % (package_count - 1) != 0:
                    chunk_size += 1
                chunks = [first_chunk] + [remaining_resources[i:i + chunk_size] for i in
                                          range(0, len(remaining_resources), chunk_size)]
            else:
                chunks = [resources]
        else:
            chunk_size = len(resources) // package_count
            if len(resources) % package_count != 0:
                chunk_size += 1
            chunks = [resources[i:i + chunk_size] for i in range(0, len(resources), chunk_size)]

        try:
            start_sequence = int(start_sequence) if start_sequence else 0
        except ValueError:
            start_sequence = 0

        folder_name = filename
        folder_path = os.path.join(self.save_directory, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        generate_txt = self.generate_txt_var.get()

        for i, chunk in enumerate(chunks):
            chunk = [line for line in chunk if line.strip()]  # 去除空白行
            file_path = os.path.join(folder_path,
                                     f"{folder_name}-{i + 1}.txt" if generate_txt else f"{folder_name}-{i + 1}.xlsx")

            if generate_txt:
                with open(file_path, 'w', encoding='utf-8') as file:
                    if manager_numbers or soldiers:
                        all_excluded_numbers = manager_numbers.union(soldiers)
                        file.write('\n'.join(all_excluded_numbers))
                        file.write('\n')  # 写入换行符
                    if chunk:  # 确保只有在有数据时才写入
                        file.write('\n'.join(chunk))
                    # 注意：我们不会在最后一行添加额外的换行符
                print(f"分包 TXT 文件 '{file_path}' 已保存")
            else:
                df = pd.DataFrame({
                    "管理": list(manager_numbers) + [''] * (len(chunk) - len(manager_numbers)),
                    "水军": list(soldiers) + [''] * (len(chunk) - len(soldiers)),
                    "进群资源": chunk,
                    "群描述": [group_description] + [''] * (len(chunk) - 1),
                    "群头像": [''] * len(chunk)
                })

                with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    workbook = writer.book
                    worksheet = writer.sheets['Sheet1']

                    if group_description:
                        worksheet.write_string(0, 3, group_description)

                    if group_name != "无群名":
                        worksheet.write_string(1, 3, group_name + (
                            '{' + str(start_sequence + i) + '}' if use_sequence else ''))

                    if self.image_path:
                        worksheet.insert_image(3, 3, self.image_path)

                print(f"分包文件 '{file_path}' 已保存")

        self.reset_data()
        messagebox.showinfo("信息", "所有分包文件已保存")

    def reset_data(self):
        self.resources_text.delete("1.0", tk.END)
        self.generate_txt_var.set(True)  # 默认勾选
        self.resource_count_label.config(text="资源条数: 0")
        self.save_directory = None


if __name__ == "__main__":
    root = tk.Tk()
    root.title("自动分包系统")
    # 设置程序图标 (Windows 使用 .ico 文件)
    root.iconbitmap("KONG.ico")
    AutoSplitPage(root)
    root.mainloop()