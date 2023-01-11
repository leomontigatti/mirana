window.addEventListener('load', calculateTotal)
window.addEventListener('load', calculateTax)

function calculateSubtotal() {
    var amountInput = this.event.target.parentNode.parentNode.querySelector('[name$="amount"]')
    var unitarioInput = this.event.target.parentNode.parentNode.querySelector('[name$="unitario"]')
    var subtotalInput = this.event.target.parentNode.parentNode.querySelector('[name$="service_subtotal"]')
    subtotalInput.value = parseFloat(amountInput.value) * parseFloat(unitarioInput.value)
    calculateTotal()
    calculateTax()
}

function calculateTotal() {
    var serviceTable = document.getElementById("service-table")
    var serviceSubtotal = document.getElementById("id_subtotal")

    var subTotal = 0
    if (serviceTable) {

        for (var row of serviceTable.rows) {
            var subtotal = row.querySelector('[name$="subtotal"]').value
            subTotal += parseFloat(subtotal)
        }
        serviceSubtotal.value = subTotal

        var taxesInputs = document.getElementsByName("tax_subtotal")
        var totalInput = document.getElementById("id_total")

        var total = subTotal
        for (var tax of taxesInputs) {
            total += parseFloat(tax.value)
        }
        totalInput.value = total
    }
}

function calculateTax() {
    if (document.getElementById("id_subtotal")) {
        var serviceSubtotal = document.getElementById("id_subtotal").value
        var taxesRow = document.getElementsByName("tax-row")
        for (var row of taxesRow) {
            var taxSelect = row.querySelector('select')
            var taxInput = row.querySelector('input')
            if (taxSelect.value) {
                var taxString = taxSelect.options[taxSelect.selectedIndex].text
                var taxPercentage = taxString.substring(
                    taxString.indexOf("(") + 1,
                    taxString.lastIndexOf(")")
                    ).replace("%", "")
                    taxInput.value = parseFloat(serviceSubtotal) * parseFloat(taxPercentage) / 100
                }
            }
            calculateTotal()
    }
}
