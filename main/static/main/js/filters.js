window.onload = loadFilters

function setFilter() {
    const filtersList = localStorage.getItem("filtersList") || localStorage.setItem("filtersList", "")
    const searchParams = new URLSearchParams(filtersList)
    const eventId = this.event.target.id
    const name = this.event.target.getAttribute("name")
    if (searchParams.has(name)) {
        searchParams.set(name, eventId)
    } else {
        searchParams.append(name, eventId)
    }
    localStorage.filtersList = searchParams
    window.location.href = "?" + searchParams
}

function getShowAll(element) {
    let startingElement = element.previousElementSibling
    while (true) {
        if (startingElement.getAttribute("name") === "show-all") {
            return startingElement
        } else {
            startingElement = startingElement.previousElementSibling
        }
    }
}

function clearFilters() {
    localStorage.setItem("filtersList", "")
    window.location.href = window.location.pathname
}

function loadFilters() {
    const filtersList = localStorage.getItem("filtersList") || localStorage.setItem("filtersList", "")
    const searchParams = new URLSearchParams(filtersList)
    const lastLocation = localStorage.getItem("lastLocation")
    if (lastLocation && lastLocation === window.location.pathname) {
        if (searchParams.toString()) {
            searchParams.forEach((value, key) => {
                let selectedItem = document.querySelector(`[name="${key}"][id="${value}"]`)
                selectedItem.classList.add("selected")
                let showAll = getShowAll(selectedItem)
                showAll.classList.remove("selected")
            })
        }
    } else {
        localStorage.setItem("lastLocation", window.location.pathname)
        localStorage.setItem("filtersList", "")
    }
}

function showAll() {
    const filtersList = localStorage.getItem("filtersList") || localStorage.setItem("filtersList", "")
    const searchParams = new URLSearchParams(filtersList)
    searchParams.delete(this.event.target.id)
    localStorage.filtersList = searchParams
    window.location.href = "?" + searchParams
}
