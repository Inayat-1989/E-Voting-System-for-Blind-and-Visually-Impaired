const na_link = document.getElementById('na_link');
const pa_link = document.getElementById('pa_link');
const voter = document.getElementById('user-component');
const has_voted_na = voter.dataset.has_voted_na === "True";
const has_voted_pa = voter.dataset.has_voted_pa === "True";
if (has_voted_na && na_link) {
    na_link.innerHTML = "<p>You have already Voted.</p>";
}
if (has_voted_pa && pa_link) {
    pa_link.innerHTML = "<p>You have Already Voted.</p>";
}

if (has_voted_na && has_voted_pa) {
    window.location.href = voter.dataset.redirectUrl;
}
