"""
UsedRobot and ImprovedRobot: adapted from RUR-PLE

(c) Andre Roberge
andre.roberge@gmail.com

Python interface for robots.  This will be used to drive create a script
fed to a javascript interpreter.
"""

ROTATE_LEFT = {
    'East': 'North',
    'North': 'West',
    'West': 'South',
    'South': 'East'
}

ROTATE_RIGHT = {
    'East': 'South',
    'South': 'West',
    'West': 'North',
    'North': 'East'
}

MOVE = {
    'East': (1, 0),
    'North': (0, 1),
    'West': (-1, 0),
    'South': (0, -1)
}

class UsedRobot(object):
    '''Simple robot that only knows how to move forward, turn left, pick up and
    put down beepers, and has a limited ability to sense the outside world.
    '''

    def __init__(self, x=0, y=0, direction='East', beepers=0, delay=100,
                 world=None):
        '''creates a robot with starting values'''
        self.x = x
        self.y = y
        self.direction = direction
        self.beepers = beepers
        self.delay = delay
        self.world = world
        self.time = self.world.time
        self.serial_number = self.world.serial_number(self)

    def turn_left(self):
        '''changes direction of robot corresponding to a 90 degree left turn.'''
        self.direction = ROTATE_LEFT[self.direction]
        self.update()

    def front_is_clear(self):
        '''determine, by querying the world, if there is a wall in front
           of the robot.'''
        return self.world.is_wall(self.x, self.y, self.direction)

    def move(self):
        '''moves forward, if no wall is present.'''
        if (self.x == 0) and (self.y == 0):
            self.world.complain("Need to go outside before we can ask to move().")
        elif self.front_is_clear():
            dx, dy = MOVE[self.direction]
            self.x += dx
            self.y += dy
            self.update()
        else:
            self.world.complain("Move not allowed; blocked by wall.")

    def put_beeper(self):
        '''puts a beeper down'''
        if self.beepers > 1:
            self.world.add_beeper(self.x, self.y)
            self.beepers -= 1
            self.update()
        else:
            self.world.complain("Empty beeper bag!")

    def pick_beeper(self):
        '''picks a beeper from the current location, if any is found'''
        if (self.x, self.y) in self.world.beepers:
            self.world.remove_beeper(self.x, self.y)
            self.beepers += 1
            self.update()
        else:
            self.world.complain("No beepers found at this location.")

    def _at_home(self):
        '''returns True if the robot is at home.'''
        return (self.x, self.y) == (0, 0)

    def make_beeper(self):
        '''makes a beeper to add to beeper bag'''
        if self._at_home():
            self.beepers += 1
            self.update()
        else:
            self.world.complain("Can't make beepers away from home.")

    def facing_north(self):
        '''returns True if facing North, False otherwise.'''
        return self.direction == 'North'

    def build_wall_on_left(self):
        '''builds the wall on the left side of the robot'''
        args = self.x, self.y, ROTATE_LEFT[self.direction]
        if self.world.is_wall(args):
            self.world.build_wall(args)
            self.update()
        else:
            self.world.complain("There is already a wall there!")

    def go_outside(self):
        '''go out from inside house'''
        if self._at_home():
            self.x = 1
            self.y = 1
            self.direction = "East"
            self.update()
        else:
            self.world.complain("Not in the house; can not go outside!")

    def enter_home(self):
        '''go inside from location next to the door, facing the door'''
        if (self.x, self.y) == (1, 1):
            if self.direction == "West":
                self.x = 0
                self.y = 0
                self.update()
            else:
                self.world.complain("Can not go in; facing wrong direction.")
        else:
            self.world.complain("Can not go in; not next to the door.")

    def set_delay(self, delay):
        '''sets the time delay between each robot action'''
        self.delay = delay

    def update(self):
        '''updates the current information about this robot'''
        self.time += self.delay
        self.world.record(self.time, self.serial_number, self.x, self.y,
                          self.direction, self.beepers)