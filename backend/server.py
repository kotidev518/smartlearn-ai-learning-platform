import uvicorn
import os

if __name__ == "__main__":
    # Check if running in a cloud environment where PORT is set
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
