import argparse
import json
import os
import sys
import openai
import gradio

from typing import Dict, Any

openai.api_key = os.getenv("OPENAPI_KEY", "YOUR_API_KEY")

messages: list
abs_route: str
abs_path: str = os.path.dirname(os.path.abspath(__file__))
father_path: str = os.path.dirname(abs_path)


def repeat_string(string: str, times: int = 140) -> str:
    return string * times


def replace_string(params: Dict) -> str:
    try:
        return params['role'].replace("{{topic}}", params['topic']).replace("{{sub-role}}",
                                                                            f" {params['sub_role']}")
    except Exception as exc:
        print(f"{exc}")
        return f"{params['role']} {params['sub_role']}"


def create_file(file_name: str) -> None:
    if os.path.isfile(file_name) is False:
        f = open(file_name, "w")
        json.dump({"messages": []}, f, indent=2)
        f.close()


def transcript(file_name: str, message: Any) -> None:
    try:
        with open(file_name, "r") as file:
            content = json.load(file)

        with open(file_name, "w") as file:
            content["messages"].append(message)
            json.dump(content, file, indent=2)
    except Exception as exc:
        print(f"{exc}")


def get_messages(file_name: str) -> None:
    try:
        with open(file_name, "r") as file:
            content: Any = json.load(file)

        if len(content["messages"]) > 0:
            for i in content["messages"]:
                messages.append(i)
    except Exception as exc:
        print(f"{exc}")


def custom_chat_gpt(user_input) -> str:
    try:
        abs_route: str = f"{abs_path}/{str(params['topic']).lower().replace(' ', '_')}.json"
        input_str: Any = {"role": "user", "content": user_input}
        messages.append({"role": "user", "content": user_input})

        transcript(f"{abs_route}", input_str)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        chat_gpt_reply = response["choices"][0]["message"]["content"]
        output_str: Any = {"role": "assistant", "content": chat_gpt_reply}

        transcript(f"{abs_route}", output_str)

        messages.append(output_str)

        return chat_gpt_reply
    except Exception as exc:
        raise RuntimeError(f"{exc}")


def start(params: Dict):
    try:
        gr = gradio.Interface(fn=custom_chat_gpt,
                              inputs=params['inputs'],
                              outputs=params['outputs'],
                              title=params['title'], )
        gr.launch(share=params['share'],
                  debug=params['debug'],
                  server_port=params['port'],
                  server_name=params['url'],
                  auth=params['auth'],
                  inbrowser=params['in_browser'])
    except Exception as exc:
        raise RuntimeError(f"{exc}")


def parse_params(params: Dict) -> Dict:
    if params['auth'] is not None:
        params['auth'] = tuple(params['auth'].split(","))
    return params


if __name__ == "__main__":
    try:
        parser: argparse.ArgumentParser = argparse.ArgumentParser(description="OpenAi Chatbot",
                                                                  formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        subparser = parser.add_subparsers(title='Script select', dest='script_type')
        parser.version = '0.0.1'
        parser.add_argument("-v", "--version", action="version")
        parser.add_argument("-t", "--topic", type=str, default="lenguaje python", help="topic to be used")
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
        parser.add_argument("--sub-role", type=str, default="que trabaja en una empresa de telecomunicaciones",
                            help="additional role to be used")

        params: Dict = vars(parser.parse_args())
        content: str = replace_string(params)
        messages = [
            {
                "role": "system",
                "content": content
            }
        ]

        abs_route: str = f"{abs_path}/{str(params['topic']).lower().replace(' ', '_')}.json"
        create_file(abs_route)
        get_messages(abs_route)
        params = parse_params(params)

        start(params)
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Bye!")
        sys.exit(0)
