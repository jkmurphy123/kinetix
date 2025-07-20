from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
import random
from chatgpt_api import get_response

class ConversationManager:
    def __init__(self, config, chat_window):
        self.config = config
        self.chat_window = chat_window
        self.running = True
        self.turn_index = 0
        self.turns = 0
        self.person1 = None
        self.person2 = None
        self.history = []

    def start(self):
        self._start_new_chat()

    def _start_new_chat(self):
        self.person1, self.person2 = self.config.get_two_random_personalities()
        self.turns = random.randint(self.config.min_turns, self.config.max_turns)
        self.turn_index = 0
        self.history = []

        # Start with person1 asking a question
        prompt = "Ask a friendly question to get to know someone."
        opener = get_response(self.person1.prompt, [{"role": "user", "content": prompt}])
        self.chat_window.add_message(self.person1.image_file_name, opener, self.person1.color, align_left=True)
        self.history.append({"role": "user", "content": opener})

        QTimer.singleShot(2000, self._next_turn)

    def _next_turn(self):
        if self.turn_index >= self.turns:
            QTimer.singleShot(self.config.chat_delay_seconds * 1000, self._start_new_chat)
            return

        if self.turn_index % 2 == 0:
            # person2 is replying
            speaker = self.person2
            responder_role = "assistant"
            align = False
        else:
            # person1 is replying
            speaker = self.person1
            responder_role = "user"
            align = True

        # --- STEP 1: Add typing bubble ---
        self.typing_label = QLabel("typing...")
        self.typing_label.setStyleSheet(f"""
            background-color: {speaker.color};
            border-radius: 10px;
            padding: 10px;
            font-style: italic;
            color: #444;
        """)
        layout = QHBoxLayout()
        avatar = QLabel()
        avatar.setPixmap(QPixmap(speaker.image_file_name).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        if align:
            layout.addWidget(avatar)
            layout.addWidget(self.typing_label)
            layout.addStretch()
        else:
            layout.addStretch()
            layout.addWidget(self.typing_label)
            layout.addWidget(avatar)

        bubble = QWidget()
        bubble.setLayout(layout)
        self.chat_window.chat_layout.addWidget(bubble)
        self.chat_window.scroll_area.verticalScrollBar().setValue(
            self.chat_window.scroll_area.verticalScrollBar().maximum()
        )

        # --- STEP 2: After delay, replace typing with real message ---
        QTimer.singleShot(2500, lambda: self._show_response(speaker, responder_role, align, bubble))

    def _show_response(self, speaker, responder_role, align, typing_widget):
        # Get actual reply
        reply = get_response(speaker.prompt, self.history)

        # Remove "typing..." bubble
        self.chat_window.chat_layout.removeWidget(typing_widget)
        typing_widget.deleteLater()

        # Show real message
        self.chat_window.add_message(speaker.image_file_name, reply, speaker.color, align)
        self.history.append({"role": responder_role, "content": reply})

        self.turn_index += 1

        # Delay next turn
        QTimer.singleShot(2000, self._next_turn)