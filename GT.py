import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog  # 需要导入 simpledialog
from tkinterdnd2 import TkinterDnD, DND_FILES

def remove_empty_lines(file_path):
    """清除文件中的空白行"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # 过滤掉空白行
        cleaned_lines = [line for line in lines if line.strip()]

        # 写回文件，确保不含空白行
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(cleaned_lines)
    except Exception as e:
        print(f"清除空白行时出错: {e}")


class FileSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GT运控文件分包工具")
        self.root.geometry("367x740")
        self.root.config(bg="#f0f0f0")  # 设置背景颜色

        # 初始化文件名和输入框
        self.file_path = ""
        self.filename = ""
        self.file_data = []

        # 创建主框架
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 上传和显示文件内容框架
        self.upload_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.upload_frame.pack(fill=tk.X, pady=10)

        # 上传按钮
        self.upload_button = tk.Button(self.upload_frame, text="上传TXT数据", command=self.upload_file,
                                       width=20, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"))
        self.upload_button.pack(pady=5)

        # 拖放区域
        self.drop_area = tk.Label(self.upload_frame, text="或将TXT文件拖到此区域", relief="solid", width=40, height=4,
                                  bg="#f8f8f8", fg="#888", font=("Helvetica", 10), anchor="center")
        self.drop_area.pack(pady=10)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.on_drop)

        # 显示文件内容框
        self.content_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.content_frame.pack(fill=tk.X, pady=10)

        self.text_area_label = tk.Label(self.content_frame, text="上传文件内容：", font=("Helvetica", 12))
        self.text_area_label.pack(pady=5)
        self.text_area = tk.Text(self.content_frame, height=5, width=35, font=("Helvetica", 10), wrap="word")
        self.text_area.pack(pady=5)

        # 文件行数显示
        self.line_count_label = tk.Label(self.content_frame, text="总行数：0", font=("Helvetica", 10), fg="green")
        self.line_count_label.pack(pady=5)

        # 输入框区域
        self.input_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.input_frame.pack(fill=tk.X, pady=10)

        # 将文件名和起始数字放入同一行的框架中
        self.filename_start_frame = tk.Frame(self.input_frame, bg="#f0f0f0")
        self.filename_start_frame.pack(fill=tk.X)

        self.filename_label = tk.Label(self.filename_start_frame, text="名称：", font=("Helvetica", 12))
        self.filename_label.pack(side=tk.LEFT, padx=5)

        self.filename_entry = tk.Entry(self.filename_start_frame, width=15, font=("Helvetica", 10))
        self.filename_entry.pack(side=tk.LEFT, padx=5)

        self.start_number_label = tk.Label(self.filename_start_frame, text="起始数字：", font=("Helvetica", 12))
        self.start_number_label.pack(side=tk.LEFT, padx=5)

        self.start_number_entry = tk.Entry(self.filename_start_frame, width=10, font=("Helvetica", 10))
        self.start_number_entry.pack(side=tk.LEFT, padx=5)
        self.start_number_entry.insert(0, "1")  # 默认为1

        # 添加复选框，供用户选择数字后缀位置
        self.name_position_var = tk.BooleanVar()
        self.name_position_check = tk.Checkbutton(self.filename_start_frame, text="数字在名称前", variable=self.name_position_var,
                                                  font=("Helvetica", 12))
        self.name_position_check.pack(side=tk.LEFT, padx=5)

        # 管理员输入框
        self.admin_input_label = tk.Label(self.input_frame, text="管理员输入（每行一个管理员）：", font=("Helvetica", 12))
        self.admin_input_label.pack(pady=5)
        self.admin_input_entry = tk.Text(self.input_frame, height=2, width=40, font=("Helvetica", 10))
        self.admin_input_entry.pack(pady=5)

        # 分包行数输入框
        self.package_size_label = tk.Label(self.input_frame, text="每包行数：", font=("Helvetica", 12))
        self.package_size_label.pack(pady=5)
        self.package_size_entry = tk.Entry(self.input_frame, width=40, font=("Helvetica", 10))
        self.package_size_entry.pack(pady=5)

        # 执行按钮
        self.start_button = tk.Button(self.main_frame, text="开始执行", command=self.start_splitting,
                                      width=20, bg="#2196F3", fg="white", font=("Helvetica", 12, "bold"))
        self.start_button.pack(pady=20)

        # 合并按钮
        self.merge_button = tk.Button(self.main_frame, text="合并数据", command=self.merge_files,
                                      width=20, bg="#FF5722", fg="white", font=("Helvetica", 12, "bold"))
        self.merge_button.pack(pady=10)
    def upload_file(self):
        """上传文件选择器"""
        self.file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if self.file_path:
            self.filename = os.path.basename(self.file_path)
            self.filename_entry.delete(0, tk.END)
            self.filename_entry.insert(0, self.filename)

            # 读取文件并显示内容
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.file_data = file.readlines()

            self.display_file_content()
            self.update_line_count()

    def on_drop(self, event):
        """拖放文件处理"""
        self.file_path = event.data.strip()

        # 去除路径中可能出现的 { } 括号
        self.file_path = self.file_path.replace("{", "").replace("}", "")

        print(f"拖拽的文件路径: {self.file_path}")  # 输出文件路径，检查格式

        # 处理路径，移除可能的 file:// 前缀
        if self.file_path.startswith("file://"):
            self.file_path = self.file_path[7:]

        # 确保是 txt 文件
        if self.file_path.endswith('.txt'):
            self.filename = os.path.basename(self.file_path)
            self.filename_entry.delete(0, tk.END)
            self.filename_entry.insert(0, self.filename)

            # 读取文件并显示内容
            try:
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    self.file_data = file.readlines()

                self.display_file_content()
                self.update_line_count()
            except Exception as e:
                messagebox.showerror("错误", f"无法读取文件: {e}")
        else:
            messagebox.showerror("错误", "请上传TXT文件")

    def display_file_content(self):
        """显示文件内容在Text控件中"""
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, ''.join(self.file_data))

    def update_line_count(self):
        """更新文件的总行数"""
        line_count = len(self.file_data)
        self.line_count_label.config(text=f"总行数：{line_count}")

    def start_splitting(self):
        """开始分包"""
        try:
            # 获取用户输入的参数
            admin_input = self.admin_input_entry.get("1.0", tk.END).strip().splitlines()
            package_size = self.package_size_entry.get().strip()
            filename_part = self.filename_entry.get().strip()
            start_number = self.start_number_entry.get().strip()

            # 校验输入
            if not self.file_path:
                messagebox.showerror("错误", "请先上传TXT文件")
                return
            if not package_size.isdigit():
                messagebox.showerror("错误", "每包行数必须为数字")
                return
            if not start_number.isdigit():
                messagebox.showerror("错误", "起始数字必须为数字")
                return

            admin_input = [line for line in admin_input if line.strip()]
            package_size = int(package_size)
            start_number = int(start_number)

            if package_size < 1:
                messagebox.showerror("错误", "每包行数必须大于0")
                return

            if len(self.file_data) < package_size:
                messagebox.showwarning("警告", "数据行数小于分包大小，自动将整个数据保存为一个包")
                package_size = len(self.file_data)

            # 如果有管理员数据，需要调整分包大小
            if admin_input:
                package_size -= len(admin_input)  # 减去管理员的数量

            # 创建保存文件的目录
            folder_name = filename_part.split('.')[0]
            folder_path = os.path.join(os.path.dirname(self.file_path), folder_name)
            os.makedirs(folder_path, exist_ok=True)

            # 分包并保存
            num_packages = len(self.file_data) // package_size + (1 if len(self.file_data) % package_size != 0 else 0)
            admin_count = len(admin_input)  # 管理员数量

            # 分包过程
            generated_files = []
            for i in range(num_packages):
                start_line = i * package_size
                end_line = min((i + 1) * package_size, len(self.file_data))
                sub_package = self.file_data[start_line:end_line]

                # 将管理员数据添加到当前分包的顶部
                final_package = admin_input + sub_package  # 管理员在前，数据在后

                # 如果管理员占用了部分行数，确保分包的实际数据行数不超过用户设定的行数
                if len(final_package) > package_size + admin_count:
                    final_package = final_package[:package_size + admin_count]

                # 去除空白行
                final_package = [line for line in final_package if line.strip()]

                # 生成文件名：如果复选框选中，则数字在名称前，否则在名称后
                if self.name_position_var.get():
                    sub_filename = f"{start_number}{filename_part.split('.')[0]}.txt"
                else:
                    sub_filename = f"{filename_part.split('.')[0]}{start_number}.txt"

                sub_filepath = os.path.join(folder_path, sub_filename)
                generated_files.append(sub_filepath)

                # 写入分包文件
                with open(sub_filepath, 'w', encoding='utf-8') as sub_file:
                    sub_file.writelines([line + '\n' for line in final_package])  # 添加换行符

                # 清除每个分包文件中的空白行
                self.remove_empty_lines(sub_filepath)

                # 更新下一个文件的序号
                start_number += 1

            # 清除每个分包文件中的空白行
            for file_path in generated_files:
                self.remove_empty_lines(file_path)

            messagebox.showinfo("成功", f"数据分包成功！文件已保存至 {folder_path}")
        except Exception as e:
            messagebox.showerror("错误", str(e))
            # 二次分包
            response = messagebox.askyesno("提示", "分包完成，是否进行二次分包？")
            if response:
                self.secondary_split(generated_files, filename_part)

            messagebox.showinfo("成功", f"数据分包成功！文件已保存至 {folder_path}")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def secondary_split(self, generated_files, filename_part):
        """执行二次分包"""
        try:
            # 获取每包行数
            secondary_package_size = simpledialog.askinteger("二次分包", "请输入每包行数", minvalue=1)
            if not secondary_package_size:
                return  # 用户取消

            # 为每个分包创建一个以文件名为命名的文件夹
            for file_path in generated_files:
                folder_name = os.path.splitext(os.path.basename(file_path))[0]
                secondary_folder_path = os.path.join(os.path.dirname(file_path), folder_name)
                os.makedirs(secondary_folder_path, exist_ok=True)

                with open(file_path, 'r', encoding='utf-8') as file:
                    file_data = file.readlines()

                num_packages = len(file_data) // secondary_package_size + (
                    1 if len(file_data) % secondary_package_size != 0 else 0)

                # 二次分包过程
                for i in range(num_packages):
                    start_line = i * secondary_package_size
                    end_line = min((i + 1) * secondary_package_size, len(file_data))
                    sub_package = file_data[start_line:end_line]

                    # 二次分包文件名
                    sub_filename = f"{folder_name}-{i + 1}.txt"
                    sub_filepath = os.path.join(secondary_folder_path, sub_filename)

                    # 写入二次分包文件
                    with open(sub_filepath, 'w', encoding='utf-8') as sub_file:
                        sub_file.writelines([line for line in sub_package])

                    # 清除空白行
                    self.remove_empty_lines(sub_filepath)

            messagebox.showinfo("成功", "二次分包完成！")
        except Exception as e:
            messagebox.showerror("错误", f"二次分包时出错: {e}")

    def merge_files(self):
        """合并多个文件"""
        folder_path = filedialog.askdirectory(title="选择包含txt文件的文件夹")
        if not folder_path:
            messagebox.showerror("错误", "没有选择文件夹")
            return

        # 提示用户是否输入过滤条件
        filter_text = simpledialog.askstring("过滤条件", "请输入要过滤的内容（可以为空，若不需过滤请直接回车）")

        # 读取所有txt文件
        all_data = []
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".txt"):
                file_path = os.path.join(folder_path, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        file_data = file.readlines()

                        if filter_text:
                            # 过滤掉包含过滤条件的行
                            file_data = [line for line in file_data if filter_text not in line]

                        # 确保文件的最后一行有换行符
                        if file_data and not file_data[-1].endswith('\n'):
                            file_data[-1] += '\n'

                        all_data.extend(file_data)
                except Exception as e:
                    messagebox.showerror("错误", f"无法读取文件 {file_name}: {e}")
                    return

        # 写入合并后的文件
        merged_file_path = os.path.join(folder_path, "-余料.txt")
        try:
            with open(merged_file_path, "w", encoding="utf-8") as merged_file:
                merged_file.writelines(all_data)

            # 清除合并文件中的空白行
            self.remove_empty_lines(merged_file_path)

            messagebox.showinfo("成功", f"数据合并完成，保存为 {merged_file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存合并文件时出错: {e}")

    def remove_empty_lines(self, file_path):
        """清除文件中的空白行"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # 过滤掉空白行
            cleaned_lines = [line for line in lines if line.strip()]

            # 写回文件，确保不含空白行
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(cleaned_lines)
        except Exception as e:
            messagebox.showerror("错误", f"清除空白行时出错: {e}")


# 创建GUI应用
root = TkinterDnD.Tk()
app = FileSplitterApp(root)
root.mainloop()
