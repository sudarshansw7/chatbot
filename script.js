document.addEventListener('DOMContentLoaded', function() {
    const chatBubble = document.getElementById('chatBubble');
    const chatBox = document.getElementById('chatBox');
    const minimizeBtn = document.getElementById('minimizeBtn');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');

    // Toggle chat box
    chatBubble.addEventListener('click', () => {
        chatBox.classList.add('active');
        chatBubble.style.display = 'none';
    });

    minimizeBtn.addEventListener('click', () => {
        chatBox.classList.remove('active');
        chatBubble.style.display = 'flex';
    });

    // Function to create a copy button
    function createCopyButton() {
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.innerHTML = '<i class="fas fa-copy"></i>';
        button.addEventListener('click', function(e) {
            const codeBlock = e.target.closest('.code-block').querySelector('code');
            navigator.clipboard.writeText(codeBlock.textContent);
            
            // Show copied notification
            button.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-copy"></i>';
            }, 2000);
        });
        return button;
    }

    // Function to format code blocks
    function formatCodeBlock(text) {
        const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
        return text.replace(codeBlockRegex, (match, language, code) => {
            const div = document.createElement('div');
            div.className = 'code-block';
            
            const codeElement = document.createElement('code');
            codeElement.className = language ? `language-${language}` : '';
            codeElement.textContent = code.trim();
            
            div.appendChild(codeElement);
            div.appendChild(createCopyButton());
            
            return div.outerHTML;
        });
    }

    // Function to format message with markdown-like syntax
    function formatMessage(text) {
        // Format bold text
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Format italic text
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        // Format links
        text = text.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
        // Format lists
        text = text.replace(/^\s*[-*]\s+(.*)$/gm, '<li>$1</li>');
        return text;
    }

    // Add message to chat
    function addMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', type);
        
        if (type === 'bot') {
            // Format the bot's message with code blocks and markdown
            let formattedMessage = formatMessage(message);
            messageDiv.innerHTML = formattedMessage;
            
            // Handle code blocks separately
            if (message.includes('```')) {
                messageDiv.innerHTML = formatCodeBlock(message);
            }
        } else {
            // User messages don't need formatting
            messageDiv.textContent = message;
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Initialize syntax highlighting if Prism is available
        if (window.Prism) {
            Prism.highlightAllUnder(messageDiv);
        }
    }

    // Send message function
    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            // Add user message to chat
            addMessage(message, 'user');
            
            // Send message to backend
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    addMessage('Sorry, something went wrong. Please try again.', 'bot');
                } else {
                    addMessage(data.response, 'bot');
                }
            })
            .catch(error => {
                addMessage('Sorry, something went wrong. Please try again.', 'bot');
            });

            userInput.value = '';
        }
    }

    // Send message on button click
    sendBtn.addEventListener('click', sendMessage);

    // Send message on Enter key
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});