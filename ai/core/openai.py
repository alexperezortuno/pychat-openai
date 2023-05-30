import argparse
import base64
import json
import os
from io import BytesIO

import gradio
import openai
from typing import List, Any, Dict

from PIL import Image

openai.api_key = os.getenv("OPENAPI_KEY", "YOUR_API_KEY")


class Core:
    messages: List[Any]
    params: Dict
    file_name: str
    abs_path: str = os.path.dirname(os.path.abspath(__file__))
    father_path: str = os.path.dirname(os.path.dirname(abs_path))

    @staticmethod
    def repeat_string(string: str, times: int = 140) -> str:
        return string * times

    @staticmethod
    def replace_string(params: Dict) -> str:
        try:
            return params['role'].replace("{{topic}}", params['topic']).replace("{{sub-role}}",
                                                                                f" {params['sub_role']}")
        except Exception as exc:
            print(f"{exc}")
            return f"{params['role']} {params['sub_role']}"

    @staticmethod
    def transcript(file_name: str, message: Any) -> None:
        try:
            with open(file_name, "r") as file:
                content = json.load(file)

            with open(file_name, "w") as file:
                content["messages"].append(message)
                json.dump(content, file, indent=2)
        except Exception as exc:
            print(f"{exc}")

    @staticmethod
    def parse_params(params: Dict) -> Dict:
        if params['auth'] is not None:
            params['auth'] = tuple(params['auth'].split(","))
        return params

    @staticmethod
    def parser() -> argparse.ArgumentParser:
        parser: argparse.ArgumentParser = argparse.ArgumentParser(description="OpenAi Chatbot",
                                                                  formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        subparser = parser.add_subparsers(title='Script select', dest='script_type')
        parser.version = '0.0.1'
        parser.add_argument("-p", "--port", type=int, default=7860, help="Port to be used")
        parser.add_argument("-v", "--version", action="version")
        parser.add_argument("--model", type=str, default="gpt-3.5-turbo", help="Model to be used")
        parser.add_argument("-i", "--inputs", type=str, default="text", help="Inputs to be used")
        parser.add_argument("-o", "--outputs", type=str, default="text", help="Outputs to be used")
        parser.add_argument("--title", type=str, default="OpenAI", help="Title for interface")
        parser.add_argument("-d", "--debug", type=bool, default=False, help="Debug mode")
        parser.add_argument("-s", "--share", type=bool, default=False, help="Share mode")
        parser.add_argument("--auth", type=str, default=None, help="Auth to be used")
        parser.add_argument("-u", "--url", type=str, default="localhost", help="Url to be used")
        parser.add_argument("--in-browser", type=bool, default=False, help="Open in browser")
        parser.add_argument("-m", "--method", type=str, default="http", help="Method to be used")

        return parser

    @staticmethod
    def image_from_base64(base64_string: str) -> Image:
        try:
            imgdata: bytes = base64.b64decode(base64_string)
            return Image.open(BytesIO(imgdata))
        except Exception as exc:
            raise RuntimeError(f"{exc}")

    @staticmethod
    def bytes_from_base64(base64_string: str) -> bytes:
        try:
            imgdata: bytes = base64.b64decode(base64_string)
            img = Image.open(BytesIO(imgdata))
            _buffer = BytesIO()
            img.save(_buffer, format="PNG")
            image_bytes = _buffer.getvalue()
            return image_bytes
        except Exception as exc:
            raise RuntimeError(f"{exc}")

    def create_file(self, file_name: str) -> None:
        file_path: str = f"{self.father_path}/{file_name}"
        if os.path.isfile(file_path) is False:
            f = open(file_path, "w")
            json.dump({"messages": []}, f, indent=2)
            f.close()

    def get_messages(self, file_name: str) -> None:
        try:
            file_path: str = f"{self.father_path}/{file_name}"
            with open(file_path, "r") as file:
                content: Any = json.load(file)

            if len(content["messages"]) > 0:
                for i in content["messages"]:
                    self.messages.append(i)
        except Exception as exc:
            print(f"{exc}")

    def chat_gpt(self, user_input) -> str:
        try:
            abs_route: str = f"{self.father_path}/{str(self.params['topic']).lower().replace(' ', '_')}.json"
            input_str: Any = {"role": "user", "content": user_input}
            self.messages.append(input_str)

            self.transcript(f"{abs_route}", input_str)

            response = openai.ChatCompletion.create(
                model=self.params['model'],
                messages=self.messages
            )

            gpt_response = response["choices"][0]["message"]["content"]
            output_str: Any = {"role": "assistant", "content": gpt_response}

            self.transcript(f"{abs_route}", output_str)

            self.messages.append(output_str)

            return gpt_response
        except Exception as exc:
            raise RuntimeError(f"{exc}")

    def image_gpt(self, user_input) -> List[str] or List[Image]:
        try:
            response = openai.Image.create(
                prompt=user_input,
                n=self.params['n'],
                size=self.params['size'],
                response_format=self.params['response_format'],
            )

            r: List[str] = [response["data"][i][self.params['response_format']] for i in range(len(response["data"]))]

            return [self.image_from_base64(r[j]) for j in range(len(r))]
        except Exception as exc:
            raise RuntimeError(f"{exc}")

    def start_gradio_chat(self):
        try:
            gr = gradio.Interface(fn=self.chat_gpt,
                                  inputs=self.params['inputs'],
                                  outputs=self.params['outputs'],
                                  title=self.params['title'],
                                  )
            gr.launch(share=self.params['share'],
                      debug=self.params['debug'],
                      server_port=self.params['port'],
                      server_name=self.params['url'],
                      auth=self.params['auth'],
                      inbrowser=self.params['in_browser'])
        except Exception as exc:
            raise RuntimeError(f"{exc}")

    def start_gradio_image(self):
        try:
            gr = gradio.Interface(fn=self.image_gpt,
                                  inputs=self.params['inputs'],
                                  outputs=["image", "image"],
                                  title=self.params['title'],
                                  )
            gr.launch(share=self.params['share'],
                      debug=self.params['debug'],
                      server_port=self.params['port'],
                      server_name=self.params['url'],
                      auth=self.params['auth'],
                      inbrowser=self.params['in_browser'])
        except Exception as exc:
            raise RuntimeError(f"{exc}")

    def set_params(self, params) -> None:
        self.params = params

    def set_messages(self, messages) -> None:
        self.messages = messages
