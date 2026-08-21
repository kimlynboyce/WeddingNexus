function updateCountdown() {
    const target = new Date("May 30, 2027 13:00:00").getTime();
    setInterval(() => {
        const now = new Date().getTime();
        const diff = target - now;
        if (diff < 0) return;
        document.getElementById('days').innerText = Math.floor(diff / (1000 * 60 * 60 * 24));
        document.getElementById('hours').innerText = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        document.getElementById('minutes').innerText = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        document.getElementById('seconds').innerText = Math.floor((diff % (1000 * 60)) / 1000);
    }, 1000);
}

let musicPlaying = false;
function toggleMusic() {
    const audio = document.getElementById('bgMusic');
    if(!musicPlaying) { audio.play(); document.getElementById('musicBtn').innerText = '⏸'; }
    else { audio.pause(); document.getElementById('musicBtn').innerText = '🎵'; }
    musicPlaying = !musicPlaying;
}

async function raiseToast() {
    const res = await fetch('/api/toast', {method:'POST'});
    const data = await res.json();
    document.getElementById('toastCount').innerText = data.toasts + ' Toasts Raised';
}

async function submitRSVP(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    await fetch('/api/rsvp', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    document.getElementById('confirmation').style.display = 'block';
    event.target.reset();
}

async function loadMemories() {
    const res = await fetch('/api/memories');
    const data = await res.json();
    const grid = document.getElementById('memoryGrid');
    if(grid) {
        grid.innerHTML = data.map(m => \<div class='gallery-item'><img src='/static/uploads/\'></div>\).join('');
    }
}

async function loadToasts() {
    const res = await fetch('/api/toasts');
    const data = await res.json();
    document.getElementById('toastCount').innerText = data.toasts + ' Toasts Raised';
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
            const file = e.target.files[0];
            const formData = new FormData();
            formData.append('file', file);
            await fetch('/api/upload', { method: 'POST', body: formData });
            loadMemories();
        });
    }
};
