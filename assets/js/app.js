// 8-20 characters long, no _ or . at the beginning, no __ or _. or ._ or .. inside,
// allowed characters, no _ or . at the end
NICKNAME_REGEX = /^(?=.{8,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$/

// Min 1 character, max 25, upper- and lowercase letters only
NAME_REGEX = /^[a-zA-Z ,.\'-]+$/

// Minimum eight characters, at least one letter and one number
PASSWORD_REGEX = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/

EMAIL_REGEX = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/


function removeAllChildren(HTMLElement) {
    HTMLElement.innerHTML = ''
}

function createRegisterForm() {
    html = `
        <form class="form register-form" id="register-form">
            <input data-verified="false" class="form__input" type="text" id="name" placeholder="name">
            <input data-verified="false" class="form__input" type="text" id="nickname" placeholder="nickname">
            <input data-verified="false" class="form__input" type="email" id="email" placeholder="email">
            <input data-verified="false" class="form__input" type="password" id="password" placeholder="password">
            <input class="form__input" type="submit" disabled id="register-submit" value="Register">
        </form>
    `
    return html
}

const registerFormSubmitHandler = (inputs) => (event) => {
    event.preventDefault()
        
    data = {
        name: inputs.nameInput.value,
        nickname: inputs.nicknameInput.value,
        password: inputs.passwordInput.value,
        email: inputs.emailInput.value,
    }

    fetch('http://127.0.0.1:5000/user/register', {
        method: 'POST',
        body: JSON.stringify(data),
    })
        .then(res => res.json())
        .then(data => console.log(data))
}

const inputVerifyHandler = (regex, input) =>  {
    if (regex.test(input.value)) {
        input.dataset.verified = true
        input.classList.remove('wrong')
        input.classList.add('right')
    } else {
        input.dataset.verified = false
        input.classList.remove('right')
        input.classList.add('wrong')
    }
}

const setSubmitButtonState = (submitButton, inputs) => {
    inputStates = Object.values(inputs).map(input => {
        if (input.dataset.verified === 'true') {
            return true
        }
        return false
    })

    if (inputStates.every(value => value)) {
        submitButton.disabled = false
    } else {
        submitButton.disabled = true
    }
}

const listenInputs = (formHTMLElement, inputs) => {
    form = formHTMLElement

    form.addEventListener('input', (event) => {
        input = event.target
        regex = RegExp()
        switch (input.id) {
            case 'name': {
                regex = NAME_REGEX
                break
            }
            case 'nickname': {
                regex = NICKNAME_REGEX
                break
            }
            case 'email': {
                regex = EMAIL_REGEX
                break
            }
            case 'password': {
                regex = PASSWORD_REGEX
                break
            }
        }
        inputVerifyHandler(regex, input)
        submitButton = form.querySelector('#register-submit')
        setSubmitButtonState(submitButton, inputs)
    })
}

function processRegisterForm(formHTMLElement) {
    form = formHTMLElement

    inputs = {
        nameInput: form.querySelector('#name'),
        nicknameInput: form.querySelector('#nickname'),
        emailInput: form.querySelector('#email'),
        passwordInput: form.querySelector('#password'),
    }

    listenInputs(form, inputs)

    form.addEventListener('submit', registerFormSubmitHandler(inputs))
}

function registerHandler() {
    app = document.querySelector('.app')
    removeAllChildren(app)

    app.innerHTML = `
        <h2>Create a new account</h2>
        ${createRegisterForm()}
    `

    form = app.querySelector('#register-form')
    
    processRegisterForm(form)
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
        callback: registerHandler,
    })
    loginButton = createElement('button', 'login-btn', 'login', {
        type: 'click',
        callback: () => console.log('click log')
    })

    app.append(title, registerButton, loginButton)
    document.body.append(app)
}

window.onload = onPageLoad
