document.addEventListener("DOMContentLoaded", () => {

    const timeElement = document.getElementById("currentTime");

    function updateClock() {

        if (!timeElement) {
            return;
        }

        const now = new Date();

        const hours = String(now.getHours()).padStart(2, "0");
        const minutes = String(now.getMinutes()).padStart(2, "0");
        const seconds = String(now.getSeconds()).padStart(2, "0");

        timeElement.textContent = `${hours}:${minutes}:${seconds}`;
    }

    updateClock();
    setInterval(updateClock, 1000);


    document.querySelectorAll(".toggle").forEach(toggle => {

        toggle.addEventListener("click", () => {
            toggle.classList.toggle("active");
        });

    });


    document.querySelectorAll('a[href^="#"]').forEach(link => {

        link.addEventListener("click", event => {

            const target = document.querySelector(
                link.getAttribute("href")
            );

            if (!target) {
                return;
            }

            event.preventDefault();

            target.scrollIntoView({
                behavior: "smooth"
            });

        });

    });

});
document.addEventListener("DOMContentLoaded", () => {

    const stats = document.querySelectorAll(".stat-card");

    stats.forEach((card, index) => {

        card.style.opacity = "0";
        card.style.transform = "translateY(12px)";

        setTimeout(() => {

            card.style.transition =
                "opacity .5s ease, transform .5s ease";

            card.style.opacity = "1";
            card.style.transform = "translateY(0)";

        }, index * 80);

    });

});