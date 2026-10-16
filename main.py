from fastapi import FastAPI

app = FastAPI(title="AP Invoice Tracker")

@app.get("/health")
def health():
    return {"status": "ok"}