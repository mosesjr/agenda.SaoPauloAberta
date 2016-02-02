var map;
var LastActive = null;
var circleExt;
var circleInt;
var circleCnt;

function InitMap(center) {
    map = new ol.Map({
    target: 'map',
    layers: [
          new ol.layer.Tile({
            source: new ol.source.MapQuest({
                    layer: 'osm'
                })
          })
    ],
    view: new ol.View({
          projection: 'EPSG:900913',
          center: ol.proj.transform(center, 'EPSG:4326', 'EPSG:900913'),
          zoom: 17
        })
    });

    // Source and vector layer
    var vectorSource = new ol.source.Vector({
        projection: 'EPSG:4326'
    });
    
    var center = map.getView().getCenter();        

    var radius = 25;
    circleExt = new ol.geom.Circle(center, radius);        
    radius = 15;
    circleInt = new ol.geom.Circle(center, radius);        
    radius = 5;
    var center = map.getView().getCenter();        
    circleCnt = new ol.geom.Circle(center, radius);
    
    vectorSource.addFeature(new ol.Feature(circleExt));
    vectorSource.addFeature(new ol.Feature(circleInt));
    vectorSource.addFeature(new ol.Feature(circleCnt));
    
    var vectorLayer = new ol.layer.Vector({
        source: vectorSource,
        style:  new ol.style.Style({
            fill : new ol.style.Fill({
                color : 'rgba(255, 17, 23 , 0.5)'
            }),
            stroke : new ol.style.Stroke({
                color : '#ff0000',
                width : 2
            })
        })
    });    
    map.addLayer(vectorLayer);
    
}

function AddListeners() {
    document.getElementsByClassName("ap-search-button")[0].addEventListener('Click', function() {SearchAddress(document.getElementById("address"))});
    document.getElementById("address").addEventListener('blur', function() {SearchAddress(this)});
    document.getElementById("address").addEventListener('keyup', function(event) {
                var keycode = (event.keyCode ? event.keyCode : event.which);
                if(keycode == '13' || keycode == '10'){
                   SearchAddress(this); 
                }
    });
    
    map.on("click", function(e) {
        var center = e.coordinate;
        SetCenter(center) 
    });
}

function SetCenter(center) {
    circleExt.setCenter(center);
    circleInt.setCenter(center);
    circleCnt.setCenter(center);
}  

function NavigateTo(lat, lon) {
    map.getView().setCenter(ol.proj.transform([lon, lat], 'EPSG:4326', 'EPSG:900913'));
    SetCenter(map.getView().getCenter());
}       

function SwitchToSuggestion(suggestion) {
    if (LastActive) {
        LastActive.className = "ap-suggestion-item";
    }

    var lat = parseFloat(suggestion.getAttribute("data-lat"));
    var lon = parseFloat(suggestion.getAttribute("data-lon"));
    suggestion.className = "ap-suggestion-item ap-suggestion-item-active";
    NavigateTo(lat, lon);
    LastActive = suggestion;
}

function SearchAddress(source) {
    $.ajax("http://maps.googleapis.com/maps/api/geocode/json?address=" + source.value + ", São Paulo, SP, Brasil", {
            type: "GET",
            success: function (data) {
                console.log(data);
                var suggestions = document.getElementsByClassName("ap-suggestions")[0];
                var divData = "<div class='ap-suggestion-container'>"; 
                
                for (var i = 0; i < data.results.length; i++) {                                        
                    var lat = parseFloat(data.results[i].geometry.location.lat);
                    var lon = parseFloat(data.results[i].geometry.location.lng);

                    divData += "<div class='ap-suggestion-item' onclick='SwitchToSuggestion(this)' data-lat='" + lat + "' data-lon='" + lon + "'>" + data.results[i].formatted_address + "</div>";
                }

                divData += "</div>"; 
                suggestions.innerHTML = divData; 
                if (data.results.length) {
                    SwitchToSuggestion(document.getElementsByClassName("ap-suggestion-item")[0]);
                }
            }
    });
}
