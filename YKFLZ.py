import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import re


class AutoSplitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("云控分包工具 孤风出品必属精品                       Telegram：+44 7498 148126 ")
        self.root.geometry("620x650")  # 调整窗口大小以容纳新元素

        self.image_path = None
        self.save_directory = None

        self.create_widgets()

    def create_widgets(self):
        # 文件名输入框
        tk.Label(self.root, text="文件名前缀:", font=("黑体", 12), fg='red').grid(row=0, column=0, padx=10, pady=5,
                                                                                  sticky='e')
        self.filename_entry = tk.Entry(self.root, width=20)
        self.filename_entry.grid(row=0, column=1, padx=10, pady=5, columnspan=3, sticky='w')

        # 群名称输入框
        tk.Label(self.root, text="群名称:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.group_name_entry = tk.Entry(self.root, width=20)
        self.group_name_entry.grid(row=1, column=1, padx=10, pady=5, columnspan=3, sticky='w')

        # 分包序列号开启关闭选项
        self.sequence_var = tk.BooleanVar()
        tk.Checkbutton(self.root, text="启用序列号", variable=self.sequence_var).grid(row=2, column=1, padx=10, pady=5,
                                                                                      columnspan=2, sticky='w')

        # 开始序号输入框
        tk.Label(self.root, text="开始序号:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.start_sequence_entry = tk.Entry(self.root, width=20)
        self.start_sequence_entry.insert(0, "1")
        self.start_sequence_entry.grid(row=3, column=1, padx=10, pady=5, sticky='w')

        # 分包数量输入框
        tk.Label(self.root, text="分包数量:", font=("黑体", 12), fg='red').grid(row=3, column=2, padx=15, pady=10,
                                                                                sticky='e')
        self.package_count_entry = tk.Entry(self.root, width=20)
        self.package_count_entry.insert(0, "6")  # 设置默认值为 6
        self.package_count_entry.grid(row=3, column=3, padx=15, pady=10, sticky='w')

        # 第一个分包数据值输入框和选项框
        tk.Label(self.root, text="第一个分包文件值:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        self.first_package_value_entry = tk.Entry(self.root, width=20)
        self.first_package_value_entry.insert(0, "1000")  # 设置默认值为 1000
        self.first_package_value_entry.grid(row=4, column=1, padx=10, pady=5, sticky='w')

        self.use_first_package_var = tk.BooleanVar()
        tk.Checkbutton(self.root, text="启用第一个数值", variable=self.use_first_package_var).grid(row=4, column=2,
                                                                                                   padx=10, pady=5,
                                                                                                   columnspan=2,
                                                                                                   sticky='w')

        # 群描述输入框
        tk.Label(self.root, text="群描述:").grid(row=5, column=0, padx=10, pady=5, sticky='e')
        self.group_description_entry = tk.Entry(self.root, width=50)
        self.group_description_entry.grid(row=5, column=1, padx=10, pady=5, columnspan=3, sticky='w')

        # 管理号和水军输入框
        tk.Label(self.root, text="管理号:").grid(row=6, column=0, padx=10, pady=5, sticky='e')
        self.manager_text = tk.Text(self.root, height=8, width=20)
        self.manager_text.grid(row=6, column=1, padx=10, pady=5, sticky='w')

        tk.Label(self.root, text="水军:").grid(row=6, column=2, padx=10, pady=5, sticky='e')
        self.soldiers_text = tk.Text(self.root, height=8, width=20)
        self.soldiers_text.grid(row=6, column=3, padx=10, pady=5, sticky='w')

        # 粉丝资源输入框
        tk.Label(self.root, text="粉丝资源:").grid(row=7, column=0, padx=10, pady=5, sticky='ne')
        self.resources_text = tk.Text(self.root, height=10, width=62)
        self.resources_text.grid(row=7, column=1, padx=10, pady=5, columnspan=3, sticky='w')

        # 上传资源按钮
        tk.Button(self.root, text="上传资源自动过料子数据", font=("黑体", 12), fg='red',
                  command=self.upload_resources).grid(row=8, column=1, padx=10, pady=5, sticky='n')

        # 上传群头像按钮
        tk.Button(self.root, text="上传群头像", command=self.upload_image).grid(row=8, column=3, padx=10, pady=5,
                                                                                sticky='se')

        # 生成TXT文件选项框
        self.generate_txt_var = tk.BooleanVar()
        tk.Checkbutton(self.root, text="生成TXT文件", variable=self.generate_txt_var).grid(row=9, column=1, padx=10,
                                                                                           pady=5, columnspan=2,
                                                                                           sticky='w')

        # 显示粉丝资源条数
        self.resource_count_label = tk.Label(self.root, text="资源条数: 0")
        self.resource_count_label.grid(row=10, column=0, padx=10, pady=5, columnspan=4, sticky='w')

        # 确定取消按键
        tk.Button(self.root, text="开始执行", command=self.process_data, font=("宋体", 12), width=65, height=2,
                  bg='black', fg='white').grid(row=11, column=0, padx=15, pady=15, columnspan=4, sticky='w')

    def upload_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.bmp")]
        )
        if self.image_path:
            messagebox.showinfo("信息", "头像已上传")

    def upload_resources(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt")]
        )
        if not file_path:
            return

        # 提取文件名并更新“文件名”输入框
        file_name = os.path.basename(file_path).split('.')[0]
        self.filename_entry.delete(0, tk.END)
        self.filename_entry.insert(0, file_name)

        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # 过滤数据：保留包含至少7位连续数字的行
        filtered_lines = []
        for line in lines:
            # 提取行内所有数字
            numbers = re.findall(r'\d+', line)
            # 只保留包含7位及以上数字的行
            if any(len(num) >= 7 for num in numbers):
                # 清除非数字字符和空格
                cleaned_line = re.sub(r'\D', '', line).strip()
                filtered_lines.append(cleaned_line)

        # 获取管理员和水军数据
        manager_numbers = set(line.strip() for line in self.manager_text.get("1.0", tk.END).strip().splitlines())
        soldiers = set(line.strip() for line in self.soldiers_text.get("1.0", tk.END).strip().splitlines())

        # 合并管理员和水军数据
        all_excluded_numbers = manager_numbers.union(soldiers)

        # 过滤掉与管理员或水军数据重复的粉丝资源数据
        filtered_lines = [line for line in filtered_lines if line not in all_excluded_numbers]

        # 更新资源文本框
        self.resources_text.delete("1.0", tk.END)
        self.resources_text.insert("1.0", '\n'.join(filtered_lines))

        # 更新资源条数标签
        self.resource_count_label.config(text=f"资源条数: {len(filtered_lines)}")

    def process_data(self):
        if self.save_directory is None:
            self.save_directory = filedialog.askdirectory(title="选择保存位置")
            if not self.save_directory:
                messagebox.showwarning("警告", "未选择保存位置")
                return

        filename = self.filename_entry.get().strip()
        group_name = self.group_name_entry.get().strip() or "无群名"  # 默认值“无群名”如果群名称为空
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

        package_count = self.package_count_entry.get().strip() or "6"  # 使用默认值 6

        if not package_count.isdigit() or int(package_count) <= 0:
            messagebox.showwarning("警告", "分包数量必须为正整数")
            return

        package_count = int(package_count)

        # 检查第一个分包数据值
        use_first_package_value = self.use_first_package_var.get()
        first_package_value = int(first_package_value) if first_package_value.isdigit() else 1000

        # 计算分包策略
        chunks = []
        if use_first_package_value:
            total_resources = len(resources)
            # 如果使用第一个分包数据值
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
            # 平均分包
            chunk_size = len(resources) // package_count
            if len(resources) % package_count != 0:
                chunk_size += 1  # Adjust chunk size if resources cannot be evenly divided
            chunks = [resources[i:i + chunk_size] for i in range(0, len(resources), chunk_size)]

        # 确保 start_sequence 是一个有效的整数，默认值为 0
        try:
            start_sequence = int(start_sequence) if start_sequence else 0
        except ValueError:
            start_sequence = 0

        # 生成文件夹名称
        folder_name = filename

        # 创建文件夹
        folder_path = os.path.join(self.save_directory, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # 根据用户选择生成 Excel 或 TXT 文件
        generate_txt = self.generate_txt_var.get()

        for i, chunk in enumerate(chunks):
            file_path = os.path.join(folder_path,
                                     f"{folder_name}-{i + 1}.txt" if generate_txt else f"{folder_name}-{i + 1}.xlsx")

            if generate_txt:
                # 生成 TXT 文件
                with open(file_path, 'w', encoding='utf-8') as file:
                    # 写入管理员和水军数据（如果存在）
                    if manager_numbers or soldiers:
                        all_excluded_numbers = manager_numbers.union(soldiers)
                        file.write('\n'.join(all_excluded_numbers) + '\n')
                    # 写入分包资源
                    file.write('\n'.join(chunk) + '\n')
                print(f"分包 TXT 文件 '{file_path}' 已保存")
            else:
                # 生成 Excel 文件
                df = pd.DataFrame({
                    "管理": list(manager_numbers) + [''] * (len(chunk) - len(manager_numbers)),
                    # Ensure column length matches
                    "水军": list(soldiers) + [''] * (len(chunk) - len(soldiers)),  # Ensure column length matches
                    "进群资源": chunk,
                    "群描述": [group_description] + [''] * (len(chunk) - 1),  # 群描述在第一行，其余行留空
                    "群头像": [''] * len(chunk)
                })

                # 使用 xlsxwriter 写入特定单元格
                with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                    workbook = writer.book
                    worksheet = writer.sheets['Sheet1']

                    # 在第四列的第一行写入群描述
                    if group_description:
                        worksheet.write_string(0, 3, group_description)

                    # 在第四列的第二行写入分包群名称
                    if group_name != "无群名":
                        worksheet.write_string(1, 3, group_name + (
                            '{' + str(start_sequence + i) + '}' if use_sequence else ''))

                    # 在第四列的第四行插入群头像
                    if self.image_path:
                        worksheet.insert_image(3, 3, self.image_path)

                print(f"分包文件 '{file_path}' 已保存")

        # 重置数据部分
        self.reset_data()
        messagebox.showinfo("信息", "所有分包文件已保存")

    def reset_data(self):
        # 清空粉丝资源文本框
        self.resources_text.delete("1.0", tk.END)

        # 取消选择的生成TXT文件复选框
        self.generate_txt_var.set(False)

        # 更新资源条数标签
        self.resource_count_label.config(text="资源条数: 0")

        # 清空保存目录
        self.save_directory = None


# 创建主窗口
root = tk.Tk()
app = AutoSplitApp(root)
root.mainloop()
