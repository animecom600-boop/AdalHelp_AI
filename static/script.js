function openAI() {
    document.getElementById("aiWindow").style.display = "flex";
}

function closeAI() {
    document.getElementById("aiWindow").style.display = "none";
}

async function sendAI() {
    const input = document.getElementById("aiInput");
    const messages = document.getElementById("aiMessages");
    const message = input.value.trim();

    if (!message) return;

    addMessage(message, "user");
    input.value = "";

    const loading = document.createElement("div");
    loading.className = "message ai";
    loading.textContent = "AdalHelp AI жауап дайындауда...";
    messages.appendChild(loading);
    messages.scrollTop = messages.scrollHeight;

    try {
        const response = await fetch("/api/ai", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message})
        });

        const data = await response.json();
        loading.remove();

        if (!response.ok) {
            addMessage(data.error || "Қате пайда болды.", "ai");
            return;
        }

        addMessage(data.answer, "ai");

    } catch (error) {
        loading.remove();
        addMessage("Сервермен байланыс жоқ. Қайта көріңіз.", "ai");
    }
}

function addMessage(text, type) {
    const messages = document.getElementById("aiMessages");
    const message = document.createElement("div");

    message.className = "message " + type;
    message.textContent = text;

    messages.appendChild(message);
    messages.scrollTop = messages.scrollHeight;
}

function openChat() {
    alert("Анонимді чат келесі кезеңде қосылады!");
}
