function hide_security_info() {
    document.getElementById("security_info").style.display = "none";
    document.getElementById("security_info_x").style.display = "none";
};

function show_security_info() {
    document.getElementById("security_info").style.display = "block";
    document.getElementById("security_info_x").style.display = "block";
}

function verify_site(attempts_left) {
    trusted_key = prompt("Enter trusted key (from the console window): ");
    if (trusted_key == '' || trusted_key == null) return;

    var j = new XMLHttpRequest();
    j.open("POST", "/set_trusted"+session_id);
    j.onreadystatechange = function() {
	    // check if user entered the correct trusted key
        if (j.readyState == 4 && j.status == 200) {
            if (j.responseText == "Success") {
	            alert('Setting site to trusted');
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
        j.open("POST", "/trust_site"+session_id);
        j.onreadystatechange = function() {
            if (j.readyState == 4 && j.status == 200) {
                verify_site(3);
            }
        }
        j.send(hostname);
    }
}

// site approval functions (move to python)
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
    approved_sites = "";
    for (site_num = 1; site_check = document.getElementById("site_"+site_num); site_num++) {
        if (site_check.checked) {
        approved_sites += site_check.value + ",";
        }
    }
    // send approval
    if (approved_sites != "") {
        // send ajax
        alert("should approve the following:\n" + approved_sites);
        hide_security_info();
    }
    else {
        app_deny_all();
    }
}

function app_deny_all() {
    //send ajax deny
    alert("deny all");
    hide_security_info();
}