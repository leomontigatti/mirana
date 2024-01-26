const tds = document.getElementsByTagName("td")
for (var element of tds) {
    element.addEventListener("click", setSelected)
    element.addEventListener("click", showTasksForDaySelected)
    if (element.innerText == today) {
        element.classList.add("bg-primary", "text-dark", "bg-opacity-25")
    }
}

function setSelected() {
    for (var element of tds) {
        element.classList.remove("selected")
        // if (element.classList.contains("selected")) {
        //     element.remove("selected")
        // }
    }
    this.classList.add("selected")
}

function showTasksForDaySelected() {
    const monthAndYear = document.querySelector("table th.month").innerText
    const day = this.innerText

    let params = new URLSearchParams()
    params.append("date", day + monthAndYear)
    window.location.href = "?" + params
}
