/*
* This demo demonstrates how to replace default map tiles with custom imagery.
* In this case, the CoordMapType displays gray tiles annotated with the tile
* coordinates.
*
* Try panning and zooming the map to see how the coordinates change.
*/

var people;

function initMap() {
    var myLatLng = {lat: 37.7749, lng: -122.4194};

    var map = new google.maps.Map(document.getElementById('map'), {
      zoom: 10,
      center: myLatLng
    });

    var marker = new google.maps.Marker({
      position: myLatLng,
      map: map,
      title: 'Needing Help!'
    });
}