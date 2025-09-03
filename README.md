# Django Realtime Chat App

A minimal real-time chat application built with **Django**, **Channels (WebSockets)**, and vanilla **JavaScript**.  
Supports direct 1-on-1 messaging, typing indicators, delete buttons on hover, and email verification via Gmail.

---

## Features
- User authentication (Django built-in auth).  
- Email verification on sign-up (using Gmail App Service).  
- Real-time private messaging over WebSockets.  
- Typing indicator ("X is typing...").  
- Message delete button shown on hover.  
- Scroll-to-bottom on new messages.  

---

## Tech Stack
- **Backend**: Django, Django Channels, Redis (as channel layer).  
- **Frontend**: HTML, CSS, Vanilla JavaScript.  
- **WebSockets**: For live messaging and presence updates.  
- **Email Service**: Gmail (App password setup required).  

---

## Requirements
- Python 3.10+  
- Redis (running locally or in Docker)  
- Gmail account (with [App Passwords](https://support.google.com/accounts/answer/185833?hl=en))  

---

## Installation

```bash
# Clone repo
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# Create virtual environment
python -m venv venv
source venv/bin/activate   # on Linux/Mac
venv\Scripts\activate      # on Windows

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
