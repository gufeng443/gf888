import subprocess
import time
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import uiautomator2 as u2
from datetime import datetime


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


# 检查群组页面是否在待批准状态
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
                time.sleep(2)  # 每次点击后等待1秒
        return True
    return False


# 向下滑动模拟鼠标滚轮的操作
def scroll_down(device):
    try:
        width, height = device.info['displayWidth'], device.info['displayHeight']
        device.swipe(width // 2, height // 1.3, width // 2, height // 2, 0.2)
        time.sleep(0.2)
        return True
    except Exception as e:
        print(f"滚动操作失败: {e}")
        return False


# 自动化批准群组的操作
def approve_groups(device_id, stop_event):
    try:
        device = u2.connect(device_id)

        # 检查是否在群组审批页面
        if not check_pending_groups_page(device):
            return

        while not stop_event.is_set():
            if not approve_pending_groups(device):
                print(f"设备 {device_id}: 没有待批准的群组，结束操作")
                break

            if not scroll_down(device):
                print(f"设备 {device_id}: 没有更多群组，结束操作")
                break

            time.sleep(1.5)

        stop_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"设备 {device_id}: 自动化任务停止，时间: {stop_time}")
        return stop_time
    except Exception as e:
        print(f"设备 {device_id}: 操作失败: {e}")
        return None


# 启动一个新的线程来执行自动化任务
def start_automation_for_device(device_id):
    stop_event = threading.Event()  # 为每个设备创建独立的停止事件
    stop_events[device_id] = stop_event  # 存储对应设备的停止事件

    # 启动线程执行自动化操作
    threading.Thread(target=approve_groups, args=(device_id, stop_event)).start()


# 定时任务的字典
timers = {}


# 定时重新启动自动化任务
def start_timer_for_device(device_id, delay_minutes):
    def restart_task():
        print(f"设备 {device_id}: 定时任务启动，开始执行自动化任务")
        start_automation_for_device(device_id)  # 启动自动化任务

    # 每 delay_minutes 分钟重新启动一次
    timer = threading.Timer(delay_minutes * 60, restart_task)  # 转换为秒
    timers[device_id] = timer
    timer.start()


# 存储每个设备的停止事件
stop_events = {}


# 停止某个设备的自动化任务
def stop_automation_for_device(device_id):
    if device_id in stop_events:
        stop_events[device_id].set()  # 触发停止事件
        print(f"设备 {device_id}: 自动化任务已停止")

        # 如果有定时任务，取消定时器
        if device_id in timers:
            timers[device_id].cancel()
            del timers[device_id]
        del stop_events[device_id]  # 清除停止事件


# 主界面和自动化控制逻辑
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("模拟器自动化批准群组")
        self.root.geometry("500x600")

        self.devices = get_connected_devices()  # 获取连接的设备
        self.device_checkboxes = {}

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

        # 动态添加设备复选框
        for device in self.devices:
            var = tk.IntVar()
            cb = tk.Checkbutton(devices_frame, text=f"模拟器: {device}", variable=var, font=('Arial', 12), bg="#f7f7f7",
                                anchor="w", padx=10)
            cb.pack(anchor="w", pady=3)
            self.device_checkboxes[device] = var

        # 定时启动时间输入框
        self.time_label = tk.Label(main_frame, text="设置定时启动时间（分钟，留空立即执行）:", font=('Arial', 12),
                                   bg="#f7f7f7")
        self.time_label.pack(pady=5)
        self.time_entry = tk.Entry(main_frame, font=('Arial', 12))
        self.time_entry.pack(pady=5)

        # 确认定时按钮
        self.confirm_button = ttk.Button(main_frame, text="确认定时", style="TButton", command=self.confirm_timing)
        self.confirm_button.pack(pady=5)

        # 控制按钮
        self.control_button = ttk.Button(main_frame, text="开始自动化", style="TButton", command=self.toggle_automation)
        self.control_button.pack(pady=20)

        self.is_automating = False
        self.stop_event = None

        # 终止定时按钮
        self.stop_timer_button = ttk.Button(main_frame, text="终止定时", style="TButton", command=self.stop_timer)
        self.stop_timer_button.pack(pady=20)

        # 结果显示标签
        self.result_label = tk.Label(main_frame, text="操作结果将显示在此", font=('Arial', 10), bg="#f7f7f7")
        self.result_label.pack(pady=10)

        # 设置按钮样式
        style = ttk.Style()
        style.configure("TButton", font=('Arial', 12), padding=10, relief="flat", background="#4CAF50",
                        foreground="white")
        style.map("TButton", background=[('active', '#45a049')])

    def confirm_timing(self):
        delay_minutes = self.get_delay_minutes()
        selected_devices = [device for device, var in self.device_checkboxes.items() if var.get() == 1]

        if selected_devices:
            if delay_minutes:
                # 设置定时启动
                for device in selected_devices:
                    self.result_label.config(text=f"设备 {device} 自动化任务将在 {delay_minutes} 分钟后启动")
                    start_timer_for_device(device, delay_minutes)
            else:
                # 立即执行
                for device in selected_devices:
                    self.result_label.config(text=f"设备 {device} 自动化任务已立即启动")
                    start_automation_for_device(device)
        else:
            messagebox.showwarning("警告", "请至少选择一个模拟器设备来启动自动化任务")

    def toggle_automation(self):
        # 该按钮在确认定时后将不起作用
        pass

    def stop_timer(self):
        selected_devices = [device for device, var in self.device_checkboxes.items() if var.get() == 1]
        if selected_devices:
            for device in selected_devices:
                stop_automation_for_device(device)
                self.result_label.config(text=f"设备 {device} 的自动化任务已停止")
        else:
            messagebox.showwarning("警告", "请至少选择一个模拟器设备来停止自动化任务")

    def get_delay_minutes(self):
        try:
            return int(self.time_entry.get()) if self.time_entry.get() else None
        except ValueError:
            return None


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
