import tkinter as tk
from tkinter import ttk, messagebox, StringVar, IntVar, Text
import subprocess
import time
import threading


def execute_adb_command(device_id, command):
    """在指定模拟器中执行 ADB 命令"""
    try:
        subprocess.run(['adb', '-s', device_id] + command.split(), check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute ADB command: {e}")


def click_coordinates(device_id, x1, y1, x2, y2):
    """点击指定坐标区域的中心"""
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    command = f'shell input tap {center_x} {center_y}'
    execute_adb_command(device_id, command)


def swipe_coordinates(device_id, x1, y1, x2, y2):
    """滑动屏幕"""
    command = f'shell input swipe {x1} {y1} {x2} {y2}'
    execute_adb_command(device_id, command)


def create_group(device_id, group_name, friend_number, group_index):
    """在指定模拟器中创建单个群组"""
    current_group_name = f"{group_name} {group_index}" if group_name else str(group_index)
    try:
        time.sleep(1)
        click_coordinates(device_id, 108, 162, 212, 198)  # 新建群组
        time.sleep(0.5)
        click_coordinates(device_id, 468, 42, 540, 114)  # 搜索选项
        time.sleep(0.5)
        click_coordinates(device_id, 96, 36, 444, 108)  # 输入好友号码
        time.sleep(0.5)
        execute_adb_command(device_id, f'shell input text "{friend_number}"')
        time.sleep(0.5)
        click_coordinates(device_id, 108, 134, 200, 170)  # 选择好友
        time.sleep(0.5)
        click_coordinates(device_id, 432, 852, 516, 936)  # 创建群组
        time.sleep(0.5)
        click_coordinates(device_id, 117, 147, 468, 211)  # 进入创建群组页面
        time.sleep(0.2)
        execute_adb_command(device_id, f'shell input text "{current_group_name}"')
        time.sleep(0.5)
        click_coordinates(device_id, 24, 370, 128, 406)  # 关闭群组权限
        time.sleep(0.1)
        click_coordinates(device_id, 420, 197, 516, 245)
        time.sleep(0.05)
        click_coordinates(device_id, 420, 415, 516, 463)
        execute_adb_command(device_id, "shell input keyevent KEYCODE_BACK")
        time.sleep(0.3)
        click_coordinates(device_id, 432, 852, 516, 936)  # 完成创建
        time.sleep(2)
        click_coordinates(device_id, 216, 81, 336, 83)  # 保存按钮
        time.sleep(1)
        swipe_coordinates(device_id, 200, 800, 200, 100)  # 页面滚动
        time.sleep(0.5)
        swipe_coordinates(device_id, 200, 800, 200, 100)
        time.sleep(0.5)
        click_coordinates(device_id, 108, 765, 212, 801)  # 退出群组
        time.sleep(2)
        click_coordinates(device_id, 358, 548, 454, 620)
        time.sleep(1.5)
        execute_adb_command(device_id, 'shell input keyevent KEYCODE_BACK')
        time.sleep(1)
        execute_adb_command(device_id, 'shell input keyevent KEYCODE_BACK')
        time.sleep(1)
        click_coordinates(device_id, 432, 731, 516, 815)  # 点击保存按钮
        time.sleep(1)
    except Exception as e:
        print(f"Failed to create group: {e}")


def get_emulators():
    """获取所有连接的模拟器设备"""
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        devices = result.stdout.splitlines()[1:]
        emulators = [device.split()[0] for device in devices if device]
        return emulators
    except Exception as e:
        print(f"Failed to get emulators: {e}")
        return []


def on_read_emulators():
    """读取模拟器并更新下拉菜单"""
    emulators = get_emulators()
    emulator_combo['values'] = emulators
    if emulators:
        emulator_combo.set(emulators[0])


def on_create_groups():
    """处理创建群组按钮点击事件"""
    selected_device = emulator_combo.get()
    if not selected_device:
        messagebox.showwarning("Warning", "Please select an emulator.")
        return

    if not group_count_entry.get().isdigit() or not start_number_entry.get().isdigit():
        messagebox.showerror("Error", "Invalid input. Please enter valid positive integers.")
        return

    group_count = int(group_count_entry.get())
    start_number = int(start_number_entry.get())
    group_name = group_name_entry.get()
    friend_number = friend_number_entry.get()

    # 启动后台线程来执行群组创建操作
    global stop_event
    stop_event.clear()
    worker_thread = threading.Thread(target=run_group_creation,
                                     args=(selected_device, group_name, friend_number, start_number))
    worker_thread.start()


def run_group_creation(device_id, group_name, friend_number, start_number):
    """后台线程执行群组创建"""
    group_count = int(group_count_entry.get())
    for i in range(start_number, start_number + group_count):
        if stop_event.is_set():
            break
        create_group(device_id, group_name, friend_number, i)


def on_stop():
    """停止后台线程"""
    stop_event.set()


# GUI 配置
root = tk.Tk()
root.title("WhatsApp 群组创建器")
root.geometry("400x550")  # 调整窗口大小以适应新控件

# 创建框架以组织组件
frame = tk.Frame(root)
frame.pack(pady=10)

# 模拟器选择
tk.Label(frame, text="选择模拟器:").grid(row=0, column=0, padx=5, pady=5)
emulator_var = StringVar()
emulator_combo = ttk.Combobox(frame, textvariable=emulator_var, state="readonly")
emulator_combo.grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame, text="读取模拟器", command=on_read_emulators).grid(row=0, column=2, padx=5, pady=5)

# 群组设置
tk.Label(frame, text="创建群组数量:").grid(row=1, column=0, padx=5, pady=5)
group_count_entry = tk.Entry(frame)
group_count_entry.insert(0, "10")
group_count_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame, text="好友号码:").grid(row=2, column=0, padx=5, pady=5)
friend_number_entry = tk.Entry(frame)
friend_number_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame, text="起始群组名:").grid(row=3, column=0, padx=5, pady=5)
group_name_entry = tk.Entry(frame)
group_name_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Label(frame, text="开始序号:").grid(row=4, column=0, padx=5, pady=5)
start_number_entry = tk.Entry(frame)  # 添加开始序号输入框
start_number_entry.insert(0, "1")
start_number_entry.grid(row=4, column=1, padx=5, pady=5)

# 版本选择
version_var = StringVar(value="个人版")
tk.Label(frame, text="选择版本:").grid(row=5, column=0, padx=5, pady=5)
tk.Radiobutton(frame, text="个人版", variable=version_var, value="个人版", command=lambda: switch_version("个人版")).grid(row=5, column=1, padx=5, pady=5)
tk.Radiobutton(frame, text="商业版", variable=version_var, value="商业版", command=lambda: switch_version("商业版")).grid(row=5, column=2, padx=5, pady=5)

# 按钮操作
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
tk.Button(button_frame, text="开始创建群组", command=on_create_groups).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="停止创建群组", command=on_stop).pack(side=tk.LEFT, padx=5)

# 群组链接显示
tk.Label(root, text="群组链接:").pack(pady=5)
group_links_box = Text(root, width=70, height=15)  # 修改为可复制的 Text
group_links_box.pack(padx=10, pady=5)

# 停止事件用于控制线程
stop_event = threading.Event()

root.mainloop()
