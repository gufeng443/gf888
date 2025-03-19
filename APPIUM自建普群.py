import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import time
import pytesseract
from PIL import Image
import threading
import pyperclip
import uiautomator2 as u2

# 配置 Tesseract 路径（根据你的系统配置）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows 示例路径

# 全局变量用于停止线程
stop_event = threading.Event()

# 设置资源ID前缀
resource_id_prefix = "com.whatsapp"  # 默认使用个人版

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

def click_coordinates(device_id, x, y):
    """点击指定坐标"""
    command = f'shell input tap {x} {y}'
    execute_adb_command(device_id, command)

def create_group(device_id, group_name):
    """使用 uiautomator2 创建一个群组"""
    if stop_event.is_set():
        return  # 如果停止事件被触发，立即返回

    print(f"Creating group: {group_name}")

    # 连接到设备
    d = u2.connect(device_id)

    # 点击添加群组按钮
    d(resourceId=f"{resource_id_prefix}:id/community_navigation_add_group_button", text="添加群组").click()
    time.sleep(2)  # 等待页面加载

    # 点击新建群组按钮
    d(text="新建群组").click()
    time.sleep(2)  # 等待页面加载

    # 输入群组名称
    d(resourceId=f"{resource_id_prefix}:id/group_name").set_text(group_name)

    # 点击群组权限控件
    d(resourceId=f"{resource_id_prefix}:id/list_item_title", text="群组权限").click()
    time.sleep(1)  # 等待页面加载

    # 开启"编辑群组设置"和"发送消息"权限
    d(resourceId=f"{resource_id_prefix}:id/edit_group_settings_switch", text="开启").click()
    d(resourceId=f"{resource_id_prefix}:id/send_messages_switch", text="开启").click()
    time.sleep(1)  # 等待页面加载

    # 返回上一页面
    d.press("back")
    time.sleep(1)

    # 点击创建群组控件
    d(resourceId=f"{resource_id_prefix}:id/ok_btn", description="创建").click()
    time.sleep(2)  # 等待页面加载

    # 点击"经由链接邀请"
    d(text="经由链接邀请").click()
    time.sleep(2)  # 等待页面加载

    # 点击确认选项
    d(text="确认").click()
    time.sleep(1)  # 等待页面加载

    # 提取群组链接信息
    group_link_element = d(resourceId=f"{resource_id_prefix}:id/link")
    if group_link_element.exists:
        group_link_info = group_link_element.info
        group_link = group_link_info.get('text', '')  # 尝试从info中获取文本
        if group_link:
            current_text = group_links_text_box.get("1.0", tk.END).strip()
            if current_text:
                group_links_text_box.insert(tk.END, f"\n{group_name}: {group_link}")
            else:
                group_links_text_box.insert(tk.END, f"{group_name}: {group_link}")

    time.sleep(1)  # 等待页面稳定

    # 返回上一页两次
    d.press("back")
    time.sleep(1)
    d.press("back")

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

    # 启动一个后台线程来执行群组创建操作
    global stop_event
    stop_event.clear()  # 清除停止标志
    worker_thread = threading.Thread(target=run_group_creation,
                                     args=(selected_device, group_count, start_number))
    worker_thread.start()

def run_group_creation(device_id, group_count, start_number):
    """后台线程执行群组创建"""
    for i in range(group_count):
        if stop_event.is_set():
            break  # 如果停止事件被触发，退出循环

        group_name = str(start_number + i)
        create_group(device_id, group_name)

def on_stop():
    """停止后台线程"""
    stop_event.set()

def on_version_change(event):
    """处理版本选择变化"""
    global resource_id_prefix
    if version_var.get() == "个人版":
        resource_id_prefix = "com.whatsapp"
    else:
        resource_id_prefix = "com.whatsapp.w4b"

# 创建 GUI
root = tk.Tk()
root.title("群组创建工具")
root.geometry("400x620")  # 增加一些空间以容纳停止按钮

# 版本选择
version_var = tk.StringVar(value="个人版")
version_label = tk.Label(root, text="选择版本:")
version_label.pack(pady=5)

version_combo = ttk.Combobox(root, textvariable=version_var, state="readonly")
version_combo['values'] = ("个人版", "商业版")
version_combo.pack(pady=5)
version_combo.bind("<<ComboboxSelected>>", on_version_change)

# 读取模拟器按钮
read_emulators_button = ttk.Button(root, text="读取模拟器", command=on_read_emulators)
read_emulators_button.pack(pady=10)

# 模拟器下拉菜单
emulator_combo = ttk.Combobox(root, state="readonly")
emulator_combo.pack(pady=10)

# 群组数量输入框
group_count_label = tk.Label(root, text="需要建几个群组:")
group_count_label.pack(pady=5)
group_count_entry = tk.Entry(root)
group_count_entry.insert(0, "6")
group_count_entry.pack(pady=5)

# 群组名称起始数字输入框
start_number_label = tk.Label(root, text="群组名称起始数字:")
start_number_label.pack(pady=5)
start_number_entry = tk.Entry(root)
start_number_entry.insert(0, "1")
start_number_entry.pack(pady=5)

# 创建群组按钮
create_groups_button = ttk.Button(root, text="创建群组", command=on_create_groups)
create_groups_button.pack(pady=10)

# 停止按钮
stop_button = ttk.Button(root, text="停止", command=on_stop)
stop_button.pack(pady=10)

# 群组链接提取文本框
group_links_label = tk.Label(root, text="群组链接:")
group_links_label.pack(pady=5)
group_links_text_box = tk.Text(root, height=15, width=50)
group_links_text_box.pack(pady=10)

root.mainloop()
