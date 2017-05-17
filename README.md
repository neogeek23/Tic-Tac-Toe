# Tic-Tac-Toe

So this is how tic tac toe would work if it was in n-space.  Basically you must claim n+1 continuous spaces in some cross section or throughout the entire n-space.  Being continuous means that the closest next space is no more than 1 location away in each coordinate but is also at least 1 location away in at least 1 coordinate (otherwise it'd be the same point).  

Example winning paths in 4 space:

1d - CS:  (0.1.2.3), (1.1.2.3), (2.1.2.3), (3.1.2.3), (4.1.2.3)

2d - CS:  (0.1.2.3), (0.2.2.2), (0.3.2.1), (0.4.2.0), (0.0.2.4)

3d - CS:  (2.2.2.2), (1.2.1.1), (0.2.0.0), (4.2.4.4), (3.2.3.3)

No CS:    (0.0.0.0), (1.1.1.1), (2.2.2.2), (3.3.3.3), (4.4.4.4)

CS = Cross Section, so a 3d cross section means that in larger space than 3 space only three dimensions can change.  It could be 1,2,4 in 5 space or 2,3,7 in 10 space, it doesn't matter which three just that is three.

This program will produce a Tic-Tac-Toe board for any space/dimension > 1.

You get three tries to input a coordinate before the game asigns you a random unclaimed location.
