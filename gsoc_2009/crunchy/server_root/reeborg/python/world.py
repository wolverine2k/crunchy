'''
The world in which robots can move.
'''


class World(object):
    '''There can only be one world.'''

    def __init__(self, nb_ave, nb_st):
        '''initializes a world object'''
        self.nb_ave = nb_ave # avenues run south to north (identified by x coord.)
        self.nb_st = nb_st   # streets run west to east (identified by y coord.)
        self.restart()

    def restart(self):
        '''re-initialize a given world'''
        self.time = 0
        self.beepers = {}
        self.robots = []
        self.states = {}
        self.west_walls = set([]) # block streets
        self.south_walls = set([]) # block avenues
        self.create_outer_walls()
        self.robot_id = -1

    def add_beeper(self, x, y):
        '''adds a beeper at the specified location'''
        if (x, y) in self.beepers:
            self.beepers[(x, y)] += 1
        else:
            self.beepers[(x, y)] = 1

    def remove_beeper(self, x, y):
        '''remove a beeper from the specified location, if at least one is
        present'''
        if (x, y) in self.beepers:
            self.beepers[(x, y)] -= 1
            if self.beepers[(x, y)] == 0:
                del self.beepers[(x, y)]
            return True
        else:
            return False

    def create_outer_walls(self):
        '''surround the world by walls'''
        for ave in range(1, self.nb_ave+1):
            self.south_walls.add((ave, 1))
            self.south_walls.add((ave, self.nb_st+1))
        for st in range(1, self.nb_st+1):
            self.west_walls.add((1, st))
            self.west_walls.add((self.nb_ave+1, st))

    def serial_number(self, robot):
        '''assigns a serial number for a new robot and records the existence
           of a new robot, and its time of creation.'''
        self.robot_id += 1
        self.robots.append(robot)
        return self.robot_id

    def is_wall(self, ave, st, direction):
        '''determines if a wall is present at a given location, in a
           given direction'''
        if direction == 'South':
            return (ave, st) in self.south_walls
        elif direction == 'West':
            return (ave, st) in self.west_walls
        elif direction == 'East':
            return (ave+1, st) in self.west_walls
        elif direction == 'North':
            return (ave, st+1) in self.south_walls
        else:
            print "Fatal error: unknown direction in is_wall()."
            raise SystemExit

    def record(self, time, serial_number, x, y, direction, beepers):
        '''records the state of a robot at a given time'''
        self.time = time
        if time not in self.states:
            self.states[time] = {}
            self.states[time][serial_number] = (x, y, direction, beepers)
            for robot in self.robots: # add info about other robots
                if robot.serial_number not in self.states[time]:
                    self.states[time][robot.serial_number] = (robot.x, robot.y,
                                                robot.direction, robot.beepers)
        else:
            self.states[time][serial_number] = (x, y, direction, beepers)

    def play_back(self):
        '''plays back all the states, in proper sequence, with time interval
        information'''
        all_times = sorted(list(self.states))
        previous_time = 0
        all_states = []
        for time in all_times:
            time_interval = time - previous_time
            previous_time = time
            current_state = [time_interval]
            for serial_number in self.states[time]:
                current_state.append(self.states[time][serial_number])
            all_states.append(current_state)
        return all_states
