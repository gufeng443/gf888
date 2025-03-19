import subprocess
import uiautomator2 as u2
import tkinter as tk
from tkinter import messagebox, StringVar, IntVar, Text
import time
import threading

# 全局变量用于控制线程
stop_thread = False
current_version_prefix = "com.whatsapp"  # 默认是个人版

def read_emulators():
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        devices = [line.split()[0] for line in result.stdout.splitlines() if line and 'device' in line]

        if devices:
            emulator_var.set(devices[0])
            update_emulator_menu(devices)
        else:
            messagebox.showwarning("警告", "没有找到已连接的模拟器或设备！")

    except Exception as e:
        messagebox.showerror("错误", str(e))

def update_emulator_menu(devices):
    menu = emulator_menu["menu"]
    menu.delete(0, "end")
    for device in devices:
        menu.add_command(label=device, command=lambda value=device: emulator_var.set(value))

def wait_for_element(d, text=None, resourceId=None, timeout=5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if resourceId and d(resourceId=resourceId).exists:
            return True
        if text and d(text=text).exists:
            return True
        time.sleep(0.1)
    return False

def create_groups():
    global stop_thread, current_version_prefix
    try:
        d = u2.connect(emulator_var.get())
        num_groups = num_groups_var.get()
        friend_number = friend_number_var.get()
        initial_group_name = int(group_name_var.get())
        group_prefix = group_prefix_var.get().strip()  # 获取群名称前缀

        for i in range(num_groups):
            if stop_thread:  # 检查是否需要停止
                messagebox.showinfo("停止", "群组创建已停止！")
                return

            group_name = f"{group_prefix}-{initial_group_name + i}" if group_prefix else str(initial_group_name + i)  # 生成群组名

            wait_for_element(d, "新建群组")
            d(text="新建群组").click()
            time.sleep(0.3)
            d(resourceId=f"{current_version_prefix}:id/menuitem_search").click()

            time.sleep(0.3)
            d(resourceId=f"{current_version_prefix}:id/search_src_text").set_text(friend_number)

            time.sleep(0.3)
            d(resourceId=f"{current_version_prefix}:id/chat_able_contacts_row_name").click()

            time.sleep(0.6)
            d(resourceId=f"{current_version_prefix}:id/next_btn").click()

            wait_for_element(d, "群组名称（可选）")
            d(resourceId=f"{current_version_prefix}:id/group_name").set_text(group_name)
            time.sleep(0.3)
            wait_for_element(d, "群组权限")
            group_permission_element = d(text="群组权限")
            if group_permission_element.exists:
                group_permission_element.click()
            else:
                messagebox.showerror("错误", "未找到群组权限选项！")
                return

            wait_for_element(d, "发送消息")
            d(resourceId=f"{current_version_prefix}:id/edit_group_settings_switch").click()
            time.sleep(0.2)
            d(resourceId=f"{current_version_prefix}:id/send_messages_switch").click()
            time.sleep(0.2)
            d.press("back")
            time.sleep(0.2)
            d(resourceId=f"{current_version_prefix}:id/ok_btn").click()
            time.sleep(0.5)

            d(resourceId=f"{current_version_prefix}:id/conversation_contact_status").click()

            user_found = False
            while not user_found:
                invite_elements = d(className='android.widget.TextView', text="经由链接邀请")
                if invite_elements.exists:
                    invite_elements.click()
                    user_found = True
                else:
                    d.swipe(0, 600, 0, 0, 0.03)
                    time.sleep(1)

            time.sleep(1.5)

            group_link = d(resourceId=f"{current_version_prefix}:id/link").get_text()
            group_links_box.insert(tk.END, f"{group_name}: {group_link}\n")  # 添加换行符

            d.press("back")
            user_found = False
            while not user_found:
                invite_elements = d(className='android.widget.TextView', text=friend_number)
                if invite_elements.exists:
                    invite_elements.click()
                    user_found = True
                else:
                    d.swipe(0, 300, 0, 0, 0.1)
                    time.sleep(0.4)

            wait_for_element(d, "选定为群组管理员")
            d(text="选定为群组管理员").click()

            time.sleep(1.7)
            d.press("back")
            time.sleep(0.6)
            d.press("back")
            time.sleep(0.3)

            d(resourceId=f"{current_version_prefix}:id/fab").click()

        messagebox.showinfo("完成", "群组创建完成！")

    except Exception as e:
        messagebox.showerror("错误", str(e))

def start_group_creation_thread():
    global stop_thread
    stop_thread = False  # 重置停止标志
    threading.Thread(target=create_groups).start()

def stop_group_creation():
    global stop_thread
    stop_thread = True  # 设置停止标志

def switch_version(version):
    global current_version_prefix
    current_version_prefix = "com.whatsapp.w4b" if version == "商业版" else "com.whatsapp"

# GUI Setup
root = tk.Tk()
root.title("WhatsApp 群组创建器")
root.geometry("400x550")  # 调整窗口大小以适应新控件

# 创建框架以组织组件
frame = tk.Frame(root)
frame.pack(pady=10)

# 模拟器选择
tk.Label(frame, text="选择模拟器:").grid(row=0, column=0, padx=5, pady=5)
emulator_var = StringVar()
emulator_menu = tk.OptionMenu(frame, emulator_var, "")
emulator_menu.grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame, text="读取模拟器", command=read_emulators).grid(row=0, column=2, padx=5, pady=5)

# 群组设置
tk.Label(frame, text="创建群组数量:").grid(row=1, column=0, padx=5, pady=5)
num_groups_var = IntVar(value=50)
tk.Entry(frame, textvariable=num_groups_var).grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame, text="好友号码:").grid(row=2, column=0, padx=5, pady=5)
friend_number_var = StringVar()
tk.Entry(frame, textvariable=friend_number_var).grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame, text="起始群组名:").grid(row=3, column=0, padx=5, pady=5)
group_name_var = StringVar(value="1")
tk.Entry(frame, textvariable=group_name_var).grid(row=3, column=1, padx=5, pady=5)

# 群名称前缀
tk.Label(frame, text="群名称前缀:").grid(row=4, column=0, padx=5, pady=5)
group_prefix_var = StringVar()
tk.Entry(frame, textvariable=group_prefix_var).grid(row=4, column=1, padx=5, pady=5)

# 版本选择
version_var = StringVar(value="个人版")
tk.Label(frame, text="选择版本:").grid(row=5, column=0, padx=5, pady=5)
tk.Radiobutton(frame, text="个人版", variable=version_var, value="个人版", command=lambda: switch_version("个人版")).grid(row=5, column=1, padx=5, pady=5)
tk.Radiobutton(frame, text="商业版", variable=version_var, value="商业版", command=lambda: switch_version("商业版")).grid(row=5, column=2, padx=5, pady=5)

# 按钮操作
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
tk.Button(button_frame, text="开始创建群组", command=start_group_creation_thread).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="停止创建群组", command=stop_group_creation).pack(side=tk.LEFT, padx=5)

# 群组链接显示
tk.Label(root, text="群组链接:").pack(pady=5)
group_links_box = Text(root, width=70, height=15)  # 修改为可复制的 Text
group_links_box.pack(padx=10, pady=5)

root.mainloop()
