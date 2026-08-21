function updateCountdown() {
    const target = new Date("May 30, 2027 13:00:00").getTime();
    setInterval(() => {
        const now = new Date().getTime();
        const diff = target - now;
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

function animateWave() {
    const bars = document.querySelectorAll('.bar');
    bars.forEach(bar => {
        const h = 10 + Math.random() * 40;
        bar.style.height = h + 'px';
    });
}

window.onload = () => {
    updateCountdown();
    setInterval(animateWave, 150);
    fetch('/api/toasts').then(r => r.json()).then(d => {
        document.getElementById('toastCount').innerText = d.toasts + ' Toasts Raised';
    });
};
