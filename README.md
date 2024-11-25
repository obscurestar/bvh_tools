NOTE:  On Mac, apple-quit is the only way to exit python-gl windows.

A set of tools for tinkering with BVH files. 

bvh_copy:
    Generates a BVH format file from skeleton data.

bvh_plot:
    loads a BVH file and displays it in a window. The spacebar toggles between pause and play
    arrow keys orbit around the center of screen
    Currently only supports classic-style BVH.  Rokoko handling coming soon.

bvh_extract:
    A tool subject to change.  Presently takes a bvh file and joint name as inputs.
    Outputs the parent relative and world positions for the joint and resting and 1st
    frame rotations.
