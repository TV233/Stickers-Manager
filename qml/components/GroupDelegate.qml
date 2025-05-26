import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    width: ListView.view.width
    height: 45

    // 直接从 model 中获取数据
    property string groupName: model.modelData.name || ""
    property string previewUrl: model.modelData.preview || ""

    Rectangle {
        anchors.fill: parent
        anchors.margins: 2
        color: mouseArea.pressed ? "#d0d0d0" : (mouseArea.hovered ? "#e0e0e0" : "#f0f0f0")
        radius: 5

        Row {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 10
            spacing: 10

            Image {
                source: previewUrl
                width: 30; height: 30
                fillMode: Image.PreserveAspectFit
            }
            Text {
                text: groupName
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        onClicked: {
            stickerManager.select_group(groupName) // 调用Python的槽函数
        }
    }
}