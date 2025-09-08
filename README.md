# ⏱️ Shift Timer Bot

### ℹ️ Description

> **Ru**
>
> > ShiftTimerBot помогает работникам указывать время начала и окончания смены прямо в конце рабочего дня.
> > Администратор подтверждает данные, чтобы исключить ошибки и сформировать точный отчёт.
> > Бот автоматически рассчитывает отработанные часы с учётом опозданий, перерывов и ранних уходов.
> > Поддерживается выбор нескольких ролей на одной смене — например, пекарь, повар или конвейерный рабочий.
> > Это простое решение для учёта времени и справедливого распределения оплаты.

> **En**
>
> > ShiftTimerBot allows employees to enter their shift start and end times at the end of the day.
> > An administrator approves the records to ensure accurate reporting.
> > The bot calculates total hours worked, accounting for late arrivals, breaks, and early departures.
> > Multiple roles per shift are supported — for example, baker, cook, or assembly line worker.
> > It’s a simple solution for time tracking and fair payment distribution.

---

### ⚙️ Libraries and Tools

- 🐍 **Python**
- ⚡ **Aiogram**
- 🧪 **SQLAlchemy**
  - 📃 **Aiosqlite** for Development
  - 🐘 **AsyncPg** for Production
- ⚗️ **Alembic**
- 🧱 **Pydantic** + **Pydantic-Settings**

---

### 💡 Quick Start

**1. Clone the repository**

```bash
git clone https://github.com/SaidKamol0612/Shift-Timer-Bot.git
```

**2. Create and activate a virtual environment**

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Create and fill the `.env` file**

```env
# Bot token from @BotFather
BOT__BOT__TOKEN=your_token
# Set to 1 on development mode
BOT__BOT__DEBUG=0

# Database URL
BOT__DB__URL=sqlite+aiosqlite:///db.sqlite3
```

**5. Run the bot**

```bash
# On Windows
# .\.venv\Scripts\activate
.\run.bat

# Ob Linux
source .venv/bin/activate
python main.py
```

---

### 📷 Screenshots (coming soon!)

---

### 📝 License

MIT
