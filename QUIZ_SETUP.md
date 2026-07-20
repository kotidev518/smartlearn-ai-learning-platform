# 🤖 AI Quiz System Setup

This document focuses on configuring the automated quiz generation system powered by Google Gemini AI and the ARQ background worker.

## 1. Prerequisites
- **Google AI Studio API Key**: Get it from [aistudio.google.com](https://aistudio.google.com/).
- **Redis Server**: Must be running as the message broker for background jobs.

## 2. Configuration
Add these to your `backend/.env`:
```env
# Gemini API Key for Quiz Generation
GEMINI_API_KEY=your-gemini-key

# Redis Connection for Background Tasks
REDIS_URL=redis://127.0.0.1:6379
```

## 3. How it Works
1. **Admin Import**: When an admin imports a YouTube playlist, the metadata is saved immediately.
2. **Background Job**: The system automatically adds video tasks to a MongoDB-backed processing queue.
3. **Automated Worker**: The backend server starts a background worker task on startup that fetches transcripts, generates embeddings, and creates AI quizzes.

## 🛠 Troubleshooting
- **No Quizzes Generated**: Check your backend server logs. You should see `🧠 Calling Gemini AI...` or any error messages there.
- **Gemini API Limits**: The worker uses exponential backoff to retry if rate-limited by Google.
- **Redis Down**: The server will log a warning if it cannot connect to the `REDIS_URL`, though basic processing may still work via the internal queue.
