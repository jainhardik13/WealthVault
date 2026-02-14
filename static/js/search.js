document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("symbolInput");
    const resultBox = document.getElementById("searchResults");

//     if not on dashboard page exit safely
    if (!input || !resultBox) return;

    input.addEventListener("input", async () => {
        const query = input.value.trim();

        if (query.length < 2) {
            resultBox.innerHTML = "";
            return;
        }

        try {
            const response = await fetch(`/search?q=${query}`);
            const data = await response.json();

            resultBox.innerHTML = "";

            data.forEach(symbol => {
                const li = document.createElement("li");
                li.textContent = symbol;
                li.style.cursor = "pointer";

                li.onclick = () => {
                    input.value = symbol;
                    resultBox.innerHTML = "";
                };

                resultBox.appendChild(li);
            });
        } catch (err) {
            console.error("Search error:", err);
        }
    });
});