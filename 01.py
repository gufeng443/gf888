import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from collections import defaultdict

# 全局变量
driver = None
browser_windows = {}

# 启动 Chrome 并启用调试模式
def start_chrome_with_debugging():
    global driver

    chrome_options = Options()
    chrome_options.add_argument("--remote-debugging-port=9223")
    chrome_options.add_argument("--user-data-dir=C:\\Temp\\ChromeProfile")  # 可选：指定用户数据目录

    try:
        driver = webdriver.Chrome(options=chrome_options)
        status_label.config(text="Chrome 已启动并启用调试模式！")
    except Exception as e:
        status_label.config(text=f"启动 Chrome 失败: {str(e)}")

# 获取已打开的浏览器窗口
def get_browser_windows():
    global browser_windows, driver

    if driver is None:
        status_label.config(text="请先启动 Chrome！")
        return

    try:
        handles = driver.window_handles
        browser_windows = {handle: driver.title for handle in handles}
        browser_dropdown['values'] = list(browser_windows.values())
        status_label.config(text="成功获取浏览器窗口！")
    except Exception as e:
        status_label.config(text=f"获取窗口失败: {str(e)}")

# 查找并点击“查询”按钮，并监视页面加载完成
def click_query_button():
    global driver

    if driver is None:
        status_label.config(text="请先启动 Chrome！")
        return

    try:
        # 查找“查询”按钮
        status_label.config(text="正在查找查询按钮...")
        query_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.el-card__body span'))
        )
        query_button.click()
        status_label.config(text="查询按钮已点击，等待页面重新加载...")

        # 监视页面加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.el-card__body'))
        )
        status_label.config(text="页面加载完成！")
    except Exception as e:
        status_label.config(text=f"操作失败: {str(e)}")

# 提取号码
def extract_numbers():
    global driver

    if driver is None:
        status_label.config(text="请先启动 Chrome！")
        return

    try:
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

        # 过滤出出现次数大于1的号码，并按出现次数从多到少排序
        sorted_numbers = sorted(number_counts.items(), key=lambda x: x[1], reverse=True)
        result = [f"({count}): {number}" for number, count in sorted_numbers if count > 1]

        # 显示结果
        result_text.delete(1.0, tk.END)
        if result:
            result_text.insert(tk.END, "\n".join(result))
        else:
            result_text.insert(tk.END, "没有找到符合条件的号码。")
    except Exception as e:
        status_label.config(text=f"提取数据失败: {str(e)}")

# 关闭浏览器
def close_browser():
    global driver

    if driver:
        driver.quit()
        driver = None
        status_label.config(text="Chrome 已关闭！")

# 创建主窗口
root = tk.Tk()
root.title("浏览器号码提取器")

# 状态标签
status_label = tk.Label(root, text="状态：未启动", fg="blue")
status_label.pack(pady=10)

# 启动浏览器按钮
start_button = tk.Button(root, text="启动 Chrome 调试模式", command=start_chrome_with_debugging)
start_button.pack(pady=10)

# 获取浏览器窗口按钮
get_windows_button = tk.Button(root, text="获取浏览器窗口", command=get_browser_windows)
get_windows_button.pack(pady=10)

# 点击查询按钮
query_button = tk.Button(root, text="点击查询按钮", command=click_query_button)
query_button.pack(pady=10)

# 浏览器窗口下拉框
browser_dropdown = ttk.Combobox(root, state="readonly")
browser_dropdown.pack(pady=10)

# 提取号码按钮
extract_button = tk.Button(root, text="提取号码", command=extract_numbers)
extract_button.pack(pady=10)

# 关闭浏览器按钮
close_button = tk.Button(root, text="关闭 Chrome", command=close_browser)
close_button.pack(pady=10)

# 结果显示文本框
result_label = tk.Label(root, text="提取结果:")
result_label.pack(pady=5)
result_text = tk.Text(root, height=10, width=80)
result_text.pack(pady=5)

# 运行主循环
root.mainloop()