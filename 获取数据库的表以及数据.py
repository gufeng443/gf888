import sqlite3
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog, ttk


# 获取已连接的模拟器设备列表
def get_connected_emulators():
    try:
        result = subprocess.check_output(["adb", "devices"]).decode("utf-8")
        devices = []
        for line in result.splitlines()[1:]:
            if line.strip() == "":
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                devices.append(parts[0])
        return devices
    except subprocess.CalledProcessError:
        messagebox.showerror("错误", "无法获取已连接的模拟器设备列表。")
        return []


# 拉取指定模拟器的 WhatsApp 数据库
def pull_whatsapp_db(device_id, whatsapp_version):
    if whatsapp_version == "个人版":
        package_name = "com.whatsapp"
    elif whatsapp_version == "商业版":
        package_name = "com.whatsapp.w4b"
    else:
        messagebox.showerror("错误", "未知的 WhatsApp 版本。")
        return None

    db_path = f"/data/data/{package_name}/databases/wa.db"
    local_path = "./wa.db"

    try:
        subprocess.check_call(["adb", "-s", device_id, "root"])  # 需要 root 权限
        subprocess.check_call(["adb", "-s", device_id, "pull", db_path, local_path])
        return local_path
    except subprocess.CalledProcessError:
        messagebox.showerror("错误", "无法拉取数据库文件，请确保模拟器已root且WhatsApp已安装。")
        return None


# 获取数据库中的所有表
def get_tables(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        return [table[0] for table in tables]
    except sqlite3.Error as e:
        messagebox.showerror("数据库错误", f"无法读取数据库中的表格: {e}")
        return []


# 获取表格中的所有数据
def get_table_data(db_path, table_name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()
        return columns, rows
    except sqlite3.Error as e:
        messagebox.showerror("数据库错误", f"无法读取表格 {table_name} 的数据: {e}")
        return [], []


# 主界面
def main():
    root = tk.Tk()
    root.title("WhatsApp 数据库读取器")

    # 连接设备并选择模拟器
    devices = get_connected_emulators()
    if not devices:
        messagebox.showerror("错误", "没有检测到模拟器。")
        root.quit()

    emulator_label = tk.Label(root, text="选择模拟器:")
    emulator_label.pack(pady=10)

    emulator_var = tk.StringVar()
    emulator_dropdown = tk.OptionMenu(root, emulator_var, *devices)
    emulator_dropdown.pack(pady=10)

    # WhatsApp版本选择框
    version_label = tk.Label(root, text="选择 WhatsApp 版本:")
    version_label.pack(pady=10)

    version_var = tk.StringVar()
    version_dropdown = tk.OptionMenu(root, version_var, "个人版", "商业版")
    version_dropdown.pack(pady=10)

    # 显示数据库内容
    def on_read_db():
        device_id = emulator_var.get()
        whatsapp_version = version_var.get()

        if not device_id or not whatsapp_version:
            messagebox.showwarning("警告", "请完整选择模拟器和 WhatsApp 版本。")
            return

        # 拉取数据库文件
        db_path = pull_whatsapp_db(device_id, whatsapp_version)
        if db_path:
            tables = get_tables(db_path)
            if tables:
                table_listbox.delete(0, tk.END)
                for table in tables:
                    table_listbox.insert(tk.END, table)

                # 显示表格内容
                def on_show_table():
                    selected_table = table_listbox.get(tk.ACTIVE)
                    columns, rows = get_table_data(db_path, selected_table)

                    if not columns:
                        messagebox.showerror("错误", f"无法加载 {selected_table} 表的数据。")
                        return

                    # 清除旧数据
                    for item in treeview.get_children():
                        treeview.delete(item)

                    # 更新 Treeview 表格
                    treeview["columns"] = columns
                    for col in columns:
                        treeview.heading(col, text=col)
                        treeview.column(col, anchor="w", width=100)

                    for row in rows:
                        treeview.insert("", "end", values=row)

                    # 复制功能
                    def on_copy():
                        clipboard_data = "\t".join(columns) + "\n"
                        for row in rows:
                            clipboard_data += "\t".join(str(x) for x in row) + "\n"
                        root.clipboard_clear()
                        root.clipboard_append(clipboard_data)
                        messagebox.showinfo("复制成功", "表格数据已复制到剪贴板。")

                    copy_button.config(state=tk.NORMAL)
                    copy_button.config(command=on_copy)

                show_table_button.config(state=tk.NORMAL)
                show_table_button.config(command=on_show_table)

    # 读取数据库按钮
    read_db_button = tk.Button(root, text="读取数据库", command=on_read_db)
    read_db_button.pack(pady=20)

    # 显示表格列表
    table_listbox = tk.Listbox(root, width=50, height=10)
    table_listbox.pack(pady=10)

    # 显示表格内容的 Treeview
    treeview = ttk.Treeview(root, show="headings")
    treeview.pack(pady=10, fill=tk.BOTH, expand=True)

    # 显示表格内容的按钮
    show_table_button = tk.Button(root, text="显示表格内容", state=tk.DISABLED)
    show_table_button.pack(pady=10)

    # 复制按钮
    copy_button = tk.Button(root, text="复制表格内容", state=tk.DISABLED)
    copy_button.pack(pady=10)

    root.mainloop()


# 运行主程序
if __name__ == "__main__":
    main()
