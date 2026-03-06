const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

// Auto-resize textarea
userInput.addEventListener('input', () => {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
});

// Send on Enter (Shift+Enter for new line)
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message to chat
    appendMessage('user', message);
    userInput.value = '';
    userInput.style.height = 'auto';
    sendBtn.disabled = true;

    // Show typing indicator
    const typingEl = showTypingIndicator();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        removeTypingIndicator(typingEl);

        if (data.error) {
            appendMessage('assistant', `Error: ${data.error}`);
        } else {
            appendMessage('assistant', data.reply);
        }
    } catch (err) {
        removeTypingIndicator(typingEl);
        appendMessage('assistant', `Error: Could not reach the server. ${err.message}`);
    }

    sendBtn.disabled = false;
    userInput.focus();
});

function appendMessage(role, content) {
    const div = document.createElement('div');
    div.classList.add('message', role);
    div.innerHTML = `<div class="message-content">${escapeHtml(content)}</div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const div = document.createElement('div');
    div.classList.add('message', 'assistant');
    div.innerHTML = `<div class="typing-indicator"><span></span><span></span><span></span></div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
}

function removeTypingIndicator(el) {
    if (el && el.parentNode) el.parentNode.removeChild(el);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
