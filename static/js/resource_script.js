document.addEventListener("DOMContentLoaded", function () {
    const qrButton = document.getElementById("qrButton");

    qrButton.addEventListener("click", function () {
        const url = qrButton.getAttribute("data-url");
        window.location.href = url;
    });
});
