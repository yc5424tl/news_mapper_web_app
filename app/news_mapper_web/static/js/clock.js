$(document).ready(function() {

    setInterval(function () {
        let dateTime;
        let dateA;
        let dateB;
        let d = new Date();
        dateA = d.toLocaleDateString();
        dateB = d.toLocaleTimeString();
        dateTime = `${dateA} @ ${dateB}`;
        document.getElementById("clock-span").textContent = dateTime;
    }, 1000);



});