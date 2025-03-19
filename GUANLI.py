import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import time

class MyApplication(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="模拟器管理页面").pack()

        # 创建一个框架来包裹这三个控件，保证它们在同一行上
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, padx=10, pady=10)

        # 创建控件并排列在同一行
        self.label = tk.Label(top_frame, text="模拟器窗口")
        self.label.pack(side=tk.LEFT, padx=10, pady=10)

        self.combobox = ttk.Combobox(top_frame, width=50)
        self.combobox.pack(side=tk.LEFT, padx=10, pady=10)

        self.read_button = tk.Button(top_frame, text="读取模拟器窗口", command=self.read_simulator)
        self.read_button.pack(side=tk.LEFT, padx=10, pady=10)

        # 状态标签
        self.status_label = tk.Label(self, text="")
        self.status_label.pack(pady=10)

        # 添加输入号码的文本框和显示结果的框架
        self.number_entry = tk.Text(self, height=10, width=50)
        self.number_entry.pack(side=tk.LEFT, padx=10, pady=10)

        self.result_frame = tk.Frame(self, bd=2, relief=tk.SUNKEN)
        self.result_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # 批量设置管理按钮
        self.batch_button = tk.Button(self, text="批量设置管理", command=self.batch_manage)
        self.batch_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # 导出失败数据按钮
        self.export_button = tk.Button(self, text="导出失败数据", command=self.export_failed_data)
        self.export_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # 添加暂停/恢复按钮
        self.pause_resume_button = tk.Button(self, text="暂停", command=self.toggle_pause)
        self.pause_resume_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.selected_window = None
        self.failed_numbers = []
        self.paused = False

        # 绑定Combobox的选择事件
        self.combobox.bind("<<ComboboxSelected>>", self.handle_combobox_selection)

    def read_simulator(self):
        # 执行ADB命令获取已连接的模拟器窗口信息
        adb_command = "adb devices"
        result = subprocess.run(adb_command, capture_output=True, text=True, shell=True)
        output = result.stdout

        # 解析输出并显示在下拉式选项框中
        devices = output.strip().split('\n')[1:]
        device_list = [device.split()[0] for device in devices]
        self.combobox['values'] = device_list

    def handle_combobox_selection(self, event=None):
        # 处理Combobox选择事件
        selected_window = self.combobox.get()
        if selected_window:
            self.selected_window = selected_window
            self.status_label.config(text=f"已选择窗口 {self.selected_window}")
        else:
            self.status_label.config(text="请先选择一个窗口")

    def toggle_pause(self):
        # 切换暂停和恢复状态
        self.paused = not self.paused
        self.pause_resume_button.config(text="恢复" if self.paused else "暂停")

    def batch_manage(self):
        # 清除之前的结果
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        # 批量设置管理的操作逻辑
        numbers = self.number_entry.get("1.0", tk.END).strip().split("\n")

        self.paused = False
        self.failed_numbers = []

        for number in numbers:
            if not number.strip():
                continue

            # 检查是否需要暂停
            while self.paused:
                self.update()
                time.sleep(0.1)

            # 执行设置管理操作
            success = self.set_as_group_admin(self.selected_window, number.strip())

            # 显示结果
            result_text = f"号码 {number.strip()} 设置管理成功" if success else f"号码 {number.strip()} 设置管理失败"
            result_label = tk.Label(self.result_frame, text=result_text, anchor="w")
            result_label.pack(fill=tk.X, padx=10, pady=5)

            # 如果设置管理失败，记录到失败号码列表
            if not success:
                self.failed_numbers.append(number.strip())

            # 更新界面
            self.update()
            time.sleep(0.002)  # 可以适当调整等待时间

        # 批量设置管理完成后更新按钮文本
        self.pause_resume_button.config(text="暂停")
        self.paused = False

    def set_as_group_admin(self, window, number):
        try:
            # 输入号码到搜索框
            adb_command = f'adb -s {window} shell input text "{number}"'
            subprocess.run(adb_command, shell=True)
            time.sleep(0.002)  # 等待界面响应，时间可以适当调整

            # 点击搜索按钮
            adb_command = f'adb -s {window} shell input tap 108 153'
            subprocess.run(adb_command, shell=True)
            time.sleep(0.002)  # 等待搜索结果，时间可以适当调整

            # 检查是否出现 "没有找到" 文本
            adb_command = f'adb -s {window} shell uiautomator dump /sdcard/ui.xml && adb -s {window} pull /sdcard/ui.xml'
            subprocess.run(adb_command, shell=True)
            time.sleep(0.002)  # 等待文件下载
            with open('ui.xml', 'r', encoding='utf8') as f:
                xml_content = f.read()
                if '没有找到' in xml_content:
                    # 点击清除查询按钮
                    adb_command = f'adb -s {window} shell input tap 460 80'
                    subprocess.run(adb_command, shell=True)
                    return False
                else:
                    # 点击选定为群组管理员
                    adb_command = f'adb -s {window} shell input tap 300 530'
                    subprocess.run(adb_command, shell=True)
                    time.sleep(0.6)  # 等待操作完成

                    # 点击清除查询按钮
                    adb_command = f'adb -s {window} shell input tap 460 80'
                    subprocess.run(adb_command, shell=True)
                    return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def export_failed_data(self):
        # 导出失败数据到文本文件
        if self.failed_numbers:
            file_path = r'C:\Users\Administrator\Desktop\没进群管理.txt'
            with open(file_path, 'w', encoding='utf-8') as f:
                for number in self.failed_numbers:
                    f.write(number + '\n')
            messagebox.showinfo("导出成功", f"失败数据已导出到 {file_path}")
        else:
            messagebox.showinfo("无失败数据", "没有失败数据需要导出")

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApplication(root)
    app.pack(fill=tk.BOTH, expand=True)  # Ensure the frame fills the root window
    root.mainloop()
