import uvicorn

if __name__ == "__main__":
    # This runs the Uvicorn server programmatically, which solves the path issues.
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)