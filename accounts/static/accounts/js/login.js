function insertCnicIntoInputField() {
    const cnicField = document.getElementById('cnic');
    document.addEventListener("DOMContentLoaded", cnicField.focus())
    if (cnicField) {
        const storedCnic = localStorage.getItem('CNIC');

        if (storedCnic) {
            cnicField.value = storedCnic; // Set the CNIC input value
            cnicField.dispatchEvent(new Event('input', { bubbles: true }));
            cnicField.dispatchEvent(new Event('change', { bubbles: true }));
            localStorage.removeItem('CNIC'); // Clear the CNIC from localStorage after setting it

            // --- AUTO-LOGIN ADDITION HERE ---
            const loginForm = cnicField.closest('form');
            if (loginForm) {
                // Short 500ms delay lets users briefly see their input before the page changes
                setTimeout(() => {
                    loginForm.submit();
                }, 500);
            }
            // ---------------------------------
        }
    } else {
        console.error("Could not find element with ID 'cnic'");
    }
}
document.addEventListener('DOMContentLoaded', insertCnicIntoInputField);
window.addEventListener('cnicUpdated', insertCnicIntoInputField);

function speak(text){
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
}

window.addEventListener('laod', function () {
    speak("Welcome to the voting system. Please say or type your 13 digit CNIC number.");
})
