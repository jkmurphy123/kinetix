from PyQt5.QtCore import QTimer
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
            # Conversation ended, start a new one after delay
            QTimer.singleShot(self.config.chat_delay_seconds * 1000, self._start_new_chat)
            return

        # Alternate speakers
        if self.turn_index % 2 == 0:
            speaker = self.person2
            role = "assistant"
            align = False
        else:
            speaker = self.person1
            role = "user"
            align = True

        reply = get_response(speaker.prompt, self.history)
        self.chat_window.add_message(speaker.image_file_name, reply, speaker.color, align)
        self.history.append({"role": role, "content": reply})
        self.turn_index += 1

        # Schedule next message
        QTimer.singleShot(2000, self._next_turn)
