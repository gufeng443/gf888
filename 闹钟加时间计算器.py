import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import Calendar
import threading
import time
from datetime import datetime, timedelta
import pygame
from tkinter.filedialog import askopenfilename
import urllib.request
import os
from tkinter import simpledialog


class AlarmClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("定时备忘和闹钟程序")
        self.root.geometry("800x600")

        # 初始化pygame
        pygame.mixer.init()

        self.alarms = []  # 存储闹钟信息
        self.selected_sound = None  # 选中的铃声
        self.create_widgets()

    def create_widgets(self):
        # 选择日期
        self.date_label = tk.Label(self.root, text="选择日期:", font=("微软雅黑", 12))
        self.date_label.pack(pady=5)

        self.calendar = Calendar(self.root, date_pattern="yyyy-mm-dd", font=("微软雅黑", 10))
        self.calendar.pack(pady=5)

        # 选择时间
        self.time_label = tk.Label(self.root, text="选择时间:", font=("微软雅黑", 12))
        self.time_label.pack(pady=5)

        self.time_frame = tk.Frame(self.root)
        self.time_frame.pack(pady=5)

        self.hours = ttk.Combobox(self.time_frame, values=[f"{i:02d}" for i in range(24)], width=4,
                                  font=("微软雅黑", 10))
        self.hours.set("00")
        self.hours.grid(row=0, column=0)

        self.minutes = ttk.Combobox(self.time_frame, values=[f"{i:02d}" for i in range(60)], width=4,
                                    font=("微软雅黑", 10))
        self.minutes.set("00")
        self.minutes.grid(row=0, column=1)

        # 备忘信息输入框
        self.reminder_label = tk.Label(self.root, text="输入闹钟提醒信息:", font=("微软雅黑", 12))
        self.reminder_label.pack(pady=5)

        self.reminder_text = tk.Entry(self.root, width=40, font=("微软雅黑", 10))
        self.reminder_text.pack(pady=5)

        # 设置铃声按钮
        self.sound_button = tk.Button(self.root, text="选择铃声", command=self.select_sound, font=("微软雅黑", 12))
        self.sound_button.pack(pady=10)

        # 添加闹钟按钮
        self.add_alarm_button = tk.Button(self.root, text="添加闹钟", command=self.add_alarm, font=("微软雅黑", 12))
        self.add_alarm_button.pack(pady=10)

        # 启动时间计算器按钮
        self.time_calculator_button = tk.Button(self.root, text="启动时间计算器", command=self.open_time_calculator,
                                                font=("微软雅黑", 12))
        self.time_calculator_button.pack(pady=10)

        # 闹钟列表显示区域
        self.alarms_list_label = tk.Label(self.root, text="已设置的闹钟:", font=("微软雅黑", 12))
        self.alarms_list_label.pack(pady=5)

        self.alarms_listbox = tk.Listbox(self.root, width=50, height=10, font=("微软雅黑", 10))
        self.alarms_listbox.pack(pady=5)

    def select_sound(self):
        # 弹出选择框让用户选择铃声来源：本地文件或在线链接
        choice = messagebox.askquestion("选择铃声", "选择铃声文件还是提供链接？\n\n按‘是’选择文件，按‘否’提供链接。")

        if choice == 'yes':
            # 本地音频文件选择
            filename = askopenfilename(title="选择铃声文件", filetypes=[("音频文件", "*.mp3;*.wav")])
            if filename:
                self.selected_sound = filename
        else:
            # 在线音频链接输入
            self.selected_sound = simpledialog.askstring("输入音频链接", "请输入音频链接（.mp3）:")

    def add_alarm(self):
        # 获取日期、时间和提醒信息
        selected_date = self.calendar.get_date()
        selected_time = f"{self.hours.get()}:{self.minutes.get()}"
        reminder_message = self.reminder_text.get()

        # 将日期和时间组合成完整的时间戳
        alarm_time_str = f"{selected_date} {selected_time}"
        alarm_time = datetime.strptime(alarm_time_str, "%Y-%m-%d %H:%M")

        if reminder_message:
            # 将闹钟添加到列表
            self.alarms.append((alarm_time, reminder_message, self.selected_sound))
            self.alarms_listbox.insert(tk.END,
                                       f"时间: {alarm_time.strftime('%Y-%m-%d %H:%M')} - 提醒: {reminder_message}")

            # 启动定时检查线程
            threading.Thread(target=self.check_alarms, daemon=True).start()

        else:
            messagebox.showwarning("输入错误", "请输入闹钟提醒信息！")

    def check_alarms(self):
        while True:
            now = datetime.now()
            print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M')}")

            # 遍历闹钟，检查是否到达提醒时间
            for alarm_time, message, sound in self.alarms:
                if now >= alarm_time:
                    print(f"触发闹钟: {alarm_time.strftime('%Y-%m-%d %H:%M')}")
                    self.show_alarm_message(message, sound)
                    self.alarms.remove((alarm_time, message, sound))  # 移除已触发的闹钟
                    self.alarms_listbox.delete(0, tk.END)
                    for alarm_time, message, sound in self.alarms:
                        self.alarms_listbox.insert(tk.END,
                                                   f"时间: {alarm_time.strftime('%Y-%m-%d %H:%M')} - 提醒: {message}")
            time.sleep(60)  # 每分钟检查一次

    def show_alarm_message(self, message, sound):
        # 创建新的Toplevel窗口作为提醒
        alarm_window = tk.Toplevel(self.root)
        alarm_window.title("闹钟提醒")
        alarm_window.geometry("400x200")
        alarm_window.attributes('-topmost', 1)  # 窗口置顶
        alarm_window.config(bg="#ffdddd")

        # 提醒信息标签
        reminder_label = tk.Label(alarm_window, text=message, font=("微软雅黑", 16), fg="red", bg="#ffdddd")
        reminder_label.pack(pady=20)

        # 播放铃声（支持本地和在线）
        if sound:
            if sound.startswith("http"):  # 检测是否是 URL 链接
                try:
                    self.play_online_sound(sound)
                except Exception as e:
                    print(f"播放在线铃声失败: {e}")
            else:
                try:
                    pygame.mixer.music.load(sound)  # 加载本地文件
                    pygame.mixer.music.play()
                    print(f"正在播放铃声: {sound}")
                except Exception as e:
                    print(f"播放本地铃声失败: {e}")
        else:
            print("没有选择铃声文件！")

        # 设置窗口关闭时停止音频
        alarm_window.protocol("WM_DELETE_WINDOW", lambda: self.stop_audio_and_close(alarm_window))

    def stop_audio_and_close(self, alarm_window):
        # 停止播放铃声
        pygame.mixer.music.stop()
        print("停止铃声播放")

        # 关闭提醒窗口
        alarm_window.destroy()

    def play_online_sound(self, url):
        # 下载音频并临时保存后播放
        local_filename = "temp_audio.mp3"
        urllib.request.urlretrieve(url, local_filename)
        pygame.mixer.music.load(local_filename)
        pygame.mixer.music.play()

    def open_time_calculator(self):
        # 打开时间计算器窗口
        TimeCalculatorWindow(self.root)


# 时间计算器窗口
class TimeCalculatorWindow:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("时间计算器")
        self.top.geometry("400x300")

        # 初始化当前时间
        self.current_time = datetime.now()

        # 显示当前时间
        self.time_label = tk.Label(self.top, text=f"当前时间: {self.current_time.strftime('%Y-%m-%d %H:%M')}",
                                   font=("微软雅黑", 12))
        self.time_label.pack(pady=20)

        # 输入框：添加或减少小时数
        self.input_label = tk.Label(self.top, text="请输入要加上或减去的小时数：", font=("微软雅黑", 12))
        self.input_label.pack(pady=10)

        self.hours_input = tk.Entry(self.top, font=("微软雅黑", 12))
        self.hours_input.pack(pady=5)

        # 计算按钮
        self.calculate_button = tk.Button(self.top, text="计算时间", command=self.calculate_time, font=("微软雅黑", 12))
        self.calculate_button.pack(pady=10)

        # 显示计算结果
        self.result_label = tk.Label(self.top, text="新的时间将显示在这里", font=("微软雅黑", 12))
        self.result_label.pack(pady=20)

    def calculate_time(self):
        user_input = self.hours_input.get()

        # 尝试将输入的小时数转换为整数
        try:
            hours_to_add = int(user_input)
            new_time = self.add_hours_to_time(self.current_time, hours_to_add)
            self.result_label.config(text=f"新的时间是: {new_time.strftime('%Y-%m-%d %H:%M')}")
        except ValueError:
            messagebox.showerror("无效输入", "请输入有效的数字！")

    def add_hours_to_time(self, current_time, hours):
        # 使用 timedelta 添加小时
        new_time = current_time + timedelta(hours=hours)
        # 只保留到小时，四舍五入
        new_time_rounded = new_time.replace(minute=0, second=0, microsecond=0)
        return new_time_rounded


# 启动应用
def main():
    root = tk.Tk()
    app = AlarmClockApp(root)
    root.mainloop()  # 确保在主循环中


if __name__ == "__main__":
    main()
