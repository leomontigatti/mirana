const addProductButton = document.getElementById("add-product")
addProductButton.addEventListener("click", addProduct)

const formsetTotalForms = document.getElementById("id_products-TOTAL_FORMS")
if (formsetTotalForms.value == "0") {
    addProduct()
}

if (document.location.pathname.includes("create")) {
    document.getElementById("id_products-INITIAL_FORMS").value = "0"
    document.getElementById("id_taxes-INITIAL_FORMS").value = "0"
}

const deleteChecks = document.querySelectorAll('input[id*="DELETE"]')
deleteChecks.forEach(element =>
    element.classList = "form-check-input"
)

function calculateSubtotal() {
    const amountInput = this.parentNode.parentNode.querySelector('[name$="amount"]')
    const unitarioInput = this.parentNode.parentNode.querySelector('[name$="unitario"]')
    const subtotalInput = this.parentNode.parentNode.querySelector('[name$="subtotal"]')
    subtotalInput.value = parseFloat(amountInput.value) * parseFloat(unitarioInput.value)
    calculateTotal()
    calculateTax()
}

function addProduct() {
    const productsTable = document.getElementById("products-table")
    const emptyFormsetTds = document.getElementById("empty-formset").querySelectorAll("td")

    const newRow = productsTable.insertRow()
    emptyFormsetTds.forEach(emptyTd => {
        const clone = emptyTd.cloneNode(true)
        for (var element of clone.children) {
            element.name = element.name.replace("__prefix__", newRow.rowIndex - 1)
            element.id = element.id.replace("__prefix__", newRow.rowIndex - 1)
        }
        newRow.appendChild(clone)
    });

    addCalculateSubtotal()

    const actionsCell = newRow.lastChild
    actionsCell.classList = "align-middle"

    document.getElementById("id_products-TOTAL_FORMS").value = productsTable.children.length
}

if (instanceId != "None") {
    const customerSelect = document.getElementById("id_customer")
    customerSelect.setAttribute("readOnly", "")
}

const receiptId = new URLSearchParams(document.location.search).get("receipt")
if (receiptId) {
    const receiptSelect = document.getElementById("id_receipt")
    receiptSelect.value = receiptId
}

function calculateTotal() {
    const productsTable = document.getElementById("products-table")
    const productsSubtotal = document.getElementById("id_subtotal")

    let subTotal = 0
    for (const row of productsTable.rows) {
        const subtotal = row.querySelector('[name$="subtotal"]').value
        subTotal += parseFloat(subtotal)
    }
    productsSubtotal.value = subTotal

    const taxesInputs = document.getElementsByClassName("tax")
    const totalInput = document.getElementById("id_total")

    let total = subTotal
    for (const tax of taxesInputs) {
        total += parseFloat(tax.value)
    }
    totalInput.value = total
}

function addCalculateSubtotal() {
    const productsTable = document.getElementById("products-table")
    const calculationInputs = productsTable.querySelectorAll('[name$="amount"], [name$="unitario"]')
    for (var input of calculationInputs) {
        input.addEventListener("change", calculateSubtotal)
    }
}

addCalculateSubtotal()

const taxSelects = document.querySelectorAll('[name$="tax_type"]')
for (const select of taxSelects) {
    select.addEventListener("change", calculateTax)
}

function calculateTax() {
    const productsSubtotal = document.getElementById("id_subtotal").value
    const taxesRow = document.getElementsByName("taxes-row")
    for (row of taxesRow) {
        var taxSelect = row.querySelector('select')
        var taxInput = row.querySelector('input')
        if (taxSelect.value) {
            var taxString = taxSelect.options[taxSelect.selectedIndex].text
            var taxPercentage = taxString.substring(
                taxString.indexOf("(") + 1,
                taxString.lastIndexOf(")")
            ).replace("%", "")
            taxInput.value = parseFloat(productsSubtotal) * parseFloat(taxPercentage) / 100
        }
    }
    calculateTotal()
}
