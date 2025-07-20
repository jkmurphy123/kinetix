import json
import random

class Personality:
    def __init__(self, name, image_file_name, color, prompt):
        self.name = name
        self.image_file_name = image_file_name
        self.color = color
        self.prompt = prompt

class ChatConfig:
    def __init__(self, config_path):
        with open(config_path, "r") as f:
            data = json.load(f)

        self.chat_delay_seconds = data.get("chat_delay_seconds", 30)
        self.min_turns = data.get("min_turns", 5)
        self.max_turns = data.get("max_turns", 10)

        self.personalities = [
            Personality(**p) for p in data["personalities"]
        ]

    def get_two_random_personalities(self):
        return random.sample(self.personalities, 2)
