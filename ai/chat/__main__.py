import argparse
import os
import sys

from typing import Dict, Any

from ai.core.openai import Core

openai_instance = Core()

abs_path: str = os.path.dirname(os.path.abspath(__file__))
father_path: str = os.path.dirname(abs_path)


def start(start_params: Dict) -> None:
    content: str = openai_instance.replace_string(params)
    messages: list = [
        {
            "role": "system",
            "content": content
        }
    ]

    file_name: str = f"{str(params['topic']).lower().replace(' ', '_')}.json"

    openai_instance.create_file(file_name)
    openai_instance.set_messages(messages)
    openai_instance.get_messages(file_name)
    openai_instance.set_params(start_params)
    openai_instance.start_gradio_chat()


if __name__ == "__main__":
    try:
        parser = openai_instance.parser()
        parser.add_argument("-t", "--topic", type=str, default="Python", help="topic to be used")
        parser.add_argument("-r", "--role", type=str,
                            default="Eres un ingeniero de software experto en {{topic}}{{sub-role}}.",
                            help="Role to be used")
        parser.add_argument("--sub-role", type=str, default="que trabaja en una empresa de TI",
                            help="additional role to be used")

        params: Dict = vars(parser.parse_args())
        params = openai_instance.parse_params(params)
        start(params)
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Bye!")
        sys.exit(0)
