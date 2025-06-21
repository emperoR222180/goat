import asyncio
import random
import logging
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait
from motor.motor_asyncio import AsyncIOMotorClient

API_ID = 20061115
API_HASH = "c30d56d90d59b3efc7954013c580e076"
SESSION_STRING = "BQEy_cEAMmE5spfKcA0nGfs19JcvfjJg7Hwb7j8DsIEnmz-l-Nf7q6SxBbkGGCcAzf8EUTsIPtHkhkUNRSvF00SpXyEnmoNKqK6SMBrNGqpfTEHiaa5H1jq7ZzSdH8dkmuYQfsM4GAmWqBuKb1FW9U2gzC8i1O6QokuWEGHC0vSCXWc1-u8jYaoCOCrtO7GIMBea_KUTz_5hgRxKKBa47HEjPtMdVqIwNwA-ecFFrVeZXdAOaCoDbR01RKWk_fXiJDyXxZssNbqbwXUFr1B-nLzzROetndZvvNBW_iFg2kjoT5mbh_a77oF0MjixgB9_iciwsSZfBMqut9GCVVXc5X7iCoznKAAAAAHL0vSAAA"
MONGO_URI = "mongodb+srv://swami2006:lptXBAFHlyS7uHvT@cluster0.iapxnlf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

MAIN_GROUP_ID = -1002340308104
FORWARD_CHANNEL_ID = None
OG_CAPTIONS = [
    "🔥 ʟᴏᴏᴋ ᴀɴ ᴏɢ ᴘʟᴀʏᴇʀ ᴊᴜꜱᴛ ᴀʀʀɪᴠᴇᴅ ᴄᴏʟʟᴇᴄᴛ ʜɪᴍ/Her ᴜꜱɪɴɢ /ᴄᴏʟʟᴇᴄᴛ ɴᴀᴍᴇ",
    "🔥 ʟᴏᴏᴋ ᴀɴ ᴏɢ ᴀᴛʜʟᴇᴛᴇ ᴊᴜꜱᴛ ᴀʀʀɪᴠᴇᴅ ᴄᴏʟʟᴇᴄᴛ ʜɪᴍ/Her ᴜꜱɪɴɢ /ᴄᴏʟʟᴇᴄᴛ ɴᴀᴍᴇ",
    "🔥 ʟᴏᴏᴋ ᴀɴ ᴏɢ ᴄᴇʟᴇʙʀɪᴛʏ ᴊᴜꜱᴛ ᴀʀʀɪᴠᴇᴅ ᴄᴏʟʟᴇᴄᴛ ʜɪᴍ/Her ᴜꜱɪɴɢ /ᴄᴏʟʟᴇᴄᴛ ɴᴀᴍᴇ",
    "🔥 ʟᴏᴏᴋ ᴀɴ ᴏɢ ᴀʟʟ sᴛᴀʀ ᴊᴜꜱᴛ ᴀʀʀɪᴠᴇᴅ ᴄᴏʟʟᴇᴄᴛ ʜɪᴍ/Her ᴜꜱɪɴɢ /ᴄᴏʟʟᴇᴄᴛ ɴᴀᴍᴇ",
    "🔥 Look an OG Player Just Arrived! Collect him/Her using /collect name"
]
MAIN_GROUP_TRIGGERS = ["/hmm", "/hii", "/coolect", "/2", "2", "M", "m", ".",]
MAIN_GROUP_STOP_WORDS = ["/afk", "/brb", "/gn", "afk", "brb", "gm", "l", "L", "/slot", "/basket"]
RARITIES_TO_FORWARD = ["Cosmic", "Limited Edition", "Exclusive", "Ultimate", "Mythic"]

logging.basicConfig(level=logging.INFO)

bot = Client(
    "main_group_collect",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

client = AsyncIOMotorClient(MONGO_URI)
db_goku = client["players_db"]["goku_players"]
player_cache = {}
collection_status = False
last_collected_file_id = None

def should_forward_message(text):
    if not text:
        return False
    for rarity in RARITIES_TO_FORWARD:
        if f"Rarity : {rarity}" in text:
            return True
    if ("✪ You Collected A" in text and "Take A Look At Your Collection Using /mycollection" in text) or \
       ("✅ Look You Collected A" in text):
        return True
    return False

@bot.on_message(filters.chat(MAIN_GROUP_ID))
async def main_group_collect(c, m):
    global collection_status, player_cache, last_collected_file_id
    try:
        # Only user 1259702343 can trigger/stop collection with text
        if m.text:
            if not (m.from_user and m.from_user.id == 7714567296):
                return
            text = m.text.strip()
            if text.lower() in [w.lower() for w in MAIN_GROUP_STOP_WORDS]:
                collection_status = False
                last_collected_file_id = None
                logging.info("Collection stopped in main group via stop command.")
                return
            if text.lower() in [w.lower() for w in MAIN_GROUP_TRIGGERS]:
                collection_status = True
                last_collected_file_id = None
                logging.info("Collection started in main group via trigger command.")
                return
            return
        # Only scan photos from user 7795661257 if collection is ON
        if m.from_user and m.from_user.id == 7795661257 and m.photo:
            if not collection_status:
                return
            if not m.caption or m.caption.strip() not in OG_CAPTIONS:
                return
            file_id = m.photo.file_unique_id
            if file_id == last_collected_file_id:
                return
            # Check player in cache (always use db_goku)
            if file_id in player_cache:
                player_name = player_cache[file_id]['name']
            else:
                file_data = await db_goku.find_one({"file_id": file_id})
                if file_data:
                    player_name = file_data['name']
                    player_cache[file_id] = {"name": player_name}
                else:
                    return
            await asyncio.sleep(random.uniform(0.8, 1.3))
            sent_message = await bot.send_message(MAIN_GROUP_ID, f"/collect {player_name}")
            last_collected_file_id = file_id
            await asyncio.sleep(1)
            async for reply in bot.get_chat_history(MAIN_GROUP_ID, limit=5):
                if reply.reply_to_message and reply.reply_to_message.message_id == sent_message.message_id:
                    if should_forward_message(reply.text):
                        await bot.forward_messages(
                            chat_id=FORWARD_CHANNEL_ID,
                            from_chat_id=MAIN_GROUP_ID,
                            message_ids=reply.message_id
                        )
                    break
    except FloodWait as e:
        await asyncio.sleep(e.value + random.randint(1, 5))
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    bot.run()
