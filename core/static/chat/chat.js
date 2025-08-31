document.addEventListener('DOMContentLoaded', () => {
    let ws = new WebSocket('ws://127.0.0.1:8000/ws/');
    const loggedUser = document.querySelector('body').dataset.user;
    const box = document.getElementById('chat-box');
    const typingText = document.querySelector('.typing-indicator');
    const inputBox = document.getElementById('chat-input');
    const boxUl = document.getElementById('chat-ul');
    const clickedProfile = document.querySelector('.clicked-profile-container')
    let currentPair = null;
    let typingTimeout = null;

    typingText.style.display = 'none';
    clickedProfile.style.display = 'none';

    document.querySelectorAll('.profile-container').forEach(container => {
        container.addEventListener('click', () => {
            const pairUser = container.dataset.username;
            clickedProfile.style.display = 'flex';
            document.querySelector('.clicked-profile-div').innerText = pairUser.charAt(0).toUpperCase();
            document.querySelector('.clicked-profile-username').innerText = pairUser;

            if (!pairUser) return;
            if (ws && currentPair === pairUser && ws.readyState === WebSocket.OPEN) {
                return;
            } else if (ws && ws.readyState === WebSocket.OPEN) {
                ws.close();
            }

            ws = new WebSocket(`ws://127.0.0.1:8000/ws/${loggedUser}/${pairUser}/`);

            ws.onopen = () => {
                currentPair = pairUser;
                console.log('websocket established.');
            };

            ws.onclose = () => {
                boxUl.innerHTML = '';
                console.log('websocket disconnected.');
            };

            ws.onmessage = (e) => {
                clearTimeout(typingTimeout);
                let data = JSON.parse(e.data);
                if (data['action'] === 'typing') {
                    typingText.style.display = 'flex';
                    clearTimeout(typingTimeout);
                    typingTimeout = setTimeout(() => {
                        typingText.style.display = 'none';
                    }, 2000);
                    return;
                };

                typingText.style.display = 'none';
                clearTimeout(typingTimeout);
                
                let li = document.createElement('li');
                let text = document.createElement('p');
                let delBtn = document.createElement('button');
                delBtn.dataset.id = data['message_id'];
                delBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#6B7A8F"><path d="M280-120q-33 0-56.5-23.5T200-200v-520h-40v-80h200v-40h240v40h200v80h-40v520q0 33-23.5 56.5T680-120H280Zm400-600H280v520h400v-520ZM360-280h80v-360h-80v360Zm160 0h80v-360h-80v360ZM280-720v520-520Z"/></svg>`;
                delBtn.className = 'delete-message';
                text.innerText = data['message'] || 'Error';
                text.style.backgroundColor = data['sender'] == loggedUser ? '#565057' : '#7d0288';
                li.setAttribute('class', 'message-li');
                li.style.display = 'flex';
                li.style.alignSelf = data['sender'] == loggedUser ? 'flex-start' : 'flex-end';
                li.style.flexDirection = li.style.alignSelf == 'flex-end' ? 'row-reverse' : 'row';
                li.appendChild(text);
                li.appendChild(delBtn);
                boxUl.appendChild(li);
                box.append(boxUl);
                let nearBottom = box.scrollTop < 50;
                console.log(nearBottom);
                if (nearBottom) {
                    box.scrollTo({
                        top: box.scrollHeight,
                        behavior: "smooth"
                    })
                }
            };

        });
    });

    inputBox.addEventListener('input', () => {
        console.log('sending typing event');
        if (ws && ws.readyState === WebSocket.OPEN && currentPair) {
            ws.send(JSON.stringify({ 'action': 'typing' }));
        }
    });
    
    document.getElementById('chat-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const inputBox = document.getElementById('chat-input');
        if (inputBox.value.trim() === '') {
            return;
        }
        ws.send(JSON.stringify({ 'message': inputBox.value }));
        inputBox.value = '';
    });

    boxUl.addEventListener('click', (e) => {
        console.log('clicked', e.target);
        button = e.target.closest('.delete-message');
        if (!button) return;

        li = button.closest('li');
        li.remove();
        button.remove();

        ws.send(JSON.stringify({
            'action': 'delete_message',
            'message_id': button.dataset.id
        }));
    });
})
