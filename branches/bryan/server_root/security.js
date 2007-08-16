function hide_security_info() {
    document.getElementById("security_info").style.display = "none";
    document.getElementById("security_info_x").style.display = "none";
};

function show_security_info() {
    document.getElementById("security_info").style.display = "block";
    document.getElementById("security_info_x").style.display = "block";
}

// want to move the following code to python so it only displays when needed
function verify_site(attempts_left) {
    trusted_key = prompt("Enter trusted key (from the console window): ");
    if (trusted_key == '' || trusted_key == null) return;

    var j = new XMLHttpRequest();
    j.open("POST", "/enter_key"+session_id);
    j.onreadystatechange = function() {
        // check if user entered the correct trusted key
        if (j.readyState == 4 && j.status == 200) {
            if (j.responseText == "Success") {
                alert("Setting site to trusted\n\nYou must restart Crunchy for these changes to take effect");
                hide_security_info();
            }
            else if (attempts_left > 1) {
                alert("Invalid trusted key. Please try again.");
                verify_site(attempts_left-1);
            }
            else {
                alert("Invalid trusted key. Sorry.");
            }
        }
    }

    j.send(trusted_key);
}

function allow_site() {
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

    if (confirm("Are you sure you wish to allow potentially dangerous content on this site? ("+hostname+")")) {
        var j = new XMLHttpRequest();
        j.open("POST", "/allow_site"+session_id);
        j.onreadystatechange = function() {
            if (j.readyState == 4 && j.status == 200) {
                verify_site(3);
            }
        }
        j.send(hostname);
    }
}

// site approval functions
function app_select_all() {
    for (site_num = 1; site_check = document.getElementById("site_"+site_num); site_num++) {
        site_check.checked = true;
    }
}

function app_select_none() {
    for (site_num = 1; site_check = document.getElementById("site_"+site_num); site_num++) {
        site_check.checked = false;
    }
}

function app_approve() {
    hide_security_info();

    approved_sites = "";
    for (site_num = 1; site_check = document.getElementById("site_"+site_num); site_num++) {
        if (site_check.checked) {
            approved_sites += site_check.value + ",";
        }
    }

    // send approval
    var j = new XMLHttpRequest();
    j.open("POST", "/set_trusted"+session_id);
    j.onreadystatechange = function() {
        if (j.readyState == 4 && j.status == 200) {
            alert("The following site(s) have been set to trusted:\n\n"+approved_sites.replace(',',"\n"));
        }
    }
    j.send(approved_sites);
}

function app_deny_all() {
    hide_security_info();

    var j = new XMLHttpRequest();
    j.open("POST", "/set_trusted"+session_id);
    j.send("");
}