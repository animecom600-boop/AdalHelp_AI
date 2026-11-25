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

// Қауымдастық чаты

function openChat() {
    document.getElementById("chatWindow").style.display = "flex";
    loadChat();
}

function closeChat() {
    document.getElementById("chatWindow").style.display = "none";
}

async function loadChat() {
    const messages = document.getElementById("communityMessages");
    messages.textContent = "Хабарламалар жүктелуде...";

    try {
        const response = await fetch("/api/chat");
        const data = await response.json();

        if (!response.ok) {
            messages.textContent = data.error || "Чатты жүктеу мүмкін болмады.";
            return;
        }

        messages.replaceChildren();

        const list = (data.messages || []).reverse();

        if (list.length === 0) {
            messages.textContent = "Әзірге хабарламалар жоқ.";
            return;
        }

        list.forEach(item => {
            const message = document.createElement("div");
            message.className = "message ai";

            const nickname = document.createElement("strong");
            nickname.textContent = item.nickname + ": ";

            const content = document.createElement("span");
            content.textContent = item.content;

            message.append(nickname, content);
            messages.appendChild(message);
        });

        messages.scrollTop = messages.scrollHeight;

    } catch (error) {
        messages.textContent = "Сервермен байланыс жоқ.";
    }
}

async function sendChat() {
    const nicknameInput = document.getElementById("chatNickname");
    const contentInput = document.getElementById("chatInput");

    const nickname = nicknameInput.value.trim();
    const content = contentInput.value.trim();

    if (!nickname || !content) {
        alert("Лақап ат пен хабарламаны толтыр.");
        return;
    }

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({nickname, content})
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.error || "Хабарламаны жіберу мүмкін болмады.");
            return;
        }

        contentInput.value = "";
        alert("Хабарлама модерацияға жіберілді.");

    } catch (error) {
        alert("Сервермен байланыс жоқ.");
    }
}
