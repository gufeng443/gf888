from pywinauto import Application
import time

# 1. 连接窗口时增加精准定位参数
app = Application(backend="uia").connect(
    class_name="ApplicationFrameWindow",
    title="WhatsApp",  # 优先用 title 精确匹配
    control_type="Window"  # 显式指定控件类型‌:ml-citation{ref="2,3" data="citationList"}
)

# 2. 定位到主容器并显式等待控件加载
main_container = app.window(title="WhatsApp")
main_container.wait("ready", timeout=15)  # 确保控件树就绪‌:ml-citation{ref="4,5" data="citationList"}

# 3. 增加容错判断
if main_container.exists():
    ctrl_tree = main_container.dump_tree()
    if ctrl_tree:
        with open("whatsapp_controls.txt", "w", encoding="utf-8") as f:
            f.write(ctrl_tree)
    else:
        print("控件树内容为空，请检查窗口句柄或控件加载状态")
else:
    print("主窗口未找到，请验证连接参数")
