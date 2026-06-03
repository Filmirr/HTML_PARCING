# 🤖 Work.ua Python Jobs Bot

A Telegram bot that automatically scrapes **work.ua** for new Python developer job listings and posts them to a Telegram channel — so you never miss a fresh vacancy.

---

## 📌 What It Does

- Parses job listings from [work.ua](https://www.work.ua/jobs/?search=python) every **30 minutes**
- Handles **pagination** automatically — scrapes all available pages
- Stores seen jobs in a local **SQLite database** to avoid duplicate notifications
- Sends **instant Telegram notifications** with job title, salary, and link
- Runs fully async via **aiogram 3.x** + **asyncio**

---

## 🛠 Tech Stack

| Tool | Purpose |
|---|---|
| `Python 3.11+` | Core language |
| `aiogram 3.x` | Telegram Bot API framework |
| `BeautifulSoup4 + lxml` | HTML parsing |
| `requests` | HTTP client for scraping |
| `SQLite3` | Lightweight local storage |
| `asyncio` | Async scheduling loop |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/workua-python-jobs-bot.git
cd workua-python-jobs-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

```bash
export BOT_TOKEN="your_telegram_bot_token"
export ChanNEL_ID="-100xxxxxxxxxx"
```

Or create a `.env` file and load it with `python-dotenv`.

### 4. Run the bot

```bash
python main.py
```

---

## ⚙️ How It Works

```
┌─────────────────────────────────────────────┐
│            Scheduler (every 30 min)          │
└────────────────────┬────────────────────────┘
                     │
                     ▼
         Scrape work.ua (all pages)
                     │
                     ▼
        For each job: is it new in DB?
          ├── YES → skip
          └── NO  → save to DB + send to Telegram
```

1. On startup, `scheduler()` runs immediately and then every 30 minutes
2. `get_all_jobs()` iterates through paginated results until no "Next" button is found
3. `parse_jobs()` extracts job ID, title, URL, and salary from each listing
4. `is_new()` checks the SQLite DB — only unseen jobs are forwarded
5. `send_job()` posts a formatted message to your Telegram channel

---

## 📬 Notification Format

```
💼 Python Developer (Middle)
https://www.work.ua/jobs/7244026/
Зарплата: 45 000 грн
```

---

## 📁 Project Structure

```
.
├── main.py          # Entry point — bot, scheduler, handlers
├── jobs.db          # SQLite database (auto-created on first run)
├── requirements.txt
└── README.md
```

---

## 📄 requirements.txt

```
aiogram>=3.0
requests
beautifulsoup4
lxml
```

---

## 💡 Possible Improvements

- [ ] Add support for multiple search queries (Django, FastAPI, etc.)
- [ ] Filter by salary range or keywords
- [ ] Docker support for easy deployment
- [ ] `/latest` command to fetch jobs on demand
- [ ] Deploy to a VPS or Railway for 24/7 uptime

---

## 👤 Author

Made by **[Your Name]** — Python developer open to freelance projects.

- Telegram: [@your_handle](https://t.me/@Fillmirr)
- GitHub: [github.com/your-username]([https://github.com/your-username](https://github.com/Filmirr))
