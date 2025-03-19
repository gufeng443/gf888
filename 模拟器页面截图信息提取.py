import tkinter as tk
from tkinter import messagebox
from tkinter import ttk, scrolledtext
import subprocess
import pytesseract
from PIL import Image

# 配置 Tesseract 路径（根据你的系统配置）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows 示例路径

def get_emulators():
    """获取所有打开的模拟器窗口信息"""
    try:
        # 执行 adb 命令获取设备列表
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        devices = result.stdout.splitlines()[1:]
        emulators = []
        for device in devices:
            if device:
                device_id = device.split()[0]
                emulators.append(device_id)
        return emulators
    except Exception as e:
        messagebox.showerror("Error", f"Failed to get emulators: {e}")
        return []

def get_screenshot(device_id):
    """获取指定模拟器的截图"""
    try:
        # 执行 adb 命令截取屏幕并保存到文件
        subprocess.run(['adb', '-s', device_id, 'shell', 'screencap', '-p', '/sdcard/screen.png'], check=True)
        subprocess.run(['adb', '-s', device_id, 'pull', '/sdcard/screen.png', 'screen.png'], check=True)

        # 读取截图文件
        image = Image.open('screen.png')
        return image
    except Exception as e:
        messagebox.showerror("Error", f"Failed to capture screenshot: {e}")
        return None

def extract_text_from_image(image):
    """从图像中提取文本"""
    try:
        # 使用中文语言包进行识别
        text = pytesseract.image_to_string(image, lang='chi_sim')
        return text
    except Exception as e:
        messagebox.showerror("Error", f"Failed to extract text: {e}")
        return ""

def on_read_emulators():
    """读取模拟器并更新下拉菜单"""
    emulators = get_emulators()
    emulator_combo['values'] = emulators
    if emulators:
        emulator_combo.set(emulators[0])

def on_capture_screenshot():
    """捕获指定模拟器的截图并进行识别"""
    selected_device = emulator_combo.get()
    if not selected_device:
        messagebox.showwarning("Warning", "Please select an emulator.")
        return

    image = get_screenshot(selected_device)
    if image:
        text = extract_text_from_image(image)
        result_text.delete('1.0', tk.END)  # 清空文本框
        result_text.insert(tk.END, text)

# 创建 GUI
root = tk.Tk()
root.title("模拟器管理工具")

# 设置窗口大小
root.geometry("600x400")

# 读取模拟器按钮
read_emulators_button = ttk.Button(root, text="读取模拟器", command=on_read_emulators)
read_emulators_button.pack(pady=10)

# 模拟器下拉菜单
emulator_combo = ttk.Combobox(root, state="readonly")
emulator_combo.pack(pady=10)

# 提取窗口截图按钮
capture_screenshot_button = ttk.Button(root, text="提取截图并识图", command=on_capture_screenshot)
capture_screenshot_button.pack(pady=10)

# 识图结果显示
result_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15)
result_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

root.mainloop()
