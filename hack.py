import asyncio

import time

from typing import Dict, Any

from aiogram import Bot, Dispatcher, F

from aiogram.types import (

Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

)

from aiogram.filters import Command

from aiogram.client.default import DefaultBotProperties

import logging

logging.basicConfig(level=logging.INFO)

# ========== CONFIG ==========

API_TOKEN = "6803648245:AAFnqImopwkF1R9Bjn-u7CjvSIJYGAQmU1Q"

JOIN_CHANNEL = "https://t.me/+xgT2L3_8UfFiMWVl"

REGISTER_LINK = "https://www.gg789game3.com/#/pages/login/register?invitationCode=6472730337"

BANNER_IMAGE_URL = None

============================

bot = Bot(

token=API_TOKEN,

default=DefaultBotProperties(parse_mode="HTML")

)

dp = Dispatcher()

USERS: Dict[int, Dict[str, Any]] = {}

DAILY_COOLDOWN = 24 * 60 * 60  # 24 hours

---------- Helpers ----------

def mk_pred_keyboard(period: int) -> InlineKeyboardMarkup:

kb = InlineKeyboardMarkup(inline_keyboard=[

    [

        InlineKeyboardButton(text="✅ Win", callback_data=f"res:win:{period}"),

        InlineKeyboardButton(text="❌ Loss", callback_data=f"res:loss:{period}")

    ],

    [

        InlineKeyboardButton(text="📢 Join Channel", url=JOIN_CHANNEL),

        InlineKeyboardButton(text="🎁 Claim Bonus", callback_data="claim:bonus")

    ]

])

return kb

def pretty_prediction_card(period: int, prediction: str) -> str:

return (

    f"<b>🚀 IQ VIP PREDICTION TOOL 🚀</b>\n"

    f"<b>⏳ Period Number:</b> <code>{str(period).zfill(3)}</code>\n"

    f"<b>🔍 Prediction:</b> <b>{prediction}</b>\n"

    f"<i>🎯 This Bot works best if you register using our official link.</i>"

)

---------- Start / Welcome ----------

@dp.message(Command(commands=["start"]))

async def cmd_start(message: Message):

user_id = message.from_user.id

USERS.setdefault(user_id, {

    "period": None, "last_result": None, "prediction": None, "history": [], "daily_bonus_ts": 0

})



kb = InlineKeyboardMarkup(inline_keyboard=[

    [InlineKeyboardButton(text="🎯 Start Prediction", callback_data="start:predict")],

    [InlineKeyboardButton(text="🔗 Register Now", url=REGISTER_LINK)],

    [InlineKeyboardButton(text="📢 Join Channel", url=JOIN_CHANNEL)]

])



welcome_text = (

    "<b>👋 स्वागत है IQ COLOUR PREDICTOR BOT 🎯</b>\n\n"

    "💡 अब आप Attractive size predictions (BIG / SMALL) पा सकते हैं — "

    "बस नीचे <b>Start Prediction</b> दबाएं और 3-digit period भेजें।\n\n"

    "📌 <i>Register करने के बाद बेहतर support मिलता है.</i>\n\n"

    "<b>➡️ Click Start Prediction to begin</b>"

)



if BANNER_IMAGE_URL:

    try:

        await message.answer_photo(photo=BANNER_IMAGE_URL, caption=welcome_text, reply_markup=kb)

        return

    except Exception:

        pass



await message.answer(welcome_text, reply_markup=kb)

---------- Start Prediction Button ----------

@dp.callback_query(F.data == "start:predict")

async def on_start_predict(cb: CallbackQuery):

user_id = cb.from_user.id

USERS.setdefault(user_id, {"period": None, "last_result": None, "prediction": None, "history": [], "daily_bonus_ts": 0})

await cb.message.answer("🔢 कृपया अपना <b>Current Period Number (3 digits)</b> भेजें (e.g. <code>123</code>)")

await cb.answer()

---------- Handle Period ----------

@dp.message(F.text.regexp(r'^\d{3}$'))

async def handle_period(message: Message):

user_id = message.from_user.id

text = message.text.strip()



USERS.setdefault(user_id, {"period": None, "last_result": None, "prediction": None, "history": [], "daily_bonus_ts": 0})

USERS[user_id]["period"] = int(text)

USERS[user_id]["last_result"] = None

USERS[user_id]["prediction"] = None



await message.reply(

    f"✅ <b>Period saved:</b> <code>{text}</code>\nअब कृपया <b>Last Result</b> भेजें (BIG / SMALL)."

)

---------- Handle BIG / SMALL ----------

@dp.message(F.text.regexp(r'^(BIG|SMALL|big|small)$'))

async def handle_result(message: Message):

user_id = message.from_user.id

text = message.text.strip().upper()



user = USERS.get(user_id)

if not user or not user.get("period"):

    await message.reply("⚠️ पहले <b>3-digit Period</b> भेजिए (e.g. <code>123</code>).")

    return



prediction = text

user["last_result"] = text

user["prediction"] = prediction



await message.reply(pretty_prediction_card(user["period"], prediction), reply_markup=mk_pred_keyboard(user["period"]))

---------- Claim Bonus ----------

@dp.callback_query(F.data == "claim:bonus")

async def claim_bonus(cb: CallbackQuery):

user_id = cb.from_user.id

u = USERS.setdefault(user_id, {"period": None, "last_result": None, "prediction": None, "history": [], "daily_bonus_ts": 0})

now = time.time()



if now - u.get("daily_bonus_ts", 0) < DAILY_COOLDOWN:

    await cb.answer("🔥 Daily bonus already claimed. Try after 24 hours.", show_alert=True)

    return



u["daily_bonus_ts"] = now

await cb.message.answer("🎁 <b>Daily Bonus Claimed!</b>\n\n💡 <i>Tip: Play responsibly — small consistent bets increase longevity.</i>\n\nGood luck! 🍀")

await cb.answer("🎁 Bonus granted!")

---------- Win/Loss ----------

@dp.callback_query(F.data.regexp(r'^res:(win|loss):(\d+)$'))

async def process_result_buttons(cb: CallbackQuery):

action, period = cb.data.split(":")[1:3]

user_id = cb.from_user.id

user = USERS.get(user_id)



if not user or not user.get("prediction"):

    await cb.answer("⚠️ No active prediction found. Start a new one.", show_alert=True)

    return



cur_period = int(period)

pred = user["prediction"]



user["history"].append({"period": cur_period, "prediction": pred, "result": action})



next_pred = pred if action == "win" else ("BIG" if pred == "SMALL" else "SMALL")

next_period = cur_period + 1



user["period"] = next_period

user["prediction"] = next_pred

user["last_result"] = None



await cb.message.answer(pretty_prediction_card(next_period, next_pred), reply_markup=mk_pred_keyboard(next_period))



total = len(user["history"])

if total > 0 and total % 10 == 0:

    wins = sum(1 for h in user["history"] if h["result"] == "win")

    losses = sum(1 for h in user["history"] if h["result"] == "loss")

    rate = (wins / total * 100)

    await cb.message.answer(

        f"<b>📊 {total} Rounds Summary</b>\n"

        f"✅ Wins: <b>{wins}</b>\n"

        f"❌ Losses: <b>{losses}</b>\n"

        f"🎯 Win Rate: <b>{rate:.2f}%</b>"

    )



await cb.answer("✅ Result recorded.")

---------- Run ----------

async def main():

print("Bot starting...")

await dp.start_polling(bot)

if name == "main":

asyncio.run(main())
