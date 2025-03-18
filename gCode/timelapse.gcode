;===================== date: 20240606 =====================
{if !spiral_mode && print_sequence != "by object"}
; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer

{if layer_z <= (initial_layer_print_height + 0.001)}
  M204 S[default_acceleration]

  G92 E0
  G17
  G2 Z{layer_z + 0.4} I0.86 J0.86 P1 F20000 ; spiral lift a little
  G1 Z{max_layer_z + 0.4}

  G1 X-38.2 Y250 F18000 ; move to safe pos
  M400 P1700
  G1 X-48.2 F3000 ; move to safe pos
  G1 X-38.2 F18000
  M400 P300

  M204 S[initial_layer_acceleration]
{else}
  G92 E0
  G17
  G2 Z{layer_z + 0.4} I0.86 J0.86 P1 F20000 ; spiral lift a little
  G1 Z{max_layer_z + 0.4}

  G1 X-38.2 Y250 F18000 ; move to safe pos
  M400 P1700
  G1 X-48.2 F3000 ; move to safe pos
  G1 X-38.2 F18000
  M400 P300
{endif}
{endif}