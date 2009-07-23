robot.py tests
===============


    >>> from robot import UsedRobot

First, we create a fake world.

    >>> class World(object):
    ...     def __init__(self):
    ...         self.toggle = True
    ...         self.time = 0
    ...         self.count = -1
    ...         self.beepers = {}
    ...
    ...     def is_wall(self, *args):
    ...         return self.toggle
    ...
    ...     def add_beeper(self, x, y):
    ...         if (x, y) in self.beepers:
    ...             self.beepers[(x, y)] += 1
    ...         else:
    ...             self.beepers[(x, y)] = 1
    ...
    ...     def remove_beeper(self, x, y):
    ...         if (x, y) in self.beepers:
    ...             self.beepers[(x, y)] -= 1
    ...             if self.beepers[(x, y)] == 0:
    ...                 del self.beepers[(x, y)]
    ...             return True
    ...         else:
    ...            return False
    ...
    ...     def serial_number(self, *args):
    ...         self.count += 1
    ...         return self.count
    ...
    ...     def complain(self, msg):
    ...         print msg
    ...
    ...     def record(self, *args):
    ...         print "[",
    ...         for arg in args:
    ...             print arg,
    ...         print "]"

    >>> world = World()
    
First, we test robot creation

    >>> robot = UsedRobot(world=world)

Next, testing turn_left()


    >>> robot.turn_left()
    [ 100 0 0 0 North 0 ]
    >>> robot.turn_left()
    [ 200 0 0 0 West 0 ]
    >>> robot.turn_left()
    [ 300 0 0 0 South 0 ]
    >>> robot.turn_left()
    [ 400 0 0 0 East 0 ]

Next, testing go_outside()

    >>> robot.go_outside()
    [ 500 0 1 1 East 0 ]

Let's try again, now that we are outside.
    >>> robot.go_outside()
    Not in the house; can not go outside!

Trying to go back in.
    >>> robot.enter_home()
    Can not go in; facing wrong direction.

Turn around, so we can go back in.
    >>> robot.turn_left() #doctest: +IGNORE_OUTPUT
    >>> robot.turn_left() #doctest: +IGNORE_OUTPUT
    >>> robot.enter_home()
    [ 800 0 0 0 West 0 ]

Turn around again, so we can try to move()

    >>> robot.turn_left() #doctest: +IGNORE_OUTPUT
    >>> robot.turn_left() #doctest: +IGNORE_OUTPUT
    >>> robot.move()
    Need to go outside before we can ask to move().
    >>> robot.go_outside()
    [ 1100 0 1 1 East 0 ]
    >>> robot.move()
    [ 1200 0 2 1 East 0 ]
    >>> world.toggle = False
    >>> robot.move()
    Move not allowed; blocked by wall.
    >>> world.toggle = True

Let's try to put and pick some beepers.

    >>> robot.put_beeper()
    Empty beeper bag!
    >>> robot.pick_beeper()
    No beepers found at this location.

Time to make some beepers.
    >>> robot.make_beeper()
    Can't make beepers away from home.
    >>> robot.turn_left() #doctest: +IGNORE_OUTPUT
    >>> robot.turn_left() #doctest: +IGNORE_OUTPUT
    >>> robot.move() #doctest: +IGNORE_OUTPUT
    >>> robot.enter_home()
    [ 1600 0 0 0 West 0 ]
    >>> robot.make_beeper()
    [ 1700 0 0 0 West 1 ]
    >>> robot.make_beeper()
    [ 1800 0 0 0 West 2 ]
    >>> robot.go_outside()
    [ 1900 0 1 1 East 2 ]
    >>> robot.put_beeper()
    [ 2000 0 1 1 East 1 ]
    >>> robot.pick_beeper()
    [ 2100 0 1 1 East 2 ]
    >>> robot.pick_beeper()
    No beepers found at this location.