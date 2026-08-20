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
