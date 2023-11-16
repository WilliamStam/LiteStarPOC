import uvicorn
import multiprocessing
import os
import sys
# from src.main import app
# db.declarative_base.metadata.create_all(bind=db.engine)

# just incase the app is run as python main.py

if __name__ == "__main__":
    os.chdir("src")
    print(os.getcwd())
    cur_dir = os.path.dirname(__file__)
    
    sys.path.insert(0, os.getcwd())
    multiprocessing.freeze_support()
    uvicorn.run("app:app",reload=True, port=8000)
    # uvicorn.run("main:app")