import os
import glob
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QScrollArea, QComboBox, QDialog, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap, QClipboard, QMovie
from PyQt5.QtCore import Qt, QMimeData, QUrl, QTimer
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from concurrent.futures import ThreadPoolExecutor
from functools import partial

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

class GroupButton(QWidget):
    clicked = pyqtSignal(str)  # 自定义信号，传递组名
    
    def __init__(self, group_name, preview_path, parent=None):
        super().__init__(parent)
        self.group_name = group_name  # 直接保存组名
        
        # 设置固定高度
        self.setFixedHeight(40)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # 预览图
        preview_label = QLabel()
        pixmap = QPixmap(preview_path)
        scaled_pixmap = pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        preview_label.setPixmap(scaled_pixmap)
        preview_label.setFixedSize(30, 30)
        
        # 组名标签
        name_label = QLabel(group_name)
        
        layout.addWidget(preview_label)
        layout.addWidget(name_label)
        layout.addStretch()
        
        # 设置样式
        self.setStyleSheet("""
            GroupButton {
                background-color: #f0f0f0;
                border-radius: 5px;
                padding: 5px;
            }
            GroupButton:hover {
                background-color: #e0e0e0;
            }
        """)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print(f"Clicked group: {self.group_name}")  # 调试输出
            self.clicked.emit(self.group_name)
            super().mousePressEvent(event)

class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.current_group = None
        self.thread_pool = ThreadPoolExecutor(max_workers=4)  # 创建线程池
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Stickers Manager Beta')
        
        # 创建主布局
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建左侧分组面板
        group_panel = QWidget()
        group_layout = QVBoxLayout(group_panel)
        group_layout.setSpacing(5)
        group_layout.setContentsMargins(5, 5, 5, 5)
        
        # 加载分组
        data_path = 'data'
        groups = sorted(os.listdir(data_path))
        for group_name in groups:
            group_path = os.path.join(data_path, group_name)
            if os.path.isdir(group_path):
                # 获取第一个图片作为预览
                preview_path = None
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
                    files = glob.glob(os.path.join(group_path, ext))
                    if files:
                        preview_path = files[0]
                        break
                
                if preview_path:
                    group_btn = GroupButton(group_name, preview_path)
                    group_btn.clicked.connect(self.onGroupSelected)
                    group_layout.addWidget(group_btn)
        
        group_layout.addStretch()
        group_panel.setFixedWidth(200)
        
        # 创建滚动区域
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.container = QWidget()
        self.layout = QGridLayout(self.container)
        self.layout.setSpacing(10)
        self.scrollArea.setWidget(self.container)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        main_layout.addWidget(group_panel)
        main_layout.addWidget(self.scrollArea)
        
        # 设置初始大小
        self.setMinimumSize(1200, 600)
        
        # 加载默认分组的图片
        if groups:
            self.current_group = groups[0]
            self.loadImages()
        
        self.show()
    
    def onGroupSelected(self, group_name):
        print(f"Switching to group: {group_name}")  # 调试输出
        if self.current_group != group_name:
            self.current_group = group_name
            self.clearImages()
            self.loadImages()
            print(f"Switched to group: {self.current_group}")  # 调试输出

    def clearImages(self):
        print("Clearing images")  # 调试输出
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        print("Images cleared")  # 调试输出

    def loadImages(self):
        if not self.current_group:
            return
            
        image_folder = os.path.join('data', self.current_group)
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(image_folder, ext)))
        
        # 计算布局参数
        total_width = 7 * 170 + 8 * self.layout.spacing()
        total_rows = min(5, max(1, (len(image_files) + 6) // 7))
        needed_height = total_rows * 150 + (total_rows + 1) * self.layout.spacing()
        
        # 设置容器和滚动区域大小
        self.container.setMinimumWidth(total_width)
        self.scrollArea.setFixedHeight(needed_height)
        self.scrollArea.setMinimumWidth(total_width)
        
        # 创建占位网格
        row = 0
        col = 0
        placeholders = []
        for i in range(len(image_files)):
            label = ImageLabel(self)
            label.setFixedSize(170, 150)
            self.layout.addWidget(label, row, col)
            placeholders.append((label, image_files[i]))
            
            col += 1
            if col == 7:
                col = 0
                row += 1
        
        # 分批加载图片
        def load_image(args):
            label, image_file = args
            pixmap = QPixmap(image_file)
            scaled_pixmap = pixmap.scaled(170, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            return label, image_file, scaled_pixmap
        
        def update_image(result):
            label, image_file, scaled_pixmap = result
            label.setPixmap(scaled_pixmap)
            label.original_image_path = image_file
            label.static_pixmap = scaled_pixmap
            label.mousePressEvent = partial(self.copyImageToClipboard, label=label)
        
        # 使用线程池加载图片
        batch_size = 20  # 每批加载的图片数量
        for i in range(0, len(placeholders), batch_size):
            batch = placeholders[i:i + batch_size]
            futures = [self.thread_pool.submit(load_image, args) for args in batch]
            for future in futures:
                result = future.result()
                update_image(result)
                QApplication.processEvents()  # 让界面保持响应

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