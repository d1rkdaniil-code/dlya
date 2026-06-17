document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = 1;
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.2 });

    cards.forEach(card => {
        card.style.opacity = 0;
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    const themeToggle = document.createElement('button');
    themeToggle.textContent = '🌙';
    themeToggle.style.cssText = `
        position: fixed; bottom: 20px; right: 20px;
        background: #1f2a3e; color: #eef4ff;
        border: none; border-radius: 50%;
        width: 50px; height: 50px;
        font-size: 1.8rem; cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        z-index: 999;
        transition: 0.3s;
    `;
    themeToggle.onmouseover = () => themeToggle.style.transform = 'scale(1.1)';
    themeToggle.onmouseout = () => themeToggle.style.transform = 'scale(1)';
    document.body.appendChild(themeToggle);

    const currentTheme = localStorage.getItem('theme') || 'dark';
    if (currentTheme === 'light') {
        document.body.classList.add('light-theme');
        themeToggle.textContent = '☀️';
    } else {
        document.body.classList.remove('light-theme');
        themeToggle.textContent = '🌙';
    }

    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('light-theme');
        const isLight = document.body.classList.contains('light-theme');
        localStorage.setItem('theme', isLight ? 'light' : 'dark');
        themeToggle.textContent = isLight ? '☀️' : '🌙';
    });

    const form = document.querySelector('.contact-form');
    if (form) {
        form.addEventListener('submit', (e) => {
            const name = form.querySelector('input[name="name"]');
            const email = form.querySelector('input[name="email"]');
            const message = form.querySelector('textarea[name="message"]');
            let valid = true;
            [name, email, message].forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = '#ff6b6b';
                    valid = false;
                } else {
                    field.style.borderColor = 'var(--border-color)';
                }
            });
            if (!valid) {
                e.preventDefault();
                alert('Пожалуйста, заполните все поля');
            }
        });
    }

    console.log('Портфолио Даниила');
    console.log('Python-разработчик, 16 лет');
    console.log('Стек: Python, Flask, JavaScript, CSS Grid');
});
