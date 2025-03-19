import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import uiautomator2 as u2
import xml.etree.ElementTree as ET

class EmulatorControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("模拟器控件信息提取器")

        self.selected_emulator = None

        self.create_widgets()

    def create_widgets(self):
        # 读取模拟器按钮
        self.read_emulators_button = ttk.Button(self.root, text="读取模拟器", command=self.read_emulators)
        self.read_emulators_button.grid(row=0, column=0, padx=10, pady=10)

        # 模拟器选择下拉框
        self.emulator_var = tk.StringVar()
        self.emulator_dropdown = ttk.Combobox(self.root, textvariable=self.emulator_var)
        self.emulator_dropdown.grid(row=0, column=1, padx=10, pady=10)

        # 提取控件信息按钮
        self.extract_controls_button = ttk.Button(self.root, text="提取控件信息", command=self.extract_controls)
        self.extract_controls_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # 输出区域
        self.output_text = tk.Text(self.root, height=10, width=50)
        self.output_text.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def read_emulators(self):
        try:
            # 使用 adb 获取模拟器列表
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
            devices_output = result.stdout.splitlines()

            # 解析设备列表
            devices = [line.split('\t')[0] for line in devices_output if line and "device" in line]

            if devices:
                # 更新下拉框选项
                self.emulator_dropdown['values'] = devices
                if devices:
                    self.emulator_var.set(devices[0])  # 默认选择第一个设备
            else:
                messagebox.showinfo("信息", "未找到任何设备或模拟器")

        except Exception as e:
            messagebox.showerror("错误", f"读取模拟器列表时出错: {e}")

    def extract_controls(self):
        selected_device = self.emulator_var.get()
        if not selected_device:
            messagebox.showwarning("警告", "请选择一个模拟器")
            return

        try:
            # 连接到模拟器
            d = u2.connect(selected_device)
            # 获取控件信息
            controls_xml = d.dump_hierarchy()

            # 解析XML并提取可操作的控件信息
            extracted_info = self.parse_xml(controls_xml)

            # 在文本区域显示控件信息
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, extracted_info)

        except Exception as e:
            messagebox.showerror("错误", f"提取控件信息时出错: {e}")

    def parse_xml(self, xml_data):
        try:
            # 解析XML数据
            root = ET.fromstring(xml_data)

            # 提取可操作控件信息
            result = []
            for node in root.iter('node'):
                if self.is_interactive(node):
                    node_info = {
                        'class': node.attrib.get('class', ''),
                        'text': node.attrib.get('text', ''),
                        'resource-id': node.attrib.get('resource-id', ''),
                        'bounds': node.attrib.get('bounds', ''),
                        'clickable': node.attrib.get('clickable', ''),
                        'focusable': node.attrib.get('focusable', ''),
                        'long-clickable': node.attrib.get('long-clickable', ''),
                    }
                    result.append(node_info)

            # 格式化输出
            info_str = '\n'.join([f"Class: {n['class']}, Text: {n['text']}, Resource-ID: {n['resource-id']}, "
                                  f"Bounds: {n['bounds']}, Clickable: {n['clickable']}, Focusable: {n['focusable']}, "
                                  f"Long-clickable: {n['long-clickable']}" for n in result])
            return info_str

        except Exception as e:
            return f"解析XML时出错: {e}"

    def is_interactive(self, node):
        # 判断节点是否是可操作的（点击、焦点等）
        return (node.attrib.get('clickable') == 'true' or
                node.attrib.get('focusable') == 'true' or
                node.attrib.get('long-clickable') == 'true')

if __name__ == "__main__":
    root = tk.Tk()
    app = EmulatorControlApp(root)
    root.mainloop()
