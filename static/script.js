function updateCountdown() {
    const target = new Date('2027-05-30T13:00:00').getTime();
    setInterval(() => {
        const now = new Date().getTime();
        const diff = target - now;
        if (isNaN(diff) || diff < 0) return;
        document.getElementById('days').innerText = Math.floor(diff / (1000 * 60 * 60 * 24)).toString().padStart(2, '0');
        document.getElementById('hours').innerText = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)).toString().padStart(2, '0');
        document.getElementById('minutes').innerText = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)).toString().padStart(2, '0');
        document.getElementById('seconds').innerText = Math.floor((diff % (1000 * 60)) / 1000).toString().padStart(2, '0');
    }, 1000);
}

let musicPlaying = false;
function toggleMusic() {
    const audio = document.getElementById('bgMusic');
    const btn = document.getElementById('musicBtn');
    if(!musicPlaying) { 
        audio.play().then(() => { btn.innerText = '⏸'; musicPlaying = true; })
        .catch(() => alert("Click the page first to enable audio."));
    } else { audio.pause(); btn.innerText = '🎵'; musicPlaying = false; }
}

async function raiseToast() {
    const res = await fetch('/api/toast', {method:'POST'});
    const data = await res.json();
    document.getElementById('toastCount').innerText = data.toasts + ' Toasts Raised';
}

async function submitRSVP(event) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.target).entries());
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
    if(grid) grid.innerHTML = data.map(m => <div class='gallery-item'><img src='/static/uploads/\'></div>).join('');
}

window.onload = () => {
    updateCountdown();
    loadMemories();
    fetch('/api/toasts').then(r => r.json()).then(d => {
        document.getElementById('toastCount').innerText = d.toasts + ' Toasts Raised';
    });
    const input = document.getElementById('photoInput');
    if(input) input.onchange = async (e) => {
        const fd = new FormData();
        fd.append('file', e.target.files[0]);
        await fetch('/api/upload', {method:'POST', body:fd});
        loadMemories();
    };
};
