import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    width: 160
    height: 160
    
    // 从model中获取图片信息
    property string imageSource: model.modelData.url || ""
    property bool isAnimated: model.modelData.animated || false

    Rectangle {
        id: background
        anchors.fill: parent
        anchors.margins: 5
        color: "transparent"
        border.color: mouseArea.containsMouse ? "lightblue" : "transparent"
        border.width: 2
        
        // 使用 AnimatedImage 来原生支持GIF
        AnimatedImage {
            id: stickerImage
            anchors.fill: parent
            anchors.margins: 5
            source: imageSource
            fillMode: Image.PreserveAspectFit
            cache: true
            
            // 动图播放控制
            playing: isAnimated && (mouseArea.containsMouse || root.copyFeedbackVisible)
            
            // 监听播放状态变化
            onPlayingChanged: {
                if (!playing) {
                    // 停止播放时重置到第一帧
                    currentFrame = 0
                }
            }
            
            // 确保加载完成后初始显示第一帧
            onStatusChanged: {
                if (status === AnimatedImage.Ready) {
                    currentFrame = 0
                }
            }
        }
    }
    
    // 复制成功的视觉反馈
    property bool copyFeedbackVisible: false
    Rectangle {
        id: copyFeedback
        anchors.fill: parent
        color: "#80ffffff"
        visible: root.copyFeedbackVisible
        opacity: visible ? 1 : 0

        Text {
            anchors.centerIn: parent
            text: "已复制"
            color: "#333333"
            font.pixelSize: 16
        }

        Behavior on opacity {
            NumberAnimation { duration: 200 }
        }
    }
    
    // 标签输入对话框
    Dialog {
        id: tagDialog
        title: "添加标签"
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
        width: 400

        anchors.centerIn: Overlay.overlay

        contentItem: ColumnLayout {
            spacing: 10
            
            Label {
                text: "输入标签（用空格分隔多个标签）"
                wrapMode: Text.WordWrap
            }
            
            TextField {
                id: tagInput
                Layout.fillWidth: true
                focus: true
                
                // 添加回车键支持
                Keys.onReturnPressed: {
                    tagDialog.accept()
                }
            }
        }

        onAccepted: {
            let tags = tagInput.text.trim().split(/\s+/)
            tags.forEach(tag => {
                if (tag) {
                    stickerManager.add_tag(imageSource, tag)
                }
            })
        }

        onOpened: tagInput.text = ""
    }

    // 右键菜单
    Menu {
        id: contextMenu

        MenuItem {
            text: "添加到收藏"
            visible: !imageSource.includes("/favorites/")  // 不在收藏夹中才显示
            onTriggered: stickerManager.add_to_favorites(imageSource)
        }

        MenuItem {
            text: "移除收藏"
            visible: imageSource.includes("/favorites/")  // 在收藏夹中才显示
            onTriggered: stickerManager.remove_from_favorites(imageSource)
        }

        MenuItem {
            text: "添加标签"
            onTriggered: tagDialog.open()
        }

        MenuItem {
            text: "管理标签"
            onTriggered: tagManagerDialog.open()
        }

        MenuItem {
            text: "删除"
            onTriggered: deleteConfirmDialog.open()
        }
    }

    // 标签管理对话框
    Dialog {
        id: tagManagerDialog
        title: "管理标签"
        modal: true
        standardButtons: Dialog.Close
        width: 400
        height: 300

        anchors.centerIn: Overlay.overlay

        // 使用 Connections 监听标签变化
        Connections {
            target: stickerManager
            function onTagsChanged() {
                tagListModel.model = stickerManager.get_tags(imageSource)
            }
        }

        ListView {
            id: tagListModel
            anchors.fill: parent
            model: stickerManager.get_tags(imageSource)
            delegate: ItemDelegate {
                width: parent.width
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    
                    Label {
                        text: modelData
                        Layout.fillWidth: true
                    }
                    
                    Button {
                        text: "删除"
                        onClicked: {
                            stickerManager.remove_tag(imageSource, modelData)
                        }
                    }
                }
            }
        }
    }

    // 删除确认对话框
    Dialog {
        id: deleteConfirmDialog
        title: "确认删除"
        modal: true
        standardButtons: Dialog.Yes | Dialog.No

        anchors.centerIn: Overlay.overlay

        // 使用 contentItem 来显示文本
        contentItem: Label {
            text: "确定要删除这个表情包吗？"
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
        }

        onAccepted: {
            stickerManager.delete_sticker(imageSource)
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton | Qt.RightButton  // 接受左键和右键

        onClicked: {
            if (mouse.button === Qt.RightButton) {
                contextMenu.popup()
            } else {
                stickerManager.copy_to_clipboard(imageSource)
                showCopyFeedback()
            }
        }
    }

    // 处理复制反馈
    Timer {
        id: feedbackTimer
        interval: 800
        onTriggered: root.copyFeedbackVisible = false
    }

    function showCopyFeedback() {
        root.copyFeedbackVisible = true
        feedbackTimer.restart()
    }

    // 监听全局复制信号
    Connections {
        target: stickerManager
        function onCopyCompleted() {
            if (stickerManager.lastCopiedImage === imageSource) {
                showCopyFeedback()
            }
        }
    }
}