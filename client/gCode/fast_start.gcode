G91
G0 Z5 F600 ; smaller lift of the print head before cleaning
G90
M106 P2 S0
M106 P1 S0
M104 S170
M140 S[bed_temperature]
M190 S[bed_temperature]
M109 S170
G28 ; homing X, Y, Z
G0 Z5 F300 ; smaller lift
G92 E0
G1 Y-2 F1000 ; small movement along the Y axis
G1 Z0.2 F300
G1 X60 E14 F360
G1 X100 F500
G0 Z10 F600
G92 E0
M104 S[nozzle_temperature]
M109 S[nozzle_temperature]
G5