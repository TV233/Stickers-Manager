import QtQuick 2.15
import QtQuick.Controls 2.15

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
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        
        onClicked: {
            stickerManager.copy_to_clipboard(imageSource)
            showCopyFeedback()
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