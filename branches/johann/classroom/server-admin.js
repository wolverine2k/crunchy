//javascript support code for the classroom server page

//////////////////////////////
//
// IMPORTANT CAVEAT: 
// the XMLRPC stuff in here is nothing like a full or compliant XML-RPC
// implementation, but it works with the Python XMLRPCServer module
// (at least with Python 2.4 :-) and my small server
//
//////////////////////////////

var loginKey = "";
var uname = "";

function getServerString()
{
	e = document.getElementById("server");
	return e.value;
};

function baseXMLRPCRequest(method, login)
{
	RPCRq = document.implementation.createDocument("","methodCall",null);
	rootnode = RPCRq.documentElement;	
	methodName = RPCRq.createElement("methodName");
	methodNameval = RPCRq.createTextNode(method);
	methodName.appendChild(methodNameval);
	rootnode.appendChild(methodName);
	params = RPCRq.createElement("params");
	params.id = "params";
	rootnode.appendChild(params);
	if (login){
		XMLRPCAddStringArg(RPCRq, loginKey);
	};
	return RPCRq;
};

function XMLRPCAddStringArg(RPCRq, val)
{
	params = RPCRq.getElementsByTagName("params")[0];
	param = RPCRq.createElement("param");
	value = RPCRq.createElement("value");
	string_elem = RPCRq.createElement("string");
	login_elem = RPCRq.createTextNode(val);
	string_elem.appendChild(login_elem);
	value.appendChild(string_elem);
	param.appendChild(value);
	params.appendChild(param);
	
};

function sendXMLRPCRequest(RPCRq)
{
	//for now this assumes that the return code is an integer
	//and also that the request succeeds! (thats a #FIXME) 
	h = new XMLHttpRequest();
	h.open("POST", "/", false);
	h.send(RPCRq);
	//alert(h.responseText);
	//look for the outermost value elem, it will be inside the only param elem
	param_elem = h.responseXML.getElementsByTagName("param")[0];
	value_childs = null;
	for(i=0;i<param_elem.childNodes.length;i++)
	{
		//alert(param_elem.childNodes[i].tagName);
		if(param_elem.childNodes[i].tagName == "value")
		{
			value_childs = param_elem.childNodes[i].childNodes;
			break;
		};
	};
	//alert(value_childs.length);
	ret_elem = null;
	ret_type = null;
	// look for an element that could be a return value	
	for(i=0; i<value_childs.length; i++)
	{
		tag = value_childs[i].tagName;
		if(tag == "string")
		{
			//alert(value_childs[i].firstChild.nodeValue + " :: string")
			if(!value_childs[i].firstChild) return "";
			return value_childs[i].firstChild.nodeValue;
		};
		if(tag == "int")
		{
			//alert(value_childs[i].firstChild.nodeValue + " :: int") 
			return parseInt(value_childs[i].firstChild.nodeValue);
		};
		if(tag == "array")
		{
			// assume it's a string array, we will make sure 
			// the server only ever returns string arrays
			
			// first look for the data elem:
			//alert("parsing array");
			data_elem = null;
			for(j=0;j<value_childs[i].childNodes.length;j++)
			{
				if(value_childs[i].childNodes[j].tagName == "data")
				{
					data_elem = value_childs[i].childNodes[j];
					break;
				};
			};
			// assume we found a data elem, now look for the value elems
			// first we need to count them
			
			value_count = 0;
			for(j=0;j<data_elem.childNodes.length; j++)
			{
				if(data_elem.childNodes[j].tagName == "value")
					value_count ++;
			};
			//alert(value_count);
			ret_array = new Array();
			l = 0;
			for(j=0;j<data_elem.childNodes.length; j++)
			{
				if(data_elem.childNodes[j].tagName == "value")
				{
					// look for the string element:
					for(k = 0; k < data_elem.childNodes[j].childNodes.length; k++)
					{
						//alert("looking for a string");
						if(data_elem.childNodes[j].childNodes[k].tagName == "string")
						{
							if(!data_elem.childNodes[j].childNodes[k].firstChild) ret_array[l] = "";
							else ret_array[l] = data_elem.childNodes[j].childNodes[k].firstChild.nodeValue;
							//alert(data_elem.childNodes[j].childNodes[k].firstChild.nodeValue);
							break;
						};
					};
					l ++;
				};
			};
			//alert(ret_array);
			return ret_array;
				
		};
	};
	return null;
};

function doLogin()
{
	loginRQ = baseXMLRPCRequest("login", false);
	uname = document.getElementById("username").value
	XMLRPCAddStringArg(loginRQ, document.getElementById("username").value);
	XMLRPCAddStringArg(loginRQ, document.getElementById("password").value);
	loginKey = sendXMLRPCRequest(loginRQ);
	if(loginKey){
		document.getElementById("loginBox").style.display = "none";
		document.getElementById("logoutBox").style.display = "block";
		document.getElementById("changePasswd").setAttribute("onclick", "change_user_password(uname)");
		document.getElementById("username_display").innerHTML = uname;
		document.getElementById("password").value = "";
		document.getElementById("username").value = "";
		init_common();
		if(sendXMLRPCRequest(baseXMLRPCRequest("is_root", true)))
			init_admin();
		else
			init_user();
	}
	else
	{
		alert("Login failed, but we don't yet know why.\nCould be a bug!\nHere is what the server says:");
		loginKey = "";
	}
	//alert(loginKey);
};

function doAddUser()
{
	pass1 = document.getElementById("add_password1").value;
	pass2 = document.getElementById("add_password2").value;
	if(pass1 != pass2)
	{
		alert("Passwords do not match!");
		document.getElementById("add_password1").value = "";
		document.getElementById("add_password2").value = "";
		return;
	};
	addRQ = baseXMLRPCRequest("add_user_self", false);
	XMLRPCAddStringArg(addRQ, document.getElementById("add_username").value);
	XMLRPCAddStringArg(addRQ, pass1);
	t = sendXMLRPCRequest(addRQ);
	if (t == 1)
	{
		document.getElementById("username").value = document.getElementById("add_username").value;
		document.getElementById("password").value = pass1;
		document.getElementById("add_password1").value = "";
		document.getElementById("add_password2").value = "";
		document.getElementById("add_username").value = "";
		doLogin(); 
	}
	else
	{
		alert("Adding the user failed miserably.");
	};
};

function doLogout()
{
	document.getElementById("loginBox").style.display = "block";
	document.getElementById("logoutBox").style.display = "none";
	loginKey = "";
	uname = "";
	document.getElementById("tabContainer").style.display = "none";
	document.getElementById("rootWarning").style.display = "none";
	hideUserList();
};

function listUsers()
{
	//call the hook function
	show_loading(t_listUsers);
};

function t_listUsers()
//actual loading function
{

	hideUserList();
	document.getElementById("userListContainer").style.display = "block";
	userList = document.createElement("table");
	userList.setAttributeNode(document.createAttribute("id"));
	userList.setAttribute("id", "userList");
	document.getElementById("userListContainer").appendChild(userList);
	list = sendXMLRPCRequest(baseXMLRPCRequest("list_all_users", true));
	if (list==0)
	{
		alert("Could not list all users. You probably don't have admin rights");
		hide_loading()
		return;
	};
	//alert(list);
	for(num=0; num < list.length; num++)
	{
		t = baseXMLRPCRequest("is_root_user", true);
		XMLRPCAddStringArg(t, list[num]);
		is_admin = sendXMLRPCRequest(t);
		
		row = document.createElement("tr");
		//the username
		name_cell = document.createElement("td");
		text = document.createTextNode(list[num]);
		name_cell.appendChild(text);
		name_cell.setAttributeNode(document.createAttribute("class"));
		name_cell.setAttribute("class", "username_disp");
		
		//the password changer
		pass_cell = document.createElement("td");
		pass_button = document.createElement("button");
		pass_button.setAttributeNode(document.createAttribute("onclick"));
		pass_button.setAttribute("onclick", "change_user_password(\""+list[num]+"\")");
		text2 = document.createTextNode("Change password");
		pass_button.appendChild(text2);
		pass_cell.appendChild(pass_button);
		
		// the password viewer
		passview_cell = document.createElement("td");
		passview_button = document.createElement("button");
		text3 = document.createTextNode("View password");
		passview_button.setAttributeNode(document.createAttribute("onclick"));
		passview_button.setAttribute("onclick", "show_user_password(\""+list[num]+"\")");
		passview_button.appendChild(text3);
		passview_cell.appendChild(passview_button);
		
		// the promote button
		promote_cell = document.createElement("td");
		promote_button = document.createElement("button");
		text4 = document.createTextNode("Make admin");
		promote_button.setAttributeNode(document.createAttribute("onclick"));
		promote_button.setAttribute("onclick", "promote_user(\""+list[num]+"\")");
		promote_button.appendChild(text4);
		promote_cell.appendChild(promote_button);
		
		//the checkbox
		check_cell = document.createElement("td");
		check_box = document.createElement("input");
		check_box.setAttributeNode(document.createAttribute("type"));
		check_box.setAttribute("type", "checkbox");
		check_box.setAttributeNode(document.createAttribute("id"));
		check_box.setAttribute("id", "select_"+list[num]);
		check_box.setAttributeNode(document.createAttribute("name"));
		check_box.setAttribute("name", "select_checkbox");
		check_cell.appendChild(check_box);
		
		//the tagger
		tag_cell = document.createElement("td");
		tag_input = document.createElement("input");
		tag_input.setAttributeNode(document.createAttribute("type"));
		tag_input.setAttribute("type", "text");
		tag_input.setAttributeNode(document.createAttribute("id"));
		tag_input.setAttribute("id", "apply_tag_"+list[num]);
		tag_button = document.createElement("button");
		text5 = document.createTextNode("Tag");
		tag_button.setAttributeNode(document.createAttribute("onclick"));
		tag_button.setAttribute("onclick", "tag_user(\""+list[num]+"\")");
		tag_button.appendChild(text5);
		tag_cell.appendChild(tag_input);
		tag_cell.appendChild(tag_button);
		
		// put it all together
		row.appendChild(check_cell);
		row.appendChild(name_cell);
		row.appendChild(tag_cell);
		row.appendChild(passview_cell);
		row.appendChild(pass_cell);
		if(!is_admin) row.appendChild(promote_cell);
		else
			row.appendChild(document.createElement("td"));
		userList.appendChild(row);
	};
	hide_loading();
	
}

function hideUserList()
{
	userList = document.getElementById("userList");
	if(! userList)	//userList doesn't exist
		return;
	document.getElementById("userListContainer").removeChild(userList);
};

function change_user_password(user)
{
	//change the password for the current user
	if(uname == "")
	{
		alert("You must log in before attempting to change a password!");
		return;
	};
	pass1 = prompt("Please enter a new password for user '" + user + "': ");
	if(pass1 == null)
		return;
	pass2 = prompt("Please confirm the new password:");
	if(pass2 == null)
		return;
	if(pass1 != pass2)
	{
		alert("The given passwords do not match.\nThe password was NOT changed.")
		return;
	};
	t = baseXMLRPCRequest("change_password", true);
	XMLRPCAddStringArg(t, user);
	XMLRPCAddStringArg(t, pass1);
	res = sendXMLRPCRequest(t);
	if(res)
		alert("Password succesfully changed.");
	else
		alert("The password could not be changed, probably because of insufficient access rights");		
};

function show_user_password(user)
{
	t = baseXMLRPCRequest("get_user_passwd", true);
	XMLRPCAddStringArg(t, user);
	res = sendXMLRPCRequest(t);
	if(res==0)
	{
		alert("Couldn't show user password.")
		return;
	};
	alert(res);
};

function promote_user(user)
{
	t = baseXMLRPCRequest("promote", true);
	XMLRPCAddStringArg(t, user);
	res = sendXMLRPCRequest(t);
	if(res==0)
	{
		alert("Promotion failed, you probably aren't root");
		return;
	};
	alert("promotion succesful");
	listUsers();
};

function quick_add_user(user)
{
	addRQ = baseXMLRPCRequest("add_user_self", false);
	XMLRPCAddStringArg(addRQ, document.getElementById("quick_add_username").value);
	XMLRPCAddStringArg(addRQ, "");
	t = sendXMLRPCRequest(addRQ);
	if (t == 1)
	{
		document.getElementById("quick_add_username").value = "";
		listUsers();
	}
	else
	{
		alert("Adding the user failed miserably.\nProbably because of a duplicate user name.");
	};
};

function toggle_select_all()
{
	elems = document.getElementsByName("select_checkbox");
	state = document.getElementById("all_select").checked;
	for(i=0;i<elems.length;i++)
	{
		elems[i].checked = state;
	};
};

function show_loading(hook)
//show the loading notice
{
	document.getElementById("loading").style.display = "block";
	setTimeout(hook, 50);
};

function hide_loading()
//hide the loading notice
{
	document.getElementById("loading").style.display = "none";
};

function init_admin()
{
	//perform initialisation for an admin user
	enable_tab("userList");
	switch_tab("userList");
	enable_tab("userLog");
	enable_tab("settings");
	t = baseXMLRPCRequest("get_user_passwd", true);
	XMLRPCAddStringArg(t, "root");
	t_res = sendXMLRPCRequest(t);
	if(t_res == "root")
		document.getElementById("rootWarning").style.display = "block";
	listUsers();
};

function switch_tab(tab_id)
{
	container = document.getElementById("tabBodyContainer");
	// the bodies
	for (t_i=0; t_i < container.childNodes.length; t_i++)
	{
		if(container.childNodes[t_i].nodeType == 1)
		{
			if(container.childNodes[t_i].getAttribute("id") != tab_id + "Container")
				container.childNodes[t_i].style.display = "none";
			else
				container.childNodes[t_i].style.display = "block";
		};
	};
	// the headers:
	container = document.getElementById("tabHeaderContainer");
	for (t_i=0; t_i < container.childNodes.length; t_i++)
	{
		if(container.childNodes[t_i].nodeType == 1)
		{
			if(container.childNodes[t_i].getAttribute("id") != tab_id + "Tab")
			{
				if(container.childNodes[t_i].getAttribute("class") != "tab_header_disabled")
					container.childNodes[t_i].setAttribute("class", "tab_header");
			}
			else
				container.childNodes[t_i].setAttribute("class", "tab_header_selected");
		};
	};
};

function init_common()
{
	document.getElementById("tabContainer").style.display = "block";
};

function init_user()
{
	enable_tab("userLog");
	switch_tab("userLog");
	disable_tab("userList");
	disable_tab("settings");
};

function disable_tab(tab_id)
{
	document.getElementById(tab_id + "Tab").setAttribute("class", "tab_header_disabled");
	document.getElementById(tab_id + "Tab").setAttribute("onclick", "");
};

function enable_tab(tab_id)
{
	document.getElementById(tab_id + "Tab").setAttribute("class", "tab_header");
	document.getElementById(tab_id + "Tab").setAttribute("onclick", "switch_tab(\""+tab_id+"\")");
};

function catch_enter(e, hook)
{
	//if the [enter] key is pressed call hook
	if (e.keyCode == 13)
		hook();
};