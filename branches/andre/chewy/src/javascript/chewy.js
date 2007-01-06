function get_http()
// get an xmlhttprequest (or equivalent) object
{
    var h;
    if (typeof(XMLHttpRequest) != "undefined") 
    {
        h = new XMLHttpRequest();
    } 
    else 
    {
        try 
        { 
            h = new ActiveXObject("Msxml2.XMLHTTP"); 
        }
        catch (e) 
        {
            try 
            { 
                h = new ActiveXObject("Microsoft.XMLHTTP"); 
            }
            catch (E) 
            { 
                alert("Your browser is not supported, you need an AJAX capable browser."); 
            }
        }
    }
    return h;
};
var changes = '';
function record(id){
changes += id + ';interpreter to editor;';
}

function update(id)
{
//alert('booh');
//alert(location.href);
location.href="/update?changed="+changes;

}
/*    h = get_http();
    h.onreadystatechange = function()
        {
            if (h.readyState == 4) 
            {			
                try
                {
                    var status = h.status;
                }
                catch(e)
                {
                    var status = "NO HTTP RESPONSE";
                }
                switch (status)
                {
                case 200:
									
                    break;
                case 12029:
                    //IE could not connect to server
                    status = "NO HTTP RESPONSE";
                default:
                    alert(status + ": " + h.responseText);
                }
            }
        };
    h.open("GET", "/update?path=dummy", true);
		h.send('');
};*/