if (document.getElementById("id_subtotal")) {
    setInvoiceSubtotal()
    setInvoiceTotal()
}

function createTdAndCloneExpense(element, newRowIndex) {
    if (element.tagName === "LABEL") {
        return
    } else {
        const createdTd = document.createElement("td")
        const clone = element.cloneNode(true)
        if (element.id.includes("invoice")) {
            clone.name = clone.name.replace("__prefix__", newRowIndex)
            clone.id = clone.id.replace("__prefix__", newRowIndex)
            clone.classList.add("visually-hidden")
            return clone
        } else {
            clone.name = clone.name.replace("__prefix__", newRowIndex)
            clone.id = clone.id.replace("__prefix__", newRowIndex)
            createdTd.appendChild(clone)
            return createdTd
        }
    }
}

function addExpense() {
    const expensesTable = document.getElementById("expenses-table")
    const emptyExpensesFormset = document.getElementById("empty-expenses-formset").children
    const newRow = expensesTable.insertRow()

    const deleteTd = document.createElement("td")
    deleteTd.innerHTML = '<i class="bi bi-x-circle text-muted"></i>'
    deleteTd.classList.add("align-middle")
    deleteTd.classList.add("text-center")
    newRow.appendChild(deleteTd)

    for (var i = 0; i < emptyExpensesFormset.length; i++) {
        const child = createTdAndCloneExpense(emptyExpensesFormset[i], newRow.rowIndex - 1)
        if (child) {
            newRow.appendChild(child)
        }
    }

    document.getElementById("id_expenses-TOTAL_FORMS").value = expensesTable.children.length
}

function setExpenseSubtotal() {
    const amountInput = this.event.target.parentNode.parentNode.querySelector('[name$="amount"]')
    const unitarioInput = this.event.target.parentNode.parentNode.querySelector('[name$="unitario"]')
    const subtotalInput = this.event.target.parentNode.parentNode.querySelector('[name$="expense_subtotal"]')
    subtotalInput.value = parseFloat(amountInput.value) * parseFloat(unitarioInput.value)

    if (document.getElementById("id_subtotal")) {
        setInvoiceSubtotal()
        setTaxSubtotal()
        setInvoiceTotal()
    }
}

function setInvoiceSubtotal() {
    const expensesTable = document.getElementById("expenses-table")
    const expensesSubtotalInputs = expensesTable.querySelectorAll('[name$="expense_subtotal"]')
    let subtotal = 0.0
    for (let subtotalInput of expensesSubtotalInputs) {
        subtotal += parseFloat(subtotalInput.value)
    }
    const invoiceSubtotalInput = document.getElementById("id_subtotal")
    invoiceSubtotalInput.value = subtotal
}

function cloneTax(element, taxesDivLength) {
    if (element.tagName === "LABEL") {
        return
    } else {
        const clone = element.cloneNode(true)
        if (element.id.includes("tax_type")) {
            clone.name = clone.name.replace("__prefix__", taxesDivLength)
            clone.id = clone.id.replace("__prefix__", taxesDivLength)
            return clone
        } else if (element.id.includes("tax_subtotal")) {
            clone.name = clone.name.replace("__prefix__", taxesDivLength)
            clone.id = clone.id.replace("__prefix__", taxesDivLength)
            return clone
        } else {
            clone.name = clone.name.replace("__prefix__", taxesDivLength)
            clone.id = clone.id.replace("__prefix__", taxesDivLength)
            clone.classList.add("visually-hidden")
            return clone
        }
    }
}

function addTax() {
    const taxesDiv = document.getElementById("taxes-div")
    const taxesDivLength = taxesDiv.childElementCount
    const emptyTaxesFormset = document.getElementById("empty-taxes-formset").children
    const rowDiv = document.createElement("div")
    rowDiv.classList.add("row")
    rowDiv.classList.add("gx-2")
    const inputGroupDiv = document.createElement("div")
    inputGroupDiv.classList.add("input-group")
    inputGroupDiv.classList.add("pb-2")

    const deleteButton = document.createElement("i")
    deleteButton.classList.add("bi")
    deleteButton.classList.add("bi-x-circle")
    deleteButton.classList.add("align-self-center")
    deleteButton.classList.add("text-muted")
    deleteButton.classList.add("me-2")
    rowDiv.appendChild(inputGroupDiv)
    inputGroupDiv.appendChild(deleteButton)

    for (var i = 0; i < emptyTaxesFormset.length; i++) {
        const child = cloneTax(emptyTaxesFormset[i], taxesDivLength)
        if (child) {
            inputGroupDiv.appendChild(child)
        }
    }

    taxesDiv.appendChild(inputGroupDiv)

    document.getElementById("id_taxes-TOTAL_FORMS").value = taxesDivLength
}

function setTaxSubtotal() {
    const invoiceSubtotal = document.getElementById("id_subtotal").value

    const taxesDiv = document.getElementById("taxes-div")
    for (const div of taxesDiv.children) {
        const taxSelect = div.querySelector("select")
        const taxInput = div.querySelector("input")
        if (taxSelect.value) {
            const taxString = taxSelect.options[taxSelect.selectedIndex].text
            const taxPercentage = taxString.substring(
                taxString.indexOf("(") + 1,
                taxString.lastIndexOf(")")
            ).replace("%", "")
            taxInput.value = parseFloat(invoiceSubtotal) * parseFloat(taxPercentage) / 100
            setInvoiceTotal()
        } else {
            taxInput.value = 0.0
            setInvoiceTotal()
        }
    }
}

function setInvoiceTotal() {
    const invoiceSubtotalInput = document.getElementById("id_subtotal")
    const invoiceSubtotal = parseFloat(invoiceSubtotalInput.value)

    const taxesDiv = document.getElementById("taxes-div")
    let taxSubtotal = 0.0
    for (const div of taxesDiv.children) {
        const subtotal = div.querySelector("input").value
        taxSubtotal += parseFloat(subtotal)
    }

    const invoiceTotalInput = document.getElementById("id_total")
    invoiceTotalInput.value = invoiceSubtotal + taxSubtotal
}
