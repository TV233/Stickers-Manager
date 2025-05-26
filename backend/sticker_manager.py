from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot, QUrl
from PyQt5.QtGui import QPixmap, QClipboard
from PyQt5.QtCore import QMimeData
from PyQt5.QtWidgets import QApplication
from PIL import Image
import os
import glob
import json
import shutil
import sys

# 这个类将掌管所有数据和逻辑，并暴露给QML
class StickerManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._groups = []
        self._current_stickers = []
        self._last_copied_image = ""
        self._current_group = ""
        self._recent_stickers = []  # 存储最近使用的表情路径
        self._load_recent_stickers()  # 加载最近使用记录
        
        # 初始化数据目录
        self._init_data_directory()
        
        self._tags_data = self._load_tags()
        self._current_search = ""
        self._search_in_group = True
        self.scan_sticker_groups()

    # --- 信号：当Python数据变化时，通知QML更新 ---
    groupsChanged = pyqtSignal()
    currentStickersChanged = pyqtSignal()
    copyCompleted = pyqtSignal()
    searchResultsChanged = pyqtSignal()
    tagsChanged = pyqtSignal()

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

    @pyqtProperty(str, notify=searchResultsChanged)
    def currentSearch(self):
        return self._current_search

    @currentSearch.setter
    def currentSearch(self, value):
        if self._current_search != value:
            self._current_search = value
            self._update_search_results()
            self.searchResultsChanged.emit()

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
        """选择分组"""
        self._current_group = group_name
        sticker_urls = []
        
        if group_name == 'recent':
            # 对于最近使用分组，使用记录的顺序
            for path in self._recent_stickers:
                if os.path.exists(path):
                    url = QUrl.fromLocalFile(path).toString()
                    is_anim = self.is_animated(path)
                    sticker_urls.append({
                        'url': url,
                        'animated': is_anim
                    })
        else:
            # 其他分组使用原有逻辑
            image_folder = os.path.join('data', group_name)
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
                for file_path in glob.glob(os.path.join(image_folder, ext)):
                    url = QUrl.fromLocalFile(file_path).toString()
                    is_anim = self.is_animated(file_path)
                    sticker_urls.append({
                        'url': url,
                        'animated': is_anim
                    })
            
            # 只对非最近使用分组进行排序
            sticker_urls = sorted(sticker_urls, key=lambda x: x['url'])
        
        self._current_stickers = sticker_urls
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
    def add_to_favorites(self, image_path):
        """添加到收藏"""
        try:
            local_path = QUrl(image_path).toLocalFile()
            favorites_dir = os.path.join('data', 'favorites')
            target_path = os.path.join(favorites_dir, os.path.basename(local_path))
            
            # 如果已经在收藏夹中，则不重复复制
            if not os.path.exists(target_path):
                shutil.copy2(local_path, target_path)
                
                # 如果原图片有标签，复制标签
                if image_path in self._tags_data:
                    target_url = QUrl.fromLocalFile(target_path).toString()
                    self._tags_data[target_url] = self._tags_data[image_path].copy()
                    self._save_tags()
            
            # 如果当前正在查看收藏夹，刷新显示
            if self._current_group == 'favorites':
                self.select_group('favorites')
                
        except Exception as e:
            print(f"Error adding to favorites: {e}")

    @pyqtSlot(str)
    def remove_from_favorites(self, image_path):
        """从收藏夹中移除"""
        try:
            local_path = QUrl(image_path).toLocalFile()
            if os.path.exists(local_path):
                os.remove(local_path)
                
                # 删除相关标签
                if image_path in self._tags_data:
                    del self._tags_data[image_path]
                    self._save_tags()
                
                # 如果当前在收藏夹中，刷新显示
                if self._current_group == 'favorites':
                    self.select_group('favorites')
        except Exception as e:
            print(f"Error removing from favorites: {e}")

    def _update_recent_stickers(self, image_path):
        """更新最近使用列表"""
        try:
            local_path = QUrl(image_path).toLocalFile()
            recent_dir = os.path.join('data', 'recent')
            
            # 如果是收藏夹或最近使用中的文件，使用原始文件路径
            if '/favorites/' in image_path or '/recent/' in image_path:
                original_path = local_path
            else:
                # 复制文件到最近使用文件夹
                target_path = os.path.join(recent_dir, os.path.basename(local_path))
                if not os.path.exists(target_path):
                    shutil.copy2(local_path, target_path)
                original_path = local_path
            
            # 更新最近使用列表
            if original_path in self._recent_stickers:
                self._recent_stickers.remove(original_path)
            self._recent_stickers.insert(0, original_path)
            
            # 保持最近使用列表最多20个
            while len(self._recent_stickers) > 20:
                old_path = self._recent_stickers.pop()
                old_file = os.path.join(recent_dir, os.path.basename(old_path))
                if os.path.exists(old_file) and '/recent/' in old_file:
                    os.remove(old_file)
            
            # 保存最近使用记录
            self._save_recent_stickers()
            
            # 如果当前正在查看最近使用，刷新显示
            if self._current_group == 'recent':
                self.select_group('recent')
                
        except Exception as e:
            print(f"Error updating recent stickers: {e}")

    @pyqtSlot(str)
    def copy_to_clipboard(self, image_path):
        self._last_copied_image = image_path
        local_path = QUrl(image_path).toLocalFile()
        clipboard = QApplication.clipboard()
        
        # 检查是否为动图
        if self.is_animated(local_path):
            mime_data = QMimeData()
            mime_data.setUrls([QUrl.fromLocalFile(os.path.abspath(local_path))])
            clipboard.setMimeData(mime_data)
        else:
            pixmap = QPixmap(local_path)
            clipboard.setPixmap(pixmap)
        
        # 更新最近使用列表
        self._update_recent_stickers(image_path)
        
        print(f"Copied {local_path} to clipboard.")
        self.copyCompleted.emit()

    @pyqtSlot(str, result=bool)
    def check_animated(self, image_path):
        """暴露给QML的动图检测方法"""
        local_path = QUrl(image_path).toLocalFile()
        return self.is_animated(local_path)

    def _load_tags(self):
        """加载标签数据"""
        tags_file = 'data/tags.json'
        if os.path.exists(tags_file):
            try:
                with open(tags_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_tags(self):
        """保存标签数据"""
        tags_file = 'data/tags.json'
        os.makedirs(os.path.dirname(tags_file), exist_ok=True)
        with open(tags_file, 'w', encoding='utf-8') as f:
            json.dump(self._tags_data, f, ensure_ascii=False, indent=2)
        self.tagsChanged.emit()

    @pyqtSlot(str, str)
    def add_tag(self, image_path, tag):
        """为图片添加标签"""
        if not image_path in self._tags_data:
            self._tags_data[image_path] = []
        if tag not in self._tags_data[image_path]:
            self._tags_data[image_path].append(tag)
            self._save_tags()
            # 发送标签更新信号
            self.tagsChanged.emit()

    @pyqtSlot(str, str)
    def remove_tag(self, image_path, tag):
        """移除图片的标签"""
        if image_path in self._tags_data and tag in self._tags_data[image_path]:
            self._tags_data[image_path].remove(tag)
            if not self._tags_data[image_path]:
                del self._tags_data[image_path]
            self._save_tags()

    @pyqtSlot(str, result='QVariantList')
    def get_tags(self, image_path):
        """获取图片的所有标签"""
        return self._tags_data.get(image_path, [])

    @pyqtSlot(str)
    def delete_sticker(self, image_path):
        """删除表情包"""
        local_path = QUrl(image_path).toLocalFile()
        try:
            # 删除文件
            os.remove(local_path)
            # 删除相关标签
            if image_path in self._tags_data:
                del self._tags_data[image_path]
                self._save_tags()
            # 刷新当前分组
            if self._current_group:
                self.select_group(self._current_group)
        except Exception as e:
            print(f"Error deleting sticker: {e}")

    def _update_search_results(self):
        """更新搜索结果"""
        if not self._current_search:
            if self._current_group:
                self.select_group(self._current_group)
            return

        search_terms = self._current_search.lower().split()
        results = []

        def check_tags(image_path):
            """检查图片标签是否匹配搜索条件"""
            if image_path not in self._tags_data:
                return False
            tags = [t.lower() for t in self._tags_data[image_path]]
            return all(any(term in tag for tag in tags) for term in search_terms)

        # 在指定范围内搜索
        search_paths = []
        if self._search_in_group and self._current_group:
            # 当前分组内搜索
            group_path = os.path.join('data', self._current_group)
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
                search_paths.extend(glob.glob(os.path.join(group_path, ext)))
        else:
            # 全局搜索
            for group in self._groups:
                group_path = os.path.join('data', group['name'])
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
                    search_paths.extend(glob.glob(os.path.join(group_path, ext)))

        # 处理搜索结果
        for file_path in search_paths:
            url = QUrl.fromLocalFile(file_path).toString()
            if check_tags(url):
                is_anim = self.is_animated(file_path)
                results.append({
                    'url': url,
                    'animated': is_anim
                })

        self._current_stickers = sorted(results, key=lambda x: x['url'])
        self.currentStickersChanged.emit()

    @pyqtSlot(str)
    def search(self, query):
        """搜索表情包"""
        self._current_search = query
        self._update_search_results()

    @pyqtSlot(bool)
    def set_search_scope(self, in_group):
        """设置搜索范围"""
        self._search_in_group = in_group
        if self._current_search:
            self._update_search_results()

    def _init_data_directory(self):
        """初始化数据目录结构"""
        # 获取应用程序包内的资源路径
        if getattr(sys, 'frozen', False):
            # 如果是打包后的应用
            bundle_dir = os.path.dirname(sys.executable)
            data_path = os.path.join(os.path.expanduser('~/Library/Application Support/StickerManager'), 'data')
        else:
            # 开发环境
            data_path = 'data'
            
        if not os.path.exists(data_path):
            os.makedirs(data_path)
            
        # 只创建收藏和最近使用文件夹
        default_groups = ['favorites', 'recent']
        for group in default_groups:
            group_path = os.path.join(data_path, group)
            if not os.path.exists(group_path):
                os.makedirs(group_path)
        
        # 创建标签文件
        tags_file = os.path.join(data_path, 'tags.json')
        if not os.path.exists(tags_file):
            with open(tags_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def _load_recent_stickers(self):
        """加载最近使用记录"""
        recent_file = os.path.join('data', 'recent.json')
        if os.path.exists(recent_file):
            try:
                with open(recent_file, 'r', encoding='utf-8') as f:
                    self._recent_stickers = json.load(f)
            except:
                self._recent_stickers = []

    def _save_recent_stickers(self):
        """保存最近使用记录"""
        recent_file = os.path.join('data', 'recent.json')
        with open(recent_file, 'w', encoding='utf-8') as f:
            json.dump(self._recent_stickers, f, ensure_ascii=False)