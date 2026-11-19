async function checkNumber() {

    const phone = document.getElementById("phone");
    const result = document.getElementById("result");
    const button = document.getElementById("checkBtn");

    const number = phone.value.trim();

    result.className = "result";

    if (!/^\+[1-9]\d{7,14}$/.test(number)) {
        result.querySelector("p").textContent =
            "INVALID PHONE NUMBER";

        return;
    }

    button.disabled = true;
    button.innerHTML = "CONNECTING TO API...";

    result.querySelector("p").textContent =
        "VERIFYING NUMBER...";

    result.querySelector(".result-icon").textContent = "⛧";

    try {

        const response = await fetch("/check", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                phone: number
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "API ERROR");
        }

        if (data.banned === true) {

            result.classList.add("banned");

            result.querySelector("p").textContent =
                "NUMÉRO BANNI";

            result.querySelector(".result-icon").textContent =
                "✖";

        } else if (data.banned === false) {

            result.classList.add("safe");

            result.querySelector("p").textContent =
                "NUMÉRO NON BANNI";

            result.querySelector(".result-icon").textContent =
                "✓";

        } else {

            throw new Error("UNKNOWN STATUS");
        }

    } catch (error) {

        result.querySelector("p").textContent =
            "VERIFICATION ERROR";

        result.querySelector(".result-icon").textContent =
            "⚠";

    } finally {

        button.disabled = false;
        button.innerHTML = "<span>⛧</span> VERIFY NUMBER";

    }
}
