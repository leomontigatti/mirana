const filtersFormLi = document.getElementById("filtersForm").getElementsByTagName("li")
for (var li of filtersFormLi) {
    li.addEventListener("click", setFilter)
}

const filtersList = localStorage.getItem("filtersList") || localStorage.setItem("filtersList", "")
const searchParams = new URLSearchParams(filtersList)

loadFilters()

function setFilter() {
    if (searchParams.has(this.getAttribute("name"))) {
        searchParams.set(this.getAttribute("name"), this.id)
    } else {
        searchParams.append(this.getAttribute("name"), this.id)
    }
    localStorage.filtersList = searchParams
    window.location.href = "?" + searchParams
}

function getShowAll(element) {
    var startingElement = element.previousElementSibling
    while (true) {
        if (startingElement.getAttribute("name") === "show-all") {
            return startingElement
        } else {
            startingElement = startingElement.previousElementSibling
        }
    }
}

document.getElementById("clear-filters").addEventListener("click", clearFilters)

function clearFilters() {
    localStorage.removeItem("filtersList")
    window.location.href = "?"
}

function loadFilters() {
    if (searchParams.toString()) {
        searchParams.forEach((value, key) => {
            var selectedLi = document.querySelector(`[name="${key}"][id="${value}"]`)
            selectedLi.classList.add("selected")
            var showAll = getShowAll(selectedLi)
            showAll.classList.remove("selected")
        })
    }
}

const showAllP = document.getElementsByName("show-all")
for (var element of showAllP) {
    element.addEventListener("click", showAll)
}

function showAll() {
    searchParams.delete(this.id)
    localStorage.filtersList = searchParams
    window.location.href = "?" + searchParams
}
