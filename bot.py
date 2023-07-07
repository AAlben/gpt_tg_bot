import os
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters


openai.api_key = os.getenv("OPENAI_API_KEY")
USER_IDS = os.getenv("USER_IDS").split(",")
USER_IDS = [int(user_id) for user_id in USER_IDS]
MODEL = "gpt-3.5-turbo-0613"


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


def request(messages, model):
    if os.getenv("DEBUG"):
        return "DEBUG"
    response = openai.ChatCompletion.create(model=model, messages=messages)
    result = ""
    for choice in response.choices:
        result += choice.message.content
    return result


# ----- START GPT Function -----


def gpt(question, user_data):
    topic = user_data.get("topic")
    model = user_data.get("model", MODEL)
    msgs = [{"role": "user", "content": question}]
    if topic:
        msgs.insert(0, {"role": "system", "content": f"只回答{topic}相关的内容"})
    return request(msgs, model)


def gpt_translate(question, user_data):
    model = user_data.get("model", MODEL)
    msgs = [{"role": "user", "content": question}]
    msgs.insert(0, {"role": "system", "content": f"你是一个中英、英中翻译机器人，翻译以下内容。"})
    return request(msgs, model)


def gpt_code(question, user_data):
    topic = user_data.get("topic")
    model = user_data.get("model", MODEL)
    msgs = [{"role": "user", "content": question}]
    msgs.insert(0, {"role": "system", "content": f"讲解{topic}代码"})
    return request(msgs, model)


def gpt_eng(question):
    model = user_data.get("model", MODEL)
    msgs = [{"role": "user", "content": question}]
    msgs.insert(0, {"role": "system", "content": "我希望你能扮演一位英语老师和改进者的角色。我会用英语与你交流，对于我的英语句子或单词，介绍一下它的基本英语语法规则和用法，并提供例句和练习题。"})
    return request(msgs, model)


# ----- END GPT Function -----


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
        content = gpt(msg, context.user_data)
    else:
        content = "TOPIC was Cleared."
    await update.message.reply_text(content)


@check_user
async def translate_callback(update, context):
    msg = update.message.text.lstrip("/t").strip()
    content = gpt_translate(msg.strip(), context.user_data)
    await update.message.reply_text(content)


@check_user
async def code_callback(update, context):
    msg = update.message.text.lstrip("/code")
    user_data = context.user_data
    topic = user_data.get("topic")
    content = gpt_code(msg, context.user_data)
    await update.message.reply_text(content)


@check_user
async def eng_callback(update, context):
    msg = update.message.text.lstrip("/eng")
    user_data = context.user_data
    content = gpt_eng(msg, context.user_data)
    await update.message.reply_text(content)


@check_user
async def general_callback(update, context):
    msg = update.message.text
    user_data = context.user_data
    topic = user_data.get("topic")
    content = gpt(msg.strip(), context.user_data)
    await update.message.reply_text(content)


@check_user
async def version_callback(update, context):
    msg = update.message.text.lstrip("/v").strip()
    model = MODEL
    if msg == "4":
        model = "gpt-4-0613"
    user_data = context.user_data
    user_data["model"] = model
    await update.message.reply_text(f"MODEL = {model}")


# ----- END Callback Function -----


def main() -> None:
    application = Application.builder().token(os.environ.get("BOT_TOKEN")).build()
    application.add_handler(CommandHandler("tp", topic_callback))
    application.add_handler(CommandHandler("c", clear_callback))
    application.add_handler(CommandHandler("t", translate_callback))
    application.add_handler(CommandHandler("code", code_callback))
    application.add_handler(CommandHandler("eng", eng_callback))
    application.add_handler(CommandHandler("v", version_callback))
    application.add_handler(MessageHandler(filters.TEXT, general_callback))
    application.run_polling()


if __name__ == "__main__":
    main()
