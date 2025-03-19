import subprocess
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import uiautomator2 as u2
import time
from datetime import datetime
import threading  # 导入 threading 模块


# 获取连接的模拟器设备
def get_connected_devices():
    result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE)
    output = result.stdout.decode().strip().split('\n')[1:]  # 跳过第一行（标题）

    devices = []
    for line in output:
        device_info = line.strip().split('\t')
        if len(device_info) == 2 and device_info[1] == 'device':
            devices.append(device_info[0])
    return devices


# 获取设备的屏幕分辨率
def get_device_screen_size(device_id):
    try:
        # 执行 adb 命令获取屏幕尺寸
        result = subprocess.run(['adb', '-s', device_id, 'shell', 'wm', 'size'], stdout=subprocess.PIPE)
        output = result.stdout.decode().strip()
        # output 格式: 'Physical size: 1080x1920'
        screen_size = output.split(":")[1].strip()
        width, height = map(int, screen_size.split('x'))
        return width, height
    except Exception as e:
        print(f"获取屏幕分辨率失败: {e}")
        return None, None


# 检查是否在待批准群组页面
def check_pending_groups_page(device):
    if not device(text="待批准群组").exists:
        messagebox.showwarning("警告", "请进入群组审批页面。")
        return False
    return True


# 批准待批准群组
def approve_pending_groups(device):
    groups = device(resourceId="com.whatsapp:id/approve_button", className="android.widget.Button")
    if groups.exists:
        for group in groups:
            approve_button = group.sibling(resourceId="com.whatsapp:id/approve_button")
            if approve_button.exists:
                print("点击批准按钮...")
                approve_button.click()
                time.sleep(1)  # 每次点击后等待1秒
        return True
    return False


# 向下滑动模拟鼠标滚轮的操作
def scroll_down(device):
    try:
        # 获取屏幕宽高
        width, height = device.info['displayWidth'], device.info['displayHeight']

        # 模拟鼠标滚轮向下滚动：从屏幕中央向下滑动
        print("开始模拟向下滚动鼠标...")
        device.swipe(width // 2, height // 1.3, width // 2, height // 2, 0.2)  # 滑动从下向上

        time.sleep(0.08)  # 等待页面加载
        return True
    except Exception as e:
        print(f"滚动操作失败: {e}")
        return False


# 自动化批准群组的主操作
def approve_groups(device_id, stop_event):
    try:
        # 连接到模拟器设备
        device = u2.connect(device_id)

        # 检查是否在群组审批页面
        if not check_pending_groups_page(device):
            return

        # 开始群组批准操作
        slide_count = 0
        while not stop_event.is_set():
            # 批准当前页面中的群组
            if not approve_pending_groups(device):
                print("没有找到待批准的群组，结束操作")
                break

            # 如果当前页面没有更多群组，尝试滚动页面
            if not scroll_down(device):
                print("没有更多群组，结束操作")
                break

            slide_count += 1  # 增加滑动次数
            print(f"已滚动 {slide_count} 次，继续检查群组...")

        # 停止操作，记录停止时间
        stop_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"自动化任务停止，时间: {stop_time}")
        return stop_time

    except Exception as e:
        print(f"操作失败: {e}")
        messagebox.showerror("错误", f"发生错误：{e}")
        return None


# 创建和显示用户界面
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("模拟器自动化批准群组")
        self.root.geometry("450x500")  # 设置窗口大小
        self.root.configure(bg="#f7f7f7")  # 设置背景色

        # 设置字体
        self.font = ('Arial', 12)

        # 获取连接的模拟器设备
        self.devices = get_connected_devices()
        self.device_checkboxes = {}

        # 如果没有连接的设备
        if not self.devices:
            messagebox.showerror("错误", "没有检测到任何连接的模拟器设备!")
            self.root.quit()
            return

        # 创建主框架
        main_frame = tk.Frame(self.root, bg="#f7f7f7")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # 标题标签
        title_label = tk.Label(main_frame, text="请选择要自动化的模拟器设备:", font=('Arial', 14, 'bold'), bg="#f7f7f7")
        title_label.pack(pady=10)

        # 设备复选框容器
        devices_frame = tk.Frame(main_frame, bg="#f7f7f7")
        devices_frame.pack(fill="both", expand=True)

        for device in self.devices:
            var = tk.IntVar()
            cb = tk.Checkbutton(devices_frame, text=f"模拟器: {device}", variable=var, font=self.font, bg="#f7f7f7",
                                anchor="w", padx=10)
            cb.pack(anchor="w", pady=3)
            self.device_checkboxes[device] = var

        # 控制按钮
        control_button = ttk.Button(main_frame, text="开始自动化", style="TButton", command=self.toggle_automation)
        control_button.pack(pady=20)

        self.control_button = control_button
        self.is_automating = False
        self.stop_event = None  # 用来停止自动化任务的事件

        # 结果显示
        self.result_label = tk.Label(main_frame, text="操作结果将显示在此", font=('Arial', 10), bg="#f7f7f7")
        self.result_label.pack(pady=10)

        # 设置按钮样式
        style = ttk.Style()
        style.configure("TButton",
                        font=('Arial', 12),
                        padding=10,
                        relief="flat",
                        background="#4CAF50",  # 按钮颜色
                        foreground="white")
        style.map("TButton", background=[('active', '#45a049')])  # 鼠标悬停时改变颜色

    def toggle_automation(self):
        selected_devices = [device for device, var in self.device_checkboxes.items() if var.get() == 1]

        if selected_devices:
            if self.is_automating:
                self.stop_automation(selected_devices)
            else:
                # 创建新的线程来执行自动化任务
                for device in selected_devices:
                    self.stop_event = threading.Event()  # 创建停止事件
                    threading.Thread(target=self.start_automation, args=(device,)).start()  # 在后台线程中执行
        else:
            messagebox.showwarning("警告", "请至少选择一个模拟器设备。")

    def start_automation(self, device):
        # 自动化批准群组的操作
        stop_time = approve_groups(device, self.stop_event)
        if stop_time:
            self.result_label.config(text=f"操作完成，停止时间: {stop_time}")
        self.is_automating = False
        self.control_button.config(text="开始自动化", style="TButton")

    def stop_automation(self, selected_devices):
        # 停止自动化
        print(f"停止自动化批准群组操作，选择的设备: {selected_devices}")
        self.is_automating = False
        self.control_button.config(text="开始自动化", style="TButton")
        if self.stop_event:
            self.stop_event.set()  # 设置停止事件，通知后台线程停止工作
        else:
            self.control_button.config(text="开始自动化", style="TButton")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
