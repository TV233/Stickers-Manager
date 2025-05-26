from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot, QUrl
from PyQt5.QtGui import QPixmap, QClipboard
from PyQt5.QtCore import QMimeData
from PyQt5.QtWidgets import QApplication
from PIL import Image
import os
import glob# 用于检测图片类型

# 这个类将掌管所有数据和逻辑，并暴露给QML
class StickerManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._groups = []
        self._current_stickers = []
        self._last_copied_image = ""
        self.scan_sticker_groups()

    # --- 信号：当Python数据变化时，通知QML更新 ---
    groupsChanged = pyqtSignal()
    currentStickersChanged = pyqtSignal()
    copyCompleted = pyqtSignal()

    # --- 属性：让QML可以直接访问这些数据 ---
    @pyqtProperty(list, notify=groupsChanged)
    def groups(self):
        return self._groups

    @pyqtProperty(list, notify=currentStickersChanged)
    def currentStickers(self):
        return self._current_stickers

    @pyqtProperty(str)
    def lastCopiedImage(self):
        return self._last_copied_image

    # --- 槽函数：让QML可以调用这些Python函数 ---
    @pyqtSlot()
    def scan_sticker_groups(self):
        data_path = 'data'
        scanned_groups = []
        
        # 获取所有文件夹并排序
        for item in sorted(os.listdir(data_path)):
            item_path = os.path.join(data_path, item)
            if os.path.isdir(item_path):
                # 查找预览图
                preview_path = None
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
                    files = glob.glob(os.path.join(item_path, ext))
                    if files:
                        # 转换为 QML 可用的 URL 格式
                        preview_path = QUrl.fromLocalFile(files[0]).toString()
                        break
                
                scanned_groups.append({
                    'name': item,
                    'preview': preview_path or ''
                })

        self._groups = scanned_groups
        self.groupsChanged.emit()
        
        # 默认加载第一个分组
        if self._groups:
            self.select_group(self._groups[0]['name'])

    @pyqtSlot(str)
    def select_group(self, group_name):
        image_folder = os.path.join('data', group_name)
        sticker_urls = []
        
        # 支持的图片格式
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
            for file_path in glob.glob(os.path.join(image_folder, ext)):
                url = QUrl.fromLocalFile(file_path).toString()
                # 检查是否为动图并添加标记
                is_anim = self.is_animated(file_path)
                sticker_urls.append({
                    'url': url,
                    'animated': is_anim
                })
        
        self._current_stickers = sorted(sticker_urls, key=lambda x: x['url'])
        self.currentStickersChanged.emit()

    def is_animated(self, file_path):
        """使用 Pillow 检查图片是否为动图"""
        try:
            with Image.open(file_path) as img:
                # 检查是否有 n_frames 属性且帧数大于1
                try:
                    return getattr(img, 'n_frames', 1) > 1
                except Exception:
                    # 某些格式可能不支持 n_frames
                    try:
                        img.seek(1)  # 尝试访问第二帧
                        return True
                    except EOFError:
                        return False  # 只有一帧
        except Exception as e:
            print(f"Error checking animation for {file_path}: {e}")
            return False

    @pyqtSlot(str)
    def copy_to_clipboard(self, image_path):
        self._last_copied_image = image_path
        local_path = QUrl(image_path).toLocalFile()
        clipboard = QApplication.clipboard()
        
        # 检查是否为动图
        if self.is_animated(local_path):
            # 动图使用文件URL方式复制
            mime_data = QMimeData()
            mime_data.setUrls([QUrl.fromLocalFile(os.path.abspath(local_path))])
            clipboard.setMimeData(mime_data)
        else:
            # 静态图片使用像素数据复制
            pixmap = QPixmap(local_path)
            clipboard.setPixmap(pixmap)
        
        print(f"Copied {local_path} to clipboard.")
        self.copyCompleted.emit()

    @pyqtSlot(str, result=bool)
    def check_animated(self, image_path):
        """暴露给QML的动图检测方法"""
        local_path = QUrl(image_path).toLocalFile()
        return self.is_animated(local_path)