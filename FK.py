# pages/emulator_selector.py

import subprocess
import threading
import time
import os
import re
from PIL import Image
import pytesseract
import tkinter as tk
from tkinter import messagebox, scrolledtext

# 全局变量，用于停止监控
stop_monitoring_flags = {}

def get_emulator_windows():
    """获取已连接的模拟器设备列表"""
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    devices = result.stdout.splitlines()
    devices = [device.split()[0] for device in devices if device.endswith('device')]
    return devices

class EmulatorSelector(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.devices = get_emulator_windows()
        self.check_vars = {}
        self.screenshot_buttons = {}
        self.monitor_threads = {}
        self.create_widgets()

    def create_widgets(self):
        """创建界面控件"""
        self.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        if not self.devices:
            tk.Label(self, text="没有找到模拟器设备。", font=("Arial", 12)).pack(pady=20)
            return

        tk.Label(self, text="模拟器窗口选择:", font=("Arial", 12)).grid(row=0, column=0, columnspan=3, pady=5)

        for i, device in enumerate(self.devices):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self, text=device, variable=var)
            chk.grid(row=i + 1, column=0, sticky='w', padx=10, pady=5)
            self.check_vars[device] = var

            # 添加“截图”按钮，动态命名
            button_text = f"窗口{i + 1}  截图"
            button = tk.Button(self, text=button_text, command=lambda d=device: self.take_screenshot(d),
                               font=("Arial", 10))
            button.grid(row=i + 1, column=1, padx=5, pady=5)
            self.screenshot_buttons[device] = button

        # 启动按钮
        self.start_button = tk.Button(self, text="开始运行", command=self.start_monitoring, font=("Arial", 10))
        self.start_button.grid(row=len(self.devices) + 1, column=0, pady=10, padx=10)

        # 停止按钮
        self.stop_button = tk.Button(self, text="停止运行", command=self.stop_monitoring, state=tk.DISABLED,
                                     font=("Arial", 10))
        self.stop_button.grid(row=len(self.devices) + 1, column=1, pady=10, padx=10)

        # 任务结果显示区
        tk.Label(self, text="执行结果:", font=("Arial", 12)).grid(row=len(self.devices) + 2, column=0, columnspan=3,
                                                                     pady=5)
        self.output_text = scrolledtext.ScrolledText(self, width=80, height=10, wrap=tk.WORD, font=("Arial", 10))
        self.output_text.grid(row=len(self.devices) + 3, column=0, columnspan=3, pady=10, padx=10)

    def append_output(self, message):
        """在结果显示区追加输出"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.yview(tk.END)

    def start_monitoring(self):
        """开始监控选中的模拟器"""
        selected_devices = [dev for dev, var in self.check_vars.items() if var.get()]
        if not selected_devices:
            messagebox.showwarning("No Selection", "Please select at least one emulator to monitor.")
        else:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            stop_monitoring_flags.clear()
            for device_id in selected_devices:
                stop_monitoring_flags[device_id] = threading.Event()
            self.monitor_threads = {
                device_id: threading.Thread(target=start_monitoring,
                                            args=(device_id, self.append_output, stop_monitoring_flags[device_id]))
                for device_id in selected_devices
            }
            for thread in self.monitor_threads.values():
                thread.start()

    def stop_monitoring(self):
        """停止所有监控"""
        for flag in stop_monitoring_flags.values():
            flag.set()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def take_screenshot(self, device_id):
        """截取选中设备的屏幕并保存"""
        if device_id in stop_monitoring_flags:
            stop_monitoring_flags[device_id].set()
            self.monitor_threads[device_id].join()
            self.screenshot(device_id)
            self.append_output(f"{device_id} 执行完毕，截图已保存.")

    def screenshot(self, device_id):
        """截图并保存到指定路径"""
        save_path = r"C:\Users\Administrator\Desktop\2222"
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        screenshot_file = f"screenshot_{device_id}.png"
        subprocess.run(['adb', '-s', device_id, 'shell', 'screencap', '-p', f'/sdcard/{screenshot_file}'])
        subprocess.run(['adb', '-s', device_id, 'pull', f'/sdcard/{screenshot_file}', screenshot_file])

        original_image = Image.open(screenshot_file)
        screenshot_path = os.path.join(save_path, f"{device_id}_screenshot.png")
        original_image.save(screenshot_path)
        os.remove(screenshot_file)
        self.append_output(f"{device_id} 执行完毕，截图已保存.")


def monitor_window(device_id, save_path, output_callback, stop_event):
    """监控指定模拟器窗口的内容"""
    prev_image = None
    prev_text = None

    while not stop_event.is_set():
        screenshot_file = f"screenshot_{device_id}.png"
        subprocess.run(['adb', '-s', device_id, 'shell', 'screencap', '-p', f'/sdcard/{screenshot_file}'])
        subprocess.run(['adb', '-s', device_id, 'pull', f'/sdcard/{screenshot_file}', screenshot_file])

        original_image = Image.open(screenshot_file)
        text = extract_text_from_image(original_image)

        match = re.search(r'(\d+)\s*位成员', text)
        if match:
            current_text = match.group(0)
            if prev_text is None:
                prev_text = current_text
                prev_image = original_image
            elif current_text != prev_text:
                prev_text = current_text
                prev_image = original_image
        else:
            if prev_image is not None:
                screenshot_path = os.path.join(save_path, f"{device_id}_screenshot.png")
                output_message = f"Saving image to {screenshot_path}"
                output_callback(output_message)
                prev_image.save(screenshot_path)
                output_message = f"{device_id} 执行完毕，截图已保存."
                output_callback(output_message)
                break  # 停止监控

        os.remove(screenshot_file)
        time.sleep(1)  # 快速轮询以确保获取最新数据


def extract_text_from_image(image):
    """从图像中提取文本"""
    custom_config = r'--oem 3 --psm 6 -l chi_sim'
    text = pytesseract.image_to_string(image, config=custom_config)
    return text


def start_monitoring(device_id, output_callback, stop_event):
    """启动监控"""
    save_path = r"C:\Users\Administrator\Desktop\2222"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    monitor_window(device_id, save_path, output_callback, stop_event)
