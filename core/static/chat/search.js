document.addEventListener('DOMContentLoaded', () => {
    const usersList = document.querySelector('.users-list');
    let searchTimeout;

    const fetchUsers = async (query) => {
        res = await fetch('http://127.0.0.1:8000/users/?q='+encodeURIComponent(query));
        if(!res.ok){
            console.error('Error fetching users.');
            return;
        };
        const data = await res.json();
        usersList.innerHTML = '';
        data.forEach(user => {
            const profileContainer = document.createElement('div');
            profileContainer.className = 'profile-container';
            profileContainer.dataset.username = user['username'];
            const profileDiv = document.createElement('div');
            profileDiv.innerText = user['username'].charAt(0).toUpperCase();
            profileDiv.className = 'profile-div';
            const p = document.createElement('p');
            p.innerText = user['username'];
            profileContainer.appendChild(profileDiv);
            profileContainer.appendChild(p);
            usersList.appendChild(profileContainer);
        });

    };

    document.getElementById('search-input').addEventListener('keyup', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            fetchUsers(e.target.value);
        }, 200);
    });
})