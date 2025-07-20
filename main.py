import sys
import asyncio
from PyQt5.QtWidgets import QApplication
from chat_gui import ChatWindow
from config_loader import ChatConfig
from conversation_manager import ConversationManager

if __name__ == "__main__":
    app = QApplication(sys.argv)

    config = ChatConfig("config.json")
    chat_window = ChatWindow()
    chat_window.showFullScreen()

    manager = ConversationManager(config, chat_window)
    manager.start()

    sys.exit(app.exec_())
