const netoTag = document.getElementById("id_neto")
const ivaTag = document.getElementById("id_iva")
const brutoTag = document.getElementById("id_bruto")

function calcularSuma () {
    let suma = parseFloat(netoTag.value) + parseFloat(ivaTag.value);
    brutoTag.value = suma;
}

function calcularIva () {
    let iva = parseFloat(netoTag.value) * .21;
    ivaTag.value = iva;
}

netoTag.addEventListener("change", calcularSuma)
ivaTag.addEventListener("change", calcularSuma)
