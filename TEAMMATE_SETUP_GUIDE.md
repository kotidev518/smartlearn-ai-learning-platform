# 📺 Teammate Resolution Plan: Fixing Video Playback

If you cannot play videos on your local system, follow these steps exactly in order.

### Step 1: Update your Code
Pull the latest changes from GitHub to get the corrected video paths and the new CORS configuration.
```bash
git pull origin main
```

### Step 2: Set up Configuration Files
Since these files are ignored by Git, you must create them manually:
1.  **Firebase Credentials**: Ask the team lead for the `serviceAccountKey.json` file and place it in the `backend/` folder.
2.  **Environment Variables**:
    - Build your `backend/.env` file based on `backend/.env.example`.
    - Build your `frontend/.env` file based on `frontend/.env.example`.
    - **Crucial**: Ensure `FIREBASE_STORAGE_BUCKET=online-course-platform-68c2c.firebasestorage.app` is set in your backend `.env`.

### Step 3: Synchronize your Local Database
Your local MongoDB still has the old YouTube links. You need to force it to update with the new Firebase paths from the code.
1.  Start your backend (`uvicorn server:app --reload`).
2.  Run this command in a terminal:
    ```bash
    curl -X POST "http://localhost:8000/api/init-data?force=true"
    ```
    *If successful, you will see a message: "Sample data initialized successfully".*

### Step 4: Fix Browser Blocking (CORS)
*Note: This only needs to be done once per bucket. If the team lead has already done this, you can skip to Step 5.*
1.  Run this command from the project root:
    ```bash
    python backend/apply_cors.py
    ```

### Step 5: Verify
1.  Restart your browser.
2.  Clear your cache or open the app in **Incognito Mode**.
3.  The videos in all courses should now play correctly.

---
**Still having issues?**
Open the browser console (F12) and check the "Network" tab for any red requests to `storage.googleapis.com`.
- **403 Error**: You are likely missing the `serviceAccountKey.json` or it doesn't have permissions.
- **404 Error**: The file path in `server.py` doesn't match the file in Firebase (check for typos).
