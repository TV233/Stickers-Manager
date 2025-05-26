import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "./components" as Components

ApplicationWindow {
    visible: true
    width: 1230
    height: 700
    title: "Stickers Manager"
    minimumWidth: 800
    minimumHeight: 600

    // 添加搜索栏
    header: ToolBar {
        RowLayout {
            anchors.fill: parent
            spacing: 10

            TextField {
                id: searchField
                Layout.fillWidth: true
                placeholderText: "搜索标签..."
                onTextChanged: stickerManager.search(text)
            }

            CheckBox {
                text: "仅当前分组"
                checked: true
                onCheckedChanged: stickerManager.set_search_scope(checked)
            }

            Button {
                text: "清除"
                onClicked: searchField.text = ""
            }
        }
    }

    // 使用 SplitView 实现左右可拖拽的布局
    SplitView {
        anchors.fill: parent

        // 左侧分组列表
        ScrollView {
            id: groupView
            SplitView.minimumWidth: 200
            SplitView.preferredWidth: 240
            SplitView.maximumWidth: 300
            SplitView.fillHeight: true

            ListView {
                anchors.fill: parent
                model: stickerManager.groups
                delegate: Components.GroupDelegate {}
                spacing: 2
            }
        }

        // 右侧表情包网格
        ScrollView {
            id: stickerView
            SplitView.fillWidth: true
            SplitView.fillHeight: true
            clip: true  // 确保内容不会溢出

            GridView {
                anchors.fill: parent
                model: stickerManager.currentStickers
                cellWidth: 160
                cellHeight: 160
                delegate: Components.StickerDelegate {}
                
                // 添加边距
                leftMargin: 10
                rightMargin: 10
                topMargin: 10
                bottomMargin: 10
            }
        }
    }
}