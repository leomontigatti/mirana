if (window.location.pathname != localStorage.getItem("currentModel")) {
    localStorage.removeItem("filtersList")
    localStorage.setItem("currentModel", window.location.pathname)
}

function cleanSearch() {
    localStorage.removeItem("filtersList")
    window.location.href = "?"
}

const cleanSearchButton = document.getElementById("clean-search")
if (cleanSearchButton) {
    cleanSearchButton.addEventListener("click", cleanSearch)
}
