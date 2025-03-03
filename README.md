# Stickers Manager

### Introduction
Stickers Manager is a lightweight desktop application for managing and using image stickers. It provides an intuitive interface for organizing and quickly copying stickers to the clipboard.

### Features
- Group-based sticker organization
- Quick copy to clipboard with single click
- GIF preview on hover
- Support for multiple image formats (JPG, PNG, GIF, WebP)
- Smooth group switching
- Responsive UI design

### Usage
1. Place your sticker images in subfolders under the `data` directory
2. Launch the application
3. Select a sticker group from the left panel
4. Click any sticker to copy it to clipboard
5. Hover over GIF stickers to preview animation

### Installation

#### Method 1: Using AppImage (Recommended)
1. Download the latest `StickersManager.AppImage` from [Releases](https://github.com/TV233/Stickers-Manager/releases)
2. Make it executable:
   ```bash
   chmod +x StickersManager.AppImage
   ```
3. Run it:
   ```bash
   ./StickersManager.AppImage
   ```

#### Method 2: From Source
1. Clone the repository:
   ```bash
   git clone https://github.com/TV233/Stickers-Manager.git
   cd Stickers-Manager
   ```
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```
