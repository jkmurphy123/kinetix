import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt, QTimer

from dotenv import load_dotenv

from config_loader import ChatConfig

from logger import get_logger
logger = get_logger("chat_gui")


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
        bubble.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        bubble.setMaximumWidth(600)

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
        self.showFullScreen()
        #self.setGeometry(100, 100, 600, 400)

        main_layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.chat_layout = QVBoxLayout(self.scroll_content)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)

        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)

    def clear_chat(self):
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


    def add_message(self, avatar_path, message, color, align_left=True):
        def add():
            # Log message
            logger.info(f"{'Left' if align_left else 'Right'}: {message}")

            bubble = ChatBubble(avatar_path, message, color, align_left)
            self.chat_layout.addWidget(bubble)
            self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            )
        QTimer.singleShot(0, add)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.quit()

    def show_placeholder_message(self, message: str):
        placeholder_label = QLabel(message)
        placeholder_label.setStyleSheet("""
            background-color: #f0f0f0;
            border: 1px dashed #aaa;
            padding: 15px;
            border-radius: 10px;
            font-style: italic;
            font-size: 16px;
            color: #555;
        """)
        placeholder_label.setAlignment(Qt.AlignCenter)

        placeholder_container = QWidget()
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(placeholder_label)
        layout.addStretch()
        placeholder_container.setLayout(layout)

        self.chat_layout.addWidget(placeholder_container)
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )


if __name__ == "__main__":
    load_dotenv()  # Loads variables from .env
    api_key = os.getenv("OPENAI_API_KEY")

    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())
