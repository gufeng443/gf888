###   使用说明：主程序可以自定义命名，根目录下 data_save.txt 为数据库文件，储存程序中的数据。如果程序中的数据过多可以将数据库文件
###           转移到其他目录或删除，再次运行程序将自动生成新的数据库文件，列表为空。粘贴进画布的截图将自动保存到E盘“交单图”文件夹下，
###           如果没有该文件夹请创建
###   功能介绍：提取成群数据  按键点击后执行的是读取画布中第一张截图中的数据（第一张应该是成群人数截图），提取图像中的文字数据后将指定行
###           的文字数据提取到文本框第一行中，完后提取图片数据后，根据图片中提取的群名称数据到“C:\Users\Administrator\Desktop\交单”文
###           件夹中读取所有txt文件对比文件中的数据，找到群链接数据后将链接导入到文本框第二行中。
###           导入管理截图   按键点击后执行的是将桌面“GL"文件夹下的图片导入到画布第二张图片的位置，（需要提前将管理截图保存到该文件夹中）
###           复制交单数据   按键点击后将文本框中的成群数据复制到剪切板中
###    快捷键： 提取成群数据（空格键）   导入管理截图（双击左键）   复制交单数据（F1）
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageGrab
import pytesseract
import os
import io

class CanvasFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.page_number = 1  # 当前页码
        self.marked_page = None  # 标记的页码
        self.canvas_pages = {}  # 保存每一页的内容
        self.drag_data = {"x": 0, "y": 0, "item": None}  # 拖拽数据
        self.image_references = []  # 保存图像引用的列表
        self.pack()
        self.create_widgets()  # 创建控件
        self.load_page(self.page_number)  # 加载当前页
        self.master.bind('<Control-v>', self.paste_from_clipboard)  # 绑定Ctrl+V事件

    def create_widgets(self):
        # 创建画布
        self.canvas = tk.Canvas(self, width=1200, height=700, bg="white")
        self.canvas.pack(side="top", fill="both", expand=True)

        # 创建文本框
        self.textbox = tk.Text(self, width=50, height=6)
        self.textbox.pack(side="top", fill="both", expand=True)

        # 创建页码标签
        self.page_label = tk.Label(self, text=f"当前页: {self.page_number}")
        self.page_label.pack(side="top", fill="x")

        # 创建按钮框架
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side="bottom", fill="x")

        # 创建“标记/返回标记页”按钮
        self.mark_button = tk.Button(self.button_frame, text="标记当前页", command=self.toggle_mark_page)
        self.mark_button.pack(side="left", padx=8)

        # 创建“上一页”按钮
        self.prev_button = tk.Button(self.button_frame, text=" 上一页 ", command=self.prev_page)
        self.prev_button.pack(side="left", padx=8)

        # 创建“下一页”按钮
        self.next_button = tk.Button(self.button_frame, text=" 下一页 ", command=self.next_page)
        self.next_button.pack(side="left", padx=8)

        # 创建“提取成群数据”按钮
        self.extract_button = tk.Button(self.button_frame, text="-------", command=self.extract_data)
        self.extract_button.pack(side="left", padx=8)

        # 创建“提取总成群人数”按钮
        self.total_count_button = tk.Button(self.button_frame, text="提取总成群人数", command=self.extract_total_group_count)
        self.total_count_button.pack(side="left", padx=8)

        # 添加“导入管理截图”按钮
        self.import_button = tk.Button(self.button_frame, text="------", command=self.import_screenshot)
        self.import_button.pack(side="left", padx=8)

        # 创建“复制交单数据”按钮
        self.copy_data_button = tk.Button(self.button_frame, text="复制交单数据", command=self.copy_data_to_clipboard, bg="yellow")
        self.copy_data_button.pack(side="left", padx=8)

    # 其他方法的定义和实现...




    def extract_total_group_count(self):
        if self.canvas_pages.get(self.page_number) and self.canvas_pages[self.page_number]["images"]:
            total_count = 0
            for image_info in self.canvas_pages[self.page_number]["images"]:
                image_path = image_info["path"]
                text = pytesseract.image_to_string(Image.open(image_path), lang='chi_sim')
                lines = text.splitlines()
                for line in lines:
                    if "位成员" in line:
                        digits = ''.join(filter(str.isdigit, line.strip()))
                        if digits.isdigit():
                            total_count += int(digits)
            if total_count > 0:
                current_text = self.textbox.get("1.0", tk.END).strip()
                if current_text:
                    self.textbox.insert(tk.END, f"\t\t{total_count}人")
                else:
                    self.textbox.insert(tk.END, f"{total_count}人")

    def load_page(self, page):
        # 加载指定页的内容
        if page not in self.canvas_pages:
            self.canvas_pages[page] = {"images": [], "textbox": ""}
        self.canvas.delete("all")  # 清空画布
        self.textbox.delete("1.0", tk.END)  # 清空文本框
        self.textbox.insert(tk.END, self.canvas_pages[page]["textbox"])

        for image_info in self.canvas_pages[page]["images"]:
            self.display_image(image_info["path"], image_info["coords"])
        self.page_label.config(text=f"当前页: {page}")
    def save_page(self):
        # 保存当前页的内容
        self.canvas_pages[self.page_number]["textbox"] = self.textbox.get("1.0", tk.END).strip()

    def next_page(self):
        # 切换到下一页
        self.save_page()
        self.page_number += 1
        self.load_page(self.page_number)

    def prev_page(self):
        # 切换到上一页
        if self.page_number > 1:
            self.save_page()
            self.page_number -= 1
            self.load_page(self.page_number)

    def toggle_mark_page(self):
        # 标记或返回标记页
        if self.marked_page is None:
            self.marked_page = self.page_number
            self.mark_button.config(text=f"返回第{self.marked_page}页",foreground="red")
            self.show_mark_text = False
        else:
            self.save_page()
            self.page_number = self.marked_page
            self.load_page(self.page_number)
            self.marked_page = None
            self.mark_button.config(text=f"标记此页" , foreground="black")
    def extract_data(self):
        # 提取成群数据
        if self.canvas_pages.get(self.page_number) and self.canvas_pages[self.page_number]["images"]:
            image_path = self.canvas_pages[self.page_number]["images"][0]["path"]
            text = pytesseract.image_to_string(Image.open(image_path), lang='chi_sim')
            lines = text.splitlines()
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            print("提取的数据如下:")
            for line in lines:
                print(line)
            group_name = None
            for i, line in enumerate(lines):
                if "中的群组" in line:
                    group_name = lines[i - 1] if i >= 1 else "未找到群组信息"
                    break

            if group_name:

                for line in lines:
                    if "位成员" in line:
                        group_count = ''.join(filter(str.isdigit, line.strip())) + "人"
                        break
                else:
                    group_count = "未找到人数信息"
                self.textbox.delete("1.0", tk.END)
                self.textbox.insert(tk.END, f"{group_name}\t{group_count}")
                self.textbox.delete("1.0", tk.END)
                self.textbox.insert(tk.END, f"{group_name}\t{group_count}")

                search_path = r'C:\Users\Administrator\Desktop\交单'
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if file.endswith(".txt"):
                            file_path = os.path.join(root, file)
                            with open(file_path, "r", encoding="utf-8") as f:
                                lines = f.readlines()
                                for i, line in enumerate(lines):
                                    if group_name in line:
                                        if i + 1 < len(lines):
                                            self.textbox.insert(tk.END, f"\n{lines[i + 1].strip()}")
                                        break

    def paste_from_clipboard(self, event=None):
        # 从剪贴板粘贴图片
        try:
            # 尝试从剪贴板获取图像
            clipboard_image = ImageGrab.grabclipboard()
            # 判断获取的数据是否为图像类型
            if isinstance(clipboard_image, Image.Image):
                # 获取当前页面上的图像列表
                images_on_page = self.canvas_pages[self.page_number]["images"]
                # 如果当前页面的图像数量小于3，则可以继续粘贴图像
                if len(images_on_page) < 30:
                    # 创建一个字节流对象来存储图像数据
                    bio = io.BytesIO()
                    # 将剪贴板中的图像保存到字节流对象中，使用PNG格式
                    clipboard_image.save(bio, format="PNG")
                    # 设置图片保存路径，命名为 "clipboard_页面号_图像索引.png"
                    image_path = f"E:\\交单图\\clipboard_{self.page_number}_{len(images_on_page) + 1}.png"
                    # 将字节流对象中的图像数据写入到指定路径的文件中
                    with open(image_path, 'wb') as f:
                        f.write(bio.getbuffer())

                    # 计算新粘贴图像的位置
                    new_coords = self.calculate_image_position(images_on_page, image_path)

                    # 将图像显示在画布上，并获取图像的ID
                    image_id = self.display_image(image_path, new_coords)
                    # 将图像的信息（路径、坐标和ID）存储到当前页面的图像列表中
                    self.canvas_pages[self.page_number]["images"].append(
                        {"path": image_path, "coords": new_coords, "image_id": image_id})
                else:
                    # 如果当前页面的图像数量已经达到3张，显示警告信息
                    messagebox.showwarning("粘贴错误", "每个页面只能粘贴三张图像.")
            else:
                # 如果剪贴板没有图像数据，显示警告信息
                messagebox.showwarning("粘贴错误", "剪贴板中没有有效的图片数据.")
        except Exception as e:
            # 如果发生任何异常，显示错误信息
            messagebox.showerror("粘贴错误", f"无法从剪贴板粘贴图片: {str(e)}")

    def calculate_image_position(self, images_on_page, image_path):
        # 计算新粘贴的图像位置
        # 如果当前页面没有任何图像，返回坐标(0,0)
        if not images_on_page:
            return 0, 0

        # 获取最后一张图像的信息
        last_image = images_on_page[-1]
        last_image_path = last_image["path"]
        last_image_coords = last_image["coords"]

        # 打开最后一张图像并获取其宽度和高度坐标
        last_image_obj = Image.open(last_image_path)
        last_image_width, _ = last_image_obj.size
        _, y = last_image_coords

        # 打开新粘贴的图像并获取其宽度（高度可以忽略，因为布局时只考虑宽度）
        new_image_obj = Image.open(image_path)
        new_image_width, _ = new_image_obj.size

        # 向左偏移量
        offset = 30

        # 如果最后一张图像的右边缘加上新图像的宽度超过了画布的宽度
        # 那么新图像将放置在新的一行的起始位置（即 x=0，y=最后一张图像的纵坐标加上其高度）
        if last_image_coords[0] + last_image_width + new_image_width > self.canvas.winfo_width():
            new_x = 0
            new_y = y + new_image_obj.size[1]
        else:
            # 否则，新图像放置在最后一张图像的右边（即 x=最后一张图像的右边缘减去偏移量，y=最后一张图像的纵坐标）
            new_x = last_image_coords[0] + last_image_width - offset
            new_y = y

        return new_x, new_y

    def display_image(self, image_path, coords, _item=None):
        # 显示图像在画布上
        image = Image.open(image_path)
        width, height = image.size
        new_height = 500
        new_width = int(width * (new_height / height))
        resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)
        image_tk = ImageTk.PhotoImage(resized_image)

        image_id = self.canvas.create_image(coords[0], coords[1], anchor='nw', image=image_tk)
        self.canvas.tag_bind(image_id, "<ButtonPress-1>", self.on_image_press)
        self.canvas.tag_bind(image_id, "<B1-Motion>", self.on_image_move)
        self.canvas.tag_bind(image_id, "<ButtonRelease-1>", self.on_image_release)
        self.image_references.append(image_tk)
        return image_id

    def on_image_press(self, event):
        # 图像按下事件处理
        item = self.canvas.find_closest(event.x, event.y)[0]
        self.drag_data["item"] = item
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_image_move(self, event):
        # 图像移动事件处理
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]
        self.canvas.move(self.drag_data["item"], delta_x, delta_y)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_image_release(self, event):
        # 图像释放事件处理
        item_coords = self.canvas.coords(self.drag_data["item"])
        for image_info in self.canvas_pages[self.page_number]["images"]:
            if image_info["image_id"] == self.drag_data["item"]:
                image_info["coords"] = (item_coords[0], item_coords[1])
                break
        self.drag_data["item"] = None
    def import_screenshot(self):
        # 从指定路径导入截图图片，并粘贴到当前画布页第一张图片右侧
        screenshot_path = "C:\\Users\\Administrator\\Desktop\\GL\\GL.png"
        images_on_page = self.canvas_pages[self.page_number]["images"]

        if os.path.exists(screenshot_path):
            if len(images_on_page) == 0:
                image_path = screenshot_path
            else:
                # 获取第一张图片的位置信息
                first_image_coords = images_on_page[0]["coords"]
                image_path = screenshot_path
                new_coords = (first_image_coords[0] + 250, first_image_coords[1])  # 放置在第一张图片的右侧
            image_id = self.display_image(image_path, new_coords)

            # 存储图片信息到当前页面的图像列表中
            self.canvas_pages[self.page_number]["images"].append(
                {"path": image_path, "coords": new_coords, "image_id": image_id})
        else:
            messagebox.showerror("导入截图错误", "指定路径下找不到图片文件。")

    def display_image(self, image_path, coords, _item=None):
        image = Image.open(image_path)
        width, height = image.size
        new_width = 270
        new_height = int(height * (new_width / width))
                # 使用 LANCOZ 方法代替 ANTIALIAS 方法
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)

        try:
            image_tk = ImageTk.PhotoImage(resized_image)
        except:
            messagebox.showerror("保存截图错误", "无法保存图像，请重试。")
            return None

        image_id = self.canvas.create_image(coords[0], coords[1], anchor='nw', image=image_tk)
        self.canvas.tag_bind(image_id, "<ButtonPress-1>", self.on_image_press)
        self.canvas.tag_bind(image_id, "<B1-Motion>", self.on_image_move)
        self.canvas.tag_bind(image_id, "<ButtonRelease-1>", self.on_image_release)
        self.image_references.append(image_tk)
        return image_id
    def copy_data_to_clipboard(self):
        # 复制文本框数据到剪切板
        data_to_copy = self.textbox.get("1.0", tk.END).strip()
        self.master.clipboard_clear()
        self.master.clipboard_append(data_to_copy)

    def save_data(self):
        # 保存所有页面的数据
        with open("data_6.txt", "w") as f:
            f.write(str(self.canvas_pages))

    def load_data(self):
        # 加载保存的数据
        if os.path.exists("data_6.txt"):
            with open("data_6.txt", "r") as f:
                self.canvas_pages = eval(f.read())
            self.load_page(self.page_number)




# 设置根Tkinter窗口
root = tk.Tk()
root.title("社群交单管理工具         孤风出品--必属精品")
app = CanvasFrame(master=root)
app.pack(fill="both", expand=True)
app.load_data()


# 定义窗口关闭事件的操作
def on_closing():
    app.save_page()
    app.save_data()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()