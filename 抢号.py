import pyautogui
import cv2
import numpy as np
import time

# 配置路径和图像文件
IMAGE_01_PATH = "01.png"  # 要监控的图标（如抢号按钮）
IMAGE_02_PATH = "0.2.png"  # 需要点击的目标图标（例如弹出确认框或按钮）

# 获取屏幕截图
def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot_cv = np.array(screenshot)
    screenshot_cv = cv2.cvtColor(screenshot_cv, cv2.COLOR_RGB2GRAY)  # 转换为灰度图像
    return screenshot_cv

# 查找图像位置
def find_image_on_screen(image_path, screenshot, threshold=0.8):
    target_img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # 读取目标图像并转换为灰度图像
    result = cv2.matchTemplate(screenshot, target_img, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)  # 匹配到的位置
    if locations[0].size > 0:
        max_loc = (locations[1][0], locations[0][0])  # 获取最大匹配位置
        return max_loc  # 返回图像位置
    return None

# 模拟右键点击目标图像
def right_click_on_image(image_position):
    if image_position:
        pyautogui.rightClick(image_position)
        print(f"右键点击位置: {image_position}")

# 模拟左键点击目标图像
def left_click_on_image(image_position):
    if image_position:
        pyautogui.click(image_position)
        print(f"左键点击位置: {image_position}")

# 监控桌面并执行操作
def monitor_and_automate():
    last_screenshot = capture_screenshot()  # 捕获初始屏幕截图
    print("开始监控屏幕，等待目标图像出现...")

    while True:
        # 捕获当前屏幕截图
        screenshot = capture_screenshot()

        # 检查新图标是否出现
        print("检查是否出现目标图像: 01.png")
        position_01 = find_image_on_screen(IMAGE_01_PATH, screenshot)

        if position_01:
            print("找到图像 01.png，模拟右键点击...")
            right_click_on_image(position_01)

            # 查找“0.2.png”图标的位置
            print("等待出现目标图像: 0.2.png")
            position_02 = None
            while position_02 is None:
                position_02 = find_image_on_screen(IMAGE_02_PATH, capture_screenshot())
                time.sleep(0.5)  # 每0.5秒检查一次，避免过度消耗CPU

            print("找到图像 0.2.png，模拟左键点击...")
            left_click_on_image(position_02)

            # 更新当前截图，防止重复点击
            last_screenshot = screenshot

        # 每2秒钟再次检查
        time.sleep(2)


if __name__ == "__main__":
    monitor_and_automate()
