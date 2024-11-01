import os
import glob
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QScrollArea, QComboBox, QDialog, QHBoxLayout, QVBoxLayout, QMessageBox
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
        # 添加预览延时定时
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
        self.group_name = group_name  # 直保存组名
        
        # 设置固定高度
        self.setFixedHeight(40)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # 预览图
        preview_label = QLabel()
        if preview_path:
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
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.loading = False  # 添加加载状态标志
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Stickers Manager Beta')
        
        # 创建主布局
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建左侧分组面板的滚动区域
        group_scroll = QScrollArea()
        group_scroll.setWidgetResizable(True)
        group_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        group_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        group_scroll.setFixedWidth(220)  # 稍微加宽以适应滚动条
        
        # 创建分组面板容器
        group_panel = QWidget()
        group_layout = QVBoxLayout(group_panel)
        group_layout.setSpacing(5)
        group_layout.setContentsMargins(5, 5, 5, 5)
        group_layout.setAlignment(Qt.AlignTop)  # 确保按钮从顶部开始排列
        
        # 加载分组并打印调试信息
        data_path = 'data'
        groups = []
        # 获取所有文件夹并进行自然排序
        for item in os.listdir(data_path):
            item_path = os.path.join(data_path, item)
            if os.path.isdir(item_path):
                groups.append(item)
        groups.sort()  # 自然排序
        
        print(f"Found {len(groups)} groups: {groups}")  # 调试输出
        
        added_buttons = 0  # 计数添加的按钮数量
        for group_name in groups:
            group_path = os.path.join(data_path, group_name)
            # 获取第一个图片作为预览
            preview_path = None
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
                files = glob.glob(os.path.join(group_path, ext))
                if files:
                    preview_path = files[0]
                    break
            
            # 只要是文件夹就添加按钮，不管是否找到预览图
            group_btn = GroupButton(group_name, preview_path or '')  # 如果没有预览图，使用空字符串
            group_btn.clicked.connect(self.onGroupSelected)
            group_layout.addWidget(group_btn)
            added_buttons += 1
            print(f"Added button for group: {group_name}")  # 调试输出
        
        print(f"Total buttons added: {added_buttons}")  # 调试输出
        
        # 设置分组面板的最小高度，确保足够显示所有按钮
        total_height = added_buttons * 45  # 每个按钮40高度 + 5间距
        group_panel.setMinimumHeight(total_height)
        
        # 设置滚动区域的内容
        group_scroll.setWidget(group_panel)
        
        # 设置滚动区域的最大高度（与图片显示区域相同）
        max_visible_height = 5 * 150 + 6 * 10  # 5行图片高度 + 间距
        group_scroll.setMaximumHeight(max_visible_height)
        
        # 创建图片显示区域的滚动区域
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.container = QWidget()
        self.layout = QGridLayout(self.container)
        self.layout.setSpacing(10)
        self.scrollArea.setWidget(self.container)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        main_layout.addWidget(group_scroll)
        main_layout.addWidget(self.scrollArea)
        
        # 设置初始大小
        self.setMinimumSize(1200, 600)
        
        # 加载默认分组的图片
        if groups:
            self.current_group = groups[0]
            self.loadImages()
        
        self.show()
    
    def onGroupSelected(self, group_name):
        if self.loading or self.current_group == group_name:  # 避免重复加载相同分组
            return
        
        print(f"Switching to group: {group_name}")
        try:
            self.loading = True
            self.current_group = group_name
            
            # 检查分组是否为空
            image_folder = os.path.join('data', self.current_group)
            has_images = any(glob.glob(os.path.join(image_folder, ext)) 
                           for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp'])
            
            if not has_images:
                QMessageBox.information(self, "提示", f"分组 '{self.current_group}' 中没有图片")
                return
            
            self.clearImages()
            self.loadImages()
            
        except Exception as e:
            print(f"Error during group switch: {e}")
            QMessageBox.warning(self, "错误", f"切换分组时发生错误: {str(e)}")
        finally:
            self.loading = False

    def disableGroupButtons(self):
        # 禁用所有分组按钮，防止连续快速点击
        for button in self.findChildren(GroupButton):
            button.setEnabled(False)

    def enableGroupButtons(self):
        # 重新启用所有分组按钮
        for button in self.findChildren(GroupButton):
            button.setEnabled(True)

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
            
        print(f"Loading images for group: {self.current_group}")
        image_folder = os.path.join('data', self.current_group)
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(image_folder, ext)))
        
        if not image_files:
            return
        
        try:
            # 创建占位网格
            row = 0
            col = 0
            placeholders = []
            
            # 预先计算布局参数
            total_width = 7 * 170 + 8 * self.layout.spacing()
            total_rows = min(5, max(1, (len(image_files) + 6) // 7))
            needed_height = total_rows * 150 + (total_rows + 1) * self.layout.spacing()
            
            # 设置容器和滚动区域大小
            self.container.setMinimumWidth(total_width)
            self.scrollArea.setFixedHeight(needed_height)
            self.scrollArea.setMinimumWidth(total_width)
            
            # 批量创建标签
            for i in range(len(image_files)):
                label = ImageLabel(self)
                label.setFixedSize(170, 150)
                self.layout.addWidget(label, row, col)
                placeholders.append((label, image_files[i]))
                
                col += 1
                if col == 7:
                    col = 0
                    row += 1
            
            # 使用更大的批次size加载图片
            batch_size = 35  # 增加批次大小
            for i in range(0, len(placeholders), batch_size):
                batch = placeholders[i:i + batch_size]
                for label, image_file in batch:
                    try:
                        pixmap = QPixmap(image_file)
                        scaled_pixmap = pixmap.scaled(170, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        label.setPixmap(scaled_pixmap)
                        label.original_image_path = image_file
                        label.static_pixmap = scaled_pixmap
                        label.mousePressEvent = partial(self.copyImageToClipboard, label=label)
                    except Exception as e:
                        print(f"Error loading image {image_file}: {e}")
                        continue
                QApplication.processEvents()  # 每批次处理完后才更新UI
            
        except Exception as e:
            print(f"Error in loadImages: {e}")

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