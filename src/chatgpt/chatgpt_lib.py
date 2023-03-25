import openai
import re
import json

class ChatGPT_Generator():
    MAX_ATTEMPTS = 3

    def __init__(self, api_key_path):
        openai.api_key_path = api_key_path
        # Original prompts author: Max Woolf (@minimaxir) 
        with open("src/chatgpt/system_prompt.txt", "r") as system_prompt_file:
            self.system = system_prompt_file.read()

    def __call__(self, card_type, description):
        prompt = 'Create ten variations of{} Magic cards{}.'
        prompt = prompt.format(
            " " + card_type if card_type else "",
            " " + description if description else ""
        )
        print("Using prompt '{}'".format(prompt))

        card_regex = '{.*}'
        card_json_paths = []
        while not card_json_paths:
            attempts = 0
            try:
                chatgpt_output = self.generate_magic_cards(prompt)
                parsed_output = re.findall(card_regex, chatgpt_output)
                msg = "{}\n Expected 10 cards in output, found {} instead, retrying..."
                assert len(parsed_output) == 10, msg.format(chatgpt_output, len(parsed_output))
                for idx in range(10):
                    card_path = "src/chatgpt/data/card_{}.json".format(idx)
                    with open(card_path, 'w') as card_file:
                        json.dump(json.loads(parsed_output[idx]), card_file,
                                  ensure_ascii=False, indent=4)
                    with open(card_path, 'r') as card_file:
                        card = json.load(card_file)
                        for key in ["name", "manaCost", "type", "text", "flavorText", "rarity"]:
                            assert key in card, "{} is missing {}".format(card, key)
                        if "Creature" in card["type"]:
                            assert "pt" in card, "{} is missing pt".format(card)
                    card_json_paths.append(card_path)
            except Exception as e:
                print(str(e))
                print("Failed to generate cards, retrying...")
                attempts += 1
                card_json_paths = []
            msg = "Failed to parse ChatGPT output too many times, exiting..."
            assert attempts < self.MAX_ATTEMPTS, msg

        return card_json_paths

    # Function modified from https://github.com/minimaxir/chatgpt_api_test/blob/main/mtg.ipynb
    # Original author: Max Woolf (@minimaxir)
    def generate_magic_cards(self, prompt):
        r = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.system},
                {"role": "user", "content": prompt},
            ],
            # stop="<|DONE|>",
            max_tokens=1500,  # sanity limit
            temperature=0.8,  # increasing temp higher than 0.8 may cause non-JSON output
        )
        # print(r["usage"])
        return r["choices"][0]["message"]["content"]
