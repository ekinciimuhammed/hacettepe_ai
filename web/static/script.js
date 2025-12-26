document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesContainer = document.getElementById('messages-container');

    // Auto-focus input
    input.focus();

    // Event Listeners
    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Modal Elements
    const modal = document.getElementById('source-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalText = document.getElementById('modal-text');
    const modalOpenPdf = document.getElementById('modal-open-pdf');
    const modalCloseBtn = document.getElementById('modal-close-btn');

    // Close Modal Events
    modalCloseBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    function openModal(title, text, pdfLink) {
        modalTitle.textContent = title;
        modalText.textContent = text;
        modalOpenPdf.href = pdfLink;
        modal.classList.add('active');
    }

    function closeModal() {
        modal.classList.remove('active');
    }

    async function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        // 1. Add User Message
        appendMessage('user', text);
        input.value = '';
        input.disabled = true;
        sendBtn.disabled = true;

        // 2. Determine Bot "Thinking" State
        // Add a temporary loading bubble
        const loadingId = appendLoadingBubble();

        try {
            // 3. API Call
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: text })
            });

            if (!response.ok) throw new Error("Network response was not ok");

            const data = await response.json();

            // 4. Remove Loading Bubble and Add Bot Message
            removeMessage(loadingId);
            appendMessage('bot', data.answer, data.sources, data.chunks);

        } catch (error) {
            console.error('Error:', error);
            removeMessage(loadingId);
            appendMessage('bot', '⚠️ Bir hata oluştu. Lütfen bağlantınızı kontrol edip tekrar deneyin.');
        } finally {
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        }
    }

    function appendMessage(sender, text, sources = [], chunks = []) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender === 'user' ? 'user-message' : 'bot-message'}`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = sender === 'user' ? '👤' : '🤖';

        const bubble = document.createElement('div');
        bubble.className = 'bubble';

        // Parse Markdown for Bot, Plain text for User
        if (sender === 'bot') {
            bubble.innerHTML = marked.parse(text);

            // Append Sources if available
            if (sources && sources.length > 0) {
                const sourcesDiv = document.createElement('div');
                sourcesDiv.className = 'sources-container';
                sourcesDiv.innerHTML = '<p class="sources-title">📚 Kaynaklar:</p>';

                sources.forEach(source => {
                    const chip = document.createElement('a');
                    chip.className = 'source-chip';
                    chip.href = '#'; // Prevent default navigation
                    chip.textContent = source;

                    // Click Event for Modal
                    chip.addEventListener('click', (e) => {
                        e.preventDefault();

                        // Find the relevant chunk text for this source
                        const chunk = chunks.find(c => c.source === source);
                        const chunkText = chunk ? chunk.text : "Bu kaynak için özel metin bulunamadı.";

                        openModal(source, chunkText, `/documents/${source}`);
                    });

                    sourcesDiv.appendChild(chip);
                });

                bubble.appendChild(sourcesDiv);
            }
        } else {
            bubble.textContent = text;
        }

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(bubble);

        messagesContainer.appendChild(msgDiv);
        scrollToBottom();
        return msgDiv;
    }

    function appendLoadingBubble() {
        const id = 'loading-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.id = id;
        msgDiv.className = 'message bot-message';

        msgDiv.innerHTML = `
            <div class="avatar">🤖</div>
            <div class="bubble" style="color: #666; font-style: italic;">
                Düşünüyor...
            </div>
        `;

        messagesContainer.appendChild(msgDiv);
        scrollToBottom();
        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
});
