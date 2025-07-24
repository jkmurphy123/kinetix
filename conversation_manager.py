from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
import random
import re
import uuid
from datetime import datetime
import os
from chatgpt_api import get_response
from functools import partial

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
        self.conv_log_path = None


    def start(self):
        self._start_new_chat()

    def _start_new_chat(self):
        self.person1, self.person2 = self.config.get_two_random_personalities()
        self.turns = random.randint(self.config.min_turns, self.config.max_turns)
        self.turn_index = 0
        self.history = []

        # Generate new conversation log file
        unique_id = uuid.uuid4().hex[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.conv_log_path = os.path.join("logs", f"conv_{timestamp}_{unique_id}.txt")

        with open(self.conv_log_path, "w", encoding="utf-8") as f:
            f.write(f"Conversation between {self.person1.name} and {self.person2.name}\n\n")

        # Start with person1 asking a question
        prompt = "Ask a friendly question to get to know someone."
        opener = get_response(self.person1.prompt, [{"role": "user", "content": prompt}])

        self.chat_window.add_message(self.person1.image_file_name, opener, self.person1.color, align_left=True)
        self.history.append({"role": "user", "content": opener})

        QTimer.singleShot(2000, self._next_turn)

    def split_message_into_chunks(self, text, max_chars=200):
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
    
    def _show_typing_bubble(self, speaker, align, final_text):
        # Create typing bubble widget
        typing_label = QLabel("typing...")
        typing_label.setStyleSheet(f"""
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
            layout.addWidget(typing_label)
            layout.addStretch()
        else:
            layout.addStretch()
            layout.addWidget(typing_label)
            layout.addWidget(avatar)

        bubble = QWidget()
        bubble.setLayout(layout)
        self.chat_window.chat_layout.addWidget(bubble)
        self.chat_window.scroll_area.verticalScrollBar().setValue(
            self.chat_window.scroll_area.verticalScrollBar().maximum()
        )

        # Replace typing with real chunk after short delay
        QTimer.singleShot(1200, lambda: self._replace_typing_bubble(bubble, speaker, final_text, align))

    def _replace_typing_bubble(self, bubble_widget, speaker, text, align):
        self.chat_window.chat_layout.removeWidget(bubble_widget)
        bubble_widget.deleteLater()

        self.chat_window.add_message(speaker.image_file_name, text, speaker.color, align)

        # Log to conversation file
        if self.conv_log_path:
            with open(self.conv_log_path, "a", encoding="utf-8") as f:
                name = speaker.name
                f.write(f"{name}: {text}\n")

    def _finalize_turn(self, responder_role, full_text):
        self.history.append({"role": responder_role, "content": full_text})

        self.turn_index += 1
        QTimer.singleShot(3000, self._next_turn)

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

        # Split long reply into chunks
        chunks = self.split_message_into_chunks(reply, 200)

        # Show each chunk with typing delay
        total_delay = 0

        for i, chunk in enumerate(chunks):
            delay = i * 2500  # adjust delay between bubbles
            QTimer.singleShot(delay, partial(self._show_typing_bubble, speaker, align, chunk))

        # Add full reply to history once all chunks are sent
        final_delay = len(chunks) * 2500 + 500  # buffer after last message
        QTimer.singleShot(final_delay, lambda: self._finalize_turn(responder_role, reply))

    def _say_goodbye(self):
        speaker = self.person1
        align = True
        role = "user"

        goodbye_prompt = "Say goodbye to the other person in a friendly and character-appropriate way."
        goodbye_text = get_response(speaker.prompt, [{"role": "user", "content": goodbye_prompt}])

        with open(self.conv_log_path, "a", encoding="utf-8") as f:
            f.write(f"{speaker.name}: {goodbye_text}\n\n[Conversation End]\n")

        self.chat_window.add_message(speaker.image_file_name, goodbye_text, speaker.color, align)
        self.history.append({"role": role, "content": goodbye_text})

        # Wait before starting a new conversation
        QTimer.singleShot((self.config.chat_delay_seconds + 1) * 1000, self._start_new_chat)        

  