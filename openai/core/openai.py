import json
import os

import gradio

import openai
from typing import List, Any, Dict

openai.api_key = os.getenv("OPENAPI_KEY", "YOUR_API_KEY")


class OpenAICore:
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
            abs_route: str = f"{self.abs_path}/{str(self.params['topic']).lower().replace(' ', '_')}.json"
            input_str: Any = {"role": "user", "content": user_input}
            self.messages.append(input_str)

            self.transcript(f"{abs_route}", input_str)

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.messages
            )

            chat_gpt_reply = response["choices"][0]["message"]["content"]
            output_str: Any = {"role": "assistant", "content": chat_gpt_reply}

            self.transcript(f"{abs_route}", output_str)

            self.messages.append(output_str)

            return chat_gpt_reply
        except Exception as exc:
            raise RuntimeError(f"{exc}")

    def start_gradio(self):
        try:
            gr = gradio.Interface(fn=self.chat_gpt,
                                  inputs=self.params['inputs'],
                                  outputs=self.params['outputs'],
                                  title=self.params['title'], )
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
