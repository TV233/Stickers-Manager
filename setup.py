import sys

if sys.platform == 'darwin':
    from setuptools import setup
    APP = ['main.py']
    DATA_FILES = ['data', 'qml']
    OPTIONS = {
        'argv_emulation': True,
        'packages': ['PyQt5'],
        'includes': ['PIL'],
        'iconfile': 'icon.icns',
        'plist': {
            'CFBundleName': 'StickerManager',
            'CFBundleDisplayName': 'Sticker Manager',
            'CFBundleIdentifier': 'me.vktia.stickermanager',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0'
        }
    }
    setup(
        name='StickerManager',
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )
elif sys.platform.startswith('win'):
    from cx_Freeze import setup, Executable
    build_exe_options = {
        'packages': ['PyQt5', 'PIL'],
        'include_files': [('qml', 'qml'), ('icon.ico', 'icon.ico')]
    }
    setup(
        name='StickerManager',
        version='1.0.0',
        description='Sticker Manager',
        options={'build_exe': build_exe_options},
        executables=[Executable('main.py', base='Win32GUI', icon='icon.ico', target_name='StickersManager.exe')]
    )
else:
    from setuptools import setup
    setup(name='StickerManager')
