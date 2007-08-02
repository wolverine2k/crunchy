function hide_security_info() {
    document.getElementById("security_info").style.display = "none";
    document.getElementById("security_info_x").style.display = "none";
};

function show_security_info() {
    document.getElementById("security_info").style.display = "block";
    document.getElementById("security_info_x").style.display = "block";
}

function allowSite() {
    // parse out the URL from the querystring
    var hostname = window.location.href;
    var queryString = window.location.href.substring((window.location.href.indexOf('?') + 1)).split('&');
    if (queryString[0].substring(0,4) == "url=") {
        hostname = unescape(queryString[0].substring(4));
    }
    if (hostname.substring(0,7) != "http://" && hostname.substring(0,7) != "file://") {
        return;
    }
    var endOfString = (hostname.indexOf("/", 7) == -1) ? hostname.length : hostname.indexOf("/", 7);
    if (hostname[endOfString-1] == "#") endOfString--;
    hostname = hostname.substring(7,endOfString);

    if (confirm("Are you sure you wish to allow potentially dangerous content on this site?")) {
        var j = new XMLHttpRequest();
        j.open("POST", "/update"+session_id+"?level=trusted", false);
        j.send(hostname);
        alert('Setting '+hostname+' to trusted');
    }
}