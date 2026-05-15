# LinkedIn AI Automation Agent 🚀

An AI-powered LinkedIn automation bot that automatically:

- Fetches trending AI topics
- Generates professional LinkedIn posts using Groq AI
- Creates topic-based AI images
- Publishes directly to LinkedIn using Playwright

---

## Features

✅ Trending AI topic detection  
✅ Unique LinkedIn post generation  
✅ AI-generated matching images  
✅ Automatic LinkedIn posting  
✅ Session-based LinkedIn login  
✅ Repeat topic avoidance  

---

## Tech Stack

- Python
- Playwright
- Groq API
- Google News RSS
- Requests
- Feedparser

---

## Project Structure

```bash
linkedin-ai-automation-agent/
│
├── agents/
│   ├── content.py
│   ├── image.py
│   └── review.py
│
├── linkedin.py
├── main.py
├── config.py
├── scheduler.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Installation

Clone repo:

```bash
git clone https://github.com/Grav-D-Scientist-08/linkedin-ai-automation-agent.git
cd linkedin-ai-automation-agent
```

Install dependencies:

```bash
pip install -r requirements.txt
playwright install
```

---

## Environment Setup

Create `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## Run Project

```bash
python main.py
```

---

## Workflow

```text
Trending Topic Fetch
        ↓
AI Post Generation
        ↓
AI Image Generation
        ↓
LinkedIn Auto Publishing
```

---

## Future Improvements

- Daily scheduled posting
- Canva-quality image generation
- Multi-platform posting
- Analytics dashboard

---

## Author

**Gaurav Bisht**
AI Trainer | Data Science | Agentic AI
