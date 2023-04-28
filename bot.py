import os
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters


openai.api_key = os.getenv("OPENAI_API_KEY")
USER_IDS = os.getenv("USER_IDS").split(",")
USER_IDS = [int(user_id) for user_id in USER_IDS]


def check_user(func):
    async def wrapper(*args, **kwargs):
        update = args[0]
        if os.getenv("DEBUG"):
            print(update.message.chat.id)        
        if update.message.chat.id in USER_IDS:
            result = await func(*args, **kwargs)
            return result
        return await update.message.reply_text(f"WRONG USER: {update.message.chat.id}")
    return wrapper


def request(messages, model="gpt-3.5-turbo"):
    if os.getenv("DEBUG"):
        return "DEBUG"
    response = openai.ChatCompletion.create(model=model, messages=messages)
    result = ""
    for choice in response.choices:
        result += choice.message.content
    return result


# ----- START Callback Function -----


def gpt(question, topic=None):
    msgs = [{"role": "user", "content": question}]
    if topic:
        msgs.insert(0, {"role": "system", "content": f"只回答{topic}相关的内容"})
    return request(msgs)


def gpt_translate(question):
    msgs = [{"role": "user", "content": question}]
    msgs.insert(0, {"role": "system", "content": f"你是一个翻译机器人，中文翻译成英文，英文翻译成中文。"})
    return request(msgs)


def gpt_code(question, topic):
    msgs = [{"role": "user", "content": question}]
    msgs.insert(0, {"role": "system", "content": f"讲解{topic}代码"})
    return request(msgs)


# ----- END Callback Function -----


# ----- START Callback Function -----


@check_user
async def topic_callback(update, context):
    msg = update.message.text.lstrip("/tp").strip()
    user_data = context.user_data
    user_data["topic"] = msg
    await update.message.reply_text(f"TOPIC = {msg}")


@check_user
async def clear_callback(update, context):
    msg = update.message.text.lstrip("/c").strip()
    context.user_data["topic"] = None
    if msg:
        content = gpt(msg)
    else:
        content = "TOPIC was Cleared."
    await update.message.reply_text(content)


@check_user
async def translate_callback(update, context):
    msg = update.message.text.lstrip("/t").strip()
    content = gpt_translate(msg.strip())
    await update.message.reply_text(content)


@check_user
async def code_callback(update, context):
    msg = update.message.text.lstrip("/code")
    user_data = context.user_data
    topic = user_data.get("topic")
    content = gpt_code(msg, topic)
    await update.message.reply_text(content)


@check_user
async def general_callback(update, context):
    msg = update.message.text
    user_data = context.user_data
    topic = user_data.get("topic")
    content = gpt(msg.strip(), topic)
    await update.message.reply_text(content)


# ----- END Callback Function -----


def main() -> None:
    application = Application.builder().token(os.environ.get("BOT_TOKEN")).build()
    application.add_handler(CommandHandler("tp", topic_callback))
    application.add_handler(CommandHandler("c", clear_callback))
    application.add_handler(CommandHandler("t", translate_callback))
    application.add_handler(CommandHandler("code", code_callback))
    application.add_handler(MessageHandler(filters.TEXT, general_callback))
    application.run_polling()


if __name__ == "__main__":
    main()
