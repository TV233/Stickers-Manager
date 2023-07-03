import os
import glob
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QScrollArea
from PyQt5.QtGui import QPixmap, QClipboard
from PyQt5.QtCore import Qt
from PyQt5 import uic

class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('k.ui', self)  # 加载UI文件
        self.setWindowTitle('Stickers Manager Beta')
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)

        self.container = QWidget()
        self.scrollArea.setWidget(self.container)
        self.scrollArea.setFixedSize(1200, 780)
        self.scrollArea.move(200,0)
        self.layout = QGridLayout(self.container)
        self.container.setLayout(self.layout)

        self.loadImages()
        # 设置程序窗口的初始大小
        self.setGeometry(100, 100, 1400, 800)  
        self.show()

    def loadImages(self):
        image_folder = 'data/group1'                 # 图像文件夹路径
        image_files = glob.glob(os.path.join(image_folder, '*.jpg'))  # 获取所有jpg文件

        row = 0
        col = 0

        for image_file in image_files:
            label = QLabel(self)
            pixmap = QPixmap(image_file)
            pixmap = pixmap.scaled(170, 150, aspectRatioMode=True)  # 缩放图片到合适尺寸
            label.setPixmap(pixmap)
            label.mousePressEvent = lambda event, label=label: self.copyImageToClipboard(event, label)  # 将自定义的鼠标点击事件绑定到label上
            self.layout.addWidget(label, row, col)

            col += 1
            if col == 7:  # 每行最多显示7张图片
                col = 0
                row += 1

    def copyImageToClipboard(self, event, label):
        pixmap = label.pixmap()
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(pixmap, mode=QClipboard.Clipboard) # 图片复制到剪贴板
        event.accept()

if __name__ == '__main__':
    app = QApplication([])
    window = ImageViewer()
    app.exec_()