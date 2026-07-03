document.addEventListener('mousemove', (e) => {
    const glow = document.getElementById('glow');
    if (glow) {
        glow.style.left = e.pageX - 200 + 'px';
        glow.style.top = e.pageY - 200 + 'px';
    }
});

const statuses = [
    "Analyzing audio frequencies...",
    "Detecting speech patterns...",
    "Filtering ambient noise...",
    "Mapping dialogue structure...",
    "Syncing text with timeline...",
    "Drafting your masterpiece..."
];

async function handleFlow() {
    const fileInput = document.getElementById('file');
    if (!fileInput.files[0]) {
        alert("Bhai, file toh select kar!");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('lang', document.getElementById('lang').value);
    
    document.getElementById('upload-section').classList.add('hidden');
    document.getElementById('status-area').classList.remove('hidden');
    document.getElementById('action-text').innerText = "Uploading File...";

    try {
        const res = await fetch('/upload', { method: 'POST', body: formData });
        const { task_id, duration } = await res.json();
        
        // Instant MM:SS update after upload
        const initialMin = Math.floor(duration / 60);
        const initialSec = Math.round(duration % 60);
        document.getElementById('eta').innerText = `${String(initialMin).padStart(2, '0')}:${String(initialSec).padStart(2, '0')}`;

        document.getElementById('action-text').innerText = "Initializing AI...";
        pollStatus(task_id, duration);
    } catch (error) {
        console.error("Upload fail ho gaya:", error);
        document.getElementById('action-text').innerText = "Upload failed!";
    }
}

async function pollStatus(task_id, duration) {
    let index = 0;
    
    const textInterval = setInterval(() => {
        document.getElementById('action-text').innerText = statuses[index % statuses.length];
        index++;
    }, 2500);

    const poll = setInterval(async () => {
        try {
            const res = await fetch(`/status/${task_id}`);
            const data = await res.json();
            
            document.getElementById('fill-shade-bar').style.width = data.progress + "%";
            document.getElementById('fill-shade').style.width = data.progress + "%";
            document.getElementById('perc-text').innerText = data.progress + "%";
            
            const remainingSeconds = Math.max(0, Math.round((duration - (duration * (data.progress / 100)))));
            const minutes = Math.floor(remainingSeconds / 60);
            const seconds = remainingSeconds % 60;
            
            document.getElementById('eta').innerText = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

            if (data.status === 'completed') {
                clearInterval(poll);
                clearInterval(textInterval);
                
                document.getElementById('action-text').innerText = "Subtitles Ready!";
                document.getElementById('eta').innerText = "00:00"; 
                
                window.finalSrt = data.srt;
                document.getElementById('status-area').classList.add('hidden');
                document.getElementById('download-section').classList.remove('hidden');
            }
        } catch (error) {
            console.error("Status check fail hua:", error);
        }
    }, 1000);
}

function downloadFile() {
    if (!window.finalSrt) return;
    const blob = new Blob([window.finalSrt], { type: 'text/srt' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = "subtitles.srt";
    a.click();
}