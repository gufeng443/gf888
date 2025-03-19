from pywinauto import Application
import uiautomation as auto
import tkinter as tk
from tkinter import ttk, messagebox
import time


class WhatsAppAutomator:
    def __init__(self):
        try:
            # 连接到Electron主窗口
            self.app = Application(backend="uia").connect(class_name="Chrome_WidgetWin_0")
            self.window = self.app.window(class_name="Chrome_WidgetWin_0")
        except Exception as e:
            messagebox.showerror("错误", f"无法连接到WhatsApp: {str(e)}")
            raise

    def safe_click(self, element, retries=3):
        """带重试机制的点击"""
        for _ in range(retries):
            try:
                element.click_input()
                return True
            except Exception:
                time.sleep(1)
        return False

    def get_groups(self):
        """获取群组列表优化版"""
        try:
            # 定位到消息列表区域
            main_pane = self.window.child_window(
                class_name="Chrome_WidgetWin_0",
                control_type="Pane"
            )

            # 等待控件加载
            scroll_view = main_pane.wait('exists', timeout=10).child_window(
                control_type="ScrollViewer",
                found_index=0
            )

            # 提取有效群组
            groups = []
            for item in scroll_view.children(control_type="ListItem"):
                name = item.name.replace('\n', ' ').strip()
                if any(keyword in name for keyword in ["群组", "Group", "多人"]):
                    groups.append(name.split(' ')[0])  # 提取群组名称
            return sorted(list(set(groups)))  # 去重排序

        except Exception as e:
            messagebox.showwarning("警告", f"获取群组失败: {str(e)}")
            return []

    def set_admin(self, group_name, numbers):
        """管理员设置优化流程"""
        try:
            # 定位目标群组
            target_group = None
            scroll_view = self.window.child_window(
                control_type="ScrollViewer",
                found_index=0
            )

            for item in scroll_view.children(control_type="ListItem"):
                if group_name in item.name:
                    target_group = item
                    break

            if not target_group:
                raise ValueError("群组不存在")

            # 打开群组设置
            self.safe_click(target_group)
            auto.SendKeys("{ENTER}", waitTime=1)  # 打开聊天窗口

            # 打开群信息
            auto.SendKeys("^i")  # Ctrl+I 快捷键
            time.sleep(2)

            # 定位到管理员设置区域
            info_window = self.app.window(title_re=".*群组信息|Group Info.*")
            members_list = info_window.child_window(
                control_type="List",
                found_index=0
            )

            # 设置管理员
            success_count = 0
            for num in numbers:
                # 搜索成员
                search_box = info_window.child_window(
                    control_type="Edit",
                    found_index=0
                )
                search_box.set_edit_text(num)
                time.sleep(1)

                # 选中成员
                member_items = members_list.children(control_type="ListItem")
                if not member_items:
                    continue

                # 右键菜单操作
                self.safe_click(member_items[0], retries=2)
                auto.RightClick(x=member_items[0].rectangle().left + 10,
                                y=member_items[0].rectangle().top + 10)
                time.sleep(0.5)

                # 选择设置管理员
                menu_item = auto.MenuItemControl(searchDepth=1, Name="设为管理员")
                if menu_item.Exists():
                    menu_item.Click()
                    success_count += 1
                    time.sleep(1)

            return success_count

        except Exception as e:
            messagebox.showerror("错误", f"设置失败: {str(e)}")
            return 0


class WhatsAppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WhatsApp Admin Manager v2.0")
        self.geometry("600x400")
        self.automator = None
        self.create_widgets()

    def create_widgets(self):
        # 连接状态提示
        self.status_label = ttk.Label(self, text="未连接")
        self.status_label.pack(pady=5)

        # 连接按钮
        ttk.Button(self, text="连接到WhatsApp",
                   command=self.connect_app).pack()

        # 群组列表
        self.group_frame = ttk.LabelFrame(self, text="群组列表")
        self.group_listbox = tk.Listbox(self.group_frame, width=50, height=10)
        self.group_listbox.pack(padx=10, pady=5)
        self.group_frame.pack(pady=10, fill="both", expand=True)

        # 号码输入
        self.num_frame = ttk.LabelFrame(self, text="管理员号码（每行一个）")
        self.num_text = tk.Text(self.num_frame, height=4)
        self.num_text.pack(padx=10, pady=5)
        self.num_frame.pack(pady=5, fill="x")

        # 操作按钮
        btn_frame = ttk.Frame(self)
        ttk.Button(btn_frame, text="刷新群组",
                   command=self.load_groups).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="设置管理员",
                   command=self.run_setting).pack(side="left", padx=5)
        btn_frame.pack(pady=10)

    def connect_app(self):
        try:
            self.automator = WhatsAppAutomator()
            self.status_label.config(text="已连接", foreground="green")
            self.load_groups()
        except:
            self.status_label.config(text="连接失败", foreground="red")

    def load_groups(self):
        if self.automator:
            groups = self.automator.get_groups()
            self.group_listbox.delete(0, tk.END)
            for g in groups:
                self.group_listbox.insert(tk.END, g)

    def run_setting(self):
        if not self.automator:
            return

        selected = self.group_listbox.curselection()
        if not selected:
            messagebox.showwarning("提示", "请先选择群组")
            return

        numbers = self.num_text.get("1.0", tk.END).splitlines()
        valid_numbers = [n.strip() for n in numbers if n.strip()]

        if not valid_numbers:
            messagebox.showwarning("提示", "请输入有效号码")
            return

        group_name = self.group_listbox.get(selected[0])

        # 确认对话框
        confirm = messagebox.askyesno("确认",
                                      f"将在群组【{group_name}】中设置 {len(valid_numbers)} 个管理员，继续？")
        if not confirm:
            return

        success = self.automator.set_admin(group_name, valid_numbers)
        messagebox.showinfo("完成",
                            f"成功设置 {success}/{len(valid_numbers)} 个管理员")


if __name__ == "__main__":
    app = WhatsAppGUI()
    app.mainloop()