#!/usr/bin/env python3
"""
Telegram Vocabulary Bot - EPS Korean
Gửi 10 từ vựng ngẫu nhiên mỗi ngày lúc 10:30 (giờ Hàn Quốc, UTC+9)
Tích hợp Gemini AI để tạo dạng thân mật (반말)
"""

import json
import random
import logging
import asyncio
import httpx
from datetime import datetime, timezone, timedelta
from pathlib import Path

from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Load vocabulary ───────────────────────────────────────────────────────────
VOCAB_FILE = Path(__file__).parent / "vocab.json"

def load_vocab() -> list[dict]:
    with open(VOCAB_FILE, encoding="utf-8") as f:
        return json.load(f)

VOCAB = load_vocab()
logger.info(f"Loaded {len(VOCAB)} vocabulary entries.")

# ── Gemini API ────────────────────────────────────────────────────────────────
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)

async def get_banmal(words: list[dict]) -> dict[str, str]:
    
    await asyncio.sleep(10)
    """Gọi Gemini để lấy dạng thân mật (반말) cho danh sách từ."""
    word_list = "\n".join(
        f"- {w['korean']} ({w['vietnamese']})" for w in words
    )
    prompt = (
        "Bạn là chuyên gia tiếng Hàn. Với mỗi từ dưới đây:\n"
        "- Nếu là động từ/tính từ (kết thúc bằng 다): cho dạng thân mật 반말 "
        "(ví dụ: 앉다→앉아, 가다→가, 예쁘다→예뻐, 먹다→먹어)\n"
        "- Nếu là danh từ hoặc cụm từ: trả về dấu gạch ngang '-'\n\n"
        f"{word_list}\n\n"
        "Trả về JSON thuần túy, không markdown, định dạng:\n"
        '{"từ_hàn_quốc": "dạng_반말", ...}'
    )

    try:
        async with httpx.AsyncClient(timeout=15) as client:  
            resp = await client.post(
                GEMINI_URL,
                params={"key": config.GEMINI_API_KEY},
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            # Strip markdown fences if present
            text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(text)
    except Exception as e:
        print("GEMINI ERROR:", e)
        logger.error(f"Gemini API error: {e}")
        return {}

# ── Message builder ───────────────────────────────────────────────────────────
def escape(text: str) -> str:
    """Escape MarkdownV2 special characters."""
    special = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in special else c for c in str(text))

def build_message(words: list[dict], banmal: dict[str, str]) -> str:
    KST = timezone(timedelta(hours=9))
    today = datetime.now(KST).strftime("%d/%m/%Y")

    lines = [
        f"📚 *Từ vựng tiếng Hàn hôm nay* — {escape(today)}",
        f"_{escape(str(len(words)))} từ ngẫu nhiên cho bạn ôn luyện\\!_\n",
    ]
    for i, w in enumerate(words, 1):
        ban = banmal.get(w["korean"], "-")
        ban_str = f"  _\\({escape(ban)}\\)_" if ban and ban != "-" else ""
        lines.append(
            f"{i}\\. 🇰🇷 *{escape(w['korean'])}*{ban_str}  ➜  🇻🇳 {escape(w['vietnamese'])}"
        )

    lines.append("\n💪 _Học đều mỗi ngày — giỏi lúc nào không hay\\!_")
    return "\n".join(lines)

# ── Send daily vocab ──────────────────────────────────────────────────────────
async def send_daily_vocab(bot: Bot):
    words = random.sample(VOCAB, min(10, len(VOCAB)))
    banmal = await get_banmal(words)
    message = build_message(words, banmal)
    try:
        await bot.send_message(
            chat_id=config.CHAT_ID,
            text=message,
            parse_mode="MarkdownV2",
        )
        logger.info(f"Daily vocab sent to {config.CHAT_ID}")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

# ── Command handlers ──────────────────────────────────────────────────────────
async def cmd_start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Xin chào! Mình là bot từ vựng EPS tiếng Hàn.\n\n"
        "⏰ Mỗi ngày lúc *10:30 giờ Hàn Quốc* mình sẽ gửi 10 từ vựng kèm dạng thân mật 반말.\n\n"
        "📌 Lệnh khả dụng:\n"
        "/vocab — Nhận 10 từ ngay bây giờ\n"
        "/stats — Xem thống kê từ điển",
        parse_mode="Markdown",
    )

async def cmd_vocab(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Đang tạo danh sách từ vựng...")
    words = random.sample(VOCAB, min(10, len(VOCAB)))
    banmal = await get_banmal(words)
    message = build_message(words, banmal)
    await update.message.reply_text(message, parse_mode="MarkdownV2")

async def cmd_stats(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📊 *Thống kê từ điển EPS*\n\n"
        f"• Tổng số từ: *{len(VOCAB)}* từ\n"
        f"• Gửi mỗi ngày: *10* từ ngẫu nhiên\n"
        f"• Giờ gửi: *10:30 KST* (08:30 VN)\n"
        f"• AI: Gemini 2\\.0 Flash ✨",
        parse_mode="Markdown",
    )

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("vocab", cmd_vocab))
    app.add_handler(CommandHandler("stats", cmd_stats))

    # Scheduler: 10:30 KST = 01:30 UTC
    async def scheduled_job():
        await send_daily_vocab(app.bot)

    scheduler = AsyncIOScheduler(timezone="Asia/Seoul")
    scheduler.add_job(
        scheduled_job,
        trigger="cron",
        hour=16,
        minute=55,
        id="daily_vocab",
    )
    scheduler.start()
    logger.info("Scheduler started — daily vocab at 12:13 KST (03:13 UTC)")

    logger.info("Bot is running... Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True, poll_interval=1, timeout=1)

if __name__ == "__main__":
    main()
