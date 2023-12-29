async function getMedicine() {
    const name = document.querySelector("input[name='medicine-name']").value
    const quantity = document.querySelector("input[name='medicine-quantity']").value
    const dosage = document.querySelector("input[name='medicine-dosage']").value
    return fetch(`/api/medicines`, {
        method: "POST",
        body: JSON.stringify({
            name,
            quantity,
            dosage
        }),
        headers: {
            "Content-Type": "application/json",
        },
    })
        .then(res => {
            if (!res.ok && res.status === 400) {
                throw new Error(`Không tìm thấy thuốc`)
            }
            return res.json()
        })
        .then(data => {
            return data
        })
        .catch(e => {
            alert(e.message)
        })
}

window.onload = function () {
    const element = document.querySelector('#medicine-form')
    element.addEventListener('submit', async event => {
        event.preventDefault()
        const medicine = await getMedicine()
        // Hien thi thong tin thuoc len phieu kham
        console.log(medicine)
    })
}

var isOpening = true
var mainBodyClasses = ""
function openNav() {
    const sidebar = document.querySelector(".sidebar")
    const body = document.querySelector("main[role='main']")
    if (!mainBodyClasses) {
        mainBodyClasses = body.className
    }
    if (isOpening) {
        sidebar.style.left = '-500px'
        body.className = ""
        body.classList.add("main-content-full")
    } else {
        sidebar.style.left = '0'
        body.className = mainBodyClasses
        body.classList.remove("main-content-full")
    }
    isOpening = !isOpening
}
