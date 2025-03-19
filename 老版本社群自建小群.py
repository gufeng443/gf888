import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import threading
import pyperclip
import uiautomator2 as u2
import time

# 全局变量用于停止线程
stop_event = threading.Event()

def get_emulators():
    """获取所有打开的模拟器窗口信息"""
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        devices = result.stdout.splitlines()[1:]
        emulators = [device.split()[0] for device in devices if device]
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

def create_group(device_id, group_name):
    """创建一个群组"""
    if stop_event.is_set():
        return

    resource_id_prefix = "com.whatsapp" if version_var.get() == "个人版" else "com.whatsapp.w4b"
    print(f"Creating group: {group_name}")

    d = u2.connect(device_id)

    # 点击"添加群组"按钮
    add_group_button = d(resourceId=f"{resource_id_prefix}:id/community_navigation_add_group_button")
    add_group_button.wait(timeout=10)
    add_group_button.click()

    # 点击"新建群组"按钮
    new_group_button = d(text="新建群组")
    new_group_button.wait(timeout=10)
    new_group_button.click()

    # 输入群组名称
    group_name_input = d(resourceId=f"{resource_id_prefix}:id/group_name")
    group_name_input.wait(timeout=10)
    group_name_input.set_text(group_name)

    # 点击群组权限控件
    group_permission_button = d(text="群组权限")
    group_permission_button.wait(timeout=10)
    group_permission_button.click()

    # 开启群组设置和发送消息权限
    edit_group_switch = d(resourceId=f"{resource_id_prefix}:id/edit_group_settings_switch")
    edit_group_switch.wait(timeout=10)
    edit_group_switch.click()
    time.sleep(0.3)
    send_message_switch = d(resourceId=f"{resource_id_prefix}:id/send_messages_switch")
    send_message_switch.wait(timeout=10)
    send_message_switch.click()

    # 返回上一页面并创建群组
    d.press('back')
    create_button = d(resourceId=f"{resource_id_prefix}:id/ok_btn")
    create_button.wait(timeout=10)
    create_button.click()
    time.sleep(1)
    # 点击"经由链接邀请"
    invite_link_button = d(text="经由链接邀请")
    invite_link_button.wait(timeout=10)
    invite_link_button.click()

    # 点击"确认"按钮
    confirm_button = d(text="确认")
    confirm_button.wait(timeout=10)
    confirm_button.click()

    # 提取群组链接信息
    group_link_element = d(resourceId=f"{resource_id_prefix}:id/link")
    if group_link_element.wait(timeout=10):
        # 等待直到元素的文本不为空
        for _ in range(10):  # 最多检查10次
            group_link_info = group_link_element.info
            group_link = group_link_info.get('text', '').strip()
            if group_link:  # 如果链接不为空，退出循环
                break
            time.sleep(0.2)  # 等待0.5秒后再检查

        if group_link:  # 确保获取到链接
            current_text = group_links_text_box.get("1.0", tk.END).strip()
            if current_text:
                group_links_text_box.insert(tk.END, f"\n{group_name}: {group_link}")
            else:
                group_links_text_box.insert(tk.END, f"{group_name}: {group_link}")

    # 返回上一页面两次
    d.press('back')
    time.sleep(0.3)
    d.press('back')

def validate_integer(value):
    """验证输入框内容是否为正整数"""
    return value.isdigit() and int(value) > 0

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

    global stop_event
    stop_event.clear()
    worker_thread = threading.Thread(target=run_group_creation,
                                     args=(selected_device, group_count, start_number))
    worker_thread.start()

def run_group_creation(device_id, group_count, start_number):
    """后台线程执行群组创建"""
    for i in range(group_count):
        if stop_event.is_set():
            break
        group_name = str(start_number + i)
        create_group(device_id, group_name)

def on_stop():
    """停止后台线程"""
    stop_event.set()

# 创建 GUI
root = tk.Tk()
root.title("群组创建工具")
root.geometry("400x620")

# 版本选择
version_var = tk.StringVar(value="个人版")
version_label = tk.Label(root, text="选择 WhatsApp 版本:")
version_label.pack(pady=5)
personal_version_radio = tk.Radiobutton(root, text="个人版", variable=version_var, value="个人版")
personal_version_radio.pack(anchor=tk.W)
business_version_radio = tk.Radiobutton(root, text="商业版", variable=version_var, value="商业版")
business_version_radio.pack(anchor=tk.W)

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
group_links_text_box = tk.Text(root, height=15, width=70)
group_links_text_box.pack(pady=10)

root.mainloop()
