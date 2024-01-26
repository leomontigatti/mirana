if (document.getElementById("id_subtotal")) {
    setInvoiceSubtotal()
    setInvoiceTotal()
}

function createTdAndCloneService(element, newRowIndex, model) {
    if (element.tagName === "LABEL") {
        return
    } else {
        const serviceTypeTd = document.createElement("td")
        const clone = element.cloneNode(true)
        if (element.id.includes("service_type")) {
            clone.name = clone.name.replace("__prefix__", newRowIndex)
            clone.id = clone.id.replace("__prefix__", newRowIndex)
            serviceTypeTd.appendChild(clone)
            return serviceTypeTd
        } else if (element.id.includes("amount")) {
            clone.name = clone.name.replace("__prefix__", newRowIndex)
            clone.id = clone.id.replace("__prefix__", newRowIndex)
            serviceTypeTd.appendChild(clone)
            return serviceTypeTd
        } else {
            if (model != "hiring") {
                if (element.id.includes("unitario")) {
                    clone.name = clone.name.replace("__prefix__", newRowIndex)
                    clone.id = clone.id.replace("__prefix__", newRowIndex)
                    serviceTypeTd.appendChild(clone)
                    return serviceTypeTd
                } else if (element.id.includes("service_subtotal")) {
                    clone.name = clone.name.replace("__prefix__", newRowIndex)
                    clone.id = clone.id.replace("__prefix__", newRowIndex)
                    serviceTypeTd.appendChild(clone)
                    return serviceTypeTd
                }
            } else {
                clone.name = clone.name.replace("__prefix__", newRowIndex)
                clone.id = clone.id.replace("__prefix__", newRowIndex)
                clone.classList.add("visually-hidden")
                return clone
            }
        }
    }
}

function addService() {
    const modelForm = document.querySelector('[id$="_form"]')
    const servicesTable = document.getElementById("services-table")
    const emptyServiceFormset = document.getElementById("empty-service-formset").children
    const newRow = servicesTable.insertRow()

    const deleteTd = document.createElement("td")
    deleteTd.innerHTML = '<i class="bi bi-x-circle text-muted"></i>'
    deleteTd.classList.add("align-middle")
    deleteTd.classList.add("text-center")
    newRow.appendChild(deleteTd)

    for (var i = 0; i < emptyServiceFormset.length; i++) {
        const child = createTdAndCloneService(emptyServiceFormset[i], newRow.rowIndex - 1, modelForm.dataset.model)
        if (child) {
            newRow.appendChild(child)
        }
    }

    document.getElementById("id_services-TOTAL_FORMS").value = servicesTable.children.length
}

function setServiceSubtotal() {
    const amountInput = this.event.target.parentNode.parentNode.querySelector('[name$="amount"]')
    const unitarioInput = this.event.target.parentNode.parentNode.querySelector('[name$="unitario"]')
    const subtotalInput = this.event.target.parentNode.parentNode.querySelector('[name$="service_subtotal"]')
    subtotalInput.value = parseFloat(amountInput.value) * parseFloat(unitarioInput.value)

    if (document.getElementById("id_subtotal")) {
        setInvoiceSubtotal()
        setTaxSubtotal()
        setInvoiceTotal()
    }
}

function setInvoiceSubtotal() {
    const servicesTable = document.getElementById("services-table")
    const serviceSubtotalInputs = servicesTable.querySelectorAll('[name$="service_subtotal"]')
    let subtotal = 0.0
    for (let subtotalInput of serviceSubtotalInputs) {
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

function renderMap() {
    window.open("/map/", "newwindow", "width=700, height=450")
    return false
}
