if (document.getElementById("type-select")) {
    const serviceRadio = document.getElementById("service-radio")
    serviceRadio.addEventListener("change", setElementVisibility)
    const productRadio = document.getElementById("product-radio")
    productRadio.addEventListener("change", setElementVisibility)

    const measurementUnitDiv = document.getElementById("measurement-unit")
    const taskTypeDiv = document.getElementById("task-type")
    const productTypeDiv = document.getElementById("product-type")
    const amountDiv = document.getElementById("amount")
    const warehouseDiv = document.getElementById("warehouse")
    const stockCuentaDiv = document.getElementById("stock-cuenta")
    const taskTypeButtonDiv = document.getElementById("task-type-button")
    function setElementVisibility() {
        if (serviceRadio.checked) {
            measurementUnitDiv.classList.add("visually-hidden")
            amountDiv.classList.add("visually-hidden")
            warehouseDiv.classList.add("visually-hidden")
            stockCuentaDiv.classList.add("visually-hidden")
            taskTypeDiv.classList.remove("visually-hidden")
            productTypeDiv.classList.remove("visually-hidden")
            taskTypeButtonDiv.classList.remove("visually-hidden")
        } else if (productRadio.checked) {
            measurementUnitDiv.classList.remove("visually-hidden")
            amountDiv.classList.remove("visually-hidden")
            warehouseDiv.classList.remove("visually-hidden")
            stockCuentaDiv.classList.remove("visually-hidden")
            taskTypeDiv.classList.add("visually-hidden")
            productTypeDiv.classList.add("visually-hidden")
            taskTypeButtonDiv.classList.add("visually-hidden")
        }
    }
    setElementVisibility()
}
