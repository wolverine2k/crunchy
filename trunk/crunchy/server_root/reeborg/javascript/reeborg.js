/*
Reeborg's world.
(c) GNU General Public license
*/

function start_page() {
  create_world();
  load('simple');
}

function Stream(lines) {
  this.i = 0;
  this.lines = lines;

  this.pop = function () {
    if (this.i >= this.lines.length) {
      return undefined;
    }
    else {
      line = this.lines[this.i];
      this.i += 1;
      return new CodeLine(line, this.i);
    }
  }

  this.unpop = function() {
    this.i -= 1;
  }
}

function CodeLine(line, line_num) {
  var re = /^( *)(.*)/;
  var matches = re.exec(line);
  this.indent = matches[1];
  this.content = matches[2];
  this.line_num = line_num;
}

function parse_program(program) {

  try {
    var lines = program.split('\n');
    var stream = new Stream(lines);
    var methods = {}

    var block = new CodeBlock(stream, methods, 0);
    return block.statements;
  } catch (e) {
    alert(e);
    throw "program invalid";
  }
}

function CodeBlock(stream, methods, min_indent_spaces) {
  var statements = []
  var desired_indent = undefined;
  builtins = {
    'move()': true,
    'turn_left()': true,
    'turn_right()': true,
    'build_wall_on_left()': true,
  }
  while (1) {
    var code_line = stream.pop();
    if (code_line == undefined) {
      break;
    }
    var indent = code_line.indent;
    var content = code_line.content;
    if (content != '') {
      if (indent.length < min_indent_spaces) {
        stream.unpop();
        break;
      }
      if ((desired_indent != undefined) && (desired_indent != indent)) {
        throw('unexpected indent');
      }
      desired_indent = indent;
      var statement = {}
      if (content.match(/^for\s+/)) {
        var matches = /for\s+[a-z_]+[a-z-0-9]*\s+in\s+range\(\s*(\d+)\s*\)\s*:/.exec(content);
        if (matches) {
          var count = matches[1];
        }
        else {
          throw('Problem parsing instruction at line ' + code_line.line_num + 'statement: ' + content);
        }
        statement.command = 'do';
        statement.count = count;
        statement.block = new CodeBlock(stream, methods, desired_indent.length + 1).statements;
      }
      else if (content.match(/^def/)) {
        var matches = /def\s+(\S+):/.exec(content);
        if (matches) {
          var method_name = matches[1];
        }
        else {
          throw('Problem parsing def instruction');
        }
        var code_block = new CodeBlock(stream, methods, desired_indent.length + 1).statements;
        methods[method_name] = code_block;
      }
      else if (builtins[content]) {
        statement.command = content;
      }
      else {
        if (methods[content]) {
          statement.command = 'method_call';
          statement.block = methods[content];
        }
        else {
          throw('Problem parsing instruction at line ' + code_line.line_num + 'statement: ' + content);
        }
      }
      if (statement.command) {
        statement.line_num = code_line.line_num;
        statements.push(statement);
      }
    }
  }
  this.statements = statements;
}

// EXECUTION CODE

function SimpleCommand(cmd) {
  this.command = cmd['command'];
  function step() {
    result = eval(this.command);
    if (result) {
      throw(result);
    }
    return 1;
  }
  this.line_num = cmd.line_num;
  this.step = step;
}

function DoCommand(cmd) {
  this.cmd = cmd;
  this.iteration = 0;
  this.count = cmd['count'];
  this.block = new Block(cmd['block']);
  this.line_num = cmd.line_num;

  this.step = function () {
    if (this.iteration >= this.count) {
      this.iteration = 0; // reset for next use
      return 1;
    }
    advance = this.block.step();
    if (advance) {
      this.iteration += 1;
    }
    return 0;
  }

}

function MethodCall(cmd) {
  // this seems wasteful to me, but I haven't
  // figured out how to eliminate it
  this.cmd = cmd;
  this.block = new Block(cmd['block']);
  this.line_num = cmd.line_num;

  this.step = function () {
    advance = this.block.step();
    if (advance) {
      return 1;
    }
    return 0;
  }
}

function get_command(cmd) {
  if (cmd['command'] == 'do') {
    return new DoCommand(cmd);
  }
  else if (cmd.command == 'method_call') {
    return new MethodCall(cmd);
  }
  else {
    return new SimpleCommand(cmd);
  }
}


function Block(program) {
  this.program = program;
  this.block = []
  this.i = 0;
  this.last_line_num = undefined;

  for (var i in this.program) {
    this.block[i] = get_command(program[i]);
  }

  function step() {
    if (this.last_line_num) {
      lowlight_line(this.last_line_num);
    }
    if (this.i >= this.program.length) {
      this.i = 0;
      return 1;
    }
    var cmd = this.block[this.i];
    if (cmd.line_num) {
      highlight_line(cmd.line_num);
    }
    advance = cmd.step();
    if (advance) {
      this.last_line_num = cmd.line_num;
      this.i += 1;
    }
    return 0;
  }
  this.step = step;

  this.step_all = function() {
    if (!RUNNING) {
      return;
    }
    done = this.step();
    if (done) {
      alert('done!');
      RUNNING = false;
      reload_img = document.getElementById("reload_image");
      reload_img.setAttribute("src", "images/reload.png");
      run_img = document.getElementById("run_image");
      run_img.setAttribute("src", "images/run.png");
    }
    else {
      delay = 200; // just enough to see
      setTimeout(
        function(thisObj) {
          thisObj.step_all();
        }, delay, this);
    }
  }
}

// ------------------------------


function text_box() {
  return document.forms['the_form'].elements['the_text'];
}

function showMsg(the_message) {
  tb = text_box();
  if (tb) {
    tb.value += the_message + "\n";
  }
}

function clearMsg() {
  tb = text_box();
  if (tb) {
    tb.value = '';
  }
}

function World() {
  this.robot_x = 1;
  this.robot_y = 1;
  this.robot_dir = "E";
  var north_walls = [];
  var east_walls = [];
  this.num_aves = 10;
  this.num_streets = 8;
  this.left = {
    'N': 'W',
    'W': 'S',
    'S': 'E',
    'E': 'N'};
  this.right = {
    'N': 'E',
    'E': 'S',
    'S': 'W',
    'W': 'N'};
  this.robot_char = {
    'N': "images/robot_n.png",
    'E': "images/robot_e.png",
    'S': "images/robot_s.png",
    'W': "images/robot_w.png"
  };
/* right wall */
for (var st = 1; st <= this.num_streets; ++st){
    east_walls[this.num_aves + "," + st] = true;
};
/* top wall */
for (var ave = 1; ave <= this.num_aves; ++ave){
    north_walls[ave + "," + this.num_streets] = true;
};
  function wall_on_north(x, y)
  {
    if (y == 0 || y == this.num_streets) {
      return true;
    }
    coords = x + "," + y;
    return (north_walls[coords] == 1);
  }
  this.wall_on_north = wall_on_north;

  function wall_on_south(x, y)
  {
    return this.wall_on_north(x, y - 1);
  }
  this.wall_on_south = wall_on_south;

  function wall_on_east(x, y)
  {
    if (x == 0 || x == this.num_aves) {
      return true;
    }
    coords = x + "," + y;
    return (east_walls[coords] == 1);
  }
  this.wall_on_east = wall_on_east;

  function wall_on_west(x, y)
  {
    return this.wall_on_east(x - 1, y);
  }
  this.wall_on_west = wall_on_west;

  function is_facing_wall() {
    switch (this.robot_dir) {
      case 'N':
        return this.wall_on_north(this.robot_x, this.robot_y);
      case 'W':
        return this.wall_on_west(this.robot_x, this.robot_y);
      case 'S':
        return this.wall_on_south(this.robot_x, this.robot_y);
      case 'E':
        return this.wall_on_east(this.robot_x, this.robot_y);
    }
  }
  this.is_facing_wall = is_facing_wall;

  this.move = function() {
    if (this.is_facing_wall()) {
      return 'blocked by wall';
    }
    switch (this.robot_dir) {
       case 'N': this.robot_y += 1; break;
       case 'W': this.robot_x -= 1; break;
       case 'S': this.robot_y -= 1; break;
       case 'E': this.robot_x += 1; break;
    }
  }


  function turn_left() {
    this.robot_dir = this.left[this.robot_dir];
  }
  this.turn_left = turn_left;

  function turn_right() {
    this.robot_dir = this.right[this.robot_dir];
  }
  this.turn_right = turn_right;

  function build_east_wall(x, y) {
    if (this.wall_on_east(x, y)) {
      return 'There is already a wall there';
    }
    coords = x + "," + y;
    east_walls[coords] = 1;
  }
  this.build_east_wall = build_east_wall;

  function build_west_wall(x, y) {
    return this.build_east_wall(x-1, y);
  }
  this.build_west_wall = build_west_wall;

  function build_north_wall(x, y) {
    if (this.wall_on_north(x, y)) {
      return 'There is already a wall there';
    }
    coords = x + "," + y;
    north_walls[coords] = 1;
  }
  this.build_north_wall = build_north_wall;

  function build_south_wall(x, y) {
    return this.build_north_wall(x, y-1);
  }
  this.build_south_wall = build_south_wall;

  function build_wall_on_left() {
    x = this.robot_x;
    y = this.robot_y;
    switch (this.robot_dir) {
      case 'N': return this.build_west_wall(x, y);
      case 'S': return this.build_east_wall(x, y);
      case 'E': return this.build_north_wall(x, y);
      case 'W': return this.build_south_wall(x, y);
    }
  }
  this.build_wall_on_left =  build_wall_on_left;

  function robot() {
    return this.robot_char[this.robot_dir];
  }
  this.robot = robot;

  function render(avenue, street)
  {
    var data = '';
    var klass = '';
    var coords = avenue + ',' + street;

    if (north_walls[coords] == 1) {
      klass += ' north';
    }
    else {
      klass += ' no_north';
    }

    if (east_walls[coords] == 1) {
      klass += ' east';
    }
    else {
      klass += ' no_east';
    }

    if (this.robot_x == avenue && this.robot_y == street) {
      data = '<img src="' + this.robot() + '">';
    }

    var text = '<td class="' + klass + '">' + data + '</td>';
    return text;
  }
  this.render = render;
}

the_world = new World();

function start_over() {
  if (RUNNING) {
    alert('program stopped');
    RUNNING = false;
    reload_img = document.getElementById("reload_image");
    reload_img.setAttribute("src", "images/reload.png");
    run_img = document.getElementById("run_image");
    run_img.setAttribute("src", "images/run.png");
  }
  else {
    draw_code('');
    refresh_world();
  }
}

function refresh_world() {
  the_world = new World();
  redraw_grid();
  clearMsg();
}

function set_row(row, text)
{
  try {
    row.innerHTML = text;
  } catch(e) {
    alert("IE not supported by this page!");
    throw("IE does not support innerHTML");
  }
}

function redraw_street(street)
{
  row = document.getElementById("street"+street);

  var text = '<th></th>';
  for (var ave = 1; ave <= the_world.num_aves; ++ave) {
    text += the_world.render(ave, street);
  }
  set_row(row, text);
  row.id = 'street' + street;
}

function create_world() {

  table = document.getElementById("world");
  for (var street = 1; street <= the_world.num_streets; ++street) {
    x = table.insertRow(1);
    x.id = "street"+street;
  }
  redraw_grid();
}

function redraw_grid() {
  for (var street = 1; street <= the_world.num_streets; ++street) {
    redraw_street(street);
  }
}

function redraw_to_bottom(street) {
  for (var i = street; i >= 1; --i) {
    redraw_street(i);
  }
}

function move() {
  old_street = the_world.robot_y;
  problem = the_world.move();
  if (problem) {
    alert(problem);
    return problem;
  }
  showMsg('move');
  new_street = the_world.robot_y;
  redraw_street(old_street);
  redraw_street(new_street);
}

function turn_left() {
  showMsg('turn_left');
  the_world.turn_left();
  street = the_world.robot_y;
  redraw_street(street);
}

function turn_right() {
  showMsg('turn_right');
  the_world.turn_right();
  street = the_world.robot_y;
  redraw_street(street);
}


function build_wall_on_left() {
  problem = the_world.build_wall_on_left()
  if (problem) {
    alert(problem);
    return problem;
  }
  showMsg('build_wall_on_left');
  var street = the_world.robot_y;
  redraw_to_bottom(street); /* browsers are stupid */
}

function run_code() {
  var code = the_program_editor().value;
  draw_code(code);
  var program = parse_program(code);
  var current_block = new Block(program, '');
  RUNNING = true;
  reload_img = document.getElementById("reload_image");
  reload_img.setAttribute("src", "images/stop.png");
  run_img = document.getElementById("run_image");
  run_img.setAttribute("src", "images/rungrey.png");
  refresh_world();
  current_block.step_all();
}

function the_program_editor() {
  return document.getElementById('the_program_editor');
}

function load_code(code) {
  tb = the_program_editor();
  tb.value = code;
  draw_code('');
}

function load(example) {
  var div = document.getElementById(example)
  var code = div.firstChild.nodeValue;
  load_code(code);
}

function highlight_line(line_num) {
  var elem_id = 'line' + line_num
  var elem = document.getElementById(elem_id);
  if (elem) {
    klass = 'highlight';
    elem.setAttribute('className', klass);
    elem.setAttribute('class', klass);
  }
  else {
    alert('unexpected call to highlight_line');
  }
}

function lowlight_line(line_num) {
  var elem_id = 'line' + line_num
  var elem = document.getElementById(elem_id);
  if (elem) {
    klass = 'lowlight';
    elem.setAttribute('className', klass);
    elem.setAttribute('class', klass);
  }
  else {
    alert('unexpected call to lowlight_line');
  }
}

function draw_code(code) {
  var elem = document.getElementById('the_program');
  var lines = code.split('\n');
  var output = '<pre>';
  for (i in lines) {
    var line = lines[i];
    var line_num = parseInt(i) + 1;
    output += '<span id="line'+ (line_num) + '">' + line + '</span><br>';
  }
  output += '</pre>'
  elem.innerHTML = output;
}