import importlib.util
import threading
import logging
from pathlib import Path
import tkinter as tk
from tkinter import scrolledtext

# 自定义日志处理器，将日志输出到 Tkinter 文本框
class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, msg + "\n")
        self.text_widget.configure(state="disabled")
        self.text_widget.yview(tk.END)  # 自动滚动到底部

def load_script(script_path):
    """
    动态加载指定路径的 Python 脚本，并返回模块对象。
    """
    try:
        # 获取脚本文件名（不带扩展名）
        script_name = Path(script_path).stem
        # 动态加载脚本
        spec = importlib.util.spec_from_file_location(script_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logging.error(f"加载脚本 {script_path} 失败: {e}")
        return None

def run_script(script_path):
    """
    运行指定路径的 Python 脚本。
    """
    module = load_script(script_path)
    if module:
        logging.info(f"开始运行脚本: {script_path}")
        try:
            # 假设脚本中有一个名为 `main` 的函数
            if hasattr(module, "main"):
                module.main()
            else:
                logging.warning(f"脚本 {script_path} 中没有找到 'main' 函数")
        except Exception as e:
            logging.error(f"运行脚本 {script_path} 时出错: {e}")
        logging.info(f"脚本 {script_path} 运行完成")

def main():
    # 定义脚本文件路径列表
    script_paths = [
        "GT运控分料子.py",
        "报表修改.py",
        "自动整理余料.py",
        "带定时自动批群（版本切换）.py",
        "第五个脚本.py",
    ]

    # 创建 Tkinter 窗口
    root = tk.Tk()
    root.title("多脚本运行器")

    # 创建一个文本框用于显示日志
    log_text = scrolledtext.ScrolledText(root, state="disabled", wrap=tk.WORD)
    log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # 配置日志
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    text_handler = TextHandler(log_text)
    text_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(text_handler)

    # 创建线程列表
    threads = []

    # 为每个脚本创建一个线程并启动
    for script_path in script_paths:
        thread = threading.Thread(target=run_script, args=(script_path,))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    logging.info("所有脚本运行完成")

    # 运行 Tkinter 主循环
    root.mainloop()

if __name__ == "__main__":
    main()