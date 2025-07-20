import random
import time
from config_loader import ChatConfig
from chatgpt_api import get_response

config = ChatConfig("config.json")
p1, p2 = config.get_two_random_personalities()

# Create shared conversation history
conversation = []

# First prompt: p1 asks a random friendly question
starter_prompt = "Ask a friendly question to get to know someone better."
first_message = get_response(p1.prompt, [{"role": "user", "content": starter_prompt}])
conversation.append({"role": "user", "content": first_message})
print(f"{p1.name}: {first_message}")

# Alternate responses for N turns
turns = random.randint(config.min_turns, config.max_turns)

for i in range(turns):
    if i % 2 == 0:
        responder = p2
        role = "assistant"
    else:
        responder = p1
        role = "user"

    response = get_response(responder.prompt, conversation)
    print(f"{responder.name}: {response}")
    conversation.append({"role": role, "content": response})

    time.sleep(1)  # optional delay for realism
