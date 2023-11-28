"""
Demonstrates how to use the `ChatInterface` to create a chatbot using
[Mistral](https://docs.mistral.ai) through
[CTransformers](https://github.com/marella/ctransformers). The chatbot includes a
memory of the conversation history.

To execute:
$ panel serve Calliope.py --show
"""

import panel as pn
from ctransformers import AutoConfig, AutoModelForCausalLM, Config
import pandas as pd

pn.extension(design="material")

SYSTEM_INSTRUCTIONS = "You are Calliope; your job is to aid user in generating and developing ideas, insights, plans, and creative works. Your tone should be intimate but not flirty or emotive. Above all, you should be an engaging conversation partner in whatever mode user decides. Do the following: Give short responses, always ask a question, ask user leading questions, discuss concepts adjacent to user's own statements, call back to unresolved lines of thought, and encourage lateral thinking. Do not do the following: summarize user's statement, use excessive exclamation points of emoji, regurgitate facts or instructional material unless explicitly prompted."
df = pd.DataFrame(columns=["user", "chat_log"])
CHAT_USER="dude@abc.com"

def apply_template(history):
    history = [message for message in history if message.user != "System"]
    prompt = ""
    for i, message in enumerate(history):
        if i == 0:
            prompt += f"<s>[INST]{SYSTEM_INSTRUCTIONS} {message.object}[/INST]"
        else:
            if message.user == "Mistral":
                prompt += f"{message.object}</s>"
            else:
                prompt += f"""[INST]{message.object}[/INST]"""
    return prompt


async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    if "mistral" not in llms:
        instance.placeholder_text = "Downloading model; please wait..."
        config = AutoConfig(
            config=Config(
                temperature=0.7, max_new_tokens=512, context_length=8184, top_p=0.8
            ),
        )
        llms["mistral"] = AutoModelForCausalLM.from_pretrained(
            "TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
            model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
            config=config,
        )

    llm = llms["mistral"]
    history = [message for message in instance.objects]
    prompt = apply_template(history)
    response = llm(prompt, stream=True)
    message = ""
    for token in response:
        message += token
        yield message
        df.loc[df['user']==CHAT_USER, "chat_log"]+= message


llms = {}
chat_interface = pn.chat.ChatInterface(
    callback=callback,
    callback_user="Mistral",
)
chat_interface.send(
    "Hello, I am Calliope. What are you thinking about today?", user="System", respond=False
)

chat_interface.servable()
print("Starting Calliope...")