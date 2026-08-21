function updateCountdown() {
    const target = new Date('May 30, 2027 13:00:00').getTime();
    setInterval(() => {
        const now = new Date().getTime();
        const diff = target - now;
        if (diff < 0) return;
        
        const d = Math.floor(diff / (1000 * 60 * 60 * 24));
        const h = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const s = Math.floor((diff % (1000 * 60)) / 1000);
        
        if(document.getElementById('days')) document.getElementById('days').innerText = d;
        if(document.getElementById('hours')) document.getElementById('hours').innerText = h;
        if(document.getElementById('minutes')) document.getElementById('minutes').innerText = m;
        if(document.getElementById('seconds')) document.getElementById('seconds').innerText = s;
    }, 1000);
}

let musicPlaying = false;
function toggleMusic() {
    const audio = document.getElementById('bgMusic');
    const btn = document.getElementById('musicBtn');
    if(!audio) return;
    if(!musicPlaying) { 
        audio.play().then(() => {
            btn.innerText = '⏸';
            musicPlaying = true;
        }).catch(e => console.log('Autoplay blocked'));
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
        if(document.getElementById('toastCount')) {
            document.getElementById('toastCount').innerText = data.toasts + ' Toasts Raised';
        }
    } catch(e) { console.error('Toast failed', e); }
}

async function submitRSVP(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    try {
        await fetch('/api/rsvp', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const conf = document.getElementById('confirmation');
        if(conf) conf.style.display = 'block';
        event.target.reset();
    } catch(e) { console.error('RSVP failed', e); }
}

async function loadMemories() {
    try {
        const res = await fetch('/api/memories');
        const data = await res.json();
        const grid = document.getElementById('memoryGrid');
        if(grid) {
            grid.innerHTML = data.map(m => <div class='gallery-item'><img src='/static/uploads/\'></div>).join('');
        }
    } catch(e) { console.error('Load memories failed', e); }
}

async function loadToasts() {
    try {
        const res = await fetch('/api/toasts');
        const data = await res.json();
        if(document.getElementById('toastCount')) {
            document.getElementById('toastCount').innerText = data.toasts + ' Toasts Raised';
        }
    } catch(e) {}
}

function animateWave() {
    const bars = document.querySelectorAll('.bar');
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
        photoInput.addEventListener('change', async (e) => {
            if(!e.target.files[0]) return;
            const formData = new FormData();
            formData.append('file', e.target.files[0]);
            try {
                await fetch('/api/upload', { method: 'POST', body: formData });
                loadMemories();
            } catch(err) { console.error('Upload failed', err); }
        });
    }
};
