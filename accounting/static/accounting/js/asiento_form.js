function createTdAndCloneEntry(element, newRowIndex) {
    if (element.tagName === "LABEL") {
        return
    } else {
        const td = document.createElement("td")
        const clone = element.cloneNode(true)
        if (element.id.includes("cuenta") || element.id.includes("debe") || element.id.includes("haber")) {
            clone.name = clone.name.replace("__prefix__", newRowIndex)
            clone.id = clone.id.replace("__prefix__", newRowIndex)
            td.appendChild(clone)
            return td
        } else {
            clone.name = clone.name.replace("__prefix__", newRowIndex)
            clone.id = clone.id.replace("__prefix__", newRowIndex)
            return clone
        }
    }
}

function addEntry() {
    const entriesTable = document.getElementById("entries-table")
    const emptyEntryFormset = document.getElementById("empty-formset").children
    const newRow = entriesTable.insertRow()

    for (var i = 0; i < emptyEntryFormset.length; i++) {
        const child = createTdAndCloneEntry(emptyEntryFormset[i], newRow.rowIndex - 1)
        if (child) {
            newRow.appendChild(child)
        }
    }

    document.getElementById("id_entries-TOTAL_FORMS").value = entriesTable.children.length
}
