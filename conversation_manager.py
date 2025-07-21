from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
import random
import re
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

    def split_message_into_chunks(text, max_chars=200):
        """Split a long message into chunks by sentence or length."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chars:
                current_chunk += " " + sentence
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks      
    
    def _next_turn(self):
        if self.turn_index >= self.turns:
            self._say_goodbye()
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

        # Split the reply into readable chunks
        #from utils import split_message_into_chunks  # or move it inline
        chunks = self.split_message_into_chunks(reply, max_chars=200)

        # Display each chunk as a separate bubble
        for i, chunk in enumerate(chunks):
            delay_ms = i * 1500  # delay each message a bit
            QTimer.singleShot(delay_ms, lambda c=chunk: self.chat_window.add_message(
                speaker.image_file_name, c, speaker.color, align
            ))

        # Only append the full message to the GPT history
        self.history.append({"role": responder_role, "content": reply})
        self.turn_index += 1

        # Schedule next turn after the final chunk
        final_delay = len(chunks) * 1500 + 3000
        QTimer.singleShot(final_delay, self._next_turn)

    def _say_goodbye(self):
        speaker = self.person1
        align = True
        role = "user"

        goodbye_prompt = "Say goodbye to the other person in a friendly and character-appropriate way."
        goodbye_text = get_response(speaker.prompt, [{"role": "user", "content": goodbye_prompt}])

        self.chat_window.add_message(speaker.image_file_name, goodbye_text, speaker.color, align)
        self.history.append({"role": role, "content": goodbye_text})

        # Wait before starting a new conversation
        QTimer.singleShot((self.config.chat_delay_seconds + 1) * 1000, self._start_new_chat)        

  