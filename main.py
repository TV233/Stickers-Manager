import os
import glob
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QScrollArea, QComboBox, QDialog
from PyQt5.QtGui import QPixmap, QClipboard, QMovie
from PyQt5.QtCore import Qt, QMimeData, QUrl, QTimer
from PyQt5 import uic

class PreviewDialog(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GIF Preview")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        
        # 创建预览标签
        self.preview_label = QLabel(self)
        layout = QGridLayout(self)
        layout.addWidget(self.preview_label)
        
        # 加载原始GIF
        self.movie = QMovie(image_path)
        # 获取GIF原始尺寸
        self.movie.jumpToFrame(0)
        size = self.movie.currentImage().size()
        self.preview_label.setFixedSize(size)
        self.preview_label.setMovie(self.movie)
        self.movie.start()
        
        # 调整窗口大小以适应内容
        self.adjustSize()

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.movie = None
        self.static_pixmap = None
        self.original_image_path = None
        self.preview_dialog = None
        # 添加预览延时定时器
        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)  # 设置为单次触发
        self.preview_timer.timeout.connect(self.showPreview)
        self.preview_delay = 300  # 300毫秒延时

    def enterEvent(self, event):
        if self.original_image_path and self.original_image_path.lower().endswith('.gif'):
            # 启动延时定时器
            self.preview_timer.start(self.preview_delay)
        event.accept()

    def leaveEvent(self, event):
        # 取消定时器
        self.preview_timer.stop()
        if self.preview_dialog:
            self.preview_dialog.close()
            self.preview_dialog = None
        event.accept()

    def showPreview(self):
        # 创建预览窗口
        if not self.preview_dialog:
            self.preview_dialog = PreviewDialog(self.original_image_path, self.window())
            
            # 计算预览窗口位置
            global_pos = self.mapToGlobal(self.rect().topRight())
            self.preview_dialog.move(global_pos)
            
        self.preview_dialog.show()

class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('k.ui', self)  # 加载UI文件
        self.setWindowTitle('Stickers Manager Beta')
        
        # 使用UI文件中的ComboBox
        self.groupComboBox = self.findChild(QComboBox, 'comboBox')
        self.loadGroups()
        self.groupComboBox.currentIndexChanged.connect(self.onGroupChanged)
        
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)

        self.container = QWidget()
        self.scrollArea.setWidget(self.container)
        self.scrollArea.move(200, 0)
        self.layout = QGridLayout(self.container)
        self.layout.setSpacing(10)  # 设置网格间距
        self.container.setLayout(self.layout)

        self.loadImages()
        
        # 添加这行来显示窗口
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
            label = ImageLabel(self)
            label.original_image_path = image_file
            
            # 显示缩略图
            pixmap = QPixmap(image_file)
            scaled_pixmap = pixmap.scaled(170, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(scaled_pixmap)
            label.static_pixmap = scaled_pixmap
            label.setFixedSize(170, 150)
            label.mousePressEvent = lambda event, label=label: self.copyImageToClipboard(event, label)
            self.layout.addWidget(label, row, col)

            col += 1
            if col == 7:
                col = 0
                row += 1
        
        # 计算一行需要的宽度（7个图片 + 间距）
        total_width = 7 * 170 + 8 * self.layout.spacing()  # 7个图片宽度 + 8个间距
        
        # 计算需要的总高度（最多显示5行）
        total_rows = min(5, max(1, (len(image_files) + 6) // 7))  # 限制最多5行，至少1行
        needed_height = total_rows * 150 + (total_rows + 1) * self.layout.spacing()
        
        # 设置容器的最小宽度，确保内容不会被压缩
        self.container.setMinimumWidth(total_width)
        
        # 设置滚动区域的大小，水平方向不设置固定值
        self.scrollArea.setFixedHeight(needed_height)  # 只固定高度
        self.scrollArea.setMinimumWidth(total_width)  # 设置最小宽度
        
        # 调整窗口大小（考虑左侧ComboBox的宽度）
        window_width = total_width + 240  # 200是ComboBox区域宽度，加上一些边距
        window_height = needed_height + 20
        self.setGeometry(100, 100, window_width, window_height)
        
        # 禁用水平滚动条
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def copyImageToClipboard(self, event, label):
        clipboard = QApplication.clipboard()
        
        if label.original_image_path.lower().endswith('.gif'):
            # 对于GIF图片，使用URI列表方式复制
            mime_data = QMimeData()
            file_path = os.path.abspath(label.original_image_path)
            url = f"file:///{file_path.replace(os.sep, '/')}"
            mime_data.setUrls([QUrl(url)])
            
            # 同时设置图片数据作为后备
            with open(label.original_image_path, 'rb') as gif_file:
                gif_data = gif_file.read()
                mime_data.setData('image/gif', gif_data)
            
            clipboard.setMimeData(mime_data)
        else:
            # 非GIF图片直接使用原始图片
            pixmap = QPixmap(label.original_image_path)
            clipboard.setPixmap(pixmap)
        
        event.accept()

if __name__ == '__main__':
    app = QApplication([])
    window = ImageViewer()
    app.exec_()