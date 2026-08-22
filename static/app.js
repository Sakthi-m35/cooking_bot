const chatMessages = document.getElementById("chatMessages");
const input = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const clearChat = document.getElementById("clearChat");

const WELCOME_HTML = `
  <div class="welcome-card">
    <div class="welcome-icon">🥘</div>
    <div>
      <span class="eyebrow">WELCOME TO DISHLY</span>
      <h3>What are we cooking today?</h3>
      <p>Ask about recipes, ingredients, substitutions, baking, Indian cuisine, meal planning, kitchen techniques or cooking problems.</p>
    </div>
  </div>
  <div class="suggestions">
    <button data-question="How do I make restaurant-style paneer butter masala?">Paneer Butter Masala</button>
    <button data-question="What is the best substitute for eggs in a cake?">Egg substitutes</button>
    <button data-question="Why does my rice become sticky and how can I fix it?">Fix sticky rice</button>
  </div>
`;

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatAnswer(text) {
  let html = escapeHtml(text);
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\n\n/g, "</p><p>");
  html = html.replace(/\n/g, "<br>");
  return `<p>${html}</p>`;
}

function addMessage(text, role) {
  const row = document.createElement("div");
  row.className = `message-row ${role}`;
  row.innerHTML = `
    <div class="avatar">${role === "user" ? "👤" : "🍳"}</div>
    <div class="bubble">${role === "user" ? escapeHtml(text).replace(/\n/g, "<br>") : formatAnswer(text)}</div>
  `;
  chatMessages.appendChild(row);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addTyping() {
  const row = document.createElement("div");
  row.className = "message-row assistant";
  row.id = "typingRow";
  row.innerHTML = `
    <div class="avatar">🍳</div>
    <div class="bubble typing"><i></i><i></i><i></i></div>
  `;
  chatMessages.appendChild(row);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function setLoading(loading) {
  sendButton.disabled = loading;
  input.disabled = loading;
  sendButton.querySelector("span").textContent = loading ? "..." : "Cook it";
}

async function sendMessage(message = null) {
  const text = (message ?? input.value).trim();
  if (!text || sendButton.disabled) return;

  addMessage(text, "user");
  input.value = "";
  input.style.height = "auto";
  setLoading(true);
  addTyping();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });

    const data = await response.json();
    document.getElementById("typingRow")?.remove();

    if (!response.ok) {
      addMessage(data.error || "Something went wrong. Please try again.", "assistant");
    } else {
      addMessage(data.answer, "assistant");
    }
  } catch (error) {
    document.getElementById("typingRow")?.remove();
    addMessage("I couldn't connect to the server. Please make sure Flask is running on port 8000.", "assistant");
  } finally {
    setLoading(false);
    input.focus();
  }
}

function bindQuestionButtons() {
  document.querySelectorAll("[data-question]").forEach((button) => {
    button.addEventListener("click", () => sendMessage(button.dataset.question));
  });
}

sendButton.addEventListener("click", () => sendMessage());

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 130)}px`;
});

clearChat.addEventListener("click", () => {
  chatMessages.innerHTML = WELCOME_HTML;
  bindQuestionButtons();
  input.focus();
});

bindQuestionButtons();
input.focus();
