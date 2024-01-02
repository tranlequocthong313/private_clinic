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
