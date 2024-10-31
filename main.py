import os
import glob
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QScrollArea, QComboBox
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
        
        # 使用UI文件中的ComboBox，不再手动创建
        self.groupComboBox = self.findChild(QComboBox, 'comboBox')  # 假设UI中的ComboBox对象名为'comboBox'
        self.loadGroups()
        self.groupComboBox.currentIndexChanged.connect(self.onGroupChanged)
        
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)

        self.container = QWidget()
        self.scrollArea.setWidget(self.container)
        self.scrollArea.setFixedSize(1200, 780)
        self.scrollArea.move(200,0)
        self.layout = QGridLayout(self.container)
        self.container.setLayout(self.layout)

        self.loadImages()
        self.setGeometry(100, 100, 1400, 800)  
        self.show()

    def loadGroups(self):
        # 获取data目录下的所有文件夹
        data_path = 'data'
        groups = []
        # 遍历data目录下的所有项目
        for item in os.listdir(data_path):
            item_path = os.path.join(data_path, item)
            # 只添加文件夹
            if os.path.isdir(item_path):
                groups.append(item)
        
        # 排序文件夹名称
        groups.sort()
        
        self.groupComboBox.clear()  # 清除UI中的默认项
        self.groupComboBox.addItems(groups)

    def onGroupChanged(self, index):
        # 当选择的组发生变化时，清除现有图片并加载新组的图片
        self.clearImages()
        self.loadImages()

    def clearImages(self):
        # 清除所有现有的图片
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def loadImages(self):
        # 获取当前选中的组
        current_group = self.groupComboBox.currentText()
        image_folder = os.path.join('data', current_group)
        
        # 支持多种图片格式
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']
        image_files = []
        
        # 获取所有支持格式的图片文件
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(image_folder, ext)))
        
        row = 0
        col = 0

        for image_file in image_files:
            label = QLabel(self)
            pixmap = QPixmap(image_file)
            pixmap = pixmap.scaled(170, 150, aspectRatioMode=True)
            label.setPixmap(pixmap)
            label.mousePressEvent = lambda event, label=label: self.copyImageToClipboard(event, label)
            self.layout.addWidget(label, row, col)

            col += 1
            if col == 7:
                col = 0
                row += 1

    def copyImageToClipboard(self, event, label):
        pixmap = label.pixmap()
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(pixmap, mode=QClipboard.Clipboard)
        event.accept()

if __name__ == '__main__':
    app = QApplication([])
    window = ImageViewer()
    app.exec_()