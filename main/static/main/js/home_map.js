const coords = document.getElementById("coords")
const initialCoordsArray = coords.value.replace("(", "").replace(")", "").split(", ")
var map
var marker
var autocomplete

var hiringValues = Object.values(hiringJson)

function initMap() {
    const initialCoords = new google.maps.LatLng(
        initialCoordsArray[0],
        initialCoordsArray[1]
        )

        const mapOptions = {
            zoom: 15,
            center: initialCoords,
        }

        map = new google.maps.Map(
            document.getElementById("map"),
            mapOptions
            )

        hiringValues.forEach((hiring) => {
            var coordsArray = hiring.fields.location.replace("(", "").replace(")", "").split(", ")
            var coords = new google.maps.LatLng(
                coordsArray[0],
                coordsArray[1]
                )
            marker = new google.maps.Marker({
                position: coords,
                map: map,
                })

            marker.addListener("click", () => redirectToHiringDetail(hiring))
            })
}

function redirectToHiringDetail(hiring) {
    window.location.replace(`/hiring/update_or_create/${hiring.pk}`)
}

function saveLocation() {
    const addressInput = window.opener.document.getElementById("id_address")
    const locationInput = window.opener.document.getElementById("id_location")
    addressInput.value = address.value
    locationInput.value = coords.value
    window.close()
}

function initialize() {
    initMap();
    initAutocomplete();
}
