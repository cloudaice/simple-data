var w = 1280,
h = 600;


var projection = d3.geo.azimuthalEquidistant()
.scale(900)
.translate([640, 380]);
//.translate([640, 360]);

var path = d3.geo.path()
.projection(projection);

var svg = d3.select("body").append("svg")
.attr("width", w)
.attr("height", h);

var states = svg.append("g")
.attr("id", "states");

var circles = svg.append("g")
.attr("id", "circles");

var cells = svg.append("g")
.attr("id", "cells");

d3.select("input[type=checkbox]").on("change", function() {
    cells.classed("voronoi", this.checked);
});

d3.json("/static/china.json", function(collection) {
    console.debug(collection);
    states.insert("path", ".graticule")
    .datum(topojson.feature(collection, collection.objects.features))
    .attr("d", path);
});

/*
var linksByOrigin = {},
countByAirport = {},
locationByAirport = {},
positions = [];

d3.csv("/static/apiport.csv", function(airports) {

    // Only consider airports with at least one flight.
    airports = airports.filter(function(airport) {
        if (!countByAirport[airport.iata]) {
            var location = [+airport.longitude, +airport.latitude];
            locationByAirport[airport.iata] = location;
            positions.push(projection(location));
            return true;
        }
    });

    // Compute the Voronoi diagram of airports' projected positions.
    var polygons = d3.geom.voronoi(positions);

    var g = cells.selectAll("g")
    .data(airports)
    .enter().append("svg:g");

    g.append("svg:path")
    .attr("class", "cell")
    .attr("d", function(d, i) { return "M" + polygons[i].join("L") + "Z"; })
    .on("mouseover", function(d, i) { d3.select("h2 span").text(d.Airport); });

    g.selectAll("path.arc")
    .data(function(d) { return linksByOrigin[d.iata] || []; })
    .enter().append("svg:path")
    .attr("class", "arc")
    .attr("d", function(d) { return path(arc(d)); });


    circles.selectAll("circle")
    .data(airports)
    .enter().append("svg:circle")
    .attr("cx", function(d, i) { return positions[i][0]; })
    .attr("cy", function(d, i) { return positions[i][1]; })
    .attr("r", 4)
});
*/
