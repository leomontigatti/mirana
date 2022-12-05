const coords = document.getElementById("coords")
const initialCoordsArray = coords.value.replace("(", "").replace(")", "").split(", ")
var map
var marker

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

    marker = new google.maps.Marker({
        position: initialCoords,
        map: map,
    })
}

window.initMap = initMap;
