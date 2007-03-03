/**
 * graphics.js
 * Graphics Routines for Crunchy, these are all primitive routines accessed
 * by the Python code running on the server.
 * 
 * Changelog:
 * 6 Feb 07: File Created, imports from the old crunchy graphics
 * 21 Feb 07: A few Fixes added, now it all seems to work
 */
 
// get the context for the given uid:
function get_ctx(uid){
    return document.getElementById("canvas_" + uid).getContext('2d');
}

// initialisation, displays the corresponding graphics element and blanks it
function init_graphics(uid){
    //alert(uid);
    //todo: implement width and height
    document.getElementById("canvas_" + uid).style.display = "block";
    clear_rect(uid, 0, 0, 400, 400);
    //alert(uid);
}

function clear_rect(uid, x, y, width, height){
    get_ctx(uid).clearRect(x, y, width, height);
}

function set_line_colour(uid, colour){
    get_ctx(uid).strokeStyle = colour;
}

function set_fill_colour(uid, colour){
    get_ctx(uid).fillStyle = colour;
}

function draw_line(uid, x1, y1, x2, y2){
    get_ctx(uid).beginPath();
    get_ctx(uid).moveTo(x1, y1);
    get_ctx(uid).lineTo(x2, y2);
    get_ctx(uid).stroke();
}

function circle_stroke(uid, x, y, r){
    get_ctx(uid).beginPath();
    get_ctx(uid).arc(x, y, r, 0, Math.PI*2, true);    //hopefully this works :)
    get_ctx(uid).stroke();
}

function circle_fill(uid, x, y, r){
    get_ctx(uid).beginPath();
    get_ctx(uid).arc(x, y, r, 0, Math.PI*2, true); 
    get_ctx(uid).fill();
}

function rectangle_stroke(uid, x, y, width, height){
    get_ctx(uid).strokeRect(x, y, width, height);
}

function rectangle_fill(uid, x, y, width, height){
    get_ctx(uid).fillRect(x, y, width, height);
}

function triangle_stroke(uid, x1, y1, x2, y2, x3, y3){
    get_ctx(uid).beginPath();
    get_ctx(uid).moveTo(x1, y1);
    get_ctx(uid).lineTo(x2, y2);
    get_ctx(uid).lineTo(x3, y3);
    get_ctx(uid).closePath();
    get_ctx(uid).stroke();
}

function triangle_fill(uid, x1, y1, x2, y2, x3, y3){
    get_ctx(uid).beginPath();
    get_ctx(uid).moveTo(x1, y1);
    get_ctx(uid).lineTo(x2, y2);
    get_ctx(uid).lineTo(x3, y3);
    get_ctx(uid).closePath();
    get_ctx(uid).fill();
}
