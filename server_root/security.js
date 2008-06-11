function hide_security_info() {
    //use jQuery
    $("#security_info,#security_info_x").hide();
};

function show_security_info() {
    //use jQuery
    $("#security_info,#security_info_x").hide();
}

function hide_security_report() {
    $("#security_report").hide();
};

function app_approve(nb_item) {
    hide_security_info();
    var approved_sites = "";
    var site_name = "";
    if (nb_item == 0){   // used for single site approval from verify_site()
      site_name = "single_site_";
      nb_item = 1;
      }
    else{
      site_name = "site_";
      }
    var chosen;
    for (var site_num = 1; site_num <= nb_item; site_num++) {
    	var site_form = document.getElementById(site_name+site_num);
    	len = site_form.rad.length;
    	for (i = 0; i < len; i++){
    		if (site_form.rad[i].checked){
    		chosen = site_form.rad[i].value;
    		approved_sites += site_form.name + " :: " + chosen + ",";
    		}
    	}
    }

    //send approval
    $.ajax({type : "POST",
            url : "/set_trusted", 
            data : approved_sites,
            processData : false
            });
}

function app_remove_all() {
    hide_security_info();
    //send approval
    $.ajax({type : "POST",
            url : "/remove_all", 
            data : approved_sites,
            processData : false
            });
}


function allow_site() {
        app_approve(0);
}
