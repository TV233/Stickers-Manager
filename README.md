# Stickers Manager

[English](#english) | [简体中文](#简体中文)

## English

### Introduction
Stickers Manager is a lightweight desktop application for managing and using image stickers. It provides an intuitive interface for organizing and quickly copying stickers to the clipboard.

### Features
- Group-based sticker organization
- Quick copy to clipboard with single click
- GIF preview on hover with delay
- Support for multiple image formats (JPG, PNG, GIF, WebP)
- Smooth group switching with batch loading
- Responsive UI design

### Requirements
- Python 3.6+
- PyQt5

### Installation

#### Create virtual environment

```bash
python -m venv venv
```



#### Activate virtual environment

##### Windows:

```bash
.\venv\Scripts\activate
```

##### Linux/Mac:

```bash
source venv/bin/activate
```

#### Install dependencies

```bash
pip install -r requirements.txt
```

#### Usage

1. Create a `data` directory in the project root
2. Create subfolders in `data` for different sticker groups
3. Place your sticker images in these subfolders
4. Launch the application:

```bash
python main.py
```

### Directory Structure

```
Stickers-Manager/
├── data/
│ ├── group1/
│ │ ├── sticker1.png
│ │ └── sticker2.gif
│ └── group2/
│ └── ...
├── main.py
├── requirements.txt
└── README.md
```



## 简体中文

### 简介
Stickers Manager 是一个轻量级的桌面应用程序，用于管理和使用图像贴纸。它提供了直观的界面，便于组织贴纸并快速复制到剪贴板。

### 功能
- 基于分组的贴纸组织
- 单击即可快速复制到剪贴板
- 悬停时可延迟预览 GIF 动图
- 支持多种图像格式（JPG、PNG、GIF、WebP）
- 流畅的分组切换和批量加载
- 响应式 UI 设计

### 系统要求
- Python 3.6+
- PyQt5

### 安装步骤

#### 创建虚拟环境

```bash
python -m venv venv
```

#### 激活虚拟环境

##### Windows:

```bash
.\venv\Scripts\activate
```

##### Linux/Mac:

```bash
source venv/bin/activate
```

#### 安装依赖

```bash
pip install -r requirements.txt
```

### 使用方法

1. 在项目根目录创建一个 `data` 文件夹
2. 在 `data` 文件夹中创建不同的子文件夹用于贴纸分组
3. 将贴纸图片放入相应的分组子文件夹
4. 启动应用程序：

```bash
python main.py
```

### 目录结构

```
Stickers-Manager/
├── data/
│   ├── group1/
│   │   ├── sticker1.png
│   │   └── sticker2.gif
│   └── group2/
│       └── ...
├── main.py
├── requirements.txt
└── README.md
```

