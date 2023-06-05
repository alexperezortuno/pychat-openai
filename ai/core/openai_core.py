import argparse
import base64
import json
import os
import gradio
import openai

from io import BytesIO
from typing import List, Any, Dict
from PIL import Image
from ai.core.commons import log_lvl, log_str
from ai.core.logger import get_logger

openai.api_key = os.getenv("OPENAPI_KEY", "YOUR_API_KEY")


class OpenAiCore:
    messages: List[Any]
    params: Dict
    file_name: str
    logger: Any
    log_lvl: str
    log_str: str
    abs_path: str = os.path.dirname(os.path.abspath(__file__))
    father_path: str = os.path.dirname(os.path.dirname(abs_path))

    def __init__(self) -> None:
        self.messages = []
        self.params = {}
        self.file_name = ""
        self.logger = get_logger(log_lvl, log_str, __name__)

    @staticmethod
    def repeat_string(string: str, times: int = 140) -> str:
        return string * times

    @staticmethod
    def parse_params(params: Dict) -> Dict:
        if params['auth'] is not None:
            params['auth'] = tuple(params['auth'].split(","))
        return params

    @staticmethod
    def default_params() -> Dict:
        response: Dict = {
            "version": "0.0.1",
            "port": 7860,
            "model": "gpt-3.5-turbo",
            "inputs": "text",
            "outputs": "text",
            "title": "OpenAI",
            "debug": False,
            "gradio": True,
            "share": False,
            "auth": None,
            "url": "localhost",
            "in_browser": False,
            "method": "http",
            "log_level": log_lvl,
            "log_format": log_str,
        }

        return response

    def replace_string(self, params: Dict) -> str:
        try:
            return params['role'].replace("{{topic}}", params['topic'])
        except Exception as exc:
            self.logger.error(f"{exc}")
            return f"{params['role']}"

    def parser(self) -> argparse.ArgumentParser:
        default_params: Dict = self.default_params()
        parser: argparse.ArgumentParser = argparse.ArgumentParser(description="OpenAi Chatbot",
                                                                  formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        subparser = parser.add_subparsers(title='Script select', dest='script_type')
        parser.version = '0.0.1'
        parser.add_argument("-p", "--port", type=int, default=default_params["port"], help="Port to be used")
        parser.add_argument("-v", "--version", action="version")
        parser.add_argument("--model", type=str, default=default_params["model"], help="Model to be used")
        parser.add_argument("-i", "--inputs", type=str, default=default_params["inputs"], help="Inputs to be used")
        parser.add_argument("-o", "--outputs", type=str, default=default_params["outputs"], help="Outputs to be used")
        parser.add_argument("--title", type=str, default=default_params["title"], help="Title for interface")
        parser.add_argument("-d", "--debug", type=bool, default=default_params["debug"], help="Debug mode")
        parser.add_argument("--gradio", type=bool, default=default_params["gradio"], help="Activate gradio mode")
        parser.add_argument("-s", "--share", type=bool, default=default_params["share"], help="Share mode")
        parser.add_argument("--auth", type=str, default=default_params["auth"], help="Auth to be used")
        parser.add_argument("-u", "--url", type=str, default=default_params["url"], help="Url to be used")
        parser.add_argument("--in-browser", type=bool, default=default_params["in_browser"], help="Open in browser")
        parser.add_argument("-m", "--method", type=str, default=default_params["method"], help="Method to be used")
        parser.add_argument("--log-level", type=str, default=default_params["log_level"])
        parser.add_argument("--log-format", type=str, default=default_params["log_format"])

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

    @staticmethod
    def get_logger(name: str, params: Dict) -> Any:
        return get_logger(params['log_level'], params['log_format'], name)

    @staticmethod
    def text_chat_gpt(user_input: str) -> str:
        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"{user_input}A:",
                temperature=0.5,
                max_tokens=128,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stop=["\n"],
            )

            return response.choices[0].text
        except Exception as exc:
            return ""

    def transcript(self, file_name: str, message: Any) -> None:
        try:
            self.logger.debug(f"Transcripting message: {message}, to file: {file_name}")
            with open(file_name, "r") as file:
                content = json.load(file)

            with open(file_name, "w") as file:
                content["messages"].append(message)
                json.dump(content, file, indent=2)
        except Exception as exc:
            print(f"{exc}")

    def set_logger(self, params: Dict) -> None:
        self.log_str: str = params['log_format']
        self.log_lvl: str = params['log_level']
        self.logger = get_logger(params['log_level'], params['log_format'], __name__)

    def create_file(self, file_name: str) -> None:
        file_path: str = f"{self.father_path}/{file_name}"
        self.logger.debug(f"File path: {file_path}")
        if os.path.isfile(file_path) is False:
            f = open(file_path, "w")
            json.dump({"messages": []}, f, indent=2)
            f.close()

    def get_messages(self, file_name: str) -> None:
        try:
            file_path: str = f"{self.father_path}/{file_name}"
            self.logger.debug(f"File path: {file_path}")
            with open(file_path, "r") as file:
                content: Any = json.load(file)

            if len(content["messages"]) > 0:
                for i in content["messages"]:
                    self.messages.append(i)
        except Exception as exc:
            print(f"{exc}")

    def chat_gpt(self, user_input) -> str:
        try:
            temp_messages: List[Any] = []
            abs_route: str = f"{self.father_path}/{str(self.params['topic']).lower().replace(' ', '_')}.json"
            input_str: Any = {"role": "user", "content": user_input}
            self.messages.append(input_str)
            self.logger.debug(f"messages route: {abs_route}")

            self.transcript(f"{abs_route}", input_str)

            first_message: str = self.messages[0]
            last_four_messages: str = self.messages[-4:]

            self.logger.debug(f"first_message: {first_message}")
            self.logger.debug(f"last_four_messages: {last_four_messages}")

            temp_messages.append(first_message)
            temp_messages.extend(last_four_messages)

            self.logger.debug(f"temp_messages: {temp_messages}")

            response = openai.ChatCompletion.create(
                model=self.params['model'],
                messages=temp_messages
            )

            gpt_response = response["choices"][0]["message"]["content"]
            output_str: Any = {"role": "assistant", "content": gpt_response}

            self.transcript(f"{abs_route}", output_str)

            self.logger.debug(f"messages: {self.messages}")
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
                      root_path=self.params['root_path'],
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
        self.set_logger(params)
        self.params = params

    def set_messages(self, messages) -> None:
        self.messages = messages

    def set_system_content(self, content) -> None:
        self.messages[0]['content'] = content
        self.logger.debug(f"Messages: {self.messages}")
