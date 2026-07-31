const savedTheme = localStorage.getItem('contrast-theme');
if (savedTheme === 'high-contrast') {
    document.documentElement.setAttribute('data-theme', 'high-contrast');
}

const toggleBtn = document.getElementById('contrast-toggle');

function updateButtonText(theme) {
    if (theme === 'high-contrast') {
        toggleBtn.innerText = "Switch to Normal Contrast";
    } else {
        toggleBtn.innerText = "Switch to High Contrast";
    }
}

updateButtonText(localStorage.getItem('contrast-theme'));

toggleBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');

    if (currentTheme === 'high-contrast') {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('contrast-theme', 'normal');
        updateButtonText('normal');
    } else {
        document.documentElement.setAttribute('data-theme', 'high-contrast');
        localStorage.setItem('contrast-theme', 'high-contrast');
        updateButtonText('high-contrast');
    }
});

// Web Speech API Interface Setup Configuration script engine
const startBtn = document.getElementById('start-btn');
const statusSpan = document.getElementById('status');
const transcriptSpan = document.getElementById('transcript');
const serverResponseSpan = document.getElementById('server-response');

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
    statusSpan.innerText = "Web Speech API not supported in this browser.";
    startBtn.disabled = true;
} else {
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';

    startBtn.addEventListener('click', (event) => {
        recognition.start();
        statusSpan.innerText = "Listening...";
        transcriptSpan.innerText = "";
        serverResponseSpan.innerText = "";
    });

    recognition.onresult = (event) => {
        const speechToText = event.results[0][0].transcript.replace(/\D/g, '').slice(0, 13);
        transcriptSpan.innerText = speechToText;
        statusSpan.innerText = "Processing on backend...";
        localStorage.setItem('CNIC', speechToText);
        window.dispatchEvent(new Event('cnicUpdated'));
        sendToDjango(speechToText);
    };

    recognition.onerror = (event) => {
        statusSpan.innerText = "Error occurred: " + event.error;
    };

    recognition.onend = () => {
        if (statusSpan.innerText === "Listening...") {
            statusSpan.innerText = "Stopped listening.";
        }
    };
}

function sendToDjango(text) {
    fetch('/api/process-speech/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text })
    })
        .then(response => response.json())
        .then(data => {
            statusSpan.innerText = "Done!";
            serverResponseSpan.innerText = data.message;
        })
        .catch(error => {
            statusSpan.innerText = "Server Error";
            console.error('Error:', error);
        });
}