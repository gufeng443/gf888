import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk, simpledialog
import os

class PhoneFilterApp:
    def __init__(self, master):
        self.master = master
        master.title("多功能数据处理工具")
        master.geometry("1000x800")
        self.selected_file = ""
        self.create_widgets()

    def create_widgets(self):
        # 创建主框架容器
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 左侧功能面板
        left_panel = ttk.LabelFrame(main_frame, text="核心功能")
        left_panel.pack(side="left", fill="y", padx=5, pady=5)

        # 右侧结果面板
        right_panel = ttk.LabelFrame(main_frame, text="处理结果")
        right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # ================== 左侧功能区域 ==================
        # 号码输入区域
        input_frame = ttk.LabelFrame(left_panel, text="号码处理")
        input_frame.pack(fill="x", pady=5)

        self.input_text = scrolledtext.ScrolledText(input_frame, height=10)
        self.input_text.pack(fill="x", padx=5)

        btn_row = ttk.Frame(input_frame)
        btn_row.pack(fill="x", pady=5)
        ttk.Button(btn_row, text="导入号码", command=self.import_numbers).pack(side="left", padx=2)
        ttk.Button(btn_row, text="查找号码", command=self.search_numbers).pack(side="left", padx=2)

        # 文件操作区域
        file_frame = ttk.LabelFrame(left_panel, text="文件操作")
        file_frame.pack(fill="x", pady=5)

        ttk.Button(file_frame, text="选择目标文件", command=self.select_file).pack(fill="x", padx=5, pady=2)
        self.file_label = ttk.Label(file_frame, text="未选择文件")
        self.file_label.pack(fill="x", padx=5)

        # 分包功能
        split_frame = ttk.Frame(file_frame)
        split_frame.pack(fill="x", pady=5)
        self.split_entry = ttk.Entry(split_frame, width=8)
        self.split_entry.pack(side="left", padx=5)
        ttk.Button(split_frame, text="分包处理", command=self.split_files).pack(side="left")

        # 合并功能
        ttk.Button(file_frame, text="合并文件", command=self.merge_files).pack(fill="x", padx=5, pady=2)

        # 过滤按钮
        ttk.Button(left_panel, text="开始执行过滤", command=self.start_filter).pack(fill="x", pady=5)

        # ================== 右侧结果区域 ==================
        # 结果展示
        result_frame = ttk.Frame(right_panel)
        result_frame.pack(fill="both", expand=True)

        # 处理结果
        self.result_text = scrolledtext.ScrolledText(result_frame, height=12)
        self.result_text.pack(side="left", fill="both", expand=True, padx=5)

        # 失败号码
        self.fail_text = scrolledtext.ScrolledText(result_frame, height=12)
        self.fail_text.pack(side="right", fill="both", expand=True, padx=5)

    # ================== 核心功能方法 ==================
    def select_file(self):
        """选择目标文件"""
        file_path = filedialog.askopenfilename(filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if file_path:
            self.selected_file = file_path
            self.file_label.config(text=os.path.basename(file_path))

    def import_numbers(self):
        """导入号码文件处理"""
        file_path = filedialog.askopenfilename(filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                numbers = []
                for line in f:
                    parts = line.strip().split(",", 1)
                    if parts and parts[0].strip().isdigit():
                        numbers.append(parts[0].strip())

                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(tk.END, "\n".join(numbers))
                messagebox.showinfo("导入完成", f"成功导入 {len(numbers)} 个有效号码")
        except Exception as e:
            messagebox.showerror("导入失败", f"文件读取失败：{str(e)}")

    def merge_files(self):
        """合并文件夹中的所有txt文件，并支持过滤条件"""
        # 选择文件夹
        folder_path = filedialog.askdirectory(title="选择包含txt文件的文件夹")
        if not folder_path:
            messagebox.showerror("错误", "没有选择文件夹")
            return

        # 提示用户输入过滤条件（可选）
        filter_text = simpledialog.askstring("过滤条件", "请输入要过滤的内容（可以为空，若不需过滤请直接回车）")

        try:
            all_data = []  # 存储所有文件的数据
            file_count = 0  # 统计处理的文件数量
            total_lines = 0  # 统计总行数

            # 遍历文件夹中的所有txt文件
            for file_name in os.listdir(folder_path):
                if file_name.endswith(".txt"):
                    file_path = os.path.join(folder_path, file_name)
                    file_count += 1

                    try:
                        with open(file_path, "r", encoding="utf-8") as file:
                            file_data = file.readlines()  # 读取文件的所有行


                            # 确保文件的最后一行有换行符
                            if file_data and not file_data[-1].endswith('\n'):
                                file_data[-1] += '\n'

                            all_data.extend(file_data)  # 将当前文件的数据添加到总数据中
                            total_lines += len(file_data)  # 统计总行数
                    except Exception as e:
                        messagebox.showerror("错误", f"无法读取文件 {file_name}: {e}")
                        return

            # 如果没有找到任何txt文件
            if file_count == 0:
                messagebox.showwarning("警告", "选择的文件夹中没有txt文件")
                return

            # 写入合并后的文件
            merged_file_path = os.path.join(folder_path, "整合合并.txt")
            try:
                with open(merged_file_path, "w", encoding="utf-8") as merged_file:
                    merged_file.writelines(all_data)  # 写入所有数据

                # 清除合并文件中的空白行
                self.remove_empty_lines(merged_file_path)

                # 显示处理结果
                result_msg = f"""合并完成！
处理文件数：{file_count}
合并总行数：{total_lines}
保存路径：{merged_file_path}"""
                if filter_text:
                    result_msg += f"\n过滤条件：'{filter_text}'"
                self.show_result(result_msg)
            except Exception as e:
                messagebox.showerror("错误", f"保存合并文件时出错: {e}")
        except Exception as e:
            messagebox.showerror("错误", f"合并过程中出错: {e}")

    def remove_empty_lines(self, file_path):
        """清除文件中的空白行"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()  # 读取所有行

            # 过滤掉空白行
            non_empty_lines = [line for line in lines if line.strip()]

            # 重新写入文件
            with open(file_path, "w", encoding="utf-8") as file:
                file.writelines(non_empty_lines)
        except Exception as e:
            messagebox.showerror("错误", f"清除空白行时出错: {e}")

    def split_files(self):
        """文件分包处理"""
        try:
            chunk_size = int(self.split_entry.get())
            if chunk_size <= 0:
                raise ValueError
        except:
            messagebox.showerror("输入错误", "请输入有效的分包数量（正整数）")
            return

        file_path = filedialog.askopenfilename(filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if not file_path:
            return

        try:
            output_dir = os.path.dirname(file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                file_counter = 1
                while True:
                    chunk = list(islice(f, chunk_size))
                    if not chunk:
                        break
                    output_path = os.path.join(output_dir, f"分包{file_counter}.txt")
                    with open(output_path, "w", encoding="utf-8") as outfile:
                        outfile.writelines(chunk)
                    file_counter += 1

            self.show_result(f"分包完成！共生成 {file_counter - 1} 个文件\n保存目录：{output_dir}")
        except Exception as e:
            messagebox.showerror("分包失败", f"分包过程中出错：{str(e)}")

    def search_numbers(self):
        """号码搜索功能"""
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        target_numbers = set(self.get_input_numbers())
        if not target_numbers:
            messagebox.showwarning("输入错误", "请输入要查找的号码")
            return

        results = []
        try:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(".txt"):
                        file_path = os.path.join(root, file)
                        with open(file_path, "r", encoding="utf-8") as f:
                            for line_num, line in enumerate(f, 1):
                                parts = line.strip().split(",", 1)
                                if parts and parts[0] in target_numbers:
                                    results.append(
                                        f"文件：{file_path}\n行号：{line_num}\n内容：{line.strip()}\n{'=' * 50}"
                                    )

            if results:
                self.show_result("\n\n".join(results))
            else:
                self.show_result("未找到匹配的号码")
        except Exception as e:
            messagebox.showerror("搜索失败", f"搜索过程中出错：{str(e)}")

    def start_filter(self):
        """开始执行过滤"""
        input_numbers = self.get_input_numbers()
        if not input_numbers:
            messagebox.showwarning("输入错误", "请输入要过滤的号码")
            return

        if not self.selected_file:
            messagebox.showwarning("文件错误", "请先选择要过滤的文件")
            return

        try:
            total, cleaned, failed = self.filter_file(input_numbers)
            result_str = f"""处理完成！
原始数据量：{total} 条
清理数据量：{cleaned} 条
剩余数据量：{total - cleaned} 条
结果文件：{os.path.dirname(self.selected_file)}/余号.txt"""
            self.show_result(result_str)
            self.fail_text.delete(1.0, tk.END)
            if failed:
                self.fail_text.insert(tk.END, "\n".join(failed))
        except Exception as e:
            messagebox.showerror("处理错误", f"处理过程中发生错误：{str(e)}")

    def filter_file(self, filter_list):
        """过滤文件中的号码"""
        filter_set = set(filter_list)
        total = cleaned = 0
        remaining = []
        failed_numbers = set(filter_list)

        with open(self.selected_file, "r", encoding="utf-8") as f:
            for line in f:
                total += 1
                parts = line.strip().split(",", 1)
                number = parts[0].strip() if parts else ""

                if number in filter_set:
                    cleaned += 1
                    if number in failed_numbers:
                        failed_numbers.remove(number)
                else:
                    remaining.append(line)

        output_path = os.path.join(os.path.dirname(self.selected_file), "余号.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(remaining)

        return total, cleaned, sorted(failed_numbers)

    def get_input_numbers(self):
        """获取输入框中的号码"""
        return [line.strip() for line in self.input_text.get(1.0, tk.END).splitlines() if line.strip()]

    def show_result(self, text):
        """显示处理结果"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)

if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneFilterApp(root)
    root.mainloop()