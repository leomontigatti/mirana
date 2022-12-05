if (window.location.pathname != localStorage.getItem("currentModel")) {
    localStorage.removeItem("filtersList")
    localStorage.setItem("currentModel", window.location.pathname)
}