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
def approve_pending_groups(device, version):
    # 根据版本选择资源ID
    resource_id = "com.whatsapp:id/approve_button" if version == "personal" else "com.whatsapp.w4b:id/approve_button"
    groups = device(resourceId=resource_id, className="android.widget.Button")
    if groups.exists:
        for group in groups:
            approve_button = group.sibling(resourceId=resource_id)
            if approve_button.exists:
                print(f"点击批准按钮 ...")
                approve_button.click()
                time.sleep(5)  # 每次点击后等待1秒
        return True
    return False


# 向下滑动模拟鼠标滚轮的操作
def scroll_down(device):
    try:
        width, height = device.info['displayWidth'], device.info['displayHeight']
        device.swipe(width // 2, height // 1.3, width // 2, height // 2.1, 0.2)
        time.sleep(1)
        return True
    except Exception as e:
        print(f"滚动操作失败: {e}")
        return False


# 自动化批准群组的操作
def approve_groups(device_id, stop_event, version):
    try:
        device = u2.connect(device_id)

        # 检查是否在群组审批页面
        if not check_pending_groups_page(device):
            return

        while not stop_event.is_set():
            if not approve_pending_groups(device, version):
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
def start_automation_for_device(device_id, version):
    stop_event = threading.Event()  # 为每个设备创建独立的停止事件
    stop_events[device_id] = stop_event  # 存储对应设备的停止事件

    # 启动线程执行自动化操作
    threading.Thread(target=approve_groups, args=(device_id, stop_event, version)).start()


# 定时任务的字典
timers = {}


# 定时重新启动自动化任务
def start_timer_for_device(device_id, delay_minutes, version):
    def restart_task():
        print(f"设备 {device_id}: 定时任务启动，开始执行自动化任务")
        start_automation_for_device(device_id, version)  # 启动自动化任务

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
        self.root.geometry("500x700")

        # 版本选择变量
        self.version_var = tk.StringVar(value="personal")  # 默认选择个人版

        self.devices = get_connected_devices()  # 获取连接的设备
        self.device_checkboxes = {}

        # 创建主框架
        main_frame = tk.Frame(self.root, bg="#f7f7f7")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # 连接控制按钮框架
        conn_frame = tk.Frame(main_frame, bg="#f7f7f7")
        conn_frame.pack(pady=10, fill="x")

        # 断开连接按钮
        self.disconnect_btn = ttk.Button(
            conn_frame,
            text="断开ADB链接",
            command=self.disconnect_adb,
            style="TButton"
        )
        self.disconnect_btn.pack(side="left", padx=5)

        # 重新获取连接按钮
        self.reconnect_btn = ttk.Button(
            conn_frame,
            text="重新获取链接",
            command=self.refresh_devices,
            style="TButton"
        )
        self.reconnect_btn.pack(side="left", padx=5)

        # 标题标签
        title_label = tk.Label(main_frame, text="请选择要自动化的模拟器设备:", font=('Arial', 14, 'bold'), bg="#f7f7f7")
        title_label.pack(pady=10)

        # 版本选择框架
        version_frame = tk.Frame(main_frame, bg="#f7f7f7")
        version_frame.pack(pady=10)

        # 版本选择标签
        version_label = tk.Label(version_frame, text="选择版本:", font=('Arial', 12), bg="#f7f7f7")
        version_label.pack(side="left", padx=5)

        # 个人版单选按钮
        personal_radio = tk.Radiobutton(
            version_frame, text="个人版", variable=self.version_var, value="personal", font=('Arial', 12), bg="#f7f7f7"
        )
        personal_radio.pack(side="left", padx=5)

        # 商业版单选按钮
        business_radio = tk.Radiobutton(
            version_frame, text="商业版", variable=self.version_var, value="business", font=('Arial', 12), bg="#f7f7f7"
        )
        business_radio.pack(side="left", padx=5)

        # 设备复选框容器
        self.devices_frame = tk.Frame(main_frame, bg="#f7f7f7")
        self.devices_frame.pack(fill="both", expand=True)

        # 初始化设备列表
        self.refresh_device_list()

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
        self.control_button.pack(pady=10)

        self.is_automating = False
        self.stop_event = None

        # 终止定时按钮
        self.stop_timer_button = ttk.Button(main_frame, text="终止定时", style="TButton", command=self.stop_timer)
        self.stop_timer_button.pack(pady=10)

        # 结果显示标签
        self.result_label = tk.Label(main_frame, text="操作结果将显示在此", font=('Arial', 10), bg="#f7f7f7")
        self.result_label.pack(pady=10)

        # 设置按钮样式
        style = ttk.Style()
        style.configure("TButton", font=('Arial', 12), padding=10, relief="flat", background="#4CAF50",
                        foreground="white")
        style.map("TButton", background=[('active', '#45a049')])

    def refresh_device_list(self):
        """刷新设备列表"""
        # 清空现有设备复选框
        for widget in self.devices_frame.winfo_children():
            widget.destroy()

        # 重新创建设备复选框
        self.device_checkboxes = {}
        for device in self.devices:
            var = tk.IntVar()
            cb = tk.Checkbutton(self.devices_frame, text=f"模拟器: {device}", variable=var, font=('Arial', 12),
                               bg="#f7f7f7", anchor="w", padx=10)
            cb.pack(anchor="w", pady=3)
            self.device_checkboxes[device] = var

    def disconnect_adb(self):
        """断开所有ADB连接"""
        try:
            # 停止所有自动化任务
            for device_id in list(stop_events.keys()):
                stop_automation_for_device(device_id)

            # 执行ADB断开连接命令
            subprocess.run(['adb', 'disconnect'], check=True)
            self.devices = []
            self.refresh_device_list()
            self.result_label.config(text="已断开所有ADB连接")
            messagebox.showinfo("成功", "ADB连接已断开")
        except Exception as e:
            messagebox.showerror("错误", f"断开连接失败: {str(e)}")

    def refresh_devices(self):
        """重新扫描连接的设备"""
        try:
            self.devices = get_connected_devices()
            if not self.devices:
                messagebox.showwarning("提示", "没有检测到连接的设备")
            self.refresh_device_list()
            self.result_label.config(text="设备列表已刷新")
        except Exception as e:
            messagebox.showerror("错误", f"刷新设备失败: {str(e)}")

    def confirm_timing(self):
        delay_minutes = self.get_delay_minutes()
        selected_devices = [device for device, var in self.device_checkboxes.items() if var.get() == 1]
        version = self.version_var.get()  # 获取用户选择的版本

        if selected_devices:
            if delay_minutes:
                # 设置定时启动
                for device in selected_devices:
                    self.result_label.config(text=f"设备 {device} 自动化任务将在 {delay_minutes} 分钟后启动")
                    start_timer_for_device(device, delay_minutes, version)
            else:
                # 立即执行
                for device in selected_devices:
                    self.result_label.config(text=f"设备 {device} 自动化任务已立即启动")
                    start_automation_for_device(device, version)
        else:
            messagebox.showwarning("警告", "请至少选择一个模拟器设备来启动自动化任务")

    def toggle_automation(self):
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