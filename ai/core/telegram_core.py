import os
import telegram

from typing import Any, Dict
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, PicklePersistence

from ai.core.commons import log_lvl, log_str
from ai.core.logger import get_logger
from ai.core.openai_core import OpenAiCore
from ai.core.redis_client import RedisClient

openai_instance = OpenAiCore()
persistance_chat = RedisClient()


class TelegramCore:
    application_builder: Any
    persistence: Any
    handler: CommandHandler
    logger: Any
    log_lvl: str
    log_str: str

    def __init__(self) -> None:
        self.logger = get_logger(log_lvl, log_str, __name__)
        if os.getenv("TELEGRAM_BOT_TOKEN", None) is not None:
            self.bot = telegram.Bot(os.getenv("TELEGRAM_BOT_TOKEN"))
            self.persistence = PicklePersistence(filepath="conversationbot")
            self.application_builder = ApplicationBuilder()\
                .token(os.getenv("TELEGRAM_BOT_TOKEN"))\
                .persistence(self.persistence).build()

    # Handle /start command
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        messages: list = [
            {
                "role": "system",
                "content": "I am a highly intelligent question answering bot. If you ask me a question that is rooted in truth, I will give you the answer. If you ask me a question that is nonsense, trickery, or has no clear answer, I will respond with 'Unknown'"
            }
        ]
        openai_instance.set_messages(messages)
        self.logger.debug(f"User {update.effective_user['username']} started the bot, context: {context}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm your personal openai bot.")

    # Generate response
    async def generate_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.logger.debug(f"User {update.effective_user['username']} sent a message., message: {update.message.text}, context: {context}")
        chat_id = update.effective_chat.id
        user_data = persistance_chat.get_chat_data(chat_id)
        temp_message = f"Q: {update.message.text}\n"
        message: str = ""

        if len(user_data) == 0:
            system_str = "Soy un bot de respuesta a preguntas altamente inteligente. Si me haces preguntas que esten basadas en la verdad, te daré la respuesta. Si me haces una pregunta que no tiene sentido, es una trampa, o no tiene una respuesta clara, responderé con 'No puedo ayudarte' y si me saludas te devolvere el saludo\n\n"
            persistance_chat.set_chat_data(chat_id, system_str)
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Hola, Soy un bot de respuesta a preguntas altamente inteligente")
            message += system_str
        else:
            for m in user_data:
                message += user_data.get(m).decode("utf-8")

        message += f"{temp_message}"

        persistance_chat.set_chat_data(chat_id, f"{temp_message}")
        response = openai_instance.text_chat_gpt(message)

        if response != "":
            persistance_chat.set_chat_data(chat_id, f"A: {response}\n")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Ocurrio un problema al generar la respuesta, por favor intenta de nuevo")

    # Handle unknow command
    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.logger.debug(f"User {update.effective_user['username']} sent an unknown command. Command: {update}, context: {context}")
        if update.message.text.startswith("/"):
            if update.message.text == "/role":
                openai_instance.set_system_content(update.message.text)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I don't understand your command.")

    def run(self, params: Dict) -> None:
        if params['telegram']:
            get_logger(params['log_level'], params['log_format'], __name__)
            self.logger.debug(f"Params: {params}")
            self.start_handler()
            self.generate_response_handler()
            self.unknown_handler()
            self.application_builder.run_polling()

    def start_handler(self):
        self.handler = CommandHandler("start", self.start)
        self.application_builder.add_handler(self.handler)

    def generate_response_handler(self):
        generate_response = MessageHandler(filters.TEXT & (~filters.COMMAND), self.generate_response)
        self.application_builder.add_handler(generate_response)

    def unknown_handler(self):
        unknown = MessageHandler(filters.COMMAND, self.unknown)
        self.application_builder.add_handler(unknown)
