import sys
import os
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import QUrl
from backend.sticker_manager import StickerManager

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    
    engine = QQmlApplicationEngine()
    
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 添加 QML 导入路径
    engine.addImportPath(os.path.join(current_dir, "qml"))
    
    # 实例化后端逻辑
    sticker_manager = StickerManager()
    
    # 将Python对象注入到QML的根上下文中
    # QML中就可以通过 "stickerManager" 这个名字来访问它
    engine.rootContext().setContextProperty("stickerManager", sticker_manager)
    
    # 加载主QML文件
    qml_file = os.path.join(current_dir, 'qml/main.qml')
    engine.load(QUrl.fromLocalFile(qml_file))
    
    if not engine.rootObjects():
        sys.exit(-1)
        
    sys.exit(app.exec_())
