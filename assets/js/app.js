function removeAllChildren(HTMLElement) {
    HTMLElement.innerHTML = ''
}

function onRegisterClick() {
    app = document.querySelector('.app')
    removeAllChildren(app)

    formHTML = `
        <form class="form register-form" id="register-form">
            <input type="text" id="name" placeholder="name">
            <input type="text" id="nickname" placeholder="nickname">
            <input type="email" id="email" placeholder="email">
            <input type="password" id="password" placeholder="password">
            <input type="submit" id="register-submit">
        </form>
    `

    app.innerHTML = formHTML

    form = app.querySelector('#register-form')
    
    nameInput = form.querySelector('#name')
    nicknameInput = form.querySelector('#nickname')
    emailInput = form.querySelector('#email')
    passwordInput = form.querySelector('#password')

    form.addEventListener('submit', event => {
        event.preventDefault()
        
        data = {
            name: nameInput.value,
            nickname: nicknameInput.value,
            password: passwordInput.value,
        }

        json = JSON.stringify(data)

        fetch('http://127.0.0.1:5000/user/register', {
            method: 'POST',
            body: json,
        })
            .then(res => res.json())
            .then(data => console.log(data))
    })
}

function createElement(tag, className, textContent, eventListener) {
    el = document.createElement(tag)
    if (typeof className == 'string' && className.trim()) {
        el.className = className
    }
    if (typeof textContent == 'string' && textContent.trim()) {
        el.textContent = textContent
    }
    if (eventListener) {
        type = eventListener.type
        callback = eventListener.callback
        el.addEventListener(type, callback)
    }
    return el
}

function onPageLoad() {
    app = createElement('div', 'app')

    title = createElement('h1', 'title', 'Welcome to the Jungle!')

    registerButton = createElement('button', 'register-btn', 'register', {
        type: 'click',
        callback: onRegisterClick,
    })
    loginButton = createElement('button', 'login-btn', 'login', {
        type: 'click',
        callback: () => console.log('click log')
    })

    app.append(title, registerButton, loginButton)
    document.body.append(app)
}

window.onload = onPageLoad
