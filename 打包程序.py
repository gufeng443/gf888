import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import PyInstaller.__main__
import os
import subprocess
import sys
import ast

def pack_and_execute():
    file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])

    if not file_path:
        return  # 用户取消选择文件，退出函数

    # 创建进度窗口
    progress_popup = tk.Toplevel()
    progress_popup.title("打包进度")
    progress_label = tk.Label(progress_popup, text="正在打包...")
    progress_label.pack(padx=10, pady=5)

    progress_bar = ttk.Progressbar(progress_popup, length=300, mode='indeterminate')
    progress_bar.pack(padx=10, pady=10)
    progress_bar.start()

    def on_complete():
        progress_bar.stop()
        progress_label.config(text="打包完成")
        messagebox.showinfo("提示", "程序打包完成并执行成功！")
        progress_popup.destroy()
        # 自动打开包含生成文件的文件夹
        output_dir = os.path.dirname(file_path)
        subprocess.run(f'explorer "{output_dir}"', shell=True)

    def update_progress():
        # 更新进度条或进行其他UI更新
        pass

    try:
        # 读取文件内容并解析 AST
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            tree = ast.parse(file_content)

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module)

        # 打包选项
        opts = ['--onefile', '--noconsole']
        for module in imports:
            opts.extend(['--hidden-import', module])

        # 确保打包程序使用的 PyInstaller 版本与目标环境兼容
        PyInstaller.__main__.run(opts + [file_path])

        on_complete()

    except Exception as e:
        progress_bar.stop()
        progress_popup.destroy()
        messagebox.showerror("错误", f"程序执行出错：{str(e)}")

# 创建主GUI窗口
root = tk.Tk()
root.title("程序打包工具")

# 添加打包按钮
pack_button = tk.Button(root, text="选择文件并打包", command=pack_and_execute)
pack_button.pack(pady=20)

# 运行主窗口的消息循环
root.mainloop()
