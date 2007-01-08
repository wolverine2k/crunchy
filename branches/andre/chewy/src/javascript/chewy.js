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
// used with chewy: record changes for individual elements
var changes = '';
function record(id, new_vlam){
document.getElementById('myButton'+id).innerHTML +=' - ok';
changes += id + ';' + new_vlam + ';';
}
// used with chewy: record all the changes done on a given page
function update()
{
if (changes == ''){
alert("No changes have been recorded!");
}
else{
location.href="/update?changed="+changes;
}
}

