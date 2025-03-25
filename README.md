# Stickers Manager / 表情包管理器

### Introduction / 介绍
Stickers Manager is a lightweight desktop application for managing and using image stickers. It provides an intuitive interface for organizing and quickly copying stickers to the clipboard.
表情包管理器是一款轻量级的桌面应用程序，用于管理和使用图片表情包。它提供了一个直观的界面，可以快速整理和复制表情包到剪贴板。

### Features / 功能
- Group-based sticker organization / 基于分组的表情包管理
- Quick copy to clipboard with single click / 单击快速复制到剪贴板
- GIF preview on hover / 悬停预览GIF动画
- Support for multiple image formats (JPG, PNG, GIF, WebP) / 支持多种图片格式（JPG, PNG, GIF, WebP）
- Smooth group switching / 流畅的分组切换
- Responsive UI design / 响应式UI设计

### Usage / 使用说明
1. Place your sticker images in subfolders under the `data` directory / 将表情包图片放入data目录下的子文件夹中 
2. Launch the application / 启动应用程序
3. Select a sticker group from the left panel / 从左侧面板选择表情包分组
4. Click any sticker to copy it to clipboard / 单击任意表情包即可复制到剪贴板
5. Hover over GIF stickers to preview animation / 悬停GIF表情包可预览动画

### Installation / 安装方法

#### For Windows / Windows 平台
1. Download the latest release package from Releases / 从Releases下载最新版本
2. Extract the package to your desired location / 将压缩包解压到目标位置
3. Create a data folder in the same directory as the executable / 在exe文件同目录下创建data文件夹
4. Place your sticker images in subfolders under the data directory / 将表情包图片放入data目录下的子文件夹中
5. Run StickersManager.exe to start the application / 运行StickersManager.exe启动应用程序

#### For Liunx / Linux 平台 
#### Method 1: Using AppImage (Recommended) / 方法1：使用AppImage（推荐）
1. Download the latest `StickersManager.AppImage` from [Releases](https://github.com/TV233/Stickers-Manager/releases) / 从[Releases](https://github.com/TV233/Stickers-Manager/releases)下载最新的StickersManager.AppImage
2. Make it executable: / 赋予可执行权限：
   ```bash
   chmod +x StickersManager.AppImage
   ```
3. Run it: / 运行：
   ```bash
   ./StickersManager.AppImage
   ```

#### Method 2: From Source / 方法2：从源码运行
1. Clone the repository: / 克隆仓库：
   ```bash
   git clone https://github.com/TV233/Stickers-Manager.git
   cd Stickers-Manager
   ```
2. Create and activate virtual environment: / 创建并激活虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies: / 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application: / 运行应用程序：
   ```bash
   python main.py
   ```
