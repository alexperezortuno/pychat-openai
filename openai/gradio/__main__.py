import argparse
import os
import sys

from typing import Dict, Any

from openai.core.openai import OpenAICore

openai_instance = OpenAICore()

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
    openai_instance.start_gradio()


if __name__ == "__main__":
    try:
        parser: argparse.ArgumentParser = argparse.ArgumentParser(description="OpenAi Chatbot",
                                                                  formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        subparser = parser.add_subparsers(title='Script select', dest='script_type')
        parser.version = '0.0.1'
        parser.add_argument("-v", "--version", action="version")
        parser.add_argument("-t", "--topic", type=str, default="Python", help="topic to be used")
        parser.add_argument("-i", "--inputs", type=str, default="text", help="Inputs to be used")
        parser.add_argument("-o", "--outputs", type=str, default="text", help="Outputs to be used")
        parser.add_argument("--title", type=str, default="OpenAI", help="Title for interface")
        parser.add_argument("-d", "--debug", type=bool, default=False, help="Debug mode")
        parser.add_argument("-s", "--share", type=bool, default=False, help="Share mode")
        parser.add_argument("-p", "--port", type=int, default=7860, help="Port to be used")
        parser.add_argument("--auth", type=str, default=None, help="Auth to be used")
        parser.add_argument("-u", "--url", type=str, default="localhost", help="Url to be used")
        parser.add_argument("--in-browser", type=bool, default=False, help="Open in browser")
        parser.add_argument("-m", "--method", type=str, default="http", help="Method to be used")
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
