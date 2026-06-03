import os
import re
from time import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sqlite3
import time
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from aiogram.types import  Message
from aiogram.filters import Command
import schedule
import asyncio
from dotenv import load_dotenv






dp = Dispatcher() 
load_dotenv("config.env")

# --------------------------- base url ---------------------------

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = "https://www.work.ua"
CHANNEL_ID = int(os.getenv("CHANNEL_ID")) 



# --------------------------- telegram bot setup ---------------------------


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML 
    )
)

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("bot is working without using /start command, just wait for new jobs to appear")



def is_new(job_id: str) -> bool:
    return cursor.execute("SELECT 1 FROM jobs WHERE id=?", (job_id,)).fetchone() is None


async def save_and_check():
    search_url = f"{BASE_URL}/jobs/?search=python"
    jobs = get_all_jobs(search_url)
    for job in jobs:
        if is_new(job["id"]):
            save_jobs_to_db([job])
            await send_job(job)
            await asyncio.sleep(1)
        
        



async def send_job(job: dict):
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"💼 <b>{job['title']}</b>\n{job['url']}\nЗарплата: {job['salary']}"
    )

async def scheduler():
    while True:
        await save_and_check()
        await asyncio.sleep(30 * 60)



# --------------------------- database setup ---------------------------


conn = sqlite3.connect("jobs.db")
cursor = conn.cursor()
cursor.execute("""

CREATE TABLE IF NOT EXISTS jobs 
               ( 
               id TEXT PRIMARY KEY, 
               title TEXT, 
               url TEXT, 
               salary TEXT 
               )
""")

def save_jobs_to_db(jobs):
    for job in jobs:
        cursor.execute("""
        INSERT OR IGNORE INTO jobs (id, title, url, salary) 
        VALUES (?, ?, ?, ?)
        """, (job["id"], job["title"], job["url"], job["salary"]))
    conn.commit()



# --------------------------- parsing logic ---------------------------

def parse_jobs(html):
    soup = BeautifulSoup(html, "lxml")
    jobs = []

    # Ищем все ссылки вида /jobs/1234567/
    job_links = soup.find_all("a", href=re.compile(r"^/jobs/\d+/$"))

    for link in job_links:
        href = link.get("href", "")

        # ID вырезаем прямо из URL: /jobs/7244026/ → '7244026'
        job_id = href.strip("/").split("/")[-1]

        title = link.get_text(strip=True)
        if not title:
            continue  # попалась служебная ссылка без текста

        # Зарплата — ищем в родительском блоке
        # Карточка: <h2><a href="/jobs/123/">Название</a></h2>
        # Зарплата обычно в соседнем теге перед <h2> или рядом
        parent = link.find_parent("h2")
        salary = None
        if parent:
            # Ищем span с зарплатой рядом с заголовком
            salary_tag = parent.find_next("span", string=re.compile(r"грн"))
            if not salary_tag:
                # Ищем выше — перед <h2>
                salary_tag = parent.find_previous("span", string=re.compile(r"грн"))
            if salary_tag:
                salary = salary_tag.get_text(strip=True)

        jobs.append({
            "id":     job_id,
            "title":  title,
            "url":    urljoin(BASE_URL, href),
            "salary": salary or "не вказано",
        })

    return jobs


# --------------------------- sorting and pagination ---------------------------


def get_all_jobs(base_url):
    all_jobs = []
    page = 1

    while True:
        url = f"{base_url}&page={page}" if page > 1 else base_url
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()

        jobs = parse_jobs(r.text)
        if not jobs:
            break  # пустая страница — конец

        all_jobs.extend(jobs)

        # Проверяем есть ли кнопка "Наступна"
        soup = BeautifulSoup(r.text, "lxml")
        next_btn = soup.find("a", string=re.compile("Наступна"))
        if not next_btn:
            break

        page += 1
        time.sleep(1.5)  # пауза между страницами

    return all_jobs

# --------------------------- main logic ---------------------------



    

async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())