import discord
import requests
import os

# 環境変数から取得（←ここが重要）
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def translate(text, target):
    url = "https://translation.googleapis.com/language/translate/v2"
    params = {
        "key": GOOGLE_API_KEY,
        "q": text,
        "target": target
    }
    res = requests.post(url, data=params)
    return res.json()["data"]["translations"][0]["translatedText"]

@client.event
async def on_ready():
    print(f"ログイン成功: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # 日本語 → インドネシア語
    if message.content.startswith("!id "):
        text = message.content[4:]
        translated = translate(text, "id")
        await message.channel.send(translated)

    # インドネシア語 → 日本語
    if message.content.startswith("!ja "):
        text = message.content[4:]
        translated = translate(text, "ja")
        await message.channel.send(translated)

client.run(DISCORD_TOKEN)