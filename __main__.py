import PyInstaller.__main__

PyInstaller.__main__.run([
    'YKFLZ.py',  # 替换为你的脚本名
    '--onefile',  # 创建单个可执行文件
    '--noconsole',  # 不显示命令行控制台（适用于 GUI 应用程序）
    '--name=AutoSplitApp'  # 可执行文件的名称
])
