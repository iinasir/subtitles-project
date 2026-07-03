from faster_whisper import WhisperModel

print("Loading Whisper Model...")
model = WhisperModel("tiny", device="cpu", compute_type="int8")
print("Model loaded successfully!")

def format_timestamp(s):
    m, s = divmod(s, 60); h, m = divmod(m, 60)
    return f"{int(h):02}:{int(m):02}:{int(s):02},{int((s%1)*1000):03}"

def generate_srt(file_path, lang_code, task_id, tasks):
    try:
        print(f"Starting transcription for task {task_id}")
        lang_param = None if lang_code == "do_it_yourself" else lang_code
        
        segments, _ = model.transcribe(file_path, beam_size=1, language=lang_param)
        srt_content = ""
        duration = tasks[task_id].get("duration", 300)
        
        for i, s in enumerate(segments):
            # Smooth progression logic
            tasks[task_id]["progress"] = min(int((s.end / duration) * 100), 99)
            srt_content += f"{i+1}\n{format_timestamp(s.start)} --> {format_timestamp(s.end)}\n{s.text.strip()}\n\n"
        
        tasks[task_id].update({"status": "completed", "progress": 100, "srt": srt_content})
        print(f"Task {task_id} completed successfully.")
        
    except Exception as e:
        print(f"Error in worker: {str(e)}")
        tasks[task_id]["status"] = "error"