// Wedding Countdown Timer
const targetDate = new Date("May 30, 2027 13:00:00").getTime();

function updateCountdown() {
    const now = new Date().getTime();
    const distance = targetDate - now;

    if (distance < 0) {
        document.getElementById("countdown").innerHTML = "<h3>The Celebration is Here!</h3>";
        return;
    }

    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    document.getElementById("days").innerText = days;
    document.getElementById("hours").innerText = hours;
    document.getElementById("minutes").innerText = minutes;
    document.getElementById("seconds").innerText = seconds;
}

// Initial call
updateCountdown();
setInterval(updateCountdown, 1000);

// RSVP Submission handling
async function submitRSVP(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/api/rsvp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        alert(result.message);
        if (result.success) event.target.reset();
    } catch (error) {
        alert("Error submitting RSVP. Please try again.");
    }
}
document.getElementById('photoInput').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('caption', 'Shared by a guest');
    await fetch('/api/upload', { method: 'POST', body: formData });
    loadMemories();
});
async function loadMemories() {
    const res = await fetch('/api/memories');
    const data = await res.json();
    const grid = document.getElementById('memoryGrid');
    grid.innerHTML = data.map(m => \<div class='gallery-item'><img src='\' title='\'></div>\).join('');
}
loadMemories();
function animateWave() {
    const bars = document.querySelectorAll('.bar');
    bars.forEach(bar => {
        const h = 10 + Math.random() * 40;
        bar.style.height = h + 'px';
        bar.style.opacity = h / 50;
    });
}
setInterval(animateWave, 150);
async function submitComment() {
    const name = document.getElementById('gbName').value;
    const message = document.getElementById('gbMsg').value;
    if(!name || !message) return alert('Please fill in both fields');
    await fetch('/api/comment', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, message})
    });
    document.getElementById('gbMsg').value = '';
    loadComments();
}
async function loadComments() {
    const res = await fetch('/api/comments');
    const data = await res.json();
    const list = document.getElementById('commentList');
    list.innerHTML = data.map(c => \<div style='border-bottom:1px solid #eee; padding:10px;'><b>\:</b> \<br><small style='color:gray'>\</small></div>\).join('');
}
loadComments();

function scrollToRSVP() {
    document.getElementById('rsvp-section').scrollIntoView({behavior: 'smooth'});
}

async function loadSongs() {
    try {
        const res = await fetch('/api/songs');
        const data = await res.json();
        const feed = document.getElementById('songFeed');
        if(feed) {
            feed.innerHTML = data.map(s => \<div style='background:var(--camel); color:white; padding:5px 15px; border-radius:20px; font-size:0.8rem;'><b>\</b> <small>(\)</small></div>\).join('');
        }
    } catch(e) {}
}
// Add to load sequence
const oldLoad = window.onload;
window.onload = () => { if(oldLoad) oldLoad(); loadSongs(); };
