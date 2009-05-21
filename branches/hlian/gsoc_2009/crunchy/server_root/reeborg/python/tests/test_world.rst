world.py tests
===============


    >>> from world import World


First, we create a very simple world (one "cell") and make
sure it is surrounded by walls.

    >>> world = World(1, 1)


Next, we test is_wall()

    >>> for direction in ["East", "North", "West", "South"]:
    ...     if world.is_wall(1, 1, direction) != True:
    ...         print "missing wall in direction", direction

Just to make sure, we do a similar test, with no walls in the specified direction.

    >>> for direction in ["East", "North", "West", "South"]:
    ...     if world.is_wall(3, 3, direction) == True:
    ...         print "missing wall in direction", direction

