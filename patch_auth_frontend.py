import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

old_login = """        function handleLoginSubmit() {
            const emailInput = document.getElementById('loginEmail').value.toLowerCase().trim();
            if (emailInput === 'admin') {
                login('admin');
            } else {
                login('user'); // defaults to user for any other input
            }
        }"""

new_login = """        async function handleLoginSubmit() {
            const emailInput = document.getElementById('loginEmail').value.trim();
            const passInput = document.getElementById('loginPass').value;
            
            // Basic validation
            if (!emailInput || !passInput) {
                alert("Please enter both email and password.");
                return;
            }
            
            try {
                const response = await fetch('http://localhost:8000/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: emailInput, password: passInput })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem('aero_token', data.token);
                    localStorage.setItem('aero_role', data.role);
                    login(data.role); // Transition to the correct dashboard
                } else {
                    alert('Invalid credentials! Please try again.');
                }
            } catch (e) {
                console.error('Login error:', e);
                alert('Server connection failed. Is the FastAPI backend running?');
            }
        }"""

html = html.replace(old_login, new_login)

# Also update the UI hint text at the bottom of the login screen
old_hint = "Enter user or admin in the ID field and click Login"
new_hint = "Admin: admin@mospi.gov.in (admin123) | Jury: jury@mospi.gov.in (jury123)"
html = html.replace(old_hint, new_hint)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
