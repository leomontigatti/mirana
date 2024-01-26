function selectAll() {
    const checkbox = this.event.target
    const taskListBody = document.getElementById("taskList")
    const allCheckboxes = taskListBody.querySelectorAll("input[type=checkbox]")
    for (element of allCheckboxes) {
        element.checked = checkbox.checked
    }
}
