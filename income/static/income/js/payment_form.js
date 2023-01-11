if (instanceId != "None" || userIsOperator == "True") {
    const customerSelect = document.getElementById("id_customer")
    customerSelect.setAttribute("readOnly", "")
}

const receiptId = new URLSearchParams(document.location.search).get("receipt")
if (receiptId) {
    const receiptSelect = document.getElementById("receipt-select")
    receiptSelect.value = receiptId
}

if (document.getElementById("id_option")) {
    const optionSelect = document.getElementById("id_option")
    optionSelect.addEventListener("change", setElementVisibility)

    const amountInputDiv = document.getElementById("amount-input")
    const methodSelectDiv = document.getElementById("method-select")

    function setElementVisibility() {
        if (optionSelect.value == '') {
            amountInputDiv.classList.add("visually-hidden")
            methodSelectDiv.classList.add("visually-hidden")
        } else {
            amountInputDiv.classList.remove("visually-hidden")
            methodSelectDiv.classList.remove("visually-hidden")
        }
    }

    setElementVisibility()
}
