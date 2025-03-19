import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import win32gui
import win32process
import psutil
import ctypes
import sys
import time
from pywinauto import Application
import uiautomation as auto


class UltimateControlInspector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("高级控件分析工具 v7.1")
        self.root.geometry("1366x900")

        self.check_admin_privileges()
        self.initialize_ui()
        self.current_app = None
        self.refresh_windows()

    def check_admin_privileges(self):
        """验证并获取管理员权限"""
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()

    def initialize_ui(self):
        """初始化用户界面"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 窗口选择组件
        self.window_selector = ttk.Combobox(
            main_frame,
            width=140,
            state="readonly",
            font=("Segoe UI", 10)
        self.window_selector.pack(fill="x", pady=5)

        # 操作按钮
        control_frame = ttk.Frame(main_frame)
        ttk.Button(
            control_frame,
            text="刷新窗口列表",
            command=self.refresh_windows,
            width=15).pack(side="left", padx=5)
        ttk.Button(
            control_frame,
            text="深度扫描控件",
            command=self.deep_scan_controls,
            width=15).pack(side="left", padx=5)
        control_frame.pack(pady=5)

        # 调试信息面板
        self.debug_console = scrolledtext.ScrolledText(
            main_frame,
            height=10,
            font=("Consolas", 8),
            wrap=tk.WORD)
        self.debug_console.pack(fill="x", pady=5)

        # 增强型控件树
        self.control_tree = ttk.Treeview(
            main_frame,
            columns=("type", "automation_id", "class", "handle"),
            show="tree",
            selectmode="extended")
        self.control_tree.heading("#0", text="控件结构", anchor="w")
        self.control_tree.column("#0", width=400)
        self.control_tree.heading("type", text="类型")
        self.control_tree.heading("automation_id", text="自动化ID")
        self.control_tree.heading("class", text="类名")
        self.control_tree.heading("handle", text="句柄")

        vsb = ttk.Scrollbar(main_frame, orient="vertical", command=self.control_tree.yview)
        hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=self.control_tree.xview)
        self.control_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.control_tree.pack(fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(fill="x")

        # 上下文菜单
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="复制信息", command=self.copy_control_info)
        self.control_tree.bind("<Button-3>", self.show_context_menu)

        # 事件绑定
        self.window_selector.bind("<<ComboboxSelected>>", self.on_window_selected)

    def enum_windows(self, hwnd, ctx):
        """枚举所有可见窗口"""
        if win32gui.IsWindowVisible(hwnd):
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                ctx.append({
                    "hwnd": hwnd,
                    "title": win32gui.GetWindowText(hwnd),
                    "class": win32gui.GetClassName(hwnd),
                    "pid": pid
                })
            except Exception as e:
                self.log_debug(f"窗口枚举错误: {str(e)}")
        return True

    def get_all_windows(self):
        """获取所有窗口的增强方法"""
        windows = []
        win32gui.EnumWindows(self.enum_windows, windows)

        # 补充进程信息
        for win in windows:
            try:
                proc = psutil.Process(win["pid"])
                win.update({
                    "exe": proc.exe(),
                    "cmdline": " ".join(proc.cmdline()),
                    "name": proc.name()
                })
            except Exception as e:
                self.log_debug(f"进程信息获取失败(PID:{win['pid']}): {str(e)}")
                win.update({"exe": "N/A", "cmdline": "N/A", "name": "N/A"})

        return windows

    def refresh_windows(self):
        """刷新窗口列表"""
        self.debug_console.delete(1.0, tk.END)
        try:
            windows = self.get_all_windows()
            display_list = [
                f"[0x{w['hwnd']:X}] {w['title']} | {w['name']} | PID:{w['pid']}"
                for w in windows
            ]
            self.window_selector["values"] = display_list
            if display_list:
                self.window_selector.current(0)
                self.on_window_selected()
            self.log_debug(f"已发现 {len(windows)} 个窗口")
        except Exception as e:
            self.log_debug(f"窗口刷新失败: {str(e)}")

    def on_window_selected(self, event=None):
        """处理窗口选择事件"""
        index = self.window_selector.current()
        if index == -1:
            return

        try:
            hwnd = int(self.window_selector.get().split("]")[0][2:], 16)
            self.connect_to_window(hwnd)
            self.build_control_tree()
        except Exception as e:
            self.log_debug(f"窗口连接失败: {str(e)}")

    def connect_to_window(self, hwnd):
        """连接到指定窗口"""
        try:
            # 尝试UIA后端
            self.current_app = Application(backend="uia").connect(handle=hwnd)
            self.log_debug("成功使用UIA后端连接")
        except Exception as e:
            try:
                # 回退到Win32后端
                self.current_app = Application(backend="win32").connect(handle=hwnd)
                self.log_debug("成功使用Win32后端连接")
            except Exception as e:
                self.log_debug(f"连接失败: {str(e)}")
                raise

    def build_control_tree(self):
        """构建增强型控件树"""
        self.control_tree.delete(*self.control_tree.get_children())
        if not self.current_app:
            return

        try:
            top_window = self.current_app.window()
            top_window.wait("exists ready", timeout=15)
            self.log_debug("开始构建控件树...")

            # Electron应用特殊处理
            if "Chrome_WidgetWin" in top_window.class_name():
                self.log_debug("检测到Electron应用，启用深度扫描模式")
                self.process_electron_controls(top_window)
            else:
                self.process_standard_controls(top_window)

            self.log_debug(f"控件树构建完成，共发现 {len(self.control_tree.get_children())} 个根节点")
        except Exception as e:
            self.log_debug(f"控件树构建失败: {str(e)}")

    def process_standard_controls(self, top_window):
        """处理标准Win32/UIA控件"""
        try:
            self._add_control_tree_item("", top_window.element_info)
        except Exception as e:
            self.log_debug(f"标准控件处理失败: {str(e)}")

    def process_electron_controls(self, top_window):
        """处理Electron/Chrome控件"""
        try:
            # 等待页面加载完成
            auto.WaitForExist(top_window.element_info, timeout=15)

            # 定位主文档容器
            main_document = top_window.child_window(
                control_type="Document",
                found_index=0)

            # 递归处理所有子控件
            self._add_electron_control_item("", main_document.element_info)
        except Exception as e:
            self.log_debug(f"Electron控件处理失败: {str(e)}")

    def _add_control_tree_item(self, parent, element, depth=0):
        """递归添加控件节点"""
        if depth > 12:  # 安全深度限制
            return

        try:
            # 获取控件信息
            name = element.name or "<未命名>"
            ctrl_type = element.control_type
            auto_id = element.automation_id or ""
            class_name = element.class_name or ""
            handle = f"0x{element.handle:X}" if element.handle else "N/A"

            # 创建树节点
            item = self.control_tree.insert(
                parent,
                "end",
                text=f"{name} [{ctrl_type}]",
                values=(ctrl_type, auto_id, class_name, handle),
                tags=(self._get_rect_info(element),)
            )

            # 处理子控件
            children = element.children()
            for child in children[:50]:  # 限制子项数量
                self._add_control_tree_item(item, child, depth + 1)

        except Exception as e:
            self.log_debug(f"添加节点失败: {str(e)}")

    def _add_electron_control_item(self, parent, element, depth=0):
        """专门处理Electron控件"""
        if depth > 15:  # Electron控件可能很深
            return

        try:
            # 获取额外属性
            role = element.get_pattern("LegacyIAccessiblePattern").Role
            states = element.get_pattern("LegacyIAccessiblePattern").States
            value = element.get_pattern("ValuePattern").Value if element.has_pattern("ValuePattern") else ""

            # 创建节点
            item = self.control_tree.insert(
                parent,
                "end",
                text=f"{element.name} [Electron-{role}]",
                values=(
                    role,
                    element.automation_id,
                    element.class_name,
                    f"0x{element.handle:X}"
                ),
                tags=(self._get_rect_info(element),)

            # 处理子项
            children = element.children()
            for child in children[:100]:  # Electron可能有很多子项
                self._add_electron_control_item(item, child, depth + 1)

        except Exception as e:
            self.log_debug(f"Electron节点处理失败: {str(e)}")

    def _get_rect_info(self, element):
        """获取控件位置信息"""
        try:
            rect = element.rectangle()
            return f"{rect.left},{rect.top}-{rect.right},{rect.bottom}"
        except:
            return "坐标不可用"

    def deep_scan_controls(self):
        """执行深度扫描"""
        try:
            if self.current_app:
                self.log_debug("开始深度扫描...")
                top_window = self.current_app.window()
                top_window.element_info.legacy_properties['depth'] = 0
                self._deep_scan_element(top_window.element_info)
                self.log_debug("深度扫描完成")
        except Exception as e:
            self.log_debug(f"深度扫描失败: {str(e)}")

    def _deep_scan_element(self, element, depth=0):
        """递归深度扫描"""
        if depth > 20:
            return

        try:
            # 强制获取所有属性
            element.ensure_visible()
            element.set_focus()

            # 获取扩展属性
            patterns = [p.PatternName for p in element.GetSupportedPatterns()]
            properties = element.GetSupportedProperties()

            # 记录调试信息
            self.log_debug(f"深度扫描: {element.name} | 模式: {patterns} | 属性: {properties}")

            # 处理子项
            for child in element.children():
                self._deep_scan_element(child, depth + 1)

        except Exception as e:
            self.log_debug(f"深度扫描错误: {str(e)}")

    def log_debug(self, message):
        """记录调试信息"""
        self.debug_console.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.debug_console.see(tk.END)

    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.control_tree.identify_row(event.y)
        if item:
            self.control_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def copy_control_info(self):
        """复制控件信息"""
        selected = self.control_tree.selection()
        if selected:
            item = self.control_tree.item(selected[0])
            info = "\n".join([
                f"名称: {item['text']}",
                f"类型: {item['values'][0]}",
                f"自动化ID: {item['values'][1]}",
                f"类名: {item['values'][2]}",
                f"句柄: {item['values'][3]}",
                f"坐标: {item['tags'][0]}"
            ])
            self.root.clipboard_clear()
            self.root.clipboard_append(info)
            self.log_debug("控件信息已复制到剪贴板")

    def run(self):
        """运行主程序"""
        self.root.mainloop()


if __name__ == "__main__":
    try:
        inspector = UltimateControlInspector()
        inspector.run()
    except Exception as e:
        messagebox.showerror("错误", f"程序异常终止: {str(e)}")
        sys.exit(1)