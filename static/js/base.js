// // ---------- TTS: makes the system speak ----------
// function speak(text, onDone) {
//     window.speechSynthesis.cancel();
//     const utterance = new SpeechSynthesisUtterance(text);
//     utterance.lang = 'en-US';
//     utterance.rate = 0.9;
//     if (onDone) utterance.onend = onDone;
//     window.speechSynthesis.speak(utterance);
// }

// ---------- Contrast theme ----------
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

// // ---------- Speech elements ----------
// const startBtn = document.getElementById('start-btn');
// const statusSpan = document.getElementById('status');
// const transcriptSpan = document.getElementById('transcript');
// const serverResponseSpan = document.getElementById('server-response');

// const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

// if (!SpeechRecognition) {
//     statusSpan.innerText = "Web Speech API not supported in this browser.";
//     startBtn.disabled = true;
// } else {
//     const recognition = new SpeechRecognition();
//     recognition.continuous = true;
//     recognition.interimResults = false;
//     recognition.lang = 'en-US';

//     let step = 'ask_signin';
//     let silentTries = 0;
//     const MAX_SILENT_TRIES = 3;
//     let cnicTries = 0;                     // NEW: counts failed CNIC verifications
//     const MAX_CNIC_TRIES = 3;              // NEW: limit before giving up
//     let pendingCnic = '';
//     let started = false;

//     // Helper function to safely process transcripts
//     function cleanTranscript(rawText) {
//         // Remove punctuation and extra whitespace
//         return rawText.toLowerCase().replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, "").trim();
//     }

//     function stopAndReset(message) {
//         speak(message);
//         started = false;
//         silentTries = 0;
//         cnicTries = 0;
//         step = 'ask_signin';
//         statusSpan.innerText = "Waiting. Press any key to start again.";
//     }

//     function listen() {
//         statusSpan.innerText = "Listening...";
//         recognition.start();
//     }

//     function askSignIn() {
//         step = 'ask_signin';
//         speak("Welcome to the e-voting system. Do you want to sign in with your I D? Say yes, okay, or no.", listen);
//     }

//     function askCnic() {
//         step = 'ask_cnic';
//         speak("Please say your C N I C number now.", listen);
//     }

//     function askConfirmCnic() {
//         step = 'confirm_cnic';
//         speak("You said " + pendingCnic.split('').join(' ') +
//               ". Is that your C N I C number? Say yes or no.", listen);
//     }

//     recognition.onresult = (event) => {
//     // Grab the latest result index
//     const resultIndex = event.resultIndex;
//     const heardRaw = event.results[resultIndex][0].transcript;
//     const heard = cleanTranscript(heardRaw);
    
//     console.log("RAW HEARD:", heardRaw, "| CLEANED:", heard, "| step:", step);
    
//     transcriptSpan.innerText = heard;
//     statusSpan.innerText = "Heard you.";
//     silentTries = 0;

//     // Stop recognition manually before playing TTS so TTS doesn't feed back into mic
//     recognition.stop();

//         // Word boundary / intent extraction helpers
//         const words = heard.split(/\s+/);
//         const saidYes = words.includes('yes') || words.includes('okay') || words.includes('ok') || heard.includes('i want');
//         const saidNo = words.includes('no') || words.includes('stop') || words.includes('cancel') || heard.includes("don't");

//         if (step === 'ask_signin') {
//             if (saidYes) {
//                 cnicTries = 0;
//                 askCnic();
//             } else if (saidNo) {
//                 stopAndReset("Okay, signing in canceled. Press any key whenever you are ready.");
//             } else {
//                 silentTries++;
//                 if (silentTries >= MAX_SILENT_TRIES) {
//                     stopAndReset("I did not understand your response. Press any key to start again.");
//                 } else {
//                     askSignIn();
//                 }
//             }
//         }
//         else if (step === 'ask_cnic') {
//             if (saidNo) {
//                 stopAndReset("CNIC entry canceled. Press any key to start again.");
//                 return;
//             }

//             const digits = heard.replace(/\D/g, '').slice(0, 13);
//             if (digits.length === 13) {
//                 pendingCnic = digits;
//                 askConfirmCnic();
//             } else {
//                 cnicTries++;
//                 if (cnicTries >= MAX_CNIC_TRIES) {
//                     stopAndReset("Maximum attempts reached for entering CNIC. Press any key to start again.");
//                 } else {
//                     speak("I heard only " + digits.length + " digits. Attempt " + cnicTries + " of " + MAX_CNIC_TRIES + ". Let's try again.", askCnic);
//                 }
//             }
//         }
//         else if (step === 'confirm_cnic') {
//             if (saidYes) {
//                 statusSpan.innerText = "Checking with server...";
//                 sendToDjango(pendingCnic);
//             } else if (saidNo) {
//                 cnicTries++;
//                 if (cnicTries >= MAX_CNIC_TRIES) {
//                     stopAndReset("Maximum attempts reached. Please contact polling staff for help.");
//                 } else {
//                     speak("Okay, let's try entering your C N I C again.", askCnic);
//                 }
//             } else {
//                 speak("Please answer with yes or no.", askConfirmCnic);
//             }
//         }
//     };

//     recognition.onerror = (event) => {
//         console.log("ERROR TYPE:", event.error, "| step:", step);
//         statusSpan.innerText = "Error occurred: " + event.error;

//         if (event.error === 'not-allowed') {
//             speak("Microphone access is blocked. Please allow the microphone and press any key.");
//             started = false;
//             return;
//         }

//         silentTries = silentTries + 1;

//         if (silentTries >= MAX_SILENT_TRIES) {
//             speak("I did not hear a response. When you are ready, press any key to start again.");
//             started = false;
//             silentTries = 0;
//             step = 'ask_signin';
//             statusSpan.innerText = "Waiting. Press any key to start again.";
//         } else {
//             if (step === 'ask_signin') askSignIn();
//             else if (step === 'ask_cnic') askCnic();
//             else if (step === 'confirm_cnic') askConfirmCnic();
//         }
//     };

//     recognition.onend = () => {
//         if (statusSpan.innerText === "Listening...") {
//             statusSpan.innerText = "Stopped listening.";
//         }
//     };

//     // ---------- Starting the conversation ----------
//     function startDialog() {
//         if (started) return;
//         started = true;
//         askSignIn();
//     }
//     window.addEventListener('keydown', startDialog);
//     window.addEventListener('click', startDialog);

//     startBtn.addEventListener('click', () => {
//         started = true;
//         askSignIn();
//     });

//     // ---------- Backend call ----------
//     function sendToDjango(text) {
//         fetch('/api/process-speech/', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text: text })
//         })
//         .then(response => response.json())
//         .then(data => {
//             serverResponseSpan.innerText = data.message;
//             if (data.verified) {
//                 cnicTries = 0;                                     // NEW: reset on success
//                 statusSpan.innerText = "Verified!";
//                 speak("You are a verified disabled user. Welcome!", function () {
//                     const cnicField = document.getElementById('cnic');
//                     if (cnicField) {
//                         cnicField.value = pendingCnic;
//                         cnicField.closest('form').submit();
//                     }
//                 });
//             } else {
//                 statusSpan.innerText = "Not found.";
//                 cnicTries = cnicTries + 1;                         // NEW: count the failure

//                 if (cnicTries >= MAX_CNIC_TRIES) {                 // NEW: give up at three
//                     speak("No voter found after three attempts. Please contact the polling staff for help. Press any key to start again.");
//                     started = false;
//                     cnicTries = 0;
//                     step = 'ask_signin';
//                     statusSpan.innerText = "Waiting. Press any key to start again.";
//                 } else {
//                     speak("No voter found with that C N I C. Attempt " + cnicTries + " of three. Let's try again.", askCnic);
//                 }
//             }
//         })
//         .catch(error => {
//             statusSpan.innerText = "Server Error";
//             console.error('Error:', error);
//             speak("Sorry, there was a server problem. Let's try again.", askCnic);
//         });
//     }
// }