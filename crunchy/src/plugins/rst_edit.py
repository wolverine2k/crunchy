'''
rst_edit is a plugin designed to insert an editor for reStructuredText with
instant previewer of corresponding html code.
'''

from src.interface import plugin, SubElement, python_version

def register():
    """registers a tag handler to make an rst widget and a callback for
    taking care of ajaxy stuff.
       """
    # 'doctest' only appears inside <pre> elements, using the notation
    # <pre title='doctest ...'>
    plugin['register_tag_handler']("pre", "title", "rst_edit", rst_edit_setup)
    plugin['register_http_handler']("/rst_edit", rst_edit_callback)

def rst_edit_setup(page, elem, dummy):
    elem.tag = "div"
    elem.text = ''
    textarea = SubElement(elem, "textarea", name="rst_enter", style="width:80%; height:20em;")
    div = SubElement(elem, "div", style="width:80%")
    div.attrib["id"] = "html_preview"
    page.add_js_code(js_code)

def rst_edit_callback(request):
    """Handles all execution of doctests. The request object will contain
    all the data in the AJAX message sent from the browser."""
    if python_version >= 3:
        request.data = request.data.decode('utf-8')
    text = request.data
    print "text = %s" % text
    request.send_response(200)
    request.send_header('Cache-Control', 'no-cache, no-store')
    request.end_headers()
    request.wfile.write(text.encode('utf-8'))


js_code = '''

function send_rst(text){
    var last_char = text.charAt(text.length-1);
    if (last_char == "\\n"){
        var j = new XMLHttpRequest();
        j.open("POST", "/rst_edit", false);
        j.send(text);
        return text;
        }
};

 $(document).ready(function(){
    $("textarea[name='rst_enter']")
      .bind("keyup", function(){ $("#html_preview").html(
                                                    send_rst($(this).val())
                                                       );
                                }
            );
    });

'''
#$("#html_preview").html( $(this).load('/rst_edit'));

'''
function keys(key) {
	if (!key) {
		key = event;
		key.which = key.keyCode;
	}
	if (key.which == 84) {
		toggle();
		return;
	}
	if (s5mode) {
		switch (key.which) {
			case 10: // return
			case 13: // enter
'''