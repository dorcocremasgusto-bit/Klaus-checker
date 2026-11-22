    
async function checkNumber() {

    const phone = document.getElementById("phone");
    const result = document.getElementById("result");
    const button = document.getElementById("checkBtn");

    const number = phone.value.trim();

    result.className = "result";

    if (!/^\+[1-9]\d{7,14}$/.test(number)) {
        result.innerHTML = `
            <div class="result-icon">⚠</div>
            <p>INVALID PHONE NUMBER</p>
        `;
        return;
    }

    button.disabled = true;
    button.textContent = "VERIFYING...";

    result.innerHTML = `
        <div class="result-icon">⏳</div>
        <p>CONNECTING TO BANCHECK...</p>
    `;

    try {

        const response = await fetch("/check", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ number: number })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "API ERROR");
        }

        const isBanned = data.banned === true;

        // MENM GLASS CARD POU TOUDE REZILTA YO
        result.className = isBanned
            ? "banned-card"
            : "banned-card safe-card";

        result.innerHTML = `
            <span class="banned-number"></span>

            <div class="banned-decoration"></div>

            <div class="banned-title"></div>

            <div class="banned-message"></div>

            <div class="banned-line"></div>

            <div class="banned-signature">
                🔴 SIGNÉ : KLAUS CHECKER
            </div>
        `;

        // AFFICHE LE NUMERO
        result.querySelector(".banned-number").textContent = number;

        // AFFICHE LE STATUT
        result.querySelector(".banned-title").textContent =
            isBanned ? "BANNI" : "NON BANNI";

        // AFFICHE LE MESSAGE
        result.querySelector(".banned-message").textContent =
            isBanned
            ? "Banni par Klaus"
            : "Numéro fiable online";

        // DECORATION
        result.querySelector(".banned-decoration").textContent =
            isBanned ? "✥ 🔴 ✥" : "✥ ✓ ✥";

    } catch (error) {

        result.className = "result";

        result.innerHTML = `
            <div class="result-icon">⚠</div>
            <p></p>
        `;

        result.querySelector("p").textContent =
            error.message || "VERIFICATION ERROR";

    } finally {

        button.disabled = false;
        button.innerHTML = "<span>⛧</span> VERIFY NUMBER";
    }
}
