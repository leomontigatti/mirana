const lat = document.getElementById("lat")
const lng = document.getElementById("lng")
const address = document.getElementById("address")
var map
var marker
var autocomplete

function initMap() {
    const initialCoords = new google.maps.LatLng(
        parseFloat(lat.value),
        parseFloat(lng.value)
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

    map.addListener("click", (e) => {
        placeMarkerAndPanTo(e.latLng)
    })
}

function placeMarkerAndPanTo(latLng) {
    if (!marker) {
        marker = new google.maps.Marker({
            position: latLng,
            map: map,
        })
    } else {
        marker.setMap(null)
        marker.setOptions({
            position: latLng,
            map: map
        })
    }
    map.panTo(latLng)
    geocoder = new google.maps.Geocoder()
    geocoder.geocode({
        "latLng": latLng
    }, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            if (results[0]) {
                address.value = results[0].formatted_address
            }
        }
    })
    lat.value = latLng.lat()
    lng.value = latLng.lng()
}

function saveLocation() {
    const addressInput = window.opener.document.getElementById("id_address")
    const latInput = window.opener.document.getElementById("id_lat")
    const lngInput = window.opener.document.getElementById("id_lng")
    addressInput.value = address.value
    latInput.value = lat.value
    lngInput.value = lng.value
    window.close()
}

function initAutocomplete() {
    autocomplete = new google.maps.places.Autocomplete(
        address,
        {
            types: ["geocode"],
            fields: ["geometry", "name"]
        })

    autocomplete.addListener("place_changed", onPlaceChanged)
}

function onPlaceChanged() {
    const place = autocomplete.getPlace()
    if (!place.geometry) {
        address.placeholder = "Buscar por domicilio"
    } else {
        marker.setMap(null)
        marker.setOptions({
            position: place.geometry.location,
            map: map
        })
        map.setCenter(place.geometry.location)
        address.innerHTML = place.name
    }
}

function geolocate() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const geolocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            }
            const circle = new google.maps.Circle({
                center: geolocation,
                radius: position.coords.accuracy
            })
            autocomplete.setBounds(circle.getBounds())
        })
    }
}

function initialize() {
    initMap();
    initAutocomplete();
}
