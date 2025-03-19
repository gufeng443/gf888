import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pywinauto import Application, Desktop
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.timings import TimeoutError
import threading
import logging

# 配置调试日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsAppAutomationGUI:
    def __init__(self, root):  # 修正这里添加root参数!!!!!!!!!!!!!!!
        self.root = root
        self.root.title("群组管理自动化工具")
        self.root.geometry("800x600")

        # 创建主容器
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 群组列表框架（左侧）
        group_frame = ttk.LabelFrame(main_frame, text="群组列表管理", padding=10)
        group_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # 自动获取按钮
        self.btn_fetch = ttk.Button(group_frame, text="获取群组列表", command=self.start_fetch_thread)
        self.btn_fetch.pack(pady=5)

        # 带滚动条的群组列表面板
        self.canvas = tk.Canvas(group_frame, borderwidth=0)
        scrollbar = ttk.Scrollbar(group_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)

        # 配置画布滚动
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", tags="frame")
        self.scroll_frame.bind("<Configure>", self.on_frame_configure)

        # 初始化群组复选框列表
        self.group_checkboxes = []

        # 自动管理框架（右侧）
        admin_frame = ttk.LabelFrame(main_frame, text="自动管理设置", padding=10)
        admin_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)

        # 管理员号码输入
        lbl_admin = ttk.Label(admin_frame, text="管理员号码（每行一个）:")
        lbl_admin.pack(anchor=tk.W)

        self.admin_input = scrolledtext.ScrolledText(admin_frame, width=30, height=15)
        self.admin_input.pack(pady=5)

        # 执行按钮
        self.btn_execute = ttk.Button(admin_frame, text="执行设置管理员", command=self.set_admins)
        self.btn_execute.pack(pady=10)

    def on_frame_configure(self, event):
        """自动调整画布滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def start_fetch_thread(self):
        """启动获取群组的线程"""
        self.btn_fetch.config(state=tk.DISABLED)
        threading.Thread(target=self.fetch_groups, daemon=True).start()

    def fetch_groups(self):
        """增强版的群组获取功能"""
        try:
            app = Application(backend="uia").connect(title_re="WhatsApp", timeout=10)
            main_window = app.window(title_re="WhatsApp")

            # 定位导航面板中的"对话"标签
            logger.info("尝试定位导航标签...")
            chat_nav_item = main_window.child_window(
                auto_id="ChatsNavigationItem",
                control_type="ListItem"
            )
            chat_nav_item.click_input()

            # 等待群组列表加载完成
            main_window.wait('ready', timeout=5)

            # 定位真正的群组列表容器
            logger.info("尝试定位群组列表容器...")
            group_container = main_window.child_window(
                auto_id="ChatList",
                control_type="List"
            )

            # 验证是否找到有效控件
            if not group_container.exists():
                raise RuntimeError("群组列表容器未找到")

            # 获取所有群组项
            items = group_container.children(control_type="ListItem")
            logger.info(f"找到 {len(items)} 个列表项")

            groups = []
            for i, item in enumerate(items, 1):
                try:
                    name = item.window_text().strip()
                    if name and name not in ["状态", "新社区", "频道"]:
                        groups.append(name)
                except Exception as e:
                    logger.error(f"处理群组项时出错: {str(e)}")

            # 验证结果
            if not groups:
                logger.warning("获取到空群组列表")
                self.root.after(0, lambda: messagebox.showwarning(
                    "警告", "成功获取列表但未发现有效群组"
                ))

            self.root.after(0, self.update_group_list, groups)

        except ElementNotFoundError:
            logger.error("WhatsApp窗口未找到")
            self.root.after(0, messagebox.showerror,
                            "连接错误", "请确保WhatsApp窗口已打开并处于前台")
        except TimeoutError as te:
            logger.error(f"操作超时: {str(te)}")
            self.root.after(0, messagebox.showerror,
                            "超时错误", "窗口响应超时，请检查网络连接")
        except Exception as e:
            logger.exception("未处理的异常:")
            self.root.after(0, messagebox.showerror,
                            "系统错误", f"发生未预期错误：{str(e)}")
        finally:
            self.root.after(0, lambda: self.btn_fetch.config(state=tk.NORMAL))

    def update_group_list(self, groups):
        """更新群组列表显示"""
        for cb in self.group_checkboxes:
            cb[0].destroy()
        self.group_checkboxes.clear()

        for group in groups:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(
                self.scroll_frame,
                text=group,
                variable=var,
                style='TCheckbutton'
            )
            cb.pack(anchor=tk.W, pady=2)
            self.group_checkboxes.append((cb, var, group))

    def set_admins(self):
        """执行管理员设置操作"""
        selected_groups = [
            group for (cb, var, group) in self.group_checkboxes if var.get()
        ]
        admin_numbers = self.admin_input.get("1.0", tk.END).strip().split('\n')

        # 输入验证
        if not selected_groups:
            messagebox.showwarning("警告", "请至少选择一个群组")
            return

        if not any(num.strip() for num in admin_numbers):
            messagebox.showwarning("警告", "至少输入一个有效的管理员号码")
            return

        # 确认对话框
        confirm = messagebox.askyesno(
            "确认操作",
            f"将在以下{len(selected_groups)}个群组设置管理员：\n"
            f"{', '.join(selected_groups)}\n"
            f"管理员号码：{', '.join(admin_numbers)}\n\n"
            "请确认是否继续？"
        )

        if confirm:
            messagebox.showinfo("提示", "开始执行自动化操作...")
            # 后续添加实际自动化代码


if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppAutomationGUI(root)  # 现在这里可以正确传递root参数
    root.mainloop()
