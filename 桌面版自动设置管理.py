import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError
import threading
import logging
import time

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("whatsapp_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WhatsAppManager:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp智能助手 v4.3")
        self.root.geometry("920x720")
        self.is_running = False
        self.app = None
        self.create_interface()
        self.bind_events()

    def create_interface(self):
        """创建程序界面"""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧：群组面板
        group_frame = ttk.LabelFrame(main_frame, text="群组管理", padding=10)
        group_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 操作按钮
        self.btn_load = ttk.Button(group_frame, text="加载群组", command=self.start_loading)
        self.btn_load.pack(pady=5)

        # 群组列表框
        self.group_list = tk.Listbox(group_frame, selectmode=tk.MULTIPLE, height=20)
        scroll_y = ttk.Scrollbar(group_frame, orient=tk.VERTICAL, command=self.group_list.yview)
        self.group_list.configure(yscrollcommand=scroll_y.set)
        self.group_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # 右侧：管理面板
        admin_frame = ttk.LabelFrame(main_frame, text="管理员配置", padding=10)
        admin_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # 管理员输入框
        ttk.Label(admin_frame, text="管理员号码（每行一个）:").pack(anchor=tk.W)
        self.txt_admins = scrolledtext.ScrolledText(admin_frame, width=30, height=15)
        self.txt_admins.pack(pady=5)

        # 操作按钮
        self.btn_setup = ttk.Button(admin_frame, text="应用设置", command=self.start_setup)
        self.btn_setup.pack(pady=10)

        # 状态栏
        self.status = ttk.Label(self.root, text="就绪")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def bind_events(self):
        """绑定事件处理"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_loading(self):
        """启动加载线程"""
        if not self.is_running:
            self.is_running = True
            self.btn_load.config(state=tk.DISABLED)
            self.status.config(text="正在加载群组...")
            threading.Thread(target=self.load_groups, daemon=True).start()

    def load_groups(self):
        """加载群组的业务逻辑"""
        try:
            # 连接到WhatsApp
            self.connect_whatsapp()
            main_window = self.get_main_window()

            # 导航到对话列表
            self.navigate_to_chats(main_window)

            # 获取列表容器
            list_container = self.get_chat_list_container(main_window)

            # 提取群组信息
            groups = self.extract_groups(list_container)

            # 更新界面
            self.root.after(0, self.update_listbox, groups)
            self.update_status(f"加载完成 | 找到 {len(groups)} 个群组")

        except Exception as e:
            logger.error(f"加载失败: {str(e)}")
            self.show_error("操作失败", f"{str(e)}")
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.btn_load.config(state=tk.NORMAL))

    def connect_whatsapp(self):
        """建立WhatsApp连接"""
        try:
            self.app = Application(backend="uia").connect(
                class_name="ApplicationFrameWindow",
                title_re="WhatsApp",
                timeout=20
            )
            logger.info("成功连接到WhatsApp进程")
        except ElementNotFoundError:
            raise Exception("找不到WhatsApp窗口，请确保：\n1. 程序已运行\n2. 窗口未被最小化")

    def get_main_window(self):
        """获取主窗口对象"""
        main_window = self.app.window(class_name="ApplicationFrameWindow")
        main_window.wait("exists visible", timeout=10)
        return main_window

    def navigate_to_chats(self, window):
        """导航到对话列表"""
        try:
            # 切换导航面板
            nav_btn = window.child_window(
                auto_id="TogglePaneButton",
                control_type="Button"
            )
            nav_btn.wait("exists visible", timeout=10)
            if "Expand" in nav_btn.get_properties().get("Name", ""):
                nav_btn.click_input()

            # 选择对话标签
            chat_item = window.child_window(
                auto_id="ChatsNavigationItem",
                control_type="ListItem"
            )
            chat_item.click_input()
            time.sleep(1)  # 等待加载

        except Exception as e:
            raise Exception(f"导航失败: {str(e)}")

    def get_chat_list_container(self, window):
        """获取群组列表容器"""
        try:
            list_container = window.child_window(
                auto_id="ChatList",
                control_type="List",
                class_name="ListView"
            )
            list_container.wait("visible ready", timeout=15)
            logger.info(f"列表容器已定位: {list_container.friendly_class_name()}")
            return list_container
        except Exception as e:
            raise Exception("找不到群组列表，请检查界面布局")

    def extract_groups(self, container):
        """提取群组名称的稳定实现"""
        groups = []
        try:
            # 确保控件准备好
            if not container.is_visible():
                container.set_focus()
                container.wait("visible", timeout=5)

            # 滚动加载更多
            self.smart_scroll(container)

            # 遍历所有列表项
            items = container.items()
            print(f"找到的列表项数量: {len(items)}")
            for item in items:
                try:
                    title = self.extract_item_title(item)
                    if title and self.is_valid_group(title):
                        groups.append(title)
                        print(f"找到有效的群组: {title}")
                    else:
                        print(f"无效的群组名称: {title}")
                except Exception as e:
                    logger.warning(f"处理项失败: {str(e)}")
                    continue

            return sorted(list(set(groups)))  # 去重排序

        except Exception as e:
            logger.error(f"提取过程中断: {str(e)}")
            raise Exception("解析群组信息失败")

    def extract_item_title(self, item):
        """从列表项中提取标题"""
        try:
            # 查找包含群组名称的 TextBlock 控件
            title_block = item.child_window(
                auto_id="Title",
                control_type="Text",
                class_name="TextBlock"
            )
            title_block.wait("exists", timeout=2)
            title = title_block.window_text()
            print(f"提取到的群组名称: {title}")
            return self.clean_title(title)
        except Exception as e:
            print(f"提取标题失败: {str(e)}")
            return None

    def clean_title(self, title):
        """清理标题中的多余字符"""
        return title.strip()

    def is_valid_group(self, title):
        """增强的验证逻辑"""
        invalid_patterns = [
            "你已成为群组管理员",
            "已暂停的群组",
            "广播列表",
            "创建社区",
            "未接来电"
        ]
        return (
                len(title) > 1 and
                not any(p in title for p in invalid_patterns) and
                not title.isdigit()
        )

    def smart_scroll(self, container):
        """智能滚动加载更多项"""
        try:
            last_count = len(container.items())
            for _ in range(3):  # 最多滚动 3 次
                container.scroll("down", "page")
                time.sleep(1)  # 等待加载
                new_count = len(container.items())
                if new_count == last_count:
                    break  # 如果没有新项加载，停止滚动
                last_count = new_count
                print(f"滚动后加载的项数: {new_count}")
        except Exception as e:
            logger.warning(f"滚动失败: {str(e)}")

    def update_listbox(self, groups):
        """更新列表框内容"""
        self.group_list.delete(0, tk.END)
        for group in sorted(groups):
            self.group_list.insert(tk.END, group)

    def update_status(self, message):
        """更新状态栏"""
        self.root.after(0, lambda: self.status.config(text=message))

    def show_error(self, title, message):
        """显示错误弹窗"""
        self.root.after(0, lambda: messagebox.showerror(title, message))

    def start_setup(self):
        """开始设置流程"""
        # TODO: 实现管理员设置逻辑
        pass

    def on_close(self):
        """处理关闭事件"""
        if self.is_running:
            messagebox.showwarning("警告", "请等待当前操作完成")
        else:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppManager(root)
    root.mainloop()