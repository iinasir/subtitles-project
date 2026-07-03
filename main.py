from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import worker, shutil, os, uuid, subprocess, time

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
tasks = {}

if not os.path.exists("uploads"): 
    os.makedirs("uploads")

def get_duration(file_path):
    # Tera exact FFprobe path
    ffprobe_path = r"C:\Users\nasir\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffprobe.exe" 
    
    if not os.path.exists(ffprobe_path):
        print(f"ERROR: ffprobe.exe yahan nahi mila: {ffprobe_path}")
        return 300.0 

    cmd = [ffprobe_path, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return float(result.stdout) if result.stdout else 300.0
    except Exception as e:
        print(f"FFprobe execution error: {e}")
        return 300.0

@app.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...), lang: str = Form(...)):
    task_id = str(uuid.uuid4())
    file_path = f"uploads/{task_id}_{file.filename}"
    
    with open(file_path, "wb") as buffer: 
        shutil.copyfileobj(file.file, buffer)
    
    time.sleep(0.5) # OS flush time
    duration = get_duration(file_path)
    
    tasks[task_id] = {"status": "processing", "progress": 0, "duration": duration}
    background_tasks.add_task(worker.generate_srt, file_path, lang, task_id, tasks)
    
    return {"task_id": task_id, "duration": duration}

@app.get("/status/{task_id}")
async def get_status(task_id: str): 
    return tasks.get(task_id, {"status": "not_found"})

@app.get("/")
def read_root(): 
    return FileResponse("static/index.html")