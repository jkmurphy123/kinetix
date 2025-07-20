import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt

class ChatBubble(QWidget):
    def __init__(self, avatar_path, message, color, align_left=True):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        avatar = QLabel()
        avatar.setPixmap(QPixmap(avatar_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        bubble = QLabel(message)
        bubble.setWordWrap(True)
        bubble.setStyleSheet(f"""
            background-color: {color};
            border-radius: 10px;
            padding: 10px;
            color: black;
            font-size: 14px;
        """)
        bubble.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        bubble.setMaximumWidth(400)

        if align_left:
            layout.addWidget(avatar)
            layout.addWidget(bubble)
            layout.addStretch()
        else:
            layout.addStretch()
            layout.addWidget(bubble)
            layout.addWidget(avatar)

        self.setLayout(layout)

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Chat Simulator")
        self.setGeometry(100, 100, 600, 400)

        main_layout = QVBoxLayout(self)

        # Scrollable chat area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.chat_layout = QVBoxLayout(self.scroll_content)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)

        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)

        # Add sample messages
        self.add_message("images/avatar1.png", "Hello there! What's your favorite movie?", "#D0F0C0", align_left=True)
        self.add_message("images/avatar2.png", "I'd say Blade Runner. You?", "#ADD8E6", align_left=False)

    def add_message(self, avatar_path, message, color, align_left=True):
        bubble = ChatBubble(avatar_path, message, color, align_left)
        self.chat_layout.addWidget(bubble)
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())
