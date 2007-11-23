function hide_security_info() {
    document.getElementById("security_info").style.display = "none";
    document.getElementById("security_info_x").style.display = "none";
};

function show_security_info() {
    document.getElementById("security_info").style.display = "block";
    document.getElementById("security_info_x").style.display = "block";
}

function app_approve(nb_item) {
    hide_security_info();
    approved_sites = "";
    if (nb_item == 0){   // used for single site approval from verify_site()
      site_name = "single_site_";
      nb_item = 1;
      }
    else{
      site_name = "site_";
      }
    for (site_num = 1; site_num <= nb_item; site_num++) {
    	site_form = document.getElementById(site_name+site_num);
    	len = site_form.rad.length;
    	for (i = 0; i < len; i++){
    		if (site_form.rad[i].checked){
    		chosen = site_form.rad[i].value;
    		approved_sites += site_form.name + " : " + chosen + ",";
    		}
    	}
    }

    // send approval
    var j = new XMLHttpRequest();
    j.open("POST", "/set_trusted");
    j.onreadystatechange = function() {
        if (j.readyState == 4 && j.status == 200) {
            alert("The following values have been selected:\n\n"+approved_sites.replace(',',"\n"));
        }
    }
    j.send(approved_sites);
}

function app_remove_all() {
    hide_security_info();
    var j = new XMLHttpRequest();
    j.open("POST", "/remove_all");
    j.onreadystatechange = function() {
        if (j.readyState == 4 && j.status == 200) {
            alert("All sites will be removed from list");
        }
    }
    j.send("");
}


function allow_site() {
        app_approve(0);
}


