from chatgpt import chatgpt_lib

class CardGenerator():

    def __init__(self):
        self.text_generator = chatgpt_lib.ChatGPT_Generator("openai_api_key")

    def __call__(self, card_type="", description=""):
        card_data_paths = self.text_generator(card_type, description)
