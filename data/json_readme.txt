This file documents the json file format created by robroute2json.

IMPORTANT:
----------

  In the robroute file format, the (x,y) are coordinates as on the
  northern hemisphere on earth: North is y -> y+1.

  But in the json format, in order to make it compatible with Karl
  Tarbe's code, North is y -> y-1 (corresponding to the southern
  hemisphere, if you like).


File Format
-----------

The format of the json files is as follows:

[NS,EW,grid,initial,terminal]

NS: north-south size of grid
EW: east-west size of grid

The Grid
--------

grid[y][x] is a string representing a subset of {E,N,W,S}.
  The set corresponds to the set of directions available at the grid
  coordinate.  An empty set signifies a grid position which is not a
  parking slot.  E.g. "EWS" means you can move east, west and south.

Initial and Terminal Positions
------------------------------

initial[y][x] is a string concatenated from the following axioms:

 * r         --- a robot
 * 0,1,2     --- a car of the that type/label
 * r0,r1,r2  --- a car carrying a robot of that type.

 For example, the string "2r" indicates that the position is occupied
 by a car of type 2 and a robot, whereas the string "r2" indicates
 that the position is occupied by a robot carrying a car of type 2.

DOT 05/2016
