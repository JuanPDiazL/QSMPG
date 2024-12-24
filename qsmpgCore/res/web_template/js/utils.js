"use strict";
const QSMPG_COOKIE_PREFIX = 'QSMPG_';
const DARKMODE_COOKIE_NAME = `${QSMPG_COOKIE_PREFIX}DARKMODE`;
const MENU_HIDE_STATE_COOKIE_NAME = `${QSMPG_COOKIE_PREFIX}MENU_HIDE_STATE`;

const BODY_ELEMENT = document.body;

const HIDE_CLASS = 'w3-hide';

const UNCAT_COLOR = '#aaaf';
const categories = {
    '': { 'Uncategorized': {color:UNCAT_COLOR, 'function': () => true} },
    'C. Dk./LTA Pct.': {
        '0-20': { 'color': '#be6b05', 'function': (x) => x <= 20 },
        '21-40': { 'color': '#f38124', 'function': (x) => x > 20 && x <= 40 },
        '41-60': { 'color': '#fec280', 'function': (x) => x > 40 && x <= 60 },
        '61-80': { 'color': '#ffe69e', 'function': (x) => x > 60 && x <= 80 },
        '81-90': { 'color': '#fff9a3', 'function': (x) => x > 80 && x <= 90 },
        '91-110': { 'color': '#f2f2f2', 'function': (x) => x > 90 && x <= 110 },
        '111-120': { 'color': '#c6eab3', 'function': (x) => x > 110 && x <= 120 },
        '121-140': { 'color': '#56cd94', 'function': (x) => x > 120 && x <= 140 },
        '141-160': { 'color': '#5cc9ea', 'function': (x) => x > 140 && x <= 160 },
        '161+': { 'color': '#2a83ba', 'function': (x) => x > 160 },
        // 'Uncategorized': { 'color': UNCAT_COLOR, 'function': () => true },
    },
    'Ensemble Med./LTA Pct.': {
        '0-20': { 'color': '#be6b05', 'function': (x) => x <= 20 },
        '21-40': { 'color': '#f38124', 'function': (x) => x > 20 && x <= 40 },
        '41-60': { 'color': '#fec280', 'function': (x) => x > 40 && x <= 60 },
        '61-80': { 'color': '#ffe69e', 'function': (x) => x > 60 && x <= 80 },
        '81-90': { 'color': '#fff9a3', 'function': (x) => x > 80 && x <= 90 },
        '91-110': { 'color': '#f2f2f2', 'function': (x) => x > 90 && x <= 110 },
        '111-120': { 'color': '#c6eab3', 'function': (x) => x > 110 && x <= 120 },
        '121-140': { 'color': '#56cd94', 'function': (x) => x > 120 && x <= 140 },
        '141-160': { 'color': '#5cc9ea', 'function': (x) => x > 140 && x <= 160 },
        '161+': { 'color': '#2a83ba', 'function': (x) => x > 160 },
        // 'Uncategorized': { 'color': UNCAT_COLOR, 'function': () => true },
    },
    'Probability Below Normal': {
        '0-15': { 'color': '#2b83ba', 'function': (x) => x >= 0 && x <= 15 },
        '16-30': { 'color': '#74b7ae', 'function': (x) => x >= 15 && x <= 30 },
        '31-45': { 'color': '#e7f6b8', 'function': (x) => x >= 30 && x <= 45 },
        '46-60': { 'color': '#ffe8a4', 'function': (x) => x >= 45 && x <= 60 },
        '61-75': { 'color': '#feba6e', 'function': (x) => x >= 60 && x <= 75 },
        '76-90': { 'color': '#ed6e43', 'function': (x) => x >= 75 && x <= 90 },
        '91-100': { 'color': '#d7191c', 'function': (x) => x >= 90 && x <= 100 },
        // 'Uncategorized': { 'color': UNCAT_COLOR, 'function': () => true },
    },
    'Probability Between Normal': {
        '0-20': { 'color': '#e6e6e6', 'function': (x) => x >= 0 && x <= 20 },
        '21-40': { 'color': '#f0f9e8', 'function': (x) => x > 20 && x <= 40 },
        '41-60': { 'color': '#bae4bc', 'function': (x) => x > 40 && x <= 60 },
        '61-80': { 'color': '#7bccc4', 'function': (x) => x > 60 && x <= 80 },
        '81-90': { 'color': '#43a2ca', 'function': (x) => x > 80 && x <= 90 },
        '91-100': { 'color': '#0868ac', 'function': (x) => x > 90 && x <= 100 },
        // 'Uncategorized': { 'color': UNCAT_COLOR, 'function': () => true },
    },
    'Probability Above Normal': {
        '0-20': { 'color': '#e6e6e6', 'function': (x) => x >= 0 && x <= 20 },
        '21-40': { 'color': '#f0f9e8', 'function': (x) => x > 20 && x <= 40 },
        '41-60': { 'color': '#bae4bc', 'function': (x) => x > 40 && x <= 60 },
        '61-80': { 'color': '#7bccc4', 'function': (x) => x > 60 && x <= 80 },
        '81-90': { 'color': '#43a2ca', 'function': (x) => x > 80 && x <= 90 },
        '91-100': { 'color': '#0868ac', 'function': (x) => x > 90 && x <= 100 },
        // 'Uncategorized': { 'color': UNCAT_COLOR, 'function': () => true },
    },
    'Ensemble Med. Pctl.': {
        '0-3': { 'color': '#7e0006', 'function': (x) => x >= 0 && x <= 3 },
        '4-6': { 'color': '#e20b00', 'function': (x) => x > 3 && x <= 6 },
        '7-11': { 'color': '#e35a1a', 'function': (x) => x > 6 && x <= 11 },
        '12-21': { 'color': '#faaf00', 'function': (x) => x > 11 && x <= 21 },
        '22-33': { 'color': '#faff0f', 'function': (x) => x > 21 && x <= 33 },
        '34-67': { 'color': '#f2f2f2', 'function': (x) => x > 33 && x <= 67 },
        '68-90': { 'color': '#a6cee3', 'function': (x) => x > 67 && x <= 90 },
        '91+': { 'color': '#1f78b4', 'function': (x) => x > 90 },
        // 'Uncategorized': { 'color': UNCAT_COLOR, 'function': () => true },
    },
    'Current Season Pctl.': {
        '0-3': { 'color': '#7e0006', 'function': (x) => x >= 0 && x <= 3 },
        '4-6': { 'color': '#e20b00', 'function': (x) => x > 3 && x <= 6 },
        '7-11': { 'color': '#e35a1a', 'function': (x) => x > 6 && x <= 11 },
        '12-21': { 'color': '#faaf00', 'function': (x) => x > 11 && x <= 21 },
        '22-33': { 'color': '#faff0f', 'function': (x) => x > 21 && x <= 33 },
        '34-67': { 'color': '#f2f2f2', 'function': (x) => x > 33 && x <= 67 },
        '68-90': { 'color': '#a6cee3', 'function': (x) => x > 67 && x <= 90 },
        '91+': { 'color': '#1f78b4', 'function': (x) => x > 90 },
        // 'Uncategorized': { 'color': UNCAT_COLOR, 'function': () => true },
    },
};
  

function navigateTo(queryParams={}, keepOlpParams=true) {
    const oldParams = keepOlpParams? getHashParamsObject() : {};
    const newParams = {...oldParams, ...queryParams };
    const paramsString = new URLSearchParams(newParams).toString();
    window.location.hash = paramsString;
}

function handleNavigation() {
    const params = getHashParamsObject();
    const mode = params['mode'];
    const place = params['place'];
    let mapRoot = $('#mapRoot');
    let plotsRoot = $('#plotsRoot');
    switch (mode) {
        case "map":
            if (isDeclared('topojson_map')) {
                mapRoot.removeClass(HIDE_CLASS);
                plotsRoot.addClass(HIDE_CLASS);
                break;
            }
        case "plots":
            plotsRoot.removeClass(HIDE_CLASS);
            mapRoot.addClass(HIDE_CLASS);
            break;
        case "test":
            mapRoot.removeClass(HIDE_CLASS);
            plotsRoot.removeClass(HIDE_CLASS);
            break;
        default:
            if (isDeclared('topojson_map')) {
                mapRoot.removeClass(HIDE_CLASS);
                plotsRoot.addClass(HIDE_CLASS);
                break;
            } else {
                mapRoot.addClass(HIDE_CLASS);
                plotsRoot.removeClass(HIDE_CLASS);
            }
            break;
    }
    

    let selectedPlace = "";
    if (Object.values(datasetProperties["place_ids"]).includes(place)){
        selectedPlace = place;
    }
    else{
        selectedPlace = firstPlaceKey
    }
    updateDocument(selectedPlace);
    previousSelectionElement = sidebarElements[selectedPlace];
    placeUnder(table4.table, table3.table);
    placeUnder(table6.table, table5.table);
}

function getHashParams(param=null) {
    const hashParams = new URLSearchParams(window.location.hash.substring(1)); // Remove the leading '#'
    if (param) {
        return hashParams.get(param);
     } else {
        return hashParams;
     }
}
function getHashParamsObject() {
    const urlSearchParams = getHashParams();
    return Object.fromEntries(urlSearchParams.entries());
}

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function setCookie(name, value) {
    var date = new Date();
    date.setDate(date.getDate() + 1); // expire in 1 day

    document.cookie = `${name}=${value}; expires=${date.toUTCString()}; SameSite=Strict`;
}

function isDeclared(variableName) {
    return typeof window[variableName] !== "undefined";   
}

function goToMap() {
    navigateTo({"mode": "map"}, false);
}

function setDarkMode(value) {
    setCookie(DARKMODE_COOKIE_NAME, value);
    if (value === "true") {
        document.body.classList.add('darkmode');
    } else {
        document.body.classList.remove('darkmode');
    }
}

function toggleDarkMode() {
    setCookie(DARKMODE_COOKIE_NAME, document.body.classList.toggle('darkmode'));
}


function getLast(arr) {
    return arr[arr.length - 1];
}

function setMenuState(value) {
    setCookie(MENU_HIDE_STATE_COOKIE_NAME, value);
    if (value === "true") {
        BODY_ELEMENT.classList.add('sidebar-closed');
    } else {
        BODY_ELEMENT.classList.remove('sidebar-closed');
    }
}

function menuToggle() {
    setCookie(MENU_HIDE_STATE_COOKIE_NAME, BODY_ELEMENT.classList.toggle('sidebar-closed'));
    window.dispatchEvent(new Event('resize'));
  }

function placeUnder(element, anchor) {
    const bbox = anchor.getBoundingClientRect();
    const xPos = anchor.style.left;
    const yPos = `${bbox.height + 10}px`;

    element.style.left = xPos;
    element.style.top = yPos;
}

function objectMap(obj, fn) {
    return Object.fromEntries(
      Object.entries(obj).map(([key, value], index) => [key, fn(value, key, index)])
    );
}

function decompress(data) {
    const compressedData = atob(data);
    const charData = compressedData.split('').map(function(x){return x.charCodeAt(0);});
    const binData = new Uint8Array(charData);
    const decompressedBin = pako.inflate(binData);
    let decompressedString = '';
    for (let i of decompressedBin) {
        decompressedString += String.fromCharCode(i);
    }
    return decompressedString;
}

function csvParse(csvString, excludeIndex=true) {
    let obj = {};
    d3.csvParse(csvString, (data, i, columns) => {
        const typedData = d3.autoType(data, i, columns);
        const index = typedData[""];
        if(excludeIndex) {
            delete typedData[""];
        }
        obj[index] = typedData;
    })
    return obj;
}

function csvParseRows(csvString, excludeIndex=true) {
    let obj = {};
    d3.csvParseRows(csvString, (data, i) => {
        if (i === 0) {return;} // skip header
        let typedData = d3.autoType(data, i);
        const index = typedData[0];
        if(excludeIndex) {
            typedData = typedData.slice(1)
        } 
        obj[index] = typedData;
    })
    return obj;
}

function parseObjectCsv(obj) {
    return objectMap(obj, csvParse);
}

function parseRowsObjectCsv(obj) {
    return objectMap(JSON.parse(obj), csvParseRows);
}

function searchFunction(){
    // Declare variables
    var input, filter, ul, li, a, i;
    input = document.getElementById("placeSearch");
    filter = input.value.toUpperCase();
    ul = document.getElementById("placeList");
    li = ul.getElementsByTagName("li");

    // Loop through all list items, and hide those who don't match the search query
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("a")[0];
        if (a.innerHTML.toUpperCase().indexOf(filter) > -1) {
            li[i].classList.remove('place-hidden');
        } else {
            li[i].classList.add('place-hidden');
        }
    }
}

function confirmSearch(event) {
    if(event.key === 'Enter') {
        const placeList = document.getElementById("placeList");
        const selectedPlace = placeList.querySelector('.place-list-element:not(.place-hidden)');
        selectedPlace.firstChild.click();
        console.log(selectedPlace, 'clicked');
    }
}

function updateDocument(place) {
    document.getElementById('contentHeaderText').textContent = place;
    const plot2Title = `Current Rainfall Status (${datasetProperties.current_season_id}). Climatology: [${datasetProperties.climatology_year_ids[0]}, ${getLast(datasetProperties.climatology_year_ids)}]`;
    const plot4Title = `Seasonal Rainfall Accumulation Up to Current Dekad for ${place}`;
    bb1.update(place);
    bb2.update(place);
    bb3.update(place);
    bb4.update(place);
    table1.update(getDataAssessmentCD(place));
    table2.update(getDataSeasonalAnalysis(place));
    table3.update(getDataProjectionEoS(place));
    table4.update(getDataProbabilityEoS(place));
    table5.update(getPercentileTable(place));
    table6.update(getCurrentSeasonTable(place));
    document.getElementById('plot2Title').textContent = plot2Title;
    document.getElementById('plot4Title').textContent = plot4Title;

    if(previousSelectionElement != null) {
        previousSelectionElement.classList.remove('selected');
    }
    sidebarElements[place].classList.add('selected');
    $('#contentHeaderText').textContent = place;
}

function makeSelectionMenu(data) {
    const sidebarList = document.getElementById('placeList');
    let sidebarElements = {};
    for (const place of data.toSorted()) {
        const listElement = document.createElement('li');
        listElement.className = 'place-list-element';
        const placeLink = document.createElement('a');
        listElement.appendChild(placeLink);
        sidebarElements[place] = placeLink;
        placeLink.id = place;
        placeLink.className = 'w3-bar-item w3-button w3-ripple';
        placeLink.innerHTML = place;
        placeLink.addEventListener('click', function () {
            navigateTo({"place": place, "mode": "plots"});
        });
        sidebarList.appendChild(listElement);
    }
    return sidebarElements;
}

function updateSelect(node, items) {
    items.forEach(item => {
        const option = document.createElement('option');
        option.value = item;  // You can set a value attribute if needed
        option.text = item;   // Set the text content of the option
        node.appendChild(option);
    });
}

function categorizeValue(value, bins) {
    for (const [binName, binData] of Object.entries(bins)) {
        const binFunction = binData['function'];
        if (binFunction(value)) {
            return binName;
        }
    }
    return 'Uncategorized';
    
}

function getColors(bins) {
    return Object.values(bins).map(bin => bin.color);
}

// Copyright 2021, Observable Inc.
// Released under the ISC license.
// https://observablehq.com/@d3/color-legend
function Legend(color, {
    title,
    tickSize = 6,
    width = 320,
    height = 44 + tickSize,
    marginTop = 18,
    marginRight = 0,
    marginBottom = 16 + tickSize,
    marginLeft = 0,
    ticks = width / 64,
    tickFormat,
    tickValues
} = {}) {

    function ramp(color, n = 256) {
        const canvas = document.createElement("canvas");
        canvas.width = n;
        canvas.height = 1;
        const context = canvas.getContext("2d");
        for (let i = 0; i < n; ++i) {
            context.fillStyle = color(i / (n - 1));
            context.fillRect(i, 0, 1, 1);
        }
        return canvas;
    }

    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .style("overflow", "visible")
        .style("display", "block");

    let tickAdjust = g => g.selectAll(".tick line").attr("y1", marginTop + marginBottom - height);
    let x;

    // Continuous
    if (color.interpolate) {
        const n = Math.min(color.domain().length, color.range().length);

        x = color.copy().rangeRound(d3.quantize(d3.interpolate(marginLeft, width - marginRight), n));

        svg.append("image")
            .attr("x", marginLeft)
            .attr("y", marginTop)
            .attr("width", width - marginLeft - marginRight)
            .attr("height", height - marginTop - marginBottom)
            .attr("preserveAspectRatio", "none")
            .attr("xlink:href", ramp(color.copy().domain(d3.quantize(d3.interpolate(0, 1), n))).toDataURL());
    }

    // Sequential
    else if (color.interpolator) {
        x = Object.assign(color.copy()
            .interpolator(d3.interpolateRound(marginLeft, width - marginRight)),
            { range() { return [marginLeft, width - marginRight]; } });

        svg.append("image")
            .attr("x", marginLeft)
            .attr("y", marginTop)
            .attr("width", width - marginLeft - marginRight)
            .attr("height", height - marginTop - marginBottom)
            .attr("preserveAspectRatio", "none")
            .attr("xlink:href", ramp(color.interpolator()).toDataURL());

        // scaleSequentialQuantile doesn’t implement ticks or tickFormat.
        if (!x.ticks) {
            if (tickValues === undefined) {
                const n = Math.round(ticks + 1);
                tickValues = d3.range(n).map(i => d3.quantile(color.domain(), i / (n - 1)));
            }
            if (typeof tickFormat !== "function") {
                tickFormat = d3.format(tickFormat === undefined ? ",f" : tickFormat);
            }
        }
    }

    // Threshold
    else if (color.invertExtent) {
        const thresholds
            = color.thresholds ? color.thresholds() // scaleQuantize
                : color.quantiles ? color.quantiles() // scaleQuantile
                    : color.domain(); // scaleThreshold

        const thresholdFormat
            = tickFormat === undefined ? d => d
                : typeof tickFormat === "string" ? d3.format(tickFormat)
                    : tickFormat;

        x = d3.scaleLinear()
            .domain([-1, color.range().length - 1])
            .rangeRound([marginLeft, width - marginRight]);

        svg.append("g")
            .selectAll("rect")
            .data(color.range())
            .join("rect")
            .attr("x", (d, i) => x(i - 1))
            .attr("y", marginTop)
            .attr("width", (d, i) => x(i) - x(i - 1))
            .attr("height", height - marginTop - marginBottom)
            .attr("fill", d => d);

        tickValues = d3.range(thresholds.length);
        tickFormat = i => thresholdFormat(thresholds[i], i);
    }

    // Ordinal
    else {
        x = d3.scaleBand()
            .domain(color.domain())
            .rangeRound([marginLeft, width - marginRight]);

        svg.append("g")
            .selectAll("rect")
            .data(color.domain())
            .join("rect")
            .attr("x", x)
            .attr("y", marginTop)
            .attr("width", Math.max(0, x.bandwidth() - 1))
            .attr("height", height - marginTop - marginBottom)
            .attr("fill", color);

        tickAdjust = () => { };
    }

    svg.append("g")
        .attr("transform", `translate(0,${height - marginBottom})`)
        .call(d3.axisBottom(x)
            .ticks(ticks, typeof tickFormat === "string" ? tickFormat : undefined)
            .tickFormat(typeof tickFormat === "function" ? tickFormat : undefined)
            .tickSize(tickSize)
            .tickValues(tickValues))
        .call(tickAdjust)
        .call(g => g.select(".domain").remove())
        .call(g => g.append("text")
            .attr("x", marginLeft)
            .attr("y", marginTop + marginBottom - height - 6)
            .attr("fill", "currentColor")
            .attr("text-anchor", "start")
            .attr("font-weight", "bold")
            .attr("class", "title")
            .text(title));

    return svg.node();
}
