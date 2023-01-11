var messagesDiv = document.getElementById("messages")
if (messagesDiv) {
    function createAlert(message) {
        var alertDiv = document.createElement("div")
        alertDiv.classList.add("alert", "alert-dismissible", `${message.tags}`, "m-2")
        alertDiv.setAttribute("role", "alert")
        var messageDiv = document.createElement("div")
        messageDiv.innerText = message.message
        var closeButton = document.createElement("button")
        closeButton.setAttribute("type", "button")
        closeButton.classList.add("btn-close")
        closeButton.setAttribute("data-bs-dismiss", "alert")

        alertDiv.append(messageDiv, closeButton)
        messagesDiv.append(alertDiv)
    }

    htmx.on("messages", (event) => {
        event.detail.value.forEach(createAlert)
    })
}
