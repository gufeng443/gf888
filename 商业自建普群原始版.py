import subprocess
import uiautomator2 as u2
import tkinter as tk
from tkinter import messagebox, StringVar, IntVar, Text
import time
import threading

# 全局变量用于控制线程
stop_thread = False

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
    global stop_thread
    try:
        d = u2.connect(emulator_var.get())
        num_groups = num_groups_var.get()
        friend_number = friend_number_var.get()
        initial_group_name = int(group_name_var.get())

        for i in range(num_groups):
            if stop_thread:  # 检查是否需要停止
                messagebox.showinfo("停止", "群组创建已停止！")
                return

            group_name = str(initial_group_name + i)  # 根据输入的数字生成群组名
            wait_for_element(d, "新建群组")
            d(text="新建群组").click()
            time.sleep(0.1)
            d(resourceId="com.whatsapp.w4b:id/menuitem_search").click()

            time.sleep(0.2)
            d(resourceId="com.whatsapp.w4b:id/search_src_text").set_text(friend_number)

            time.sleep(0.2)
            d(resourceId="com.whatsapp.w4b:id/chat_able_contacts_row_name").click()

            time.sleep(0.2)
            d(resourceId="com.whatsapp.w4b:id/next_btn").click()

            wait_for_element(d, "群组名称（可选）")
            d(resourceId="com.whatsapp.w4b:id/group_name").set_text(group_name)
            time.sleep(0.2)
            wait_for_element(d, "群组权限")
            # 点击群组权限文字位置
            group_permission_element = d(text="群组权限")
            if group_permission_element.exists:
                group_permission_element.click()
            else:
                messagebox.showerror("错误", "未找到群组权限选项！")
                return

            wait_for_element(d, "发送消息")
            d(resourceId="com.whatsapp.w4b:id/edit_group_settings_switch").click()
            time.sleep(0.2)
            d(resourceId="com.whatsapp.w4b:id/send_messages_switch").click()

            d.press("back")

            d(resourceId="com.whatsapp.w4b:id/ok_btn").click()
            time.sleep(1.5)
            wait_for_element(d, "只有管理员可发送消息")
            d(resourceId="com.whatsapp.w4b:id/conversation_contact_status").click()

            # 向下滑动并找到“经由链接邀请”
            user_found = False
            while not user_found:
                invite_elements = d(className='android.widget.TextView', text="经由链接邀请")
                if invite_elements.exists:
                    invite_elements.click()
                    user_found = True
                else:
                    d.swipe(0, 300, 0, 0, 0.1)
                    time.sleep(0.5)

            time.sleep(1.5)

            group_link = d(resourceId="com.whatsapp.w4b:id/link").get_text()
            group_links_box.insert(tk.END, f"{group_name}: {group_link}\n")  # 添加换行符


            # 返回上一页面
            d.press("back")

            # 向下滑动直到找到“群组名称”元素
            while not d(text="退出群组").exists:
                d.swipe(0.5, 0.8, 0.5, 0.2, 0.02)
                time.sleep(0.3)

            # 向下滑动直到找到“群组名称”元素
            user_found = False
            while not user_found:
                d.swipe(0.5, 0.8, 0.5, 0.2, 0.02)
                time.sleep(0.3)

                user_elements = d(resourceId="com.whatsapp.w4b:id/name")

                count = 0
                for user in user_elements:
                    if count == 1:  # 点击第二个元素
                        user.click()
                        user_found = True
                        break
                    count += 1

            # 等待“选定为群组管理员”元素出现
            wait_for_element(d, "选定为群组管理员")

            # 点击“选定为群组管理员”
            d(text="选定为群组管理员").click()

            time.sleep(1.5)
            d.press("back")
            time.sleep(0.5)
            d.press("back")
            time.sleep(0.3)

            d(resourceId="com.whatsapp.w4b:id/fab").click()

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

# GUI Setup
root = tk.Tk()
root.title("WhatsApp 群组创建器")

emulator_var = StringVar()
num_groups_var = IntVar(value=45)  # 默认创建群组数量为45
friend_number_var = StringVar()
group_name_var = StringVar(value="1")  # 默认起始群组名为1

tk.Label(root, text="选择模拟器:").pack()
emulator_menu = tk.OptionMenu(root, emulator_var, "")
emulator_menu.pack()
tk.Button(root, text="读取模拟器", command=read_emulators).pack()

tk.Label(root, text="创建群组数量:").pack()
tk.Entry(root, textvariable=num_groups_var).pack()

tk.Label(root, text="好友号码:").pack()
tk.Entry(root, textvariable=friend_number_var).pack()

tk.Label(root, text="起始群组名:").pack()  # 修改标签
tk.Entry(root, textvariable=group_name_var).pack()

tk.Button(root, text="开始创建群组", command=start_group_creation_thread).pack()
tk.Button(root, text="停止创建群组", command=stop_group_creation).pack()  # 修改停止按钮功能

tk.Label(root, text="群组链接:").pack()
group_links_box = Text(root, width=70, height=20)  # 修改为可复制的 Text
group_links_box.pack()

root.mainloop()
