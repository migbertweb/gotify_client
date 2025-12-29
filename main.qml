import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15

ApplicationWindow {
    id: window
    visible: true
    width: 400
    height: 600
    title: "Gotify Client"
    
    Material.theme: Material.Dark
    Material.accent: Material.Blue

    property bool isConnected: false

    onClosing: function(close) {
        close.accepted = false
        backend.minimize_window()
    }

    Connections {
        target: backend
        function onConnectionStatusChanged(connected) {
            window.isConnected = connected
        }
    }

    header: ToolBar {
        Material.background: Material.primary
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 10
            
            Label {
                text: "Gotify"
                font.pixelSize: 20
                font.bold: true
                color: "white"
                Layout.fillWidth: true
            }

            Rectangle {
                width: 12
                height: 12
                radius: 6
                color: window.isConnected ? "#4CAF50" : "#F44336" // Green or Red
                border.color: "white"
                border.width: 1
            }

            ToolButton {
                text: "⚙"
                font.pixelSize: 18
                onClicked: settingsDialog.open()
            }
        }
    }

    ListView {
        id: messageListView
        anchors.fill: parent
        model: messageModel
        spacing: 10
        clip: true
        
        // Add some padding at the top and bottom
        header: Item { height: 10 }
        footer: Item { height: 10 }

        delegate: Item {
            width: messageListView.width
            height: cardContent.height + 20

            Rectangle {
                id: card
                width: parent.width - 20
                height: parent.height - 10
                anchors.centerIn: parent
                radius: 8
                color: Material.color(Material.Grey, Material.Shade800)
                
                // Add simple shadow effect
                layer.enabled: true
                
                ColumnLayout {
                    id: cardContent
                    anchors.fill: parent
                    anchors.margins: 15
                    spacing: 5

                    Label {
                        text: model.title
                        font.bold: true
                        font.pixelSize: 16
                        color: "white"
                        Layout.fillWidth: true
                        wrapMode: Text.Wrap
                    }

                    Label {
                        text: model.message
                        font.pixelSize: 14
                        color: "#DDDDDD"
                        Layout.fillWidth: true
                        wrapMode: Text.Wrap
                    }

                    Label {
                        text: model.date
                        font.pixelSize: 10
                        color: "#AAAAAA"
                        Layout.alignment: Qt.AlignRight
                    }
                }
            }
        }
    }
    
    Label {
        anchors.centerIn: parent
        text: "No messages yet"
        visible: messageListView.count === 0
        color: "grey"
        font.pixelSize: 16
    }

    Dialog {
        id: settingsDialog
        title: "Settings"
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        width: parent.width * 0.9
        modal: true
        
        standardButtons: Dialog.Save | Dialog.Cancel

        onAccepted: {
            backend.save_settings(urlField.text, tokenField.text)
        }
        
        onOpened: {
            var settings = backend.get_settings()
            urlField.text = settings.url
            tokenField.text = settings.token
        }

        ColumnLayout {
            spacing: 20
            width: parent.width

            TextField {
                id: urlField
                placeholderText: "https://gotify.example.com"
                Layout.fillWidth: true
                selectByMouse: true
                
                Label {
                    text: "Server URL"
                    anchors.bottom: parent.top
                    font.pixelSize: 12
                    color: Material.accent
                }
            }

            TextField {
                id: tokenField
                placeholderText: "Client Token"
                Layout.fillWidth: true
                echoMode: TextInput.Password
                selectByMouse: true

                Label {
                    text: "Client Token"
                    anchors.bottom: parent.top
                    font.pixelSize: 12
                    color: Material.accent
                }
            }
        }
    }
}
