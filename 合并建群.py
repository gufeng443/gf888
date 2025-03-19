import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, StringVar, IntVar, Text
import threading
import time

# 全局变量
current_creator = None

# 基础函数
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

# GUI设置
root = tk.Tk()
root.title("群组创建工具")
root.geometry("400x620")

# 模拟器选择
tk.Label(root, text="选择模拟器:").pack(pady=5)
emulator_var = StringVar()
emulator_menu = tk.OptionMenu(root, emulator_var, "")
emulator_menu.pack(pady=5)
tk.Button(root, text="读取模拟器", command=read_emulators).pack(pady=10)

# 群组链接显示
tk.Label(root, text="群组链接:").pack(pady=5)
group_links_box = Text(root, height=15, width=50)
group_links_box.pack(pady=10)

# 切换按钮
def switch_to_normal():
    global current_creator
    if current_creator:
        current_creator.stop()
    current_creator = NormalGroupCreator(root, emulator_var, group_links_box)

def switch_to_community():
    global current_creator
    if current_creator:
        current_creator.stop()
    current_creator = CommunityGroupCreator(root, emulator_var, group_links_box)

# 切换按钮
tk.Button(root, text="普通群组创建器", command=switch_to_normal).pack(pady=5)
tk.Button(root, text="社群群组创建器", command=switch_to_community).pack(pady=5)

root.mainloop()


class NormalGroupCreator:
    def __init__(self, master, emulator_var, group_links_box):
        self.master = master
        self.emulator_var = emulator_var
        self.group_links_box = group_links_box
        self.stop_event = threading.Event()
        self.setup_ui()

    def setup_ui(self):
        self.frame = tk.Frame(self.master)
        self.frame.pack(pady=10)

        # 群组设置
        tk.Label(self.frame, text="创建群组数量:").grid(row=0, column=0, padx=5, pady=5)
        self.num_groups_var = IntVar(value=1)
        tk.Entry(self.frame, textvariable=self.num_groups_var).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.frame, text="好友号码:").grid(row=1, column=0, padx=5, pady=5)
        self.friend_number_var = StringVar()
        tk.Entry(self.frame, textvariable=self.friend_number_var).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.frame, text="起始群组名:").grid(row=2, column=0, padx=5, pady=5)
        self.group_name_var = StringVar(value="1")
        tk.Entry(self.frame, textvariable=self.group_name_var).grid(row=2, column=1, padx=5, pady=5)

        # 按钮
        tk.Button(self.frame, text="开始创建群组", command=self.start_creation_thread).grid(row=3, column=0, padx=5,
                                                                                            pady=5)
        tk.Button(self.frame, text="停止创建群组", command=self.stop_creation).grid(row=3, column=1, padx=5, pady=5)

    def start_creation_thread(self):
        self.stop_event.clear()
        threading.Thread(target=self.create_groups).start()

    def stop_creation(self):
        self.stop_event.set()

    def create_groups():
        global stop_thread, current_version_prefix
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
                d(resourceId=f"{current_version_prefix}:id/menuitem_search").click()

                time.sleep(0.2)
                d(resourceId=f"{current_version_prefix}:id/search_src_text").set_text(friend_number)

                time.sleep(0.2)
                d(resourceId=f"{current_version_prefix}:id/chat_able_contacts_row_name").click()

                time.sleep(0.2)
                d(resourceId=f"{current_version_prefix}:id/next_btn").click()

                wait_for_element(d, "群组名称（可选）")
                d(resourceId=f"{current_version_prefix}:id/group_name").set_text(group_name)
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
                d(resourceId=f"{current_version_prefix}:id/edit_group_settings_switch").click()
                time.sleep(0.2)
                d(resourceId=f"{current_version_prefix}:id/send_messages_switch").click()

                d.press("back")

                d(resourceId=f"{current_version_prefix}:id/ok_btn").click()
                time.sleep(1.5)
                wait_for_element(d, "只有管理员可发送消息")
                d(resourceId=f"{current_version_prefix}:id/conversation_contact_status").click()

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

                group_link = d(resourceId=f"{current_version_prefix}:id/link").get_text()
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

                    user_elements = d(resourceId=f"{current_version_prefix}:id/name")

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

                d(resourceId=f"{current_version_prefix}:id/fab").click()

            messagebox.showinfo("完成", "群组创建完成！")

        except Exception as e:
            messagebox.showerror("错误", str(e))

    def stop(self):
        self.stop_event.set()
        self.frame.destroy()
#社群
class CommunityGroupCreator:
    def __init__(self, master, emulator_var, group_links_box):
        self.master = master
        self.emulator_var = emulator_var
        self.group_links_box = group_links_box
        self.stop_event = threading.Event()
        self.setup_ui()

    def setup_ui(self):
        self.frame = tk.Frame(self.master)
        self.frame.pack(pady=10)

        # 群组设置
        tk.Label(self.frame, text="需要建几个社群:").grid(row=0, column=0, padx=5, pady=5)
        self.group_count_var = IntVar(value=1)
        tk.Entry(self.frame, textvariable=self.group_count_var).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.frame, text="社群名称起始数字:").grid(row=1, column=0, padx=5, pady=5)
        self.start_number_var = IntVar(value=1)
        tk.Entry(self.frame, textvariable=self.start_number_var).grid(row=1, column=1, padx=5, pady=5)

        # 是否打开发送消息的选项框
        self.send_message_var = tk.BooleanVar()
        send_message_check = tk.Checkbutton(self.frame, text="是否打开发送消息", variable=self.send_message_var)
        send_message_check.grid(row=2, columnspan=2, padx=5, pady=10)

        # 按钮
        tk.Button(self.frame, text="开始创建社群", command=self.start_creation_thread).grid(row=3, column=0, padx=5, pady=5)
        tk.Button(self.frame, text="停止创建社群", command=self.stop_creation).grid(row=3, column=1, padx=5, pady=5)

    def start_creation_thread(self):
        self.stop_event.clear()
        threading.Thread(target=self.create_groups).start()

    def stop_creation(self):
        self.stop_event.set()

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

    def stop(self):
        self.stop_event.set()
        self.frame.destroy()

# 启动主循环
if __name__ == "__main__":
    root.mainloop()
