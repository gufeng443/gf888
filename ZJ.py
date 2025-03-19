import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import time
import pytesseract
from PIL import Image
import threading
import pyperclip

# 确保 Tesseract 路径正确
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 全局变量用于停止线程
stop_event = threading.Event()

def get_emulators():
    """获取所有打开的模拟器窗口信息"""
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        devices = result.stdout.splitlines()[1:]
        emulators = []
        for device in devices:
            if device:
                device_id = device.split()[0]
                emulators.append(device_id)
        return emulators
    except Exception as e:
        print(f"Failed to get emulators: {e}")
        return []

def execute_adb_command(device_id, command):
    """执行 ADB 命令"""
    try:
        subprocess.run(['adb', '-s', device_id] + command.split(), check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute ADB command: {e}")

def click_coordinates(device_id, x1, y1, x2, y2):
    """点击指定坐标"""
    command = f'shell input tap {x1} {y1}'
    execute_adb_command(device_id, command)

def resize_image(image, scale_factor):
    """放大图片"""
    width, height = image.size
    new_size = (int(width * scale_factor), int(height * scale_factor))
    return image.resize(new_size, Image.Resampling.LANCZOS)  # 使用新的 Resampling 方法

def extract_text_from_image(image):
    """从图像中提取文本"""
    try:
        text = pytesseract.image_to_string(image, lang='chi_sim')
        return text
    except Exception as e:
        print(f"Failed to extract text: {e}")
        return ""

def get_screenshot(device_id):
    """获取指定模拟器的截图"""
    try:
        execute_adb_command(device_id, 'shell screencap -p /sdcard/screen.png')
        execute_adb_command(device_id, 'pull /sdcard/screen.png screen.png')
        image = Image.open('screen.png')
        return image
    except Exception as e:
        print(f"Failed to capture screenshot: {e}")
        return None


def create_group(device_id, group_name, send_message):
    """创建一个群组"""
    if stop_event.is_set():
        return  # 如果停止事件被触发，立即返回

    print(f"Creating group: {group_name}")

    image = get_screenshot(device_id)
    if image:
        # 放大图片
        image = resize_image(image, scale_factor=2)  # 放大倍数可以根据需要调整
        text = extract_text_from_image(image)

        # 直接执行点击操作来创建群组，不检查“公告”
        click_coordinates(device_id, 12, 876, 528, 948)
        time.sleep(0.1)
        click_coordinates(device_id, 108, 151, 540, 184)
        time.sleep(0.2)
        click_coordinates(device_id, 0, 233, 540, 298)
        time.sleep(0.1)
        execute_adb_command(device_id, f'shell input text "{group_name}"')
        click_coordinates(device_id, 24, 435, 128, 471)
        time.sleep(0.1)
        click_coordinates(device_id, 420, 197, 516, 245)
        time.sleep(0.05)
        if not send_message:
            click_coordinates(device_id, 420, 415, 516, 463)
        execute_adb_command(device_id, "shell input keyevent KEYCODE_BACK")
        time.sleep(0.3)
        click_coordinates(device_id, 432, 852, 516, 936)

        # 监测页面并提取链接
        monitor_page(device_id, "经由链接邀请", [(75, 698, 465, 770)], delay=1)
        time.sleep(0.1)
        click_coordinates(device_id, 358, 557, 454, 629)
        time.sleep(0.1)

        # 提取群组链接逻辑
        try:
            # 点击“复制链接”按钮两次
            click_coordinates(device_id, 129, 508, 522, 544)  # 第一次点击
            time.sleep(0.5)
            click_coordinates(device_id, 129, 508, 522, 544)  # 第二次点击

            # 获取剪切板中的内容
            time.sleep(1)  # 等待剪切板更新
            link = pyperclip.paste()

            # 将链接添加到群组链接文本框中
            if link:
                current_text = group_links_text_box.get("1.0", tk.END).strip()
                if current_text:
                    group_links_text_box.insert(tk.END, "\n" + link)
                else:
                    group_links_text_box.insert(tk.END, link)
        except Exception as e:
            print(f"Failed to extract and display link: {e}")

        time.sleep(1)
        execute_adb_command(device_id, "shell input keyevent KEYCODE_BACK")
        time.sleep(0.3)
        execute_adb_command(device_id, "shell input keyevent KEYCODE_BACK")


def monitor_page(device_id, check_text, click_coordinates_list, delay=1):
    """监视页面直到找到指定文本并执行点击操作"""
    while not stop_event.is_set():
        image = get_screenshot(device_id)
        if image:
            # 放大图片
            image = resize_image(image, scale_factor=2)
            text = extract_text_from_image(image)
            if check_text in text:
                for coords in click_coordinates_list:
                    click_coordinates(device_id, *coords)
                break
        time.sleep(delay)

def validate_integer(value):
    """验证输入框内容是否为正整数"""
    if value.isdigit() and int(value) > 0:
        return True
    return False

def on_read_emulators():
    """读取模拟器并更新下拉菜单"""
    emulators = get_emulators()
    emulator_combo['values'] = emulators
    if emulators:
        emulator_combo.set(emulators[0])

def on_create_groups():
    """处理创建群组的逻辑"""
    selected_device = emulator_combo.get()
    if not selected_device:
        messagebox.showwarning("Warning", "Please select an emulator.")
        return

    group_count = group_count_entry.get()
    start_number = start_number_entry.get()

    if not validate_integer(group_count) or not validate_integer(start_number):
        messagebox.showerror("Error", "Invalid input. Please enter valid positive integers.")
        return

    group_count = int(group_count)
    start_number = int(start_number)
    send_message = send_message_var.get()

    # 启动一个后台线程来执行群组创建操作
    global stop_event
    stop_event.clear()  # 清除停止标志
    worker_thread = threading.Thread(target=run_group_creation,
                                     args=(selected_device, group_count, start_number, send_message))
    worker_thread.start()

def run_group_creation(device_id, group_count, start_number, send_message):
    """后台线程执行群组创建"""
    for i in range(group_count):
        if stop_event.is_set():
            break  # 如果停止事件被触发，退出循环

        group_name = str(start_number + i)
        create_group(device_id, group_name, send_message)

def on_stop():
    """停止后台线程"""
    stop_event.set()

# GUI 创建代码
class ZJ(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        # 读取模拟器按钮
        read_emulators_button = ttk.Button(self, text="读取模拟器", command=on_read_emulators)
        read_emulators_button.pack(pady=10)

        # 模拟器下拉菜单
        global emulator_combo
        emulator_combo = ttk.Combobox(self, state="readonly")
        emulator_combo.pack(pady=10)

        # 群组数量输入框
        group_count_label = tk.Label(self, text="需要建几个群组:")
        group_count_label.pack(pady=5)
        global group_count_entry
        group_count_entry = tk.Entry(self)
        group_count_entry.insert(0, "6")
        group_count_entry.pack(pady=5)

        # 群组名称起始数字输入框
        start_number_label = tk.Label(self, text="群组名称起始数字:")
        start_number_label.pack(pady=5)
        global start_number_entry
        start_number_entry = tk.Entry(self)
        start_number_entry.insert(0, "1")
        start_number_entry.pack(pady=5)

        # 是否打开发送消息的选项框
        global send_message_var
        send_message_var = tk.BooleanVar()
        send_message_check = tk.Checkbutton(self, text="是否打开发送消息", variable=send_message_var)
        send_message_check.pack(pady=10)

        # 创建群组按钮
        create_groups_button = ttk.Button(self, text="创建群组", command=on_create_groups)
        create_groups_button.pack(pady=10)

        # 停止按钮
        stop_button = ttk.Button(self, text="停止", command=on_stop)
        stop_button.pack(pady=10)

        # 群组链接文本框
        global group_links_text_box
        group_links_text_box = tk.Text(self, height=10, width=50)
        group_links_text_box.pack(pady=10)

        # 初始化时读取模拟器列表
        on_read_emulators()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("群组创建器")
    ZJ(root).pack(fill=tk.BOTH, expand=True)
    root.mainloop()
