import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from collections import defaultdict
import time

# 全局变量
drivers = []  # 存储多个浏览器窗口的驱动实例

# 启动 Chrome 调试模式并打开三个窗口
def start_chrome_with_debugging():
    global drivers

    try:
        # 启动第一个窗口：https://web.whatsapp.com/
        chrome_options1 = Options()
        chrome_options1.add_argument("--remote-debugging-port=9222")
        chrome_options1.add_argument("--user-data-dir=C:\\Temp\\ChromeProfile1")  # 可选：指定用户数据目录
        driver1 = webdriver.Chrome(options=chrome_options1)
        driver1.get("https://web.whatsapp.com/")
        drivers.append(driver1)

        # 启动第二个窗口：http://47.243.35.38/#/task/pullGroup
        chrome_options2 = Options()
        chrome_options2.add_argument("--remote-debugging-port=9223")
        chrome_options2.add_argument("--user-data-dir=C:\\Temp\\ChromeProfile2")  # 可选：指定用户数据目录
        driver2 = webdriver.Chrome(options=chrome_options2)
        driver2.get("http://47.243.35.38/#/task/pullGroup")
        drivers.append(driver2)

        # 启动第三个窗口：http://47.243.35.38/#/task/pullGroup
        chrome_options3 = Options()
        chrome_options3.add_argument("--remote-debugging-port=9224")
        chrome_options3.add_argument("--user-data-dir=C:\\Temp\\ChromeProfile3")  # 可选：指定用户数据目录
        driver3 = webdriver.Chrome(options=chrome_options3)
        driver3.get("http://47.243.35.38/#/task/pullGroup")
        drivers.append(driver3)

        status_label.config(text="已启动三个 Chrome 窗口并加载指定网址！")

        # 自动输入账号和密码
        auto_login(driver2)  # 对第二个窗口自动登录
        auto_login(driver3)  # 对第三个窗口自动登录
    except Exception as e:
        status_label.config(text=f"启动 Chrome 失败: {str(e)}")

# 自动输入账号和密码
def auto_login(driver):
    try:
        # 等待页面加载完成
        time.sleep(3)

        # 找到用户名输入框并输入账号
        username_input = driver.find_element(By.CSS_SELECTOR, 'input.el-input__inner[type="text"][placeholder*="用户名"]')
        username_input.clear()
        username_input.send_keys("bs007")

        # 找到密码输入框并输入密码
        password_input = driver.find_element(By.CSS_SELECTOR, 'input.el-input__inner[type="password"][placeholder*="密码"]')
        password_input.clear()
        password_input.send_keys("3322ddd")

        status_label.config(text="账号和密码已自动输入！")
    except Exception as e:
        status_label.config(text=f"自动登录失败: {str(e)}")

# 提取号码
def extract_numbers():
    global drivers

    if not drivers:
        status_label.config(text="请先启动 Chrome 窗口！")
        return

    try:
        # 获取当前选中的窗口索引
        selected_index = browser_dropdown.current()
        if selected_index == -1:
            status_label.config(text="请先选择一个浏览器窗口！")
            return

        # 获取当前窗口的驱动实例
        driver = drivers[selected_index]

        # 获取当前浏览器页面的源码
        page_source = driver.page_source

        # 使用 BeautifulSoup 解析页面源码
        soup = BeautifulSoup(page_source, 'html.parser')
        number_counts = defaultdict(int)

        # 查找所有符合条件的 <span> 标签
        spans = soup.find_all('span', {'style': 'color: rgb(22, 119, 255); cursor: pointer;'})
        for span in spans:
            number = span.text.strip()
            if number:  # 确保号码不为空
                number_counts[number] += 1

        # 过滤出出现次数大于1的号码
        result = []
        for number, count in number_counts.items():
            if count > 1:
                result.append(f"({count}): {number}")

        # 显示结果
        result_text.delete(1.0, tk.END)
        if result:
            result_text.insert(tk.END, "\n".join(result))
        else:
            result_text.insert(tk.END, "没有找到符合条件的号码。")
    except Exception as e:
        status_label.config(text=f"提取数据失败: {str(e)}")

# 关闭所有浏览器窗口
def close_browser():
    global drivers

    if drivers:
        for driver in drivers:
            driver.quit()
        drivers = []
        status_label.config(text="所有 Chrome 窗口已关闭！")
        browser_dropdown['values'] = []  # 清空下拉框

# 创建主窗口
root = tk.Tk()
root.title("浏览器号码提取器")

# 状态标签
status_label = tk.Label(root, text="状态：未启动", fg="blue")
status_label.pack(pady=10)

# 启动浏览器按钮
start_button = tk.Button(root, text="启动 Chrome 调试模式并打开三个窗口", command=start_chrome_with_debugging)
start_button.pack(pady=10)

# 浏览器窗口下拉框
browser_dropdown = ttk.Combobox(root, state="readonly")
browser_dropdown['values'] = ["窗口 1: WhatsApp", "窗口 2: 任务页面 1", "窗口 3: 任务页面 2"]
browser_dropdown.pack(pady=10)

# 提取号码按钮
extract_button = tk.Button(root, text="提取号码", command=extract_numbers)
extract_button.pack(pady=10)

# 关闭浏览器按钮
close_button = tk.Button(root, text="关闭所有 Chrome 窗口", command=close_browser)
close_button.pack(pady=10)

# 结果显示文本框
result_label = tk.Label(root, text="提取结果:")
result_label.pack(pady=5)
result_text = tk.Text(root, height=10, width=80)
result_text.pack(pady=5)

# 运行主循环
root.mainloop()