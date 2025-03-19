import tkinter as tk
import uiautomator2 as u2
import threading
import re
import time
import subprocess
import json
import os


class AdminSimulatorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("自动化管理员设置模拟器")

        self.frame = tk.Frame(master)
        self.frame.pack(pady=20, padx=20)

        self.version_var = tk.StringVar(value='business')  # 默认选择商业版
        self.simulators = []
        self.selected_simulator = None
        self.stop_event = threading.Event()

        self.state_file = "processed_groups.json"
        self.processed_groups = set()
        self.load_processed_groups()

        self.last_group_label = tk.Label(self.frame, text="最后设置的群组: 无")
        self.last_group_label.grid(row=0, column=0, columnspan=2, pady=5)

        # 版本选择
        tk.Label(self.frame, text="选择版本:").grid(row=1, column=0, pady=5)
        tk.Radiobutton(self.frame, text="商业版", variable=self.version_var, value='business').grid(row=1, column=1, pady=5)
        tk.Radiobutton(self.frame, text="个人版", variable=self.version_var, value='personal').grid(row=1, column=2, pady=5)

        self.read_button = tk.Button(self.frame, text="读取模拟器", command=self.read_simulators)
        self.read_button.grid(row=2, column=0, pady=5)

        self.simulator_listbox = tk.Listbox(self.frame, selectmode=tk.SINGLE, width=50)
        self.simulator_listbox.grid(row=2, column=1, pady=5)

        self.start_button = tk.Button(self.frame, text="开始执行", command=self.start_execution)
        self.start_button.grid(row=3, column=0, pady=5)

        self.stop_button = tk.Button(self.frame, text="立即停止", command=self.stop_execution)
        self.stop_button.grid(row=3, column=1, pady=5)

        self.reset_button = tk.Button(self.frame, text="重置", command=self.reset)
        self.reset_button.grid(row=4, column=0, pady=5)

        self.status_label = tk.Label(self.frame, text="状态: 未开始")
        self.status_label.grid(row=4, column=1, pady=5)

    def load_processed_groups(self):
        """加载已处理的群组状态"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                self.processed_groups = set(json.load(f))
        else:
            self.processed_groups = set()

    def save_processed_group(self, group_name):
        """将处理的群组名保存到文件"""
        self.processed_groups.add(group_name)
        with open(self.state_file, 'w') as f:
            json.dump(list(self.processed_groups), f)

    def read_simulators(self):
        try:
            result = subprocess.check_output(['adb', 'devices']).decode('utf-8')
            self.simulators = [line.split('\t')[0] for line in result.splitlines() if '\tdevice' in line]
            self.simulator_listbox.delete(0, tk.END)
            for simulator in self.simulators:
                self.simulator_listbox.insert(tk.END, simulator)
        except Exception as e:
            self.status_label.config(text=f"读取模拟器失败: {str(e)}")

    def start_execution(self):
        selected = self.simulator_listbox.curselection()
        if selected:
            self.selected_simulator = self.simulators[selected[0]]
            self.stop_event.clear()
            self.status_label.config(text=f"状态: 正在执行 {self.selected_simulator}")

            # 启动群组监控线程
            threading.Thread(target=self.monitor_groups).start()
        else:
            self.status_label.config(text="请先选择一个模拟器。")

    def stop_execution(self):
        self.stop_event.set()
        self.status_label.config(text="状态: 停止执行")

    def reset(self):
        self.simulators = []
        self.selected_simulator = None
        self.simulator_listbox.delete(0, tk.END)
        self.stop_event.set()
        self.processed_groups.clear()
        self.status_label.config(text="状态: 未开始")
        self.last_group_label.config(text="最后设置的群组: 无")
        if os.path.exists(self.state_file):
            os.remove(self.state_file)

    def monitor_groups(self):
        """持续监测当前页面上的群组是否有新加入的成员并设置管理员"""
        device = u2.connect(self.selected_simulator)
        version_prefix = 'com.whatsapp.w4b' if self.version_var.get() == 'business' else 'com.whatsapp'

        while not self.stop_event.is_set():
            try:
                groups = device(className='android.widget.RelativeLayout',
                                resourceId=f'{version_prefix}:id/contact_row_container')

                if groups.exists:
                    for group in groups:
                        if self.stop_event.is_set():
                            break
                        group_name_element = group.child(
                            resourceId=f'{version_prefix}:id/conversations_row_contact_name')
                        dynamic_info_element = group.child(resourceId=f'{version_prefix}:id/single_msg_tv')

                        if group_name_element.exists and dynamic_info_element.exists:
                            group_name = group_name_element.get_text()

                            if group_name in self.processed_groups:
                                continue

                            dynamic_info = dynamic_info_element.get_text()

                            if "使用了群组邀请链接加入群组" in dynamic_info:
                                number = re.search(r'(\+\d[\d\s\-\(\)]*)', dynamic_info)
                                if number:
                                    self.set_admin(group_name, number.group(0).strip())
                                    self.save_processed_group(group_name)

                    print(f"处理完毕当前页面群组，继续监控...")
                else:
                    print("未找到任何群组，请确保群组列表可见。")

            except Exception as e:
                print(f"监控群组时发生错误: {e}")

            # 暂停1秒后继续监控
            time.sleep(1)

    def set_admin(self, group_name, number):
        device = u2.connect(self.selected_simulator)
        version_prefix = 'com.whatsapp.w4b' if self.version_var.get() == 'business' else 'com.whatsapp'
        print(f"进入群组: {group_name}，设置管理员: {number}")

        try:
            time.sleep(1)
            device(resourceId=f'{version_prefix}:id/conversations_row_contact_name', text=group_name).click()
            time.sleep(1)

            device(resourceId=f'{version_prefix}:id/conversation_contact_status', text='只有管理员可发送消息').click()
            time.sleep(1)

            user_found = False
            while not user_found and not self.stop_event.is_set():
                user_elements = device(className='android.widget.TextView', text=number)
                if user_elements.exists:
                    user_elements.click()
                    user_found = True
                else:
                    device.swipe(0, 300, 0, 0, 0.1)
                    time.sleep(0.4)

            time.sleep(1)

            max_retries = 5
            for attempt in range(max_retries):
                if self.stop_event.is_set():
                    return
                try:
                    device(resourceId='android:id/title', text='选定为群组管理员').click()
                    time.sleep(1)
                    break
                except u2.exceptions.UiObjectNotFoundError:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                    else:
                        print("未能找到'选定为群组管理员'按钮，请检查界面状态。")
                        return

            time.sleep(0.8)
            for _ in range(2):
                if self.stop_event.is_set():
                    return
                device.press('back')
                time.sleep(0.8)

            print(f"已将 {number} 设置为 {group_name} 的管理员")

            self.processed_groups.add(group_name)
            self.last_group_label.config(text=f"最后设置的群组: {group_name}")

        except Exception as e:
            print(f"设置管理员时发生错误: {e}")



# 创建 Tkinter 应用程序窗口
root = tk.Tk()
app = AdminSimulatorApp(root)
root.mainloop()
