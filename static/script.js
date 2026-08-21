function updateCountdown() {
    const targetDate = '2027-05-30T13:00:00';
    const target = new Date(targetDate).getTime();
    
    const interval = setInterval(() => {
        const now = new Date().getTime();
        const diff = target - now;
        
        if (isNaN(diff) || diff < 0) {
            clearInterval(interval);
            return;
        }
        
        const d = Math.floor(diff / (1000 * 60 * 60 * 24));
        const h = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const s = Math.floor((diff % (1000 * 60)) / 1000);
        
        const ids = ['days', 'hours', 'minutes', 'seconds'];
        const values = [d, h, m, s];
        
        ids.forEach((id, idx) => {
            const el = document.getElementById(id);
            if(el) el.innerText = values[idx].toString().padStart(2, '0');
        });
    }, 1000);
}

let musicPlaying = false;
function toggleMusic() {
    const audio = document.getElementById('bgMusic');
    const btn = document.getElementById('musicBtn');
    if(!audio || !btn) return;
    
    if(!musicPlaying) { 
        audio.play().then(() => {
            btn.innerText = '⏸';
            musicPlaying = true;
        }).catch(err => {
            console.log("Audio play failed:", err);
            alert("Click the page first to enable music!");
        });
    } else { 
        audio.pause(); 
        btn.innerText = '🎵'; 
        musicPlaying = false;
    }
}

async function raiseToast() {
    try {
        const res = await fetch('/api/toast', {method:'POST'});
        const data = await res.json();
        const el = document.getElementById('toastCount');
        if(el) el.innerText = (data.toasts || 0) + ' Toasts Raised';
    } catch(e) { console.error('Toast error:', e); }
}

async function submitRSVP(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    try {
        const res = await fetch('/api/rsvp', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        if(res.ok) {
            const conf = document.getElementById('confirmation');
            if(conf) conf.style.display = 'block';
            event.target.reset();
        }
    } catch(e) { console.error('RSVP error:', e); }
}

async function loadMemories() {
    try {
        const res = await fetch('/api/memories');
        const data = await res.json();
        const grid = document.getElementById('memoryGrid');
        if(grid && Array.isArray(data)) {
            grid.innerHTML = data.map(m => 
                <div class='gallery-item'>
                    <img src='/static/uploads/\' onerror="this.src='https://via.placeholder.com/200?text=Error'">
                </div>
            ).join('');
        }
    } catch(e) { console.error('Memory load error:', e); }
}

async function loadToasts() {
    try {
        const res = await fetch('/api/toasts');
        const data = await res.json();
        const el = document.getElementById('toastCount');
        if(el) el.innerText = (data.toasts || 0) + ' Toasts Raised';
    } catch(e) {}
}

function animateWave() {
    const bars = document.querySelectorAll('.bar');
    if(!bars.length) return;
    bars.forEach(bar => {
        const h = 10 + Math.random() * 40;
        bar.style.height = h + 'px';
    });
}

window.onload = () => {
    updateCountdown();
    loadMemories();
    loadToasts();
    setInterval(animateWave, 150);
    
    const photoInput = document.getElementById('photoInput');
    if(photoInput) {
        photoInput.onchange = async (e) => {
            if(!e.target.files[0]) return;
            const formData = new FormData();
            formData.append('file', e.target.files[0]);
            try {
                const res = await fetch('/api/upload', { method: 'POST', body: formData });
                if(res.ok) loadMemories();
            } catch(err) { console.error('Upload error:', err); }
        };
    }
};
