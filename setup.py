from setuptools import setup

APP = ['main.py']  # 替换为你的主程序入口文件名
DATA_FILES = [
    'data',  # 数据目录
    'qml'    # QML文件目录
]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt5'],
    'includes': ['PIL'],
    'iconfile': 'icon.ico',  # 如果你有应用图标的话
    'plist': {
        'CFBundleName': 'StickerManager',
        'CFBundleDisplayName': 'Sticker Manager',
        'CFBundleIdentifier': 'me.vktia.stickermanager',
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': 'Copyright © 2025'
    }
}

setup(
    name="StickerManager",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 