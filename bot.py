import discord
import aiohttp
import os

# 環境変数からトークンとAPIキーを取得
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

async def translate(text, target):
    """テキストを指定された言語に翻訳する関数（非同期）"""
    if not GOOGLE_API_KEY:
        return "⚠️ エラー: `GOOGLE_API_KEY` が環境変数に設定されていません。"
    
    url = "https://translation.googleapis.com/language/translate/v2"
    params = {
        "key": GOOGLE_API_KEY,
        "q": text,
        "target": target
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=params) as res:
                res_json = await res.json()
                if "error" in res_json:
                    return f"⚠️ Google翻訳APIエラー: {res_json['error']['message']}"
                
                return res_json["data"]["translations"][0]["translatedText"]
    except Exception as e:
        return f"⚠️ 翻訳処理中にエラーが発生しました: {e}"

@client.event
async def on_ready():
    print(f"ログイン成功: {client.user}")

@client.event
async def on_message(message):
    # Bot自身のメッセージには反応しない
    if message.author.bot:
        return

    content = message.content.strip()

    # 日本語 → インドネシア語
    if content.startswith("!id "):
        text = content[4:]
        if text:
            translated = await translate(text, "id")
            await message.channel.send(translated)

    # インドネシア語 → 日本語
    elif content.startswith("!ja "):
        text = content[4:]
        if text:
            translated = await translate(text, "ja")
            await message.channel.send(translated)

    # 自動判定翻訳 (!tr で始まる場合)
    elif content.startswith("!tr "):
        text = content[4:]
        if text:
            if not GOOGLE_API_KEY:
                await message.channel.send("⚠️ エラー: `GOOGLE_API_KEY` が環境変数に設定されていません。")
                return
                
            url = "https://translation.googleapis.com/language/translate/v2"
            params = {
                "key": GOOGLE_API_KEY,
                "q": text,
                "target": "id" # デフォルトでインドネシア語に翻訳して判定を確認
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, data=params) as res:
                        res_json = await res.json()
                        if "error" in res_json:
                            await message.channel.send(f"⚠️ Google翻訳APIエラー: {res_json['error']['message']}")
                            return
                        
                        translation_data = res_json["data"]["translations"][0]
                        detected_lang = translation_data.get("detectedSourceLanguage")
                        
                        # 入力がインドネシア語だった場合は日本語に翻訳し直す
                        if detected_lang == "id":
                            translated = await translate(text, "ja")
                            await message.channel.send(translated)
                        else:
                            await message.channel.send(translation_data["translatedText"])
            except Exception as e:
                await message.channel.send(f"⚠️ 翻訳処理中にエラーが発生しました: {e}")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("エラー: DISCORD_TOKEN が設定されていません。")
    else:
        client.run(DISCORD_TOKEN)