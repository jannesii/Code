; HEADER_BLOCK_START
; BambuStudio 02.00.03.54
; model printing time: 4m 29s; total estimated time: 10m 47s
; total layer number: 26
; total filament length [mm] : 180.81
; total filament volume [cm^3] : 434.90
; total filament weight [g] : 0.54
; filament_density: 1.24
; filament_diameter: 1.75
; max_z_height: 5.20
; HEADER_BLOCK_END

; CONFIG_BLOCK_START
; accel_to_decel_enable = 0
; accel_to_decel_factor = 50%
; activate_air_filtration = 0
; additional_cooling_fan_speed = 70
; apply_scarf_seam_on_circles = 1
; auxiliary_fan = 0
; bed_custom_model = 
; bed_custom_texture = 
; bed_exclude_area = 
; bed_temperature_formula = by_first_filament
; before_layer_change_gcode = 
; best_object_pos = 0.5,0.5
; bottom_color_penetration_layers = 3
; bottom_shell_layers = 3
; bottom_shell_thickness = 0
; bottom_surface_pattern = monotonic
; bridge_angle = 0
; bridge_flow = 1
; bridge_no_support = 0
; bridge_speed = 50
; brim_object_gap = 0.1
; brim_type = auto_brim
; brim_width = 5
; chamber_temperatures = 0
; change_filament_gcode = ;===== A1 20250206 =======================\nM1007 S0 ; turn off mass estimation\nG392 S0\nM620 S[next_extruder]A\nM204 S9000\nG1 Z{max_layer_z + 3.0} F1200\n\nM400\nM106 P1 S0\nM106 P2 S0\n{if old_filament_temp > 142 && next_extruder < 255}\nM104 S[old_filament_temp]\n{endif}\n\nG1 X267 F18000\n\n{if long_retractions_when_cut[previous_extruder]}\nM620.11 S1 I[previous_extruder] E-{retraction_distances_when_cut[previous_extruder]} F1200\n{else}\nM620.11 S0\n{endif}\nM400\n\nM620.1 E F[old_filament_e_feedrate] T{nozzle_temperature_range_high[previous_extruder]}\nM620.10 A0 F[old_filament_e_feedrate]\nT[next_extruder]\nM620.1 E F[new_filament_e_feedrate] T{nozzle_temperature_range_high[next_extruder]}\nM620.10 A1 F[new_filament_e_feedrate] L[flush_length] H[nozzle_diameter] T[nozzle_temperature_range_high]\n\nG1 Y128 F9000\n\n{if next_extruder < 255}\n\n{if long_retractions_when_cut[previous_extruder]}\nM620.11 S1 I[previous_extruder] E{retraction_distances_when_cut[previous_extruder]} F{old_filament_e_feedrate}\nM628 S1\nG92 E0\nG1 E{retraction_distances_when_cut[previous_extruder]} F[old_filament_e_feedrate]\nM400\nM629 S1\n{else}\nM620.11 S0\n{endif}\n\nM400\nG92 E0\nM628 S0\n\n{if flush_length_1 > 1}\n; FLUSH_START\n; always use highest temperature to flush\nM400\nM1002 set_filament_type:UNKNOWN\nM109 S[nozzle_temperature_range_high]\nM106 P1 S60\n{if flush_length_1 > 23.7}\nG1 E23.7 F{old_filament_e_feedrate} ; do not need pulsatile flushing for start part\nG1 E{(flush_length_1 - 23.7) * 0.02} F50\nG1 E{(flush_length_1 - 23.7) * 0.23} F{old_filament_e_feedrate}\nG1 E{(flush_length_1 - 23.7) * 0.02} F50\nG1 E{(flush_length_1 - 23.7) * 0.23} F{new_filament_e_feedrate}\nG1 E{(flush_length_1 - 23.7) * 0.02} F50\nG1 E{(flush_length_1 - 23.7) * 0.23} F{new_filament_e_feedrate}\nG1 E{(flush_length_1 - 23.7) * 0.02} F50\nG1 E{(flush_length_1 - 23.7) * 0.23} F{new_filament_e_feedrate}\n{else}\nG1 E{flush_length_1} F{old_filament_e_feedrate}\n{endif}\n; FLUSH_END\nG1 E-[old_retract_length_toolchange] F1800\nG1 E[old_retract_length_toolchange] F300\nM400\nM1002 set_filament_type:{filament_type[next_extruder]}\n{endif}\n\n{if flush_length_1 > 45 && flush_length_2 > 1}\n; WIPE\nM400\nM106 P1 S178\nM400 S3\nG1 X-38.2 F18000\nG1 X-48.2 F3000\nG1 X-38.2 F18000\nG1 X-48.2 F3000\nG1 X-38.2 F18000\nG1 X-48.2 F3000\nM400\nM106 P1 S0\n{endif}\n\n{if flush_length_2 > 1}\nM106 P1 S60\n; FLUSH_START\nG1 E{flush_length_2 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_2 * 0.02} F50\nG1 E{flush_length_2 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_2 * 0.02} F50\nG1 E{flush_length_2 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_2 * 0.02} F50\nG1 E{flush_length_2 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_2 * 0.02} F50\nG1 E{flush_length_2 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_2 * 0.02} F50\n; FLUSH_END\nG1 E-[new_retract_length_toolchange] F1800\nG1 E[new_retract_length_toolchange] F300\n{endif}\n\n{if flush_length_2 > 45 && flush_length_3 > 1}\n; WIPE\nM400\nM106 P1 S178\nM400 S3\nG1 X-38.2 F18000\nG1 X-48.2 F3000\nG1 X-38.2 F18000\nG1 X-48.2 F3000\nG1 X-38.2 F18000\nG1 X-48.2 F3000\nM400\nM106 P1 S0\n{endif}\n\n{if flush_length_3 > 1}\nM106 P1 S60\n; FLUSH_START\nG1 E{flush_length_3 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_3 * 0.02} F50\nG1 E{flush_length_3 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_3 * 0.02} F50\nG1 E{flush_length_3 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_3 * 0.02} F50\nG1 E{flush_length_3 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_3 * 0.02} F50\nG1 E{flush_length_3 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_3 * 0.02} F50\n; FLUSH_END\nG1 E-[new_retract_length_toolchange] F1800\nG1 E[new_retract_length_toolchange] F300\n{endif}\n\n{if flush_length_3 > 45 && flush_length_4 > 1}\n; WIPE\nM400\nM106 P1 S178\nM400 S3\nG1 X-38.2 F18000\nG1 X-48.2 F3000\nG1 X-38.2 F18000\nG1 X-48.2 F3000\nG1 X-38.2 F18000\nG1 X-48.2 F3000\nM400\nM106 P1 S0\n{endif}\n\n{if flush_length_4 > 1}\nM106 P1 S60\n; FLUSH_START\nG1 E{flush_length_4 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_4 * 0.02} F50\nG1 E{flush_length_4 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_4 * 0.02} F50\nG1 E{flush_length_4 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_4 * 0.02} F50\nG1 E{flush_length_4 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_4 * 0.02} F50\nG1 E{flush_length_4 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_4 * 0.02} F50\n; FLUSH_END\n{endif}\n\nM629\n\nM400\nM106 P1 S60\nM109 S[new_filament_temp]\nG1 E6 F{new_filament_e_feedrate} ;Compensate for filament spillage during waiting temperature\nM400\nG92 E0\nG1 E-[new_retract_length_toolchange] F1800\nM400\nM106 P1 S178\nM400 S3\nG1 X-38.2 F18000\nG1 X-48.2 F3000\nG1 X-38.2 F18000\nG1 X-48.2 F3000\nG1 X-38.2 F18000\nG1 X-48.2 F3000\nG1 X-38.2 F18000\nG1 X-48.2 F3000\nM400\nG1 Z{max_layer_z + 3.0} F3000\nM106 P1 S0\n{if layer_z <= (initial_layer_print_height + 0.001)}\nM204 S[initial_layer_acceleration]\n{else}\nM204 S[default_acceleration]\n{endif}\n{else}\nG1 X[x_after_toolchange] Y[y_after_toolchange] Z[z_after_toolchange] F12000\n{endif}\n\nM622.1 S0\nM9833 F{outer_wall_volumetric_speed/2.4} A0.3 ; cali dynamic extrusion compensation\nM1002 judge_flag filament_need_cali_flag\nM622 J1\n  G92 E0\n  G1 E-[new_retract_length_toolchange] F1800\n  M400\n  \n  M106 P1 S178\n  M400 S4\n  G1 X-38.2 F18000\n  G1 X-48.2 F3000\n  G1 X-38.2 F18000 ;wipe and shake\n  G1 X-48.2 F3000\n  G1 X-38.2 F12000 ;wipe and shake\n  G1 X-48.2 F3000\n  M400\n  M106 P1 S0 \nM623\n\nM621 S[next_extruder]A\nG392 S0\n\nM1007 S1\n
; circle_compensation_manual_offset = 0
; circle_compensation_speed = 200
; close_fan_the_first_x_layers = 1
; complete_print_exhaust_fan_speed = 70
; cool_plate_temp = 35
; cool_plate_temp_initial_layer = 35
; counter_coef_1 = 0
; counter_coef_2 = 0.025
; counter_coef_3 = -0.11
; counter_limit_max = 0.05
; counter_limit_min = -0.04
; curr_bed_type = Supertack Plate
; default_acceleration = 6000
; default_filament_colour = ""
; default_filament_profile = "Bambu PLA Basic @BBL A1"
; default_jerk = 0
; default_nozzle_volume_type = Standard
; default_print_profile = 0.20mm Standard @BBL A1
; deretraction_speed = 30
; detect_floating_vertical_shell = 1
; detect_narrow_internal_solid_infill = 1
; detect_overhang_wall = 1
; detect_thin_wall = 0
; diameter_limit = 50
; different_settings_to_system = enable_support;prime_tower_infill_gap;prime_tower_rib_wall;sparse_infill_density;;
; draft_shield = disabled
; during_print_exhaust_fan_speed = 70
; elefant_foot_compensation = 0.075
; enable_arc_fitting = 1
; enable_circle_compensation = 0
; enable_long_retraction_when_cut = 2
; enable_overhang_bridge_fan = 1
; enable_overhang_speed = 1
; enable_pre_heating = 0
; enable_pressure_advance = 0
; enable_prime_tower = 0
; enable_support = 1
; enforce_support_layers = 0
; eng_plate_temp = 0
; eng_plate_temp_initial_layer = 0
; ensure_vertical_shell_thickness = enabled
; exclude_object = 1
; extruder_ams_count = 1#0|4#0;1#0|4#0
; extruder_clearance_dist_to_rod = 56.5
; extruder_clearance_height_to_lid = 256
; extruder_clearance_height_to_rod = 25
; extruder_clearance_max_radius = 73
; extruder_colour = #018001
; extruder_offset = 0x0
; extruder_printable_area = 
; extruder_type = Direct Drive
; extruder_variant_list = "Direct Drive Standard"
; fan_cooling_layer_time = 80
; fan_max_speed = 80
; fan_min_speed = 60
; filament_adhesiveness_category = 0
; filament_change_length = 10
; filament_colour = #FFFFFF
; filament_cost = 24.95
; filament_density = 1.24
; filament_diameter = 1.75
; filament_end_gcode = "; filament end gcode \nM106 P3 S0\n"
; filament_extruder_variant = "Direct Drive Standard"
; filament_flow_ratio = 0.98
; filament_ids = P157143e
; filament_is_support = 0
; filament_map = 1
; filament_map_mode = Auto For Flush
; filament_max_volumetric_speed = 12
; filament_minimal_purge_on_wipe_tower = 15
; filament_notes = 
; filament_prime_volume = 45
; filament_scarf_gap = 0
; filament_scarf_height = 0%
; filament_scarf_length = 10
; filament_scarf_seam_type = none
; filament_self_index = 1
; filament_settings_id = "Clas Ohlson PLA Basic @Bambu Lab A1 0.4 nozzle"
; filament_shrink = 100%
; filament_soluble = 0
; filament_start_gcode = "; filament start gcode\n{if  (bed_temperature[current_extruder] >45)||(bed_temperature_initial_layer[current_extruder] >45)}M106 P3 S255\n{elsif(bed_temperature[current_extruder] >35)||(bed_temperature_initial_layer[current_extruder] >35)}M106 P3 S180\n{endif};Prevent PLA from jamming\n\n\n{if activate_air_filtration[current_extruder] && support_air_filtration}\nM106 P3 S{during_print_exhaust_fan_speed_num[current_extruder]} \n{endif}"
; filament_type = PLA
; filament_vendor = "Clas Ohlson"
; filename_format = {input_filename_base}_{filament_type[0]}_{print_time}.gcode
; filter_out_gap_fill = 0
; first_layer_print_sequence = 0
; flush_into_infill = 0
; flush_into_objects = 0
; flush_into_support = 1
; flush_multiplier = 1
; flush_volumes_matrix = 0
; flush_volumes_vector = 140,140
; full_fan_speed_layer = 0
; fuzzy_skin = none
; fuzzy_skin_point_distance = 0.8
; fuzzy_skin_thickness = 0.3
; gap_infill_speed = 250
; gcode_add_line_number = 0
; gcode_flavor = marlin
; grab_length = 17.4
; has_scarf_joint_seam = 1
; head_wrap_detect_zone = 226x224,256x224,256x256,226x256
; hole_coef_1 = 0
; hole_coef_2 = -0.025
; hole_coef_3 = 0.28
; hole_limit_max = 0.25
; hole_limit_min = 0.08
; host_type = octoprint
; hot_plate_temp = 65
; hot_plate_temp_initial_layer = 65
; hotend_cooling_rate = 2
; hotend_heating_rate = 2
; impact_strength_z = 0
; independent_support_layer_height = 1
; infill_combination = 0
; infill_direction = 45
; infill_jerk = 9
; infill_rotate_step = 0
; infill_shift_step = 0.4
; infill_wall_overlap = 15%
; initial_layer_acceleration = 500
; initial_layer_flow_ratio = 1
; initial_layer_infill_speed = 105
; initial_layer_jerk = 9
; initial_layer_line_width = 0.5
; initial_layer_print_height = 0.2
; initial_layer_speed = 50
; initial_layer_travel_acceleration = 6000
; inner_wall_acceleration = 0
; inner_wall_jerk = 9
; inner_wall_line_width = 0.45
; inner_wall_speed = 300
; interface_shells = 0
; interlocking_beam = 0
; interlocking_beam_layer_count = 2
; interlocking_beam_width = 0.8
; interlocking_boundary_avoidance = 2
; interlocking_depth = 2
; interlocking_orientation = 22.5
; internal_bridge_support_thickness = 0.8
; internal_solid_infill_line_width = 0.42
; internal_solid_infill_pattern = zig-zag
; internal_solid_infill_speed = 250
; ironing_direction = 45
; ironing_flow = 10%
; ironing_inset = 0.21
; ironing_pattern = zig-zag
; ironing_spacing = 0.15
; ironing_speed = 30
; ironing_type = no ironing
; is_infill_first = 0
; layer_change_gcode = ; layer num/total_layer_count: {layer_num+1}/[total_layer_count]\n; update layer progress\nM73 L{layer_num+1}\nM991 S0 P{layer_num} ;notify layer change
; layer_height = 0.2
; line_width = 0.42
; long_retractions_when_cut = 0
; machine_end_gcode = ;===== date: 20231229 =====================\nG392 S0 ;turn off nozzle clog detect\n\nM400 ; wait for buffer to clear\nG92 E0 ; zero the extruder\nG1 E-0.8 F1800 ; retract\nG1 Z{max_layer_z + 0.5} F900 ; lower z a little\nG1 X0 Y{first_layer_center_no_wipe_tower[1]} F18000 ; move to safe pos\nG1 X-13.0 F3000 ; move to safe pos\n{if !spiral_mode && print_sequence != "by object"}\nM1002 judge_flag timelapse_record_flag\nM622 J1\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM400 P100\nM971 S11 C11 O0\nM991 S0 P-1 ;end timelapse at safe pos\nM623\n{endif}\n\nM140 S0 ; turn off bed\nM106 S0 ; turn off fan\nM106 P2 S0 ; turn off remote part cooling fan\nM106 P3 S0 ; turn off chamber cooling fan\n\n;G1 X27 F15000 ; wipe\n\n; pull back filament to AMS\nM620 S255\nG1 X267 F15000\nT255\nG1 X-28.5 F18000\nG1 X-48.2 F3000\nG1 X-28.5 F18000\nG1 X-48.2 F3000\nM621 S255\n\nM104 S0 ; turn off hotend\n\nM400 ; wait all motion done\nM17 S\nM17 Z0.4 ; lower z motor current to reduce impact if there is something in the bottom\n{if (max_layer_z + 100.0) < 256}\n    G1 Z{max_layer_z + 100.0} F600\n    G1 Z{max_layer_z +98.0}\n{else}\n    G1 Z256 F600\n    G1 Z256\n{endif}\nM400 P100\nM17 R ; restore z current\n\nG90\nG1 X-48 Y180 F3600\n\nM220 S100  ; Reset feedrate magnitude\nM201.2 K1.0 ; Reset acc magnitude\nM73.2   R1.0 ;Reset left time magnitude\nM1002 set_gcode_claim_speed_level : 0\n\n;=====printer finish  sound=========\nM17\nM400 S1\nM1006 S1\nM1006 A0 B20 L100 C37 D20 M40 E42 F20 N60\nM1006 A0 B10 L100 C44 D10 M60 E44 F10 N60\nM1006 A0 B10 L100 C46 D10 M80 E46 F10 N80\nM1006 A44 B20 L100 C39 D20 M60 E48 F20 N60\nM1006 A0 B10 L100 C44 D10 M60 E44 F10 N60\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N60\nM1006 A0 B10 L100 C39 D10 M60 E39 F10 N60\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N60\nM1006 A0 B10 L100 C44 D10 M60 E44 F10 N60\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N60\nM1006 A0 B10 L100 C39 D10 M60 E39 F10 N60\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N60\nM1006 A0 B10 L100 C48 D10 M60 E44 F10 N80\nM1006 A0 B10 L100 C0 D10 M60 E0 F10  N80\nM1006 A44 B20 L100 C49 D20 M80 E41 F20 N80\nM1006 A0 B20 L100 C0 D20 M60 E0 F20 N80\nM1006 A0 B20 L100 C37 D20 M30 E37 F20 N60\nM1006 W\n;=====printer finish  sound=========\n\n;M17 X0.8 Y0.8 Z0.5 ; lower motor current to 45% power\nM400\nM18 X Y Z\n\n
; machine_load_filament_time = 25
; machine_max_acceleration_e = 5000,5000
; machine_max_acceleration_extruding = 12000,12000
; machine_max_acceleration_retracting = 5000,5000
; machine_max_acceleration_travel = 9000,9000
; machine_max_acceleration_x = 12000,12000
; machine_max_acceleration_y = 12000,12000
; machine_max_acceleration_z = 1500,1500
; machine_max_jerk_e = 3,3
; machine_max_jerk_x = 9,9
; machine_max_jerk_y = 9,9
; machine_max_jerk_z = 3,3
; machine_max_speed_e = 30,30
; machine_max_speed_x = 500,200
; machine_max_speed_y = 500,200
; machine_max_speed_z = 30,30
; machine_min_extruding_rate = 0,0
; machine_min_travel_rate = 0,0
; machine_pause_gcode = M400 U1
; machine_start_gcode = ;===== machine: A1 =========================\n;===== date: 20240620 =====================\nG392 S0\nM9833.2\n;M400\n;M73 P1.717\n\n;===== start to heat heatbead&hotend==========\nM1002 gcode_claim_action : 2\nM1002 set_filament_type:{filament_type[initial_no_support_extruder]}\nM104 S140\nM140 S[bed_temperature_initial_layer_single]\n\n;=====start printer sound ===================\nM17\nM400 S1\nM1006 S1\nM1006 A0 B10 L100 C37 D10 M60 E37 F10 N60\nM1006 A0 B10 L100 C41 D10 M60 E41 F10 N60\nM1006 A0 B10 L100 C44 D10 M60 E44 F10 N60\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N60\nM1006 A43 B10 L100 C46 D10 M70 E39 F10 N80\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N80\nM1006 A0 B10 L100 C43 D10 M60 E39 F10 N80\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N80\nM1006 A0 B10 L100 C41 D10 M80 E41 F10 N80\nM1006 A0 B10 L100 C44 D10 M80 E44 F10 N80\nM1006 A0 B10 L100 C49 D10 M80 E49 F10 N80\nM1006 A0 B10 L100 C0 D10 M80 E0 F10 N80\nM1006 A44 B10 L100 C48 D10 M60 E39 F10 N80\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N80\nM1006 A0 B10 L100 C44 D10 M80 E39 F10 N80\nM1006 A0 B10 L100 C0 D10 M60 E0 F10 N80\nM1006 A43 B10 L100 C46 D10 M60 E39 F10 N80\nM1006 W\nM18 \n;=====start printer sound ===================\n\n;=====avoid end stop =================\nG91\nG380 S2 Z40 F1200\nG380 S3 Z-15 F1200\nG90\n\n;===== reset machine status =================\n;M290 X39 Y39 Z8\nM204 S6000\n\nM630 S0 P0\nG91\nM17 Z0.3 ; lower the z-motor current\n\nG90\nM17 X0.65 Y1.2 Z0.6 ; reset motor current to default\nM960 S5 P1 ; turn on logo lamp\nG90\nM220 S100 ;Reset Feedrate\nM221 S100 ;Reset Flowrate\nM73.2   R1.0 ;Reset left time magnitude\n;M211 X0 Y0 Z0 ; turn off soft endstop to prevent protential logic problem\n\n;====== cog noise reduction=================\nM982.2 S1 ; turn on cog noise reduction\n\nM1002 gcode_claim_action : 13\n\nG28 X\nG91\nG1 Z5 F1200\nG90\nG0 X128 F30000\nG0 Y254 F3000\nG91\nG1 Z-5 F1200\n\nM109 S25 H140\n\nM17 E0.3\nM83\nG1 E10 F1200\nG1 E-0.5 F30\nM17 D\n\nG28 Z P0 T140; home z with low precision,permit 300deg temperature\nM104 S{nozzle_temperature_initial_layer[initial_extruder]}\n\nM1002 judge_flag build_plate_detect_flag\nM622 S1\n  G39.4\n  G90\n  G1 Z5 F1200\nM623\n\n;M400\n;M73 P1.717\n\n;===== prepare print temperature and material ==========\nM1002 gcode_claim_action : 24\n\nM400\n;G392 S1\nM211 X0 Y0 Z0 ;turn off soft endstop\nM975 S1 ; turn on\n\nG90\nG1 X-28.5 F30000\nG1 X-48.2 F3000\n\nM620 M ;enable remap\nM620 S[initial_no_support_extruder]A   ; switch material if AMS exist\n    M1002 gcode_claim_action : 4\n    M400\n    M1002 set_filament_type:UNKNOWN\n    M109 S[nozzle_temperature_initial_layer]\n    M104 S250\n    M400\n    T[initial_no_support_extruder]\n    G1 X-48.2 F3000\n    M400\n\n    M620.1 E F{filament_max_volumetric_speed[initial_no_support_extruder]/2.4053*60} T{nozzle_temperature_range_high[initial_no_support_extruder]}\n    M109 S250 ;set nozzle to common flush temp\n    M106 P1 S0\n    G92 E0\n    G1 E50 F200\n    M400\n    M1002 set_filament_type:{filament_type[initial_no_support_extruder]}\nM621 S[initial_no_support_extruder]A\n\nM109 S{nozzle_temperature_range_high[initial_no_support_extruder]} H300\nG92 E0\nG1 E50 F200 ; lower extrusion speed to avoid clog\nM400\nM106 P1 S178\nG92 E0\nG1 E5 F200\nM104 S{nozzle_temperature_initial_layer[initial_no_support_extruder]}\nG92 E0\nG1 E-0.5 F300\n\nG1 X-28.5 F30000\nG1 X-48.2 F3000\nG1 X-28.5 F30000 ;wipe and shake\nG1 X-48.2 F3000\nG1 X-28.5 F30000 ;wipe and shake\nG1 X-48.2 F3000\n\n;G392 S0\n\nM400\nM106 P1 S0\n;===== prepare print temperature and material end =====\n\n;M400\n;M73 P1.717\n\n;===== auto extrude cali start =========================\nM975 S1\n;G392 S1\n\nG90\nM83\nT1000\nG1 X-48.2 Y0 Z10 F10000\nM400\nM1002 set_filament_type:UNKNOWN\n\nM412 S1 ;  ===turn on  filament runout detection===\nM400 P10\nM620.3 W1; === turn on filament tangle detection===\nM400 S2\n\nM1002 set_filament_type:{filament_type[initial_no_support_extruder]}\n\n;M1002 set_flag extrude_cali_flag=1\nM1002 judge_flag extrude_cali_flag\n\nM622 J1\n    M1002 gcode_claim_action : 8\n\n    M109 S{nozzle_temperature[initial_extruder]}\n    G1 E10 F{outer_wall_volumetric_speed/2.4*60}\n    M983 F{outer_wall_volumetric_speed/2.4} A0.3 H[nozzle_diameter]; cali dynamic extrusion compensation\n\n    M106 P1 S255\n    M400 S5\n    G1 X-28.5 F18000\n    G1 X-48.2 F3000\n    G1 X-28.5 F18000 ;wipe and shake\n    G1 X-48.2 F3000\n    G1 X-28.5 F12000 ;wipe and shake\n    G1 X-48.2 F3000\n    M400\n    M106 P1 S0\n\n    M1002 judge_last_extrude_cali_success\n    M622 J0\n        M983 F{outer_wall_volumetric_speed/2.4} A0.3 H[nozzle_diameter]; cali dynamic extrusion compensation\n        M106 P1 S255\n        M400 S5\n        G1 X-28.5 F18000\n        G1 X-48.2 F3000\n        G1 X-28.5 F18000 ;wipe and shake\n        G1 X-48.2 F3000\n        G1 X-28.5 F12000 ;wipe and shake\n        M400\n        M106 P1 S0\n    M623\n    \n    G1 X-48.2 F3000\n    M400\n    M984 A0.1 E1 S1 F{outer_wall_volumetric_speed/2.4} H[nozzle_diameter]\n    M106 P1 S178\n    M400 S7\n    G1 X-28.5 F18000\n    G1 X-48.2 F3000\n    G1 X-28.5 F18000 ;wipe and shake\n    G1 X-48.2 F3000\n    G1 X-28.5 F12000 ;wipe and shake\n    G1 X-48.2 F3000\n    M400\n    M106 P1 S0\nM623 ; end of "draw extrinsic para cali paint"\n\n;G392 S0\n;===== auto extrude cali end ========================\n\n;M400\n;M73 P1.717\n\nM104 S170 ; prepare to wipe nozzle\nM106 S255 ; turn on fan\n\n;===== mech mode fast check start =====================\nM1002 gcode_claim_action : 3\n\nG1 X128 Y128 F20000\nG1 Z5 F1200\nM400 P200\nM970.3 Q1 A5 K0 O3\nM974 Q1 S2 P0\n\nM970.2 Q1 K1 W58 Z0.1\nM974 S2\n\nG1 X128 Y128 F20000\nG1 Z5 F1200\nM400 P200\nM970.3 Q0 A10 K0 O1\nM974 Q0 S2 P0\n\nM970.2 Q0 K1 W78 Z0.1\nM974 S2\n\nM975 S1\nG1 F30000\nG1 X0 Y5\nG28 X ; re-home XY\n\nG1 Z4 F1200\n\n;===== mech mode fast check end =======================\n\n;M400\n;M73 P1.717\n\n;===== wipe nozzle ===============================\nM1002 gcode_claim_action : 14\n\nM975 S1\nM106 S255 ; turn on fan (G28 has turn off fan)\nM211 S; push soft endstop status\nM211 X0 Y0 Z0 ;turn off Z axis endstop\n\n;===== remove waste by touching start =====\n\nM104 S170 ; set temp down to heatbed acceptable\n\nM83\nG1 E-1 F500\nG90\nM83\n\nM109 S170\nG0 X108 Y-0.5 F30000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X110 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X112 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X114 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X116 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X118 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X120 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X122 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X124 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X126 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X128 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X130 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X132 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X134 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X136 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X138 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X140 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X142 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X144 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X146 F10000\nG380 S3 Z-5 F1200\nG1 Z2 F1200\nG1 X148 F10000\nG380 S3 Z-5 F1200\n\nG1 Z5 F30000\n;===== remove waste by touching end =====\n\nG1 Z10 F1200\nG0 X118 Y261 F30000\nG1 Z5 F1200\nM109 S{nozzle_temperature_initial_layer[initial_extruder]-50}\n\nG28 Z P0 T300; home z with low precision,permit 300deg temperature\nG29.2 S0 ; turn off ABL\nM104 S140 ; prepare to abl\nG0 Z5 F20000\n\nG0 X128 Y261 F20000  ; move to exposed steel surface\nG0 Z-1.01 F1200      ; stop the nozzle\n\nG91\nG2 I1 J0 X2 Y0 F2000.1\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\n\nG90\nG1 Z10 F1200\n\n;===== brush material wipe nozzle =====\n\nG90\nG1 Y250 F30000\nG1 X55\nG1 Z1.300 F1200\nG1 Y262.5 F6000\nG91\nG1 X-35 F30000\nG1 Y-0.5\nG1 X45\nG1 Y-0.5\nG1 X-45\nG1 Y-0.5\nG1 X45\nG1 Y-0.5\nG1 X-45\nG1 Y-0.5\nG1 X45\nG1 Z5.000 F1200\n\nG90\nG1 X30 Y250.000 F30000\nG1 Z1.300 F1200\nG1 Y262.5 F6000\nG91\nG1 X35 F30000\nG1 Y-0.5\nG1 X-45\nG1 Y-0.5\nG1 X45\nG1 Y-0.5\nG1 X-45\nG1 Y-0.5\nG1 X45\nG1 Y-0.5\nG1 X-45\nG1 Z10.000 F1200\n\n;===== brush material wipe nozzle end =====\n\nG90\n;G0 X128 Y261 F20000  ; move to exposed steel surface\nG1 Y250 F30000\nG1 X138\nG1 Y261\nG0 Z-1.01 F1200      ; stop the nozzle\n\nG91\nG2 I1 J0 X2 Y0 F2000.1\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\nG2 I1 J0 X2\nG2 I-0.75 J0 X-1.5\n\nM109 S140\nM106 S255 ; turn on fan (G28 has turn off fan)\n\nM211 R; pop softend status\n\n;===== wipe nozzle end ================================\n\n;M400\n;M73 P1.717\n\n;===== bed leveling ==================================\nM1002 judge_flag g29_before_print_flag\n\nG90\nG1 Z5 F1200\nG1 X0 Y0 F30000\nG29.2 S1 ; turn on ABL\n\nM190 S[bed_temperature_initial_layer_single]; ensure bed temp\nM109 S140\nM106 S0 ; turn off fan , too noisy\n\nM622 J1\n    M1002 gcode_claim_action : 1\n    G29 A1 X{first_layer_print_min[0]} Y{first_layer_print_min[1]} I{first_layer_print_size[0]} J{first_layer_print_size[1]}\n    M400\n    M500 ; save cali data\nM623\n;===== bed leveling end ================================\n\n;===== home after wipe mouth============================\nM1002 judge_flag g29_before_print_flag\nM622 J0\n\n    M1002 gcode_claim_action : 13\n    G28\n\nM623\n\n;===== home after wipe mouth end =======================\n\n;M400\n;M73 P1.717\n\nG1 X108.000 Y-0.500 F30000\nG1 Z0.300 F1200\nM400\nG2814 Z0.32\n\nM104 S{nozzle_temperature_initial_layer[initial_extruder]} ; prepare to print\n\n;===== nozzle load line ===============================\n;G90\n;M83\n;G1 Z5 F1200\n;G1 X88 Y-0.5 F20000\n;G1 Z0.3 F1200\n\n;M109 S{nozzle_temperature_initial_layer[initial_extruder]}\n\n;G1 E2 F300\n;G1 X168 E4.989 F6000\n;G1 Z1 F1200\n;===== nozzle load line end ===========================\n\n;===== extrude cali test ===============================\n\nM400\n    M900 S\n    M900 C\n    G90\n    M83\n\n    M109 S{nozzle_temperature_initial_layer[initial_extruder]}\n    G0 X128 E8  F{outer_wall_volumetric_speed/(24/20)    * 60}\n    G0 X133 E.3742  F{outer_wall_volumetric_speed/(0.3*0.5)/4     * 60}\n    G0 X138 E.3742  F{outer_wall_volumetric_speed/(0.3*0.5)     * 60}\n    G0 X143 E.3742  F{outer_wall_volumetric_speed/(0.3*0.5)/4     * 60}\n    G0 X148 E.3742  F{outer_wall_volumetric_speed/(0.3*0.5)     * 60}\n    G0 X153 E.3742  F{outer_wall_volumetric_speed/(0.3*0.5)/4     * 60}\n    G91\n    G1 X1 Z-0.300\n    G1 X4\n    G1 Z1 F1200\n    G90\n    M400\n\nM900 R\n\nM1002 judge_flag extrude_cali_flag\nM622 J1\n    G90\n    G1 X108.000 Y1.000 F30000\n    G91\n    G1 Z-0.700 F1200\n    G90\n    M83\n    G0 X128 E10  F{outer_wall_volumetric_speed/(24/20)    * 60}\n    G0 X133 E.3742  F{outer_wall_volumetric_speed/(0.3*0.5)/4     * 60}\n    G0 X138 E.3742  F{outer_wall_volumetric_speed/(0.3*0.5)     * 60}\n    G0 X143 E.3742  F{outer_wall_volumetric_speed/(0.3*0.5)/4     * 60}\n    G0 X148 E.3742  F{outer_wall_volumetric_speed/(0.3*0.5)     * 60}\n    G0 X153 E.3742  F{outer_wall_volumetric_speed/(0.3*0.5)/4     * 60}\n    G91\n    G1 X1 Z-0.300\n    G1 X4\n    G1 Z1 F1200\n    G90\n    M400\nM623\n\nG1 Z0.2\n\n;M400\n;M73 P1.717\n\n;========turn off light and wait extrude temperature =============\nM1002 gcode_claim_action : 0\nM400\n\n;===== for Textured PEI Plate , lower the nozzle as the nozzle was touching topmost of the texture when homing ==\n;curr_bed_type={curr_bed_type}\n{if curr_bed_type=="Textured PEI Plate"}\nG29.1 Z{-0.02} ; for Textured PEI Plate\n{endif}\n\nM960 S1 P0 ; turn off laser\nM960 S2 P0 ; turn off laser\nM106 S0 ; turn off fan\nM106 P2 S0 ; turn off big fan\nM106 P3 S0 ; turn off chamber fan\n\nM975 S1 ; turn on mech mode supression\nG90\nM83\nT1000\n\nM211 X0 Y0 Z0 ;turn off soft endstop\n;G392 S1 ; turn on clog detection\nM1007 S1 ; turn on mass estimation\nG29.4\n
; machine_switch_extruder_time = 0
; machine_unload_filament_time = 29
; master_extruder_id = 1
; max_bridge_length = 0
; max_layer_height = 0.28
; max_travel_detour_distance = 0
; min_bead_width = 85%
; min_feature_size = 25%
; min_layer_height = 0.08
; minimum_sparse_infill_area = 15
; mmu_segmented_region_interlocking_depth = 0
; mmu_segmented_region_max_width = 0
; nozzle_diameter = 0.4
; nozzle_height = 4.76
; nozzle_temperature = 220
; nozzle_temperature_initial_layer = 220
; nozzle_temperature_range_high = 240
; nozzle_temperature_range_low = 190
; nozzle_type = stainless_steel
; nozzle_volume = 92
; nozzle_volume_type = Standard
; only_one_wall_first_layer = 0
; ooze_prevention = 0
; other_layers_print_sequence = 0
; other_layers_print_sequence_nums = 0
; outer_wall_acceleration = 5000
; outer_wall_jerk = 9
; outer_wall_line_width = 0.42
; outer_wall_speed = 200
; overhang_1_4_speed = 0
; overhang_2_4_speed = 50
; overhang_3_4_speed = 30
; overhang_4_4_speed = 10
; overhang_fan_speed = 100
; overhang_fan_threshold = 50%
; overhang_threshold_participating_cooling = 95%
; overhang_totally_speed = 10
; physical_extruder_map = 0
; post_process = 
; pre_start_fan_time = 0
; precise_z_height = 0
; pressure_advance = 0.02
; prime_tower_brim_width = 3
; prime_tower_enable_framework = 0
; prime_tower_extra_rib_length = 0
; prime_tower_fillet_wall = 1
; prime_tower_infill_gap = 100%
; prime_tower_lift_height = -1
; prime_tower_lift_speed = 90
; prime_tower_max_speed = 90
; prime_tower_rib_wall = 0
; prime_tower_rib_width = 8
; prime_tower_skip_points = 1
; prime_tower_width = 35
; print_compatible_printers = "Bambu Lab A1 0.4 nozzle"
; print_extruder_id = 1
; print_extruder_variant = "Direct Drive Standard"
; print_flow_ratio = 1
; print_sequence = by layer
; print_settings_id = 0.20mm Standard @BBL A1
; printable_area = 0x0,256x0,256x256,0x256
; printable_height = 256
; printer_extruder_id = 1
; printer_extruder_variant = "Direct Drive Standard"
; printer_model = Bambu Lab A1
; printer_notes = 
; printer_settings_id = Bambu Lab A1 0.4 nozzle
; printer_structure = i3
; printer_technology = FFF
; printer_variant = 0.4
; printhost_authorization_type = key
; printhost_ssl_ignore_revoke = 0
; printing_by_object_gcode = 
; process_notes = 
; raft_contact_distance = 0.1
; raft_expansion = 1.5
; raft_first_layer_density = 90%
; raft_first_layer_expansion = 2
; raft_layers = 0
; reduce_crossing_wall = 0
; reduce_fan_stop_start_freq = 1
; reduce_infill_retraction = 1
; required_nozzle_HRC = 3
; resolution = 0.012
; retract_before_wipe = 0%
; retract_length_toolchange = 2
; retract_lift_above = 0
; retract_lift_below = 255
; retract_restart_extra = 0
; retract_restart_extra_toolchange = 0
; retract_when_changing_layer = 1
; retraction_distances_when_cut = 18
; retraction_length = 0.8
; retraction_minimum_travel = 1
; retraction_speed = 30
; role_base_wipe_speed = 1
; scan_first_layer = 0
; scarf_angle_threshold = 155
; seam_gap = 15%
; seam_position = aligned
; seam_slope_conditional = 1
; seam_slope_entire_loop = 0
; seam_slope_inner_walls = 1
; seam_slope_steps = 10
; silent_mode = 0
; single_extruder_multi_material = 1
; skirt_distance = 2
; skirt_height = 1
; skirt_loops = 0
; slice_closing_radius = 0.049
; slicing_mode = regular
; slow_down_for_layer_cooling = 1
; slow_down_layer_time = 8
; slow_down_min_speed = 20
; small_perimeter_speed = 50%
; small_perimeter_threshold = 0
; smooth_coefficient = 80
; smooth_speed_discontinuity_area = 1
; solid_infill_filament = 1
; sparse_infill_acceleration = 100%
; sparse_infill_anchor = 400%
; sparse_infill_anchor_max = 20
; sparse_infill_density = 25%
; sparse_infill_filament = 1
; sparse_infill_line_width = 0.45
; sparse_infill_pattern = grid
; sparse_infill_speed = 270
; spiral_mode = 0
; spiral_mode_max_xy_smoothing = 200%
; spiral_mode_smooth = 0
; standby_temperature_delta = -5
; start_end_points = 30x-3,54x245
; supertack_plate_temp = 35
; supertack_plate_temp_initial_layer = 35
; support_air_filtration = 0
; support_angle = 0
; support_base_pattern = default
; support_base_pattern_spacing = 2.5
; support_bottom_interface_spacing = 0.5
; support_bottom_z_distance = 0.2
; support_chamber_temp_control = 0
; support_critical_regions_only = 0
; support_expansion = 0
; support_filament = 0
; support_interface_bottom_layers = 2
; support_interface_filament = 0
; support_interface_loop_pattern = 0
; support_interface_not_for_body = 1
; support_interface_pattern = auto
; support_interface_spacing = 0.5
; support_interface_speed = 80
; support_interface_top_layers = 2
; support_line_width = 0.42
; support_object_first_layer_gap = 0.2
; support_object_xy_distance = 0.35
; support_on_build_plate_only = 0
; support_remove_small_overhang = 1
; support_speed = 150
; support_style = default
; support_threshold_angle = 30
; support_top_z_distance = 0.2
; support_type = tree(auto)
; symmetric_infill_y_axis = 0
; temperature_vitrification = 45
; template_custom_gcode = 
; textured_plate_temp = 65
; textured_plate_temp_initial_layer = 65
; thick_bridges = 0
; thumbnail_size = 50x50
; time_lapse_gcode = ;===================== date: 20250206 =====================\n{if !spiral_mode && print_sequence != "by object"}\n; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer\n; SKIPPABLE_START\n; SKIPTYPE: timelapse\nM622.1 S1 ; for prev firware, default turned on\nM1002 judge_flag timelapse_record_flag\nM622 J1\nG92 E0\nG1 Z{max_layer_z + 0.4}\nG1 X0 Y{first_layer_center_no_wipe_tower[1]} F18000 ; move to safe pos\nG1 X-48.2 F3000 ; move to safe pos\nM400\nM1004 S5 P1  ; external shutter\nM400 P300\nM971 S11 C11 O0\nG92 E0\nG1 X0 F18000\nM623\n\n; SKIPTYPE: head_wrap_detect\nM622.1 S1\nM1002 judge_flag g39_3rd_layer_detect_flag\nM622 J1\n    ; enable nozzle clog detect at 3rd layer\n    {if layer_num == 2}\n      M400\n      G90\n      M83\n      M204 S5000\n      G0 Z2 F4000\n      G0 X261 Y250 F20000\n      M400 P200\n      G39 S1\n      G0 Z2 F4000\n    {endif}\n\n\n    M622.1 S1\n    M1002 judge_flag g39_detection_flag\n    M622 J1\n      {if !in_head_wrap_detect_zone}\n        M622.1 S0\n        M1002 judge_flag g39_mass_exceed_flag\n        M622 J1\n        {if layer_num > 2}\n            G392 S0\n            M400\n            G90\n            M83\n            M204 S5000\n            G0 Z{max_layer_z + 0.4} F4000\n            G39.3 S1\n            G0 Z{max_layer_z + 0.4} F4000\n            G392 S0\n          {endif}\n        M623\n    {endif}\n    M623\nM623\n; SKIPPABLE_END\n{endif}\n
; timelapse_type = 0
; top_area_threshold = 200%
; top_color_penetration_layers = 5
; top_one_wall_type = all top
; top_shell_layers = 5
; top_shell_thickness = 1
; top_solid_infill_flow_ratio = 1
; top_surface_acceleration = 2000
; top_surface_jerk = 9
; top_surface_line_width = 0.42
; top_surface_pattern = monotonicline
; top_surface_speed = 200
; travel_acceleration = 10000
; travel_jerk = 9
; travel_speed = 700
; travel_speed_z = 0
; tree_support_branch_angle = 45
; tree_support_branch_diameter = 2
; tree_support_branch_diameter_angle = 5
; tree_support_branch_distance = 5
; tree_support_wall_count = 0
; unprintable_filament_types = ""
; upward_compatible_machine = "Bambu Lab H2D 0.4 nozzle"
; use_firmware_retraction = 0
; use_relative_e_distances = 1
; vertical_shell_speed = 80%
; wall_distribution_count = 1
; wall_filament = 1
; wall_generator = classic
; wall_loops = 2
; wall_sequence = inner wall/outer wall
; wall_transition_angle = 10
; wall_transition_filter_deviation = 25%
; wall_transition_length = 100%
; wipe = 1
; wipe_distance = 2
; wipe_speed = 80%
; wipe_tower_no_sparse_layers = 0
; wipe_tower_rotation_angle = 0
; wipe_tower_x = 0,0
; wipe_tower_y = 250,250
; xy_contour_compensation = 0
; xy_hole_compensation = 0
; z_direction_outwall_speed_continuous = 0
; z_hop = 0.4
; z_hop_types = Auto Lift
; CONFIG_BLOCK_END

; EXECUTABLE_BLOCK_START
M73 P0 R10
M201 X12000 Y12000 Z1500 E5000
M203 X500 Y500 Z30 E30
M204 P12000 R5000 T12000
M205 X9.00 Y9.00 Z3.00 E3.00
M106 S0
M106 P2 S0
; FEATURE: Custom
;===== machine: A1 =========================
;===== date: 20240620 =====================
G392 S0
M9833.2
;M400
;M73 P1.717

;===== start to heat heatbead&hotend==========
M1002 gcode_claim_action : 2
M1002 set_filament_type:PLA
M104 S140
M140 S35

;=====start printer sound ===================
M17
M400 S1
M1006 S1
M1006 A0 B10 L100 C37 D10 M60 E37 F10 N60
M1006 A0 B10 L100 C41 D10 M60 E41 F10 N60
M1006 A0 B10 L100 C44 D10 M60 E44 F10 N60
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N60
M1006 A43 B10 L100 C46 D10 M70 E39 F10 N80
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N80
M1006 A0 B10 L100 C43 D10 M60 E39 F10 N80
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N80
M1006 A0 B10 L100 C41 D10 M80 E41 F10 N80
M1006 A0 B10 L100 C44 D10 M80 E44 F10 N80
M1006 A0 B10 L100 C49 D10 M80 E49 F10 N80
M1006 A0 B10 L100 C0 D10 M80 E0 F10 N80
M1006 A44 B10 L100 C48 D10 M60 E39 F10 N80
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N80
M1006 A0 B10 L100 C44 D10 M80 E39 F10 N80
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N80
M1006 A43 B10 L100 C46 D10 M60 E39 F10 N80
M1006 W
M18 
;=====start printer sound ===================

;=====avoid end stop =================
G91
G380 S2 Z40 F1200
G380 S3 Z-15 F1200
G90

;===== reset machine status =================
;M290 X39 Y39 Z8
M204 S6000

M630 S0 P0
G91
M17 Z0.3 ; lower the z-motor current

G90
M17 X0.65 Y1.2 Z0.6 ; reset motor current to default
M960 S5 P1 ; turn on logo lamp
G90
M220 S100 ;Reset Feedrate
M221 S100 ;Reset Flowrate
M73.2   R1.0 ;Reset left time magnitude
;M211 X0 Y0 Z0 ; turn off soft endstop to prevent protential logic problem

;====== cog noise reduction=================
M982.2 S1 ; turn on cog noise reduction

M1002 gcode_claim_action : 13

G28 X
G91
G1 Z5 F1200
G90
G0 X128 F30000
G0 Y254 F3000
G91
G1 Z-5 F1200

M109 S25 H140

M17 E0.3
M83
G1 E10 F1200
G1 E-0.5 F30
M17 D

G28 Z P0 T140; home z with low precision,permit 300deg temperature
M104 S220

M1002 judge_flag build_plate_detect_flag
M622 S1
  G39.4
  G90
M73 P1 R10
  G1 Z5 F1200
M623

;M400
;M73 P1.717

;===== prepare print temperature and material ==========
M1002 gcode_claim_action : 24

M400
;G392 S1
M211 X0 Y0 Z0 ;turn off soft endstop
M975 S1 ; turn on

G90
G1 X-28.5 F30000
G1 X-48.2 F3000

M620 M ;enable remap
M620 S0A   ; switch material if AMS exist
    M1002 gcode_claim_action : 4
    M400
    M1002 set_filament_type:UNKNOWN
    M109 S220
    M104 S250
    M400
    T0
    G1 X-48.2 F3000
    M400

    M620.1 E F299.339 T240
    M109 S250 ;set nozzle to common flush temp
    M106 P1 S0
    G92 E0
    G1 E50 F200
    M400
    M1002 set_filament_type:PLA
M621 S0A

M109 S240 H300
G92 E0
G1 E50 F200 ; lower extrusion speed to avoid clog
M400
M106 P1 S178
G92 E0
G1 E5 F200
M104 S220
G92 E0
M73 P5 R10
G1 E-0.5 F300

G1 X-28.5 F30000
M73 P7 R9
G1 X-48.2 F3000
M73 P10 R9
G1 X-28.5 F30000 ;wipe and shake
G1 X-48.2 F3000
G1 X-28.5 F30000 ;wipe and shake
G1 X-48.2 F3000

;G392 S0

M400
M106 P1 S0
;===== prepare print temperature and material end =====

;M400
;M73 P1.717

;===== auto extrude cali start =========================
M975 S1
;G392 S1

G90
M83
T1000
G1 X-48.2 Y0 Z10 F10000
M400
M1002 set_filament_type:UNKNOWN

M412 S1 ;  ===turn on  filament runout detection===
M400 P10
M620.3 W1; === turn on filament tangle detection===
M400 S2

M1002 set_filament_type:PLA

;M1002 set_flag extrude_cali_flag=1
M1002 judge_flag extrude_cali_flag

M622 J1
    M1002 gcode_claim_action : 8

    M109 S220
    G1 E10 F300
    M983 F5 A0.3 H0.4; cali dynamic extrusion compensation

    M106 P1 S255
    M400 S5
    G1 X-28.5 F18000
    G1 X-48.2 F3000
    G1 X-28.5 F18000 ;wipe and shake
    G1 X-48.2 F3000
M73 P12 R9
    G1 X-28.5 F12000 ;wipe and shake
    G1 X-48.2 F3000
    M400
    M106 P1 S0

    M1002 judge_last_extrude_cali_success
    M622 J0
        M983 F5 A0.3 H0.4; cali dynamic extrusion compensation
        M106 P1 S255
        M400 S5
M73 P13 R9
        G1 X-28.5 F18000
        G1 X-48.2 F3000
        G1 X-28.5 F18000 ;wipe and shake
        G1 X-48.2 F3000
        G1 X-28.5 F12000 ;wipe and shake
        M400
        M106 P1 S0
    M623
    
M73 P14 R9
    G1 X-48.2 F3000
    M400
    M984 A0.1 E1 S1 F5 H0.4
    M106 P1 S178
    M400 S7
    G1 X-28.5 F18000
    G1 X-48.2 F3000
    G1 X-28.5 F18000 ;wipe and shake
    G1 X-48.2 F3000
    G1 X-28.5 F12000 ;wipe and shake
    G1 X-48.2 F3000
    M400
    M106 P1 S0
M623 ; end of "draw extrinsic para cali paint"

;G392 S0
;===== auto extrude cali end ========================

;M400
;M73 P1.717

M104 S170 ; prepare to wipe nozzle
M106 S255 ; turn on fan

;===== mech mode fast check start =====================
M1002 gcode_claim_action : 3

G1 X128 Y128 F20000
G1 Z5 F1200
M400 P200
M970.3 Q1 A5 K0 O3
M974 Q1 S2 P0

M970.2 Q1 K1 W58 Z0.1
M974 S2

G1 X128 Y128 F20000
G1 Z5 F1200
M400 P200
M970.3 Q0 A10 K0 O1
M974 Q0 S2 P0

M970.2 Q0 K1 W78 Z0.1
M974 S2

M975 S1
G1 F30000
G1 X0 Y5
G28 X ; re-home XY

G1 Z4 F1200

;===== mech mode fast check end =======================

;M400
;M73 P1.717

;===== wipe nozzle ===============================
M1002 gcode_claim_action : 14

M975 S1
M106 S255 ; turn on fan (G28 has turn off fan)
M211 S; push soft endstop status
M211 X0 Y0 Z0 ;turn off Z axis endstop

;===== remove waste by touching start =====

M104 S170 ; set temp down to heatbed acceptable

M83
G1 E-1 F500
G90
M83

M109 S170
G0 X108 Y-0.5 F30000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X110 F10000
G380 S3 Z-5 F1200
M73 P55 R4
G1 Z2 F1200
G1 X112 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X114 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X116 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X118 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X120 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X122 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X124 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X126 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X128 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X130 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X132 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X134 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X136 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X138 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X140 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X142 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X144 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X146 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X148 F10000
G380 S3 Z-5 F1200

G1 Z5 F30000
;===== remove waste by touching end =====

G1 Z10 F1200
G0 X118 Y261 F30000
G1 Z5 F1200
M109 S170

G28 Z P0 T300; home z with low precision,permit 300deg temperature
G29.2 S0 ; turn off ABL
M104 S140 ; prepare to abl
G0 Z5 F20000

G0 X128 Y261 F20000  ; move to exposed steel surface
G0 Z-1.01 F1200      ; stop the nozzle

G91
G2 I1 J0 X2 Y0 F2000.1
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5

G90
G1 Z10 F1200

;===== brush material wipe nozzle =====

G90
G1 Y250 F30000
G1 X55
G1 Z1.300 F1200
G1 Y262.5 F6000
G91
G1 X-35 F30000
G1 Y-0.5
G1 X45
G1 Y-0.5
G1 X-45
G1 Y-0.5
G1 X45
M73 P56 R4
G1 Y-0.5
G1 X-45
G1 Y-0.5
G1 X45
G1 Z5.000 F1200

G90
G1 X30 Y250.000 F30000
G1 Z1.300 F1200
G1 Y262.5 F6000
G91
G1 X35 F30000
G1 Y-0.5
G1 X-45
G1 Y-0.5
G1 X45
G1 Y-0.5
G1 X-45
G1 Y-0.5
G1 X45
G1 Y-0.5
G1 X-45
G1 Z10.000 F1200

;===== brush material wipe nozzle end =====

G90
;G0 X128 Y261 F20000  ; move to exposed steel surface
G1 Y250 F30000
G1 X138
G1 Y261
G0 Z-1.01 F1200      ; stop the nozzle

G91
G2 I1 J0 X2 Y0 F2000.1
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5
G2 I1 J0 X2
G2 I-0.75 J0 X-1.5

M109 S140
M106 S255 ; turn on fan (G28 has turn off fan)

M211 R; pop softend status

;===== wipe nozzle end ================================

;M400
;M73 P1.717

;===== bed leveling ==================================
M1002 judge_flag g29_before_print_flag

G90
G1 Z5 F1200
G1 X0 Y0 F30000
G29.2 S1 ; turn on ABL

M190 S35; ensure bed temp
M109 S140
M106 S0 ; turn off fan , too noisy

M622 J1
    M1002 gcode_claim_action : 1
    G29 A1 X118.57 Y118.57 I18.8592 J18.8592
    M400
    M500 ; save cali data
M623
;===== bed leveling end ================================

;===== home after wipe mouth============================
M1002 judge_flag g29_before_print_flag
M622 J0

    M1002 gcode_claim_action : 13
    G28

M623

;===== home after wipe mouth end =======================

;M400
;M73 P1.717

G1 X108.000 Y-0.500 F30000
M73 P57 R4
G1 Z0.300 F1200
M400
G2814 Z0.32

M104 S220 ; prepare to print

;===== nozzle load line ===============================
;G90
;M83
;G1 Z5 F1200
;G1 X88 Y-0.5 F20000
;G1 Z0.3 F1200

;M109 S220

;G1 E2 F300
;G1 X168 E4.989 F6000
;G1 Z1 F1200
;===== nozzle load line end ===========================

;===== extrude cali test ===============================

M400
    M900 S
    M900 C
    G90
    M83

    M109 S220
    G0 X128 E8  F720
    G0 X133 E.3742  F1200
    G0 X138 E.3742  F4800
    G0 X143 E.3742  F1200
    G0 X148 E.3742  F4800
    G0 X153 E.3742  F1200
    G91
    G1 X1 Z-0.300
    G1 X4
    G1 Z1 F1200
    G90
    M400

M900 R

M1002 judge_flag extrude_cali_flag
M622 J1
    G90
    G1 X108.000 Y1.000 F30000
    G91
    G1 Z-0.700 F1200
    G90
    M83
    G0 X128 E10  F720
    G0 X133 E.3742  F1200
    G0 X138 E.3742  F4800
    G0 X143 E.3742  F1200
    G0 X148 E.3742  F4800
    G0 X153 E.3742  F1200
    G91
    G1 X1 Z-0.300
    G1 X4
    G1 Z1 F1200
    G90
    M400
M623

G1 Z0.2

;M400
;M73 P1.717

;========turn off light and wait extrude temperature =============
M1002 gcode_claim_action : 0
M400

;===== for Textured PEI Plate , lower the nozzle as the nozzle was touching topmost of the texture when homing ==
;curr_bed_type=Supertack Plate


M960 S1 P0 ; turn off laser
M960 S2 P0 ; turn off laser
M106 S0 ; turn off fan
M106 P2 S0 ; turn off big fan
M106 P3 S0 ; turn off chamber fan

M975 S1 ; turn on mech mode supression
G90
M83
T1000

M211 X0 Y0 Z0 ;turn off soft endstop
;G392 S1 ; turn on clog detection
M1007 S1 ; turn on mass estimation
G29.4
; MACHINE_START_GCODE_END
; filament start gcode
;Prevent PLA from jamming


;VT0
G90
G21
M83 ; use relative distances for extrusion
M981 S1 P20000 ;open spaghetti detector
; CHANGE_LAYER
; Z_HEIGHT: 0.2
; LAYER_HEIGHT: 0.2
G1 E-.8 F1800
; layer num/total_layer_count: 1/26
; update layer progress
M73 L1
M991 S0 P0 ;notify layer change
M106 S0
M106 P2 S0
; OBJECT_ID: 123
G1 X124.478 Y130.298 F42000
M204 S6000
G1 Z.4
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.5
G1 F2477
M204 S500
G1 X124.469 Y130.269 E.00111
G3 X127.91 Y123.799 I3.537 J-2.269 E.33154
G3 X131.539 Y125.725 I.101 J4.193 E.15994
G3 X124.827 Y130.749 I-3.533 J2.275 E.46967
G1 X124.515 Y130.345 E.01902
M204 S6000
G1 X124.849 Y130.031 F42000
; FEATURE: Outer wall
G1 F2477
M204 S500
G1 X124.855 Y130.021 E.00043
G3 X127.942 Y124.255 I3.152 J-2.022 E.29622
G3 X130.027 Y124.846 I.013 J3.928 E.08177
M73 P58 R4
G3 X125.175 Y130.448 I-2.02 J3.153 E.47832
G1 X124.886 Y130.078 E.01749
; WIPE_START
G1 F3000
G1 X124.855 Y130.021 E-.0245
G1 X124.59 Y129.557 E-.20302
G1 X124.403 Y129.056 E-.20327
G1 X124.289 Y128.534 E-.20323
G1 X124.266 Y128.203 E-.12598
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X125.904 Y134.058 Z.6 F42000
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F2477
M204 S500
G1 X125.917 Y133.878 E.00674
G2 X125.45 Y132.8 I-1.861 J.166 E.04451
G2 X124.741 Y132.277 I-3.796 J4.407 E.03284
G3 X123.412 Y130.811 I3.388 J-4.406 E.0741
G1 X123.2 Y130.55 E.01251
G1 X122.881 Y130.309 E.01491
G1 X122.515 Y130.15 E.01486
G1 X122.109 Y130.083 E.01533
G1 X121.942 Y130.096 E.00625
G3 X121.942 Y125.904 I5.992 J-2.096 E.15915
G1 X122.122 Y125.917 E.00674
G2 X123.2 Y125.45 I-.166 J-1.861 E.04451
G2 X123.723 Y124.741 I-4.407 J-3.796 E.03284
G3 X125.189 Y123.412 I4.406 J3.388 E.0741
G1 X125.45 Y123.2 E.01251
G1 X125.691 Y122.881 E.01491
G1 X125.85 Y122.515 E.01486
G1 X125.917 Y122.109 E.01533
G1 X125.904 Y121.941 E.00628
G3 X128.26 Y121.597 I2.111 J6.214 E.08919
G3 X130.096 Y121.942 I-.152 J5.865 E.06989
G1 X130.083 Y122.122 E.00674
G2 X130.55 Y123.2 I1.861 J-.165 E.04452
G2 X131.259 Y123.723 I3.799 J-4.412 E.03284
G3 X132.588 Y125.189 I-3.387 J4.405 E.0741
G1 X132.8 Y125.45 E.01251
G1 X133.119 Y125.691 E.01491
G1 X133.485 Y125.85 E.01486
G1 X133.891 Y125.917 E.01533
G1 X134.059 Y125.904 E.00628
G3 X134.058 Y130.096 I-6.003 J2.095 E.15914
G1 X133.878 Y130.083 E.00674
G2 X132.8 Y130.55 I.165 J1.861 E.04452
G2 X132.277 Y131.259 I4.412 J3.799 E.03284
G3 X130.811 Y132.588 I-4.406 J-3.388 E.0741
G1 X130.55 Y132.8 E.01251
G1 X130.309 Y133.119 E.01491
G1 X130.15 Y133.485 E.01486
G1 X130.083 Y133.891 E.01532
G1 X130.096 Y134.059 E.0063
G3 X125.96 Y134.078 I-2.095 J-6.003 E.15691
M204 S6000
G1 X125.436 Y134.186 F42000
; FEATURE: Outer wall
G1 F2477
M204 S500
G1 X125.454 Y133.9 E.01068
G2 X124.915 Y132.954 I-1.182 J.046 E.04217
G3 X123.046 Y131.085 I3.289 J-5.157 E.09918
G2 X121.652 Y130.616 I-.993 J.642 E.05917
G3 X121.652 Y125.384 I6.272 J-2.616 E.2
G2 X123.046 Y124.915 I.402 J-1.112 E.05917
G3 X124.915 Y123.046 I5.157 J3.289 E.09918
G2 X125.385 Y121.652 I-.642 J-.993 E.05915
G3 X128.279 Y121.14 I2.563 J6.048 E.11041
G3 X130.616 Y121.652 I-.284 J6.888 E.08954
G2 X131.085 Y123.046 I1.112 J.402 E.05917
G3 X132.954 Y124.915 I-3.289 J5.157 E.09918
G2 X134.348 Y125.385 I.993 J-.642 E.05915
G3 X134.348 Y130.616 I-6.266 J2.616 E.2
G2 X132.954 Y131.085 I-.402 J1.112 E.05917
G3 X131.085 Y132.954 I-5.157 J-3.289 E.09918
G2 X130.615 Y134.348 I.642 J.993 E.05915
G3 X125.384 Y134.348 I-2.616 J-6.266 E.2
G2 X125.418 Y134.24 I-1.112 J-.402 E.00423
; WIPE_START
G1 F3000
G1 X125.454 Y133.9 E-.1299
G1 X125.408 Y133.615 E-.10959
G1 X125.294 Y133.351 E-.10955
G1 X125.119 Y133.12 E-.11017
G1 X124.915 Y132.954 E-.10002
G1 X124.48 Y132.652 E-.20078
; WIPE_END
G1 E-.04 F1800
M204 S6000
G17
G3 Z.6 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z0.6
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.261 Y131.935 F42000
G1 Z.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.756084
G1 F2477
M204 S500
M73 P59 R4
G3 X124.065 Y130.739 I3.299 J-4.495 E.09867
; WIPE_START
G1 F3000
G1 X124.397 Y131.156 E-.23838
G1 X124.769 Y131.534 E-.2375
G1 X125.261 Y131.935 E-.28412
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X123.964 Y126.289 Z.6 F42000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.50347
G1 F2477
M204 S500
G1 X123.435 Y125.76 E.0281
G1 X123.061 Y126.037 E.01747
G1 X123.627 Y126.603 E.03007
G1 X123.59 Y126.705 E.00406
G1 X123.498 Y127.126 E.01616
G1 X122.601 Y126.229 E.04758
G1 X122.226 Y126.293 E.0143
G2 X122.176 Y126.455 I.875 J.358 E.00636
G1 X123.425 Y127.703 E.06626
G2 X123.429 Y128.359 I2.283 J.312 E.0247
G1 X122.061 Y126.991 E.07262
G2 X121.992 Y127.574 I3.316 J.684 E.02206
G1 X123.555 Y129.136 E.08294
G1 X123.59 Y129.295 E.00609
G1 X123.819 Y129.909 E.02461
G1 X123.989 Y130.222 E.01337
G1 X121.984 Y128.216 E.10646
G2 X122.052 Y128.936 I4.187 J-.033 E.02715
G1 X123.818 Y130.702 E.09374
; WIPE_START
G1 F6300
G1 X122.404 Y129.288 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X124.065 Y125.261 Z.6 F42000
G1 Z.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.756084
G1 F2477
M204 S500
G3 X125.261 Y124.065 I4.495 J3.299 E.09867
; WIPE_START
G1 F3000
G1 X124.844 Y124.397 E-.23838
G1 X124.466 Y124.769 E-.2375
G1 X124.065 Y125.261 E-.28412
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X130.701 Y123.819 Z.6 F42000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.5033
G1 F2477
M204 S500
G1 X128.933 Y122.051 E.09381
G2 X128.214 Y121.983 I-.866 J5.393 E.02708
G1 X130.218 Y123.987 E.10631
G1 X129.909 Y123.819 E.0132
G1 X129.295 Y123.59 E.02459
G1 X129.134 Y123.555 E.00617
G1 X127.572 Y121.992 E.08289
G2 X126.99 Y122.062 I.115 J3.437 E.022
G1 X128.363 Y123.434 E.07282
G2 X127.702 Y123.425 I-.368 J2.643 E.02485
G1 X126.454 Y122.176 E.06624
G2 X126.291 Y122.226 I.21 J.973 E.0064
G1 X126.229 Y122.602 E.01431
G1 X127.125 Y123.498 E.04752
G1 X126.705 Y123.59 E.01612
G1 X126.603 Y123.628 E.00408
G1 X126.037 Y123.061 E.03004
G1 X125.759 Y123.435 E.01746
G1 X126.289 Y123.964 E.02808
; WIPE_START
G1 F6300
G1 X125.759 Y123.435 E-.28443
G1 X126.037 Y123.061 E-.17685
G1 X126.593 Y123.617 E-.29872
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X130.739 Y124.065 Z.6 F42000
G1 Z.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.756078
G1 F2477
M204 S500
G3 X131.935 Y125.261 I-3.299 J4.495 E.09866
M204 S6000
G1 X132.182 Y125.298 F42000
; FEATURE: Bottom surface
; LINE_WIDTH: 0.5035
G1 F2477
M204 S500
G1 X133.948 Y127.064 E.09371
G3 X134.016 Y127.783 I-4.073 J.751 E.02717
G1 X132.01 Y125.777 E.10648
G1 X132.181 Y126.091 E.01339
G1 X132.41 Y126.705 E.02461
G1 X132.445 Y126.863 E.00608
G1 X134.008 Y128.426 E.08294
G3 X133.939 Y129.009 I-3.38 J-.1 E.02206
G1 X132.571 Y127.641 E.07263
G3 X132.575 Y128.297 I-2.279 J.344 E.0247
G1 X133.824 Y129.545 E.06627
G3 X133.774 Y129.707 I-.933 J-.199 E.00637
G1 X133.399 Y129.771 E.0143
G1 X132.502 Y128.874 E.04759
G1 X132.41 Y129.295 E.01616
G1 X132.373 Y129.396 E.00406
G1 X132.939 Y129.963 E.03007
G1 X132.565 Y130.24 E.01748
G1 X132.036 Y129.711 E.0281
; WIPE_START
G1 F6300
G1 X132.565 Y130.24 E-.28449
G1 X132.939 Y129.963 E-.17694
G1 X132.384 Y129.407 E-.29857
; WIPE_END
M73 P60 R4
G1 E-.04 F1800
M204 S6000
G1 X131.935 Y130.739 Z.6 F42000
G1 Z.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.756079
G1 F2477
M204 S500
G3 X130.739 Y131.935 I-4.496 J-3.3 E.09866
; WIPE_START
G1 F3000
G1 X131.156 Y131.603 E-.23838
G1 X131.534 Y131.231 E-.2375
G1 X131.935 Y130.739 E-.28412
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X129.711 Y132.036 Z.6 F42000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.5033
G1 F2477
M204 S500
G1 X130.241 Y132.565 E.02808
G1 X129.963 Y132.939 E.01746
G1 X129.397 Y132.372 E.03005
G1 X129.295 Y132.41 E.00408
G1 X128.875 Y132.502 E.01612
G1 X129.771 Y133.398 E.04752
G1 X129.709 Y133.774 E.01431
G3 X129.546 Y133.824 I-.37 J-.916 E.0064
G1 X128.298 Y132.575 E.06624
G3 X127.642 Y132.571 I-.313 J-2.281 E.02467
G1 X129.01 Y133.938 E.07254
G3 X128.428 Y134.008 I-.686 J-3.286 E.02201
G1 X126.866 Y132.445 E.08288
G1 X126.705 Y132.41 E.00617
G1 X126.091 Y132.181 E.02459
G1 X125.782 Y132.013 E.0132
G1 X127.786 Y134.017 E.10634
G3 X127.067 Y133.949 I.027 J-4.116 E.02714
G1 X125.299 Y132.181 E.09379
; CHANGE_LAYER
; Z_HEIGHT: 0.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6300
G1 X126.713 Y133.595 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 2/26
; update layer progress
M73 L2
M991 S0 P1 ;notify layer change
M106 S201.45
M106 P2 S178
; open powerlost recovery
M1003 S1
; OBJECT_ID: 123
M204 S10000
G17
G3 Z.6 I1.037 J-.637 P1  F42000
G1 X124.628 Y130.197 Z.6
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3019
M204 S6000
G1 X124.62 Y130.173 E.00087
G3 X127.853 Y123.984 I3.386 J-2.17 E.28053
G3 X131.864 Y126.865 I.157 J4.012 E.17644
G3 X124.963 Y130.632 I-3.858 J1.137 E.36232
G1 X124.664 Y130.245 E.01621
M204 S10000
G1 X124.95 Y129.96 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3019
M204 S5000
G3 X127.881 Y124.375 I3.056 J-1.958 E.23489
G3 X131.057 Y126.035 I.131 J3.616 E.1152
G3 X124.983 Y130.01 I-3.051 J1.967 E.34887
; WIPE_START
G1 F9547.055
M204 S6000
G1 X124.695 Y129.509 E-.21958
G1 X124.513 Y129.024 E-.19699
G1 X124.403 Y128.517 E-.19701
G1 X124.376 Y128.133 E-.14641
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X125.701 Y134.259 Z.8 F42000
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3019
M204 S6000
G1 X125.712 Y134.222 E.0013
G2 X125.081 Y132.732 I-1.504 J-.241 E.05657
G3 X123.268 Y130.919 I3.141 J-4.954 E.08574
G2 X121.612 Y130.321 I-1.241 J.845 E.06241
G3 X121.618 Y125.663 I6.5 J-2.322 E.1576
G1 X121.778 Y125.712 E.00558
G2 X123.268 Y125.081 I.241 J-1.504 E.05657
G3 X125.081 Y123.268 I4.954 J3.141 E.08574
G2 X125.679 Y121.612 I-.845 J-1.242 E.06241
G3 X128.521 Y121.226 I2.364 J6.754 E.09578
G3 X130.337 Y121.618 I-.503 J6.746 E.06181
G1 X130.288 Y121.778 E.00558
G2 X130.919 Y123.268 I1.504 J.241 E.05657
G3 X132.732 Y125.081 I-3.141 J4.954 E.08574
G2 X134.388 Y125.679 I1.252 J-.873 E.06226
G3 X134.382 Y130.337 I-6.501 J2.322 E.1576
G1 X134.222 Y130.288 E.00558
G2 X132.732 Y130.919 I-.241 J1.504 E.05657
G3 X130.919 Y132.732 I-4.954 J-3.141 E.08574
G2 X130.321 Y134.388 I.845 J1.241 E.06241
G3 X125.663 Y134.382 I-2.322 J-6.5 E.1576
G1 X125.683 Y134.316 E.00229
M204 S10000
G1 X125.315 Y134.177 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3019
M204 S5000
G1 X125.32 Y134.149 E.00088
G2 X124.845 Y133.046 I-1.094 J-.183 E.03899
G3 X122.954 Y131.155 I3.35 J-5.241 E.08282
G2 X122.358 Y130.711 I-.918 J.61 E.0233
G1 X122.092 Y130.659 E.00832
G1 X121.864 Y130.675 E.00704
G1 X121.549 Y130.776 E.01015
G1 F2040
G1 X121.405 Y130.844 E.00489
G3 X121.405 Y125.156 I6.594 J-2.844 E.17968
G1 F3019
G1 X121.55 Y125.223 E.00489
G1 X121.85 Y125.324 E.00975
G1 X122.092 Y125.341 E.00744
G1 X122.348 Y125.29 E.00801
G2 X122.954 Y124.845 I-.313 J-1.064 E.02358
G3 X124.845 Y122.954 I5.241 J3.35 E.08282
G2 X125.289 Y122.358 I-.61 J-.918 E.0233
G1 X125.341 Y122.092 E.00832
G1 X125.325 Y121.864 E.00704
G1 X125.224 Y121.55 E.01014
G1 F2040
G1 X125.156 Y121.405 E.00491
G3 X128.547 Y120.835 I2.872 J6.716 E.10665
G3 X130.844 Y121.405 I-.608 J7.364 E.07303
G1 F3019
G1 X130.776 Y121.55 E.00489
G1 X130.676 Y121.85 E.00975
G1 X130.659 Y122.092 E.00744
G1 X130.71 Y122.348 E.00801
G2 X131.155 Y122.954 I1.064 J-.313 E.02358
G3 X133.046 Y124.845 I-3.35 J5.241 E.08282
G2 X133.643 Y125.286 I.921 J-.623 E.02327
G1 X133.908 Y125.341 E.00829
G1 X134.136 Y125.325 E.00704
G1 X134.45 Y125.224 E.01014
G1 F2040
G1 X134.595 Y125.156 E.00491
G3 X134.595 Y130.844 I-6.594 J2.844 E.17968
G1 F3019
G1 X134.451 Y130.776 E.00489
G1 X134.15 Y130.676 E.00975
G1 X133.908 Y130.659 E.00744
G1 X133.652 Y130.71 E.00802
G2 X133.046 Y131.155 I.313 J1.064 E.02358
G3 X131.155 Y133.046 I-5.241 J-3.35 E.08282
G2 X130.711 Y133.642 I.61 J.918 E.0233
G1 X130.659 Y133.908 E.00832
G1 X130.675 Y134.136 E.00704
G1 X130.776 Y134.45 E.01013
G1 F2040
G1 X130.844 Y134.595 E.00491
G3 X125.156 Y134.595 I-2.844 J-6.594 E.17968
G1 F3019
G1 X125.224 Y134.45 E.00489
G1 X125.296 Y134.234 E.00701
; WIPE_START
G1 F5184.855
M204 S6000
G1 X125.32 Y134.149 E-.03366
G1 X125.341 Y133.908 E-.0918
G1 X125.298 Y133.65 E-.09942
G1 X125.194 Y133.409 E-.0997
G1 X125.036 Y133.2 E-.0997
G1 X124.845 Y133.046 E-.09305
G1 X124.394 Y132.732 E-.20887
G1 X124.326 Y132.675 E-.03379
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z.8 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z0.8
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X130.178 Y123.699 F42000
G1 Z.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.46953
G1 F3019
M204 S6000
G1 X130.4 Y123.842 E.00921
; LINE_WIDTH: 0.43623
G1 X130.623 Y123.986 E.00849
; LINE_WIDTH: 0.407309
G3 X132.091 Y125.509 I-3.151 J4.506 E.0632
M204 S10000
G1 X129.198 Y122.951 F42000
; LINE_WIDTH: 0.466927
G1 F3019
M204 S6000
G1 X129.264 Y122.965 E.00236
G1 X129.142 Y122.499 E.01665
G1 X128.457 Y122.4 E.0239
G2 X127.288 Y122.428 I-.391 J8.24 E.04043
G1 X126.855 Y122.51 E.01525
G1 X126.735 Y122.967 E.01632
G3 X128.671 Y122.849 I1.308 J5.556 E.06735
G1 X129.139 Y122.939 E.01646
M204 S10000
G1 X127.12 Y123.294 F42000
; LINE_WIDTH: 0.423006
G1 F3019
M204 S6000
G1 X127.96 Y123.205 E.02615
G1 X128.642 Y123.248 E.02119
G3 X129.96 Y123.61 I-.79 J5.458 E.04242
; LINE_WIDTH: 0.456788
G1 X130.178 Y123.699 E.00794
M73 P61 R4
G1 X129.837 Y123.234 E.01944
; LINE_WIDTH: 0.420551
G1 X129.607 Y122.743 E.01667
G1 X129.5 Y122.167 E.01805
G2 X128.43 Y121.995 I-1.598 J6.542 E.03336
G1 X127.53 Y121.995 E.02771
G2 X126.499 Y122.186 I.218 J4.052 E.03235
G1 X126.388 Y122.758 E.01793
G1 X126.162 Y123.235 E.01624
G1 X125.824 Y123.656 E.01662
G1 X125.563 Y123.873 E.01045
G3 X127.062 Y123.307 I2.506 J4.367 E.04952
M204 S10000
G1 X125.157 Y123.702 F42000
; LINE_WIDTH: 0.41999
G1 F3019
M204 S6000
G1 X124.515 Y124.189 E.02476
G1 X123.888 Y124.875 E.02857
G1 X123.369 Y125.579 E.02686
G1 X122.967 Y125.885 E.01552
G1 X122.514 Y126.065 E.01497
G1 X122.108 Y126.128 E.01264
G1 X121.887 Y126.113 E.00679
G2 X121.897 Y129.887 I5.961 J1.873 E.1178
G1 X122.155 Y129.874 E.00796
G1 X122.607 Y129.958 E.01412
G1 X123.008 Y130.138 E.0135
G1 X123.363 Y130.414 E.01382
G3 X124.189 Y131.485 I-24.809 J19.983 E.04155
G1 X124.875 Y132.112 E.02857
G1 X125.579 Y132.631 E.02686
G1 X125.885 Y133.033 E.01552
G1 X126.065 Y133.486 E.01497
G1 X126.128 Y133.892 E.01264
G1 X126.113 Y134.113 E.00679
G2 X129.887 Y134.103 I1.873 J-5.962 E.1178
G1 X129.874 Y133.845 E.00796
G1 X129.958 Y133.393 E.01412
G1 X130.138 Y132.992 E.0135
G1 X130.414 Y132.637 E.01382
G3 X131.485 Y131.811 I20.005 J24.838 E.04155
G1 X132.112 Y131.125 E.02857
G1 X132.631 Y130.421 E.02687
G1 X133.033 Y130.115 E.01551
G1 X133.486 Y129.935 E.01498
G1 X133.892 Y129.872 E.01264
G1 X134.113 Y129.887 E.00679
G2 X134.103 Y126.113 I-5.97 J-1.873 E.11779
G1 X133.845 Y126.126 E.00796
G1 X133.393 Y126.042 E.01411
G1 X132.987 Y125.858 E.0137
G1 X132.637 Y125.586 E.01362
G3 X131.811 Y124.515 I24.771 J-19.954 E.04155
G1 X131.125 Y123.888 E.02857
G1 X130.421 Y123.369 E.02687
G1 X130.115 Y122.967 E.01552
G1 X129.932 Y122.499 E.01545
G1 X129.872 Y122.108 E.01215
G1 X129.887 Y121.887 E.00679
G2 X128 Y121.618 I-1.803 J5.886 E.05881
G2 X126.917 Y121.69 I-.21 J5.03 E.03341
G1 X126.113 Y121.896 E.0255
G1 X126.126 Y122.155 E.00799
G1 X126.042 Y122.607 E.01412
G1 X125.862 Y123.008 E.01349
G1 X125.586 Y123.363 E.01382
G1 X125.204 Y123.665 E.01495
M204 S10000
G1 X123.686 Y125.841 F42000
; LINE_WIDTH: 0.47217
G1 F3019
M204 S6000
G1 X123.836 Y125.609 E.00966
; LINE_WIDTH: 0.43711
G1 X123.986 Y125.377 E.00887
; LINE_WIDTH: 0.40737
G3 X125.513 Y123.907 I4.516 J3.161 E.06335
M204 S10000
G1 X122.951 Y126.802 F42000
; LINE_WIDTH: 0.470476
G1 F3019
M204 S6000
G1 X122.965 Y126.735 E.00238
G1 X122.5 Y126.858 E.01675
G2 X122.509 Y129.145 I5.174 J1.124 E.0803
G1 X122.966 Y129.265 E.01647
G3 X122.941 Y126.862 I4.886 J-1.253 E.08454
M204 S10000
G1 X123.294 Y128.88 F42000
; LINE_WIDTH: 0.423635
G1 F3019
M204 S6000
G1 X123.205 Y128.04 E.02619
G1 X123.248 Y127.358 E.02122
G3 X123.607 Y126.039 I5.635 J.827 E.04249
; LINE_WIDTH: 0.459127
G1 X123.686 Y125.841 E.00723
G1 X123.234 Y126.163 E.01883
; LINE_WIDTH: 0.420552
G1 X122.743 Y126.393 E.01667
G1 X122.167 Y126.5 E.01804
G1 X122.052 Y127.067 E.01778
G1 X121.98 Y127.89 E.02545
G2 X122.186 Y129.501 I5.479 J.119 E.05014
G1 X122.758 Y129.612 E.01794
G1 X123.235 Y129.838 E.01624
G1 X123.656 Y130.176 E.01662
G1 X123.873 Y130.437 E.01045
G3 X123.307 Y128.938 I4.368 J-2.506 E.04952
M204 S10000
G1 X125.342 Y131.517 F42000
; LINE_WIDTH: 0.419989
G1 F3019
M204 S6000
G1 X125.096 Y131.331 E.00949
G3 X124.045 Y129.957 I3.263 J-3.584 E.05344
G1 X123.793 Y129.336 E.02058
G1 X123.662 Y128.8 E.01696
G1 X123.581 Y128.013 E.02428
G3 X125.033 Y124.732 I4.4 J-.015 E.11358
G1 X125.6 Y124.29 E.02207
G3 X127.2 Y123.662 I2.488 J3.991 E.05312
G1 X127.987 Y123.581 E.02429
G3 X131.268 Y125.033 I.015 J4.4 E.11358
G1 X131.71 Y125.6 E.02207
G3 X132.338 Y127.201 I-3.993 J2.489 E.05316
G1 X132.419 Y127.987 E.02426
G3 X130.967 Y131.268 I-4.4 J.015 E.11358
G1 X130.4 Y131.71 E.02207
G3 X128.8 Y132.338 I-2.488 J-3.992 E.05313
G1 X128.013 Y132.419 E.02428
G3 X125.39 Y131.553 I.037 J-4.519 E.08626
M204 S10000
G1 X125.841 Y132.314 F42000
; LINE_WIDTH: 0.47217
G1 F3019
M204 S6000
G1 X125.609 Y132.164 E.00966
; LINE_WIDTH: 0.43711
G1 X125.377 Y132.014 E.00887
; LINE_WIDTH: 0.407381
G3 X123.907 Y130.487 I3.163 J-4.517 E.06335
M204 S10000
G1 X126.802 Y133.049 F42000
; LINE_WIDTH: 0.470467
G1 F3019
M204 S6000
G1 X126.735 Y133.035 E.00239
G1 X126.858 Y133.5 E.01675
G2 X129.145 Y133.491 I1.124 J-5.174 E.0803
G1 X129.265 Y133.034 E.01646
G3 X126.862 Y133.059 I-1.253 J-4.886 E.08454
M204 S10000
G1 X128.88 Y132.706 F42000
; LINE_WIDTH: 0.423635
G1 F3019
M204 S6000
G1 X128.04 Y132.795 E.02619
G1 X127.358 Y132.752 E.02122
G3 X126.039 Y132.393 I.827 J-5.634 E.04249
; LINE_WIDTH: 0.459127
G1 X125.841 Y132.314 E.00723
G1 X126.163 Y132.766 E.01883
; LINE_WIDTH: 0.42055
G1 X126.393 Y133.257 E.01667
G1 X126.5 Y133.833 E.01803
G1 X127.067 Y133.948 E.01778
G1 X127.89 Y134.02 E.02545
G2 X129.501 Y133.814 I.119 J-5.48 E.05014
G1 X129.612 Y133.242 E.01794
G1 X129.838 Y132.765 E.01624
G1 X130.176 Y132.344 E.01662
G1 X130.437 Y132.127 E.01045
G3 X128.938 Y132.693 I-2.506 J-4.368 E.04952
M204 S10000
G1 X132.301 Y130.178 F42000
; LINE_WIDTH: 0.469545
G1 F3019
M204 S6000
G1 X132.158 Y130.4 E.00921
; LINE_WIDTH: 0.436235
G1 X132.014 Y130.623 E.00849
; LINE_WIDTH: 0.407364
G3 X130.487 Y132.093 I-4.517 J-3.163 E.06335
M204 S10000
G1 X133.049 Y129.198 F42000
; LINE_WIDTH: 0.470462
G1 F3019
M204 S6000
G1 X133.035 Y129.265 E.00238
G1 X133.5 Y129.142 E.01675
G2 X133.491 Y126.855 I-5.174 J-1.124 E.0803
G1 X133.034 Y126.735 E.01647
G3 X133.059 Y129.139 I-4.886 J1.253 E.08456
M204 S10000
G1 X132.706 Y127.121 F42000
; LINE_WIDTH: 0.423008
G1 F3019
M204 S6000
G1 X132.795 Y127.96 E.02611
G1 X132.752 Y128.642 E.02119
G3 X132.39 Y129.96 I-5.46 J-.79 E.04242
; LINE_WIDTH: 0.4568
G1 X132.301 Y130.178 E.00794
G1 X132.766 Y129.837 E.01944
; LINE_WIDTH: 0.420482
G1 X133.257 Y129.607 E.01667
G1 X133.833 Y129.5 E.01804
G1 X133.948 Y128.933 E.01778
G2 X134.024 Y128.005 I-10.289 J-1.307 E.02867
G2 X133.814 Y126.499 I-5.632 J.018 E.04692
G1 X133.241 Y126.387 E.01795
G1 X132.759 Y126.158 E.01641
G1 X132.344 Y125.824 E.01642
G1 X132.127 Y125.563 E.01045
G3 X132.693 Y127.063 I-4.367 J2.506 E.04954
; CHANGE_LAYER
; Z_HEIGHT: 0.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F9534.872
G1 X132.589 Y126.61 E-.17637
G1 X132.378 Y126.045 E-.22935
G1 X132.127 Y125.563 E-.20669
G1 X132.344 Y125.824 E-.12907
G1 X132.382 Y125.854 E-.01853
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 3/26
; update layer progress
M73 L3
M991 S0 P2 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z.8 I-.589 J-1.065 P1  F42000
G1 X124.6 Y130.155 Z.8
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3106
M204 S6000
G1 X124.343 Y129.67 E.0182
G3 X127.427 Y124.014 I3.656 J-1.675 E.2478
G1 X127.784 Y123.989 E.01188
G1 X128 Y123.973 E.00718
G3 X124.637 Y130.201 I0 J4.022 E.55117
M204 S10000
G1 X124.949 Y129.961 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3106
M204 S5000
G3 X127.812 Y124.38 I3.056 J-1.957 E.23271
G3 X131.487 Y126.976 I.199 J3.616 E.14917
G3 X124.982 Y130.011 I-3.481 J1.028 E.317
; WIPE_START
G1 F9547.055
M204 S6000
G1 X124.695 Y129.509 E-.21958
G1 X124.513 Y129.024 E-.19699
G1 X124.403 Y128.517 E-.19701
G1 X124.376 Y128.133 E-.14641
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X125.687 Y134.278 Z1 F42000
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3106
M204 S6000
G1 X125.716 Y134.17 E.0037
G2 X125.081 Y132.732 I-1.502 J-.196 E.05481
G3 X123.268 Y130.919 I3.141 J-4.954 E.08574
G2 X121.426 Y130.398 I-1.232 J.839 E.06894
G3 X121.426 Y125.604 I6.634 J-2.398 E.16226
G2 X123.268 Y125.081 I.601 J-1.391 E.06878
G3 X125.081 Y123.268 I4.954 J3.141 E.08574
G2 X125.602 Y121.426 I-.839 J-1.232 E.06894
G3 X128.492 Y121.024 I2.393 J6.615 E.0975
G3 X130.396 Y121.426 I-.476 J6.977 E.06476
G2 X130.919 Y123.268 I1.391 J.601 E.06878
M73 P62 R4
G3 X132.732 Y125.081 I-3.141 J4.954 E.08574
G2 X134.574 Y125.602 I1.232 J-.839 E.06894
G3 X134.574 Y130.396 I-6.634 J2.398 E.16226
G2 X132.732 Y130.919 I-.601 J1.391 E.06878
G3 X130.919 Y132.732 I-4.954 J-3.141 E.08574
G2 X130.398 Y134.574 I.839 J1.232 E.06894
G3 X125.604 Y134.574 I-2.398 J-6.634 E.16226
G1 X125.671 Y134.335 E.00823
M204 S10000
G1 X125.309 Y134.207 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3106
M204 S5000
G1 X125.314 Y134.178 E.00089
G2 X125.194 Y133.409 I-1.209 J-.205 E.02433
G2 X124.845 Y133.046 I-.914 J.527 E.01562
G3 X122.954 Y131.155 I3.35 J-5.241 E.08282
G2 X122.371 Y130.718 I-.921 J.623 E.02281
G1 X122.046 Y130.66 E.01014
G1 X121.828 Y130.679 E.00671
G1 X121.592 Y130.756 E.00763
G1 X121.368 Y130.861 E.00761
G1 F2040
G1 X121.224 Y130.928 E.00489
G3 X121.224 Y125.072 I6.727 J-2.928 E.18511
G1 F3106
G1 X121.368 Y125.139 E.00489
G1 X121.607 Y125.25 E.0081
G1 X121.821 Y125.317 E.00691
G1 X122.092 Y125.329 E.00832
G2 X122.591 Y125.194 I-.065 J-1.225 E.01601
G2 X122.954 Y124.845 I-.527 J-.914 E.01562
G3 X124.845 Y122.954 I5.241 J3.35 E.08282
G2 X125.282 Y122.371 I-.623 J-.921 E.02281
G1 X125.34 Y122.046 E.01014
G1 X125.321 Y121.828 E.00671
G1 X125.244 Y121.592 E.00763
G1 X125.139 Y121.368 E.00761
G1 F2040
G1 X125.072 Y121.224 E.00489
G3 X128.512 Y120.633 I2.941 J6.817 E.10828
G3 X130.928 Y121.224 I-.556 J7.511 E.07678
G1 F3106
G1 X130.861 Y121.368 E.00489
G1 X130.75 Y121.607 E.00809
G1 X130.683 Y121.821 E.00691
G1 X130.671 Y122.092 E.00832
G2 X130.806 Y122.591 I1.225 J-.065 E.01601
G2 X131.155 Y122.954 I.914 J-.527 E.01562
G3 X133.046 Y124.845 I-3.35 J5.241 E.08282
G2 X133.629 Y125.282 I.921 J-.623 E.02281
G1 X133.954 Y125.34 E.01014
G1 X134.172 Y125.321 E.00671
G1 X134.408 Y125.244 E.00763
G1 X134.632 Y125.139 E.00761
G1 F2040
G1 X134.776 Y125.072 E.00489
G3 X134.776 Y130.928 I-6.727 J2.928 E.18511
G1 F3106
G1 X134.632 Y130.861 E.00489
G1 X134.393 Y130.75 E.00809
G1 X134.179 Y130.683 E.00691
G1 X133.908 Y130.671 E.00832
G2 X133.409 Y130.806 I.065 J1.225 E.01601
G2 X133.046 Y131.155 I.527 J.914 E.01562
G3 X131.155 Y133.046 I-5.241 J-3.35 E.08282
G2 X130.718 Y133.629 I.623 J.921 E.02281
G1 X130.66 Y133.954 E.01014
G1 X130.679 Y134.172 E.00671
G1 X130.756 Y134.408 E.00763
G1 X130.861 Y134.632 E.00761
G1 F2040
G1 X130.928 Y134.776 E.00489
G3 X125.072 Y134.776 I-2.928 J-6.727 E.18511
G1 F3106
G1 X125.139 Y134.632 E.00489
G1 X125.256 Y134.395 E.00812
G1 X125.292 Y134.264 E.00418
; WIPE_START
G1 F7041.765
M204 S6000
G1 X125.314 Y134.178 E-.03378
G1 X125.341 Y133.908 E-.10325
G1 X125.298 Y133.65 E-.09927
G1 X125.194 Y133.409 E-.09967
G1 X125.036 Y133.2 E-.09967
G1 X124.845 Y133.046 E-.09307
G1 X124.394 Y132.732 E-.20885
G1 X124.349 Y132.695 E-.02243
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z1 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z1
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    
      M400
      G90
      M83
      M204 S5000
      G0 Z2 F4000
      G0 X261 Y250 F20000
      M400 P200
      G39 S1
      G0 Z2 F4000
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.563 Y123.873 F42000
G1 Z.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.422416
G1 F3106
M204 S6000
G3 X127.278 Y123.26 I2.611 J4.592 E.05661
G1 X127.96 Y123.205 E.02116
G1 X128.642 Y123.248 E.02116
G3 X129.96 Y123.61 I-.79 J5.46 E.04235
; LINE_WIDTH: 0.456778
G1 X130.178 Y123.699 E.00794
G1 X129.837 Y123.234 E.01944
; LINE_WIDTH: 0.420308
G1 X129.607 Y122.743 E.01665
G1 X129.502 Y122.213 E.01662
G1 X129.511 Y121.964 E.00766
G2 X126.977 Y121.86 I-1.536 J6.525 E.07846
G1 X126.496 Y121.982 E.01525
G1 X126.454 Y122.484 E.01549
G1 X126.256 Y123.053 E.01855
G1 X125.958 Y123.505 E.01664
G1 X125.607 Y123.832 E.01477
M204 S10000
G1 X123.686 Y125.842 F42000
; LINE_WIDTH: 0.472175
G1 F3106
M204 S6000
G1 X123.836 Y125.609 E.00967
; LINE_WIDTH: 0.437125
G1 X123.986 Y125.377 E.00888
; LINE_WIDTH: 0.407379
G3 X125.513 Y123.907 I4.517 J3.163 E.06335
M204 S10000
G1 X122.908 Y129.21 F42000
; LINE_WIDTH: 0.567303
G1 F3106
M204 S6000
G3 X122.78 Y127.539 I5.195 J-1.237 E.0719
G1 X122.9 Y126.812 E.03149
G1 X122.336 Y126.934 E.02466
G2 X122.342 Y129.078 I5.141 J1.058 E.09229
G1 X122.852 Y129.189 E.02229
M204 S10000
G1 X123.873 Y130.437 F42000
; LINE_WIDTH: 0.422816
G1 F3106
M204 S6000
G3 X123.26 Y128.722 I4.593 J-2.611 E.05667
G1 X123.205 Y128.04 E.02118
G1 X123.248 Y127.358 E.02118
G3 X123.607 Y126.039 I5.635 J.827 E.0424
; LINE_WIDTH: 0.45913
G1 X123.686 Y125.842 E.00723
G1 X123.234 Y126.163 E.01882
; LINE_WIDTH: 0.420307
G1 X122.743 Y126.393 E.01666
G1 X122.213 Y126.498 E.01662
G1 X121.964 Y126.489 E.00767
M73 P62 R3
G1 X121.852 Y127.066 E.01807
G1 X121.782 Y127.881 E.02516
G1 X121.808 Y128.6 E.02212
M73 P63 R3
G2 X121.963 Y129.504 I70.901 J-11.657 E.02822
G1 X122.481 Y129.545 E.01598
G1 X123.053 Y129.744 E.01864
G1 X123.505 Y130.042 E.01664
G1 X123.832 Y130.393 E.01477
M204 S10000
G1 X125.842 Y132.314 F42000
; LINE_WIDTH: 0.472175
G1 F3106
M204 S6000
G1 X125.609 Y132.164 E.00967
; LINE_WIDTH: 0.437125
G1 X125.377 Y132.014 E.00888
; LINE_WIDTH: 0.407388
G3 X123.907 Y130.487 I3.162 J-4.516 E.06336
M204 S10000
G1 X126.968 Y132.287 F42000
; LINE_WIDTH: 0.41999
G1 F3106
M204 S6000
G1 X126.176 Y132.025 E.02562
G3 X124.732 Y130.967 I2.103 J-4.385 E.05535
G1 X124.29 Y130.4 E.02207
G1 X124.045 Y129.956 E.01557
G1 X123.78 Y129.302 E.0217
G1 X123.628 Y128.642 E.0208
G3 X125.033 Y124.732 I4.44 J-.612 E.13276
G1 X125.6 Y124.29 E.02207
G1 X126.043 Y124.045 E.01557
G1 X126.698 Y123.78 E.02171
G1 X127.358 Y123.628 E.0208
G3 X131.268 Y125.033 I.612 J4.441 E.13276
G1 X131.71 Y125.6 E.02207
G1 X131.955 Y126.043 E.01557
G1 X132.22 Y126.698 E.02171
G1 X132.372 Y127.358 E.0208
G3 X130.967 Y131.268 I-4.441 J.612 E.13276
G1 X130.4 Y131.71 E.02207
G1 X129.956 Y131.955 E.01557
G1 X129.302 Y132.22 E.0217
G1 X128.642 Y132.372 E.0208
G3 X127.027 Y132.3 I-.599 J-4.71 E.04994
M204 S10000
G1 X129.21 Y133.092 F42000
; LINE_WIDTH: 0.567301
G1 F3106
M204 S6000
G3 X127.539 Y133.22 I-1.237 J-5.197 E.0719
G1 X126.812 Y133.1 E.03149
G1 X126.934 Y133.664 E.02466
G2 X129.078 Y133.658 I1.058 J-5.145 E.09229
G1 X129.189 Y133.148 E.02229
M204 S10000
G1 X130.437 Y132.127 F42000
; LINE_WIDTH: 0.422816
G1 F3106
M204 S6000
G3 X128.722 Y132.74 I-2.611 J-4.592 E.05667
G1 X128.04 Y132.795 E.02118
G1 X127.358 Y132.752 E.02118
G3 X126.039 Y132.393 I.827 J-5.636 E.0424
; LINE_WIDTH: 0.45913
G1 X125.842 Y132.314 E.00723
G1 X126.163 Y132.766 E.01882
; LINE_WIDTH: 0.420307
G1 X126.393 Y133.257 E.01666
G1 X126.498 Y133.787 E.01662
G1 X126.489 Y134.036 E.00767
G1 X127.066 Y134.148 E.01807
G1 X127.881 Y134.218 E.02516
G1 X128.599 Y134.192 E.0221
G2 X129.504 Y134.037 I-11.7 J-71.204 E.02824
G1 X129.545 Y133.519 E.01599
G1 X129.744 Y132.947 E.01864
G1 X130.042 Y132.495 E.01664
G1 X130.393 Y132.168 E.01477
M204 S10000
G1 X130.843 Y132.298 F42000
; LINE_WIDTH: 0.41999
G1 F3106
M204 S6000
G1 X131.485 Y131.811 E.02476
G1 X132.112 Y131.125 E.02857
G1 X132.631 Y130.421 E.02687
G1 X133.033 Y130.115 E.01551
G1 X133.449 Y129.941 E.01387
G1 X133.907 Y129.873 E.01422
G1 X134.309 Y129.931 E.01246
G2 X134.438 Y126.599 I-6.333 J-1.916 E.10359
G1 X134.305 Y126.072 E.01668
G1 X133.936 Y126.124 E.01146
G1 X133.515 Y126.069 E.01305
G1 X133.038 Y125.887 E.0157
G1 X132.637 Y125.586 E.0154
G3 X131.811 Y124.515 I24.877 J-20.035 E.04155
G1 X131.125 Y123.888 E.02857
G1 X130.421 Y123.369 E.02687
G1 X130.115 Y122.967 E.01551
G1 X129.941 Y122.551 E.01387
G1 X129.873 Y122.093 E.01422
G1 X129.931 Y121.691 E.01246
G2 X128 Y121.416 I-1.925 J6.586 E.06014
G2 X126.909 Y121.489 I-.19 J5.379 E.03367
G1 X126.073 Y121.7 E.02649
G1 X126.124 Y122.064 E.0113
G1 X126.069 Y122.485 E.01305
G1 X125.887 Y122.962 E.0157
G1 X125.586 Y123.363 E.0154
G3 X124.515 Y124.189 I-20.035 J-24.877 E.04155
G1 X123.888 Y124.875 E.02857
G1 X123.369 Y125.579 E.02687
G1 X122.967 Y125.885 E.01551
G1 X122.551 Y126.059 E.01387
G1 X122.093 Y126.127 E.01422
G1 X121.691 Y126.069 E.01246
G2 X121.562 Y129.401 I6.319 J1.915 E.1036
G1 X121.695 Y129.928 E.01668
G1 X122.064 Y129.876 E.01146
G1 X122.485 Y129.931 E.01305
G1 X122.962 Y130.113 E.01571
G1 X123.363 Y130.414 E.01539
G3 X124.189 Y131.485 I-24.821 J19.992 E.04155
G1 X124.875 Y132.112 E.02857
G1 X125.579 Y132.631 E.02687
G1 X125.885 Y133.033 E.01551
G1 X126.059 Y133.449 E.01387
G1 X126.127 Y133.907 E.01422
G1 X126.069 Y134.309 E.01246
G2 X129.401 Y134.439 I1.915 J-6.32 E.10359
G1 X129.928 Y134.305 E.01668
G1 X129.876 Y133.936 E.01146
G1 X129.931 Y133.515 E.01305
G1 X130.113 Y133.038 E.01571
G1 X130.414 Y132.637 E.01539
G1 X130.796 Y132.335 E.01495
M204 S10000
G1 X132.301 Y130.178 F42000
; LINE_WIDTH: 0.469545
G1 F3106
M204 S6000
G1 X132.158 Y130.4 E.00921
; LINE_WIDTH: 0.436235
G1 X132.014 Y130.623 E.00849
; LINE_WIDTH: 0.407359
G3 X130.487 Y132.093 I-4.516 J-3.162 E.06335
M204 S10000
G1 X133.092 Y126.79 F42000
; LINE_WIDTH: 0.567298
G1 F3106
M204 S6000
G3 X133.22 Y128.461 I-5.196 J1.237 E.0719
G1 X133.1 Y129.188 E.03149
G1 X133.664 Y129.066 E.02466
G2 X133.658 Y126.922 I-5.142 J-1.058 E.09229
G1 X133.148 Y126.811 E.02229
M204 S10000
G1 X132.127 Y125.563 F42000
; LINE_WIDTH: 0.422415
G1 F3106
M204 S6000
G3 X132.74 Y127.278 I-4.592 J2.611 E.05661
G1 X132.795 Y127.96 E.02116
G1 X132.752 Y128.642 E.02116
G3 X132.39 Y129.96 I-5.461 J-.791 E.04235
; LINE_WIDTH: 0.456801
G1 X132.301 Y130.178 E.00794
G1 X132.766 Y129.837 E.01944
; LINE_WIDTH: 0.420306
G1 X133.257 Y129.607 E.01666
G1 X133.787 Y129.502 E.01662
G1 X134.036 Y129.511 E.00766
G1 X134.148 Y128.934 E.01807
G2 X134.223 Y127.986 I-10.181 J-1.284 E.02925
G1 X134.192 Y127.4 E.01804
G2 X134.037 Y126.496 I-70.572 J11.597 E.02823
G1 X133.519 Y126.455 E.01599
G1 X132.947 Y126.256 E.01864
G1 X132.495 Y125.958 E.01664
G1 X132.168 Y125.607 E.01477
M204 S10000
G1 X130.178 Y123.699 F42000
; LINE_WIDTH: 0.46951
G1 F3106
M204 S6000
G1 X130.4 Y123.842 E.00921
; LINE_WIDTH: 0.43621
G1 X130.623 Y123.986 E.00849
; LINE_WIDTH: 0.407365
G3 X132.093 Y125.513 I-3.163 J4.517 E.06335
M204 S10000
G1 X129.189 Y122.901 F42000
; LINE_WIDTH: 0.565264
G1 F3106
M204 S6000
G1 X129.066 Y122.329 E.02489
G2 X126.925 Y122.338 I-1.048 J5.68 E.09165
G1 X126.842 Y122.78 E.01914
G1 X126.795 Y122.904 E.00563
G3 X128.674 Y122.8 I1.243 J5.454 E.08051
G1 X129.13 Y122.89 E.01976
; CHANGE_LAYER
; Z_HEIGHT: 0.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6892.012
G1 X128.674 Y122.8 E-.17639
G1 X127.928 Y122.758 E-.28421
G1 X127.325 Y122.799 E-.22939
G1 X127.145 Y122.835 E-.07001
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 4/26
; update layer progress
M73 L4
M991 S0 P3 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z1 I-1.152 J-.394 P1  F42000
G1 X124.628 Y130.197 Z1
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3294
M204 S6000
G1 X124.619 Y130.173 E.00086
G3 X127.427 Y124.014 I3.381 J-2.178 E.26685
G1 X127.715 Y123.994 E.00958
G1 X128 Y123.973 E.00948
G3 X124.963 Y130.632 I0 J4.022 E.53326
G1 X124.664 Y130.245 E.01621
M204 S10000
G1 X124.949 Y129.961 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3294
M204 S5000
G3 X127.483 Y124.403 I3.051 J-1.965 E.22305
G1 X127.743 Y124.385 E.00801
G1 X128 Y124.366 E.00792
G3 X124.982 Y130.011 I0 J3.629 E.45981
; WIPE_START
G1 F9547.055
M204 S6000
G1 X124.695 Y129.509 E-.21958
G1 X124.513 Y129.024 E-.197
G1 X124.403 Y128.517 E-.197
G1 X124.376 Y128.133 E-.14641
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X125.704 Y134.209 Z1.2 F42000
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3294
M204 S6000
G1 X125.719 Y134.156 E.00183
G2 X125.081 Y132.732 I-1.508 J-.18 E.05436
G3 X123.268 Y130.919 I3.141 J-4.954 E.08574
G2 X121.243 Y130.486 I-1.245 J.872 E.07555
G3 X121.243 Y125.514 I6.896 J-2.486 E.16829
G2 X123.268 Y125.081 I.78 J-1.303 E.07556
G3 X125.081 Y123.268 I4.954 J3.141 E.08574
G2 X125.514 Y121.243 I-.872 J-1.245 E.07555
G3 X128.454 Y120.822 I2.51 J7.042 E.09919
G3 X130.486 Y121.243 I-.45 J7.278 E.06909
G2 X130.919 Y123.268 I1.303 J.78 E.07556
G3 X132.732 Y125.081 I-3.141 J4.954 E.08574
G2 X134.757 Y125.514 I1.245 J-.872 E.07555
G3 X134.757 Y130.486 I-6.896 J2.486 E.16829
G2 X132.732 Y130.919 I-.78 J1.303 E.07556
G3 X130.919 Y132.732 I-4.954 J-3.141 E.08574
G2 X130.486 Y134.757 I.872 J1.245 E.07555
G3 X125.514 Y134.757 I-2.486 J-6.896 E.16829
G2 X125.616 Y134.552 I-1.303 J-.78 E.00759
G1 X125.689 Y134.267 E.00975
M204 S10000
G1 X125.296 Y134.226 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3294
M204 S5000
G1 X125.329 Y134.111 E.00366
G2 X124.845 Y133.046 I-1.082 J-.152 E.03793
G3 X122.954 Y131.155 I3.35 J-5.241 E.08282
G2 X122.027 Y130.662 I-.917 J.608 E.03364
G1 X121.828 Y130.679 E.00612
G1 X121.592 Y130.756 E.00762
G1 X121.186 Y130.946 E.01376
G1 F2040
G1 X121.042 Y131.013 E.00489
G3 X121.042 Y124.987 I6.946 J-3.013 E.19043
G1 F3158.699
G1 X121.186 Y125.054 E.00489
G1 F3294
G1 X121.596 Y125.245 E.01388
G1 X121.889 Y125.329 E.00937
G2 X122.954 Y124.845 I.152 J-1.082 E.03793
G3 X124.845 Y122.954 I5.241 J3.35 E.08282
G2 X125.338 Y122.027 I-.608 J-.917 E.03364
G1 X125.321 Y121.828 E.00612
G1 X125.244 Y121.592 E.00762
G1 X125.054 Y121.186 E.01376
G1 F2040
G1 X124.987 Y121.042 E.00489
G3 X128.474 Y120.43 I3 J6.856 E.10982
G3 X131.013 Y121.042 I-.506 J7.675 E.08063
G1 F3158.731
G1 X130.946 Y121.186 E.00489
G1 F3294
G1 X130.756 Y121.593 E.01379
G1 X130.671 Y121.889 E.00945
G2 X131.155 Y122.954 I1.082 J.152 E.03793
G3 X133.046 Y124.845 I-3.35 J5.241 E.08282
G2 X133.973 Y125.338 I.917 J-.608 E.03364
G1 X134.172 Y125.321 E.00612
G1 X134.408 Y125.244 E.00762
G1 X134.814 Y125.054 E.01376
G1 F2040
G1 X134.958 Y124.987 E.00489
G3 X134.958 Y131.013 I-6.946 J3.013 E.19043
G1 F3158.731
G1 X134.814 Y130.946 E.00489
G1 F3294
G1 X134.407 Y130.756 E.01379
G1 X134.111 Y130.671 E.00945
G2 X133.046 Y131.155 I-.152 J1.082 E.03793
G3 X131.155 Y133.046 I-5.241 J-3.35 E.08282
G2 X130.662 Y133.973 I.608 J.917 E.03364
G1 X130.679 Y134.172 E.00612
G1 X130.756 Y134.408 E.00762
G1 X130.946 Y134.814 E.01376
G1 F2040
G1 X131.013 Y134.958 E.00489
M73 P64 R3
G3 X124.987 Y134.958 I-3.013 J-6.946 E.19043
G1 F3158.731
G1 X125.054 Y134.814 E.00489
G1 F3294
G1 X125.243 Y134.406 E.01379
G1 X125.279 Y134.283 E.00395
; WIPE_START
G1 F9253.436
M204 S6000
G1 X125.329 Y134.111 E-.06806
G1 X125.34 Y133.914 E-.0751
G1 X125.297 Y133.648 E-.10217
G1 X125.194 Y133.409 E-.09897
G1 X125.036 Y133.2 E-.09968
G1 X124.845 Y133.046 E-.09307
G1 X124.394 Y132.732 E-.20887
G1 X124.365 Y132.709 E-.01409
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z1.2 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z1.2
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z1.2 F4000
            G39.3 S1
            G0 Z1.2 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X123.296 Y128.892 F42000
G1 Z.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.423624
G1 F3294
M204 S6000
G1 X123.205 Y128.04 E.02656
G1 X123.248 Y127.358 E.02122
G3 X123.607 Y126.039 I5.635 J.827 E.04249
; LINE_WIDTH: 0.459128
G1 X123.686 Y125.841 E.00723
G1 X123.234 Y126.163 E.01883
; LINE_WIDTH: 0.420497
G1 X122.748 Y126.391 E.01652
G1 X122.191 Y126.497 E.01744
G1 X121.762 Y126.474 E.0132
G1 X121.654 Y127.045 E.01787
G1 X121.583 Y127.872 E.02552
G2 X121.78 Y129.518 I5.373 J.191 E.05121
G1 X122.173 Y129.519 E.01208
G1 X122.801 Y129.629 E.01962
G1 X123.237 Y129.839 E.0149
G1 X123.656 Y130.176 E.01654
G1 X123.873 Y130.437 E.01045
G3 X123.31 Y128.95 I4.362 J-2.503 E.04914
M204 S10000
G1 X122.44 Y128.736 F42000
; LINE_WIDTH: 0.542125
G1 F3294
M204 S6000
G3 X122.434 Y127.338 I6.738 J-.728 E.05694
M204 S10000
G1 X122.857 Y127.543 F42000
; LINE_WIDTH: 0.41999
G1 F3294
M204 S6000
G3 X123.001 Y126.692 I8.052 J.928 E.02653
G3 X122.057 Y126.88 I-1.05 J-2.817 E.02969
G2 X122.073 Y129.131 I5.68 J1.088 E.06961
G1 X122.704 Y129.213 E.01956
G1 X123 Y129.305 E.00955
G1 X122.891 Y128.803 E.01581
G1 X122.829 Y128.067 E.02267
G1 X122.854 Y127.603 E.01429
M204 S10000
G1 X123.856 Y126.495 F42000
; LINE_WIDTH: 0.41999
G1 F3294
M204 S6000
G3 X125.033 Y124.732 I4.104 J1.466 E.06581
G1 X125.6 Y124.29 E.02207
G3 X127.189 Y123.665 I2.485 J3.986 E.05276
G1 X127.987 Y123.581 E.02465
G3 X131.268 Y125.033 I.015 J4.4 E.11358
G1 X131.71 Y125.6 E.02207
G3 X132.326 Y127.147 I-3.971 J2.477 E.05145
G1 X132.419 Y127.987 E.02595
G3 X130.967 Y131.268 I-4.4 J.015 E.11358
G1 X130.4 Y131.71 E.02207
G3 X128.811 Y132.335 I-2.485 J-3.986 E.05276
G1 X128.013 Y132.419 E.02465
G3 X124.732 Y130.967 I-.015 J-4.4 E.11358
G1 X124.29 Y130.4 E.02207
G3 X123.665 Y128.811 I3.986 J-2.485 E.05276
G1 X123.581 Y128.013 E.02465
G3 X123.835 Y126.551 I4.834 J.088 E.04578
M204 S10000
G1 X123.686 Y125.841 F42000
; LINE_WIDTH: 0.472175
G1 F3294
M204 S6000
G1 X123.836 Y125.609 E.00966
; LINE_WIDTH: 0.437125
G1 X123.986 Y125.377 E.00888
; LINE_WIDTH: 0.407379
G3 X125.513 Y123.907 I4.517 J3.163 E.06336
M204 S10000
G1 X125.157 Y123.702 F42000
; LINE_WIDTH: 0.41999
G1 F3294
M204 S6000
G1 X124.515 Y124.189 E.02476
G1 X123.888 Y124.875 E.02857
G1 X123.369 Y125.579 E.02687
G1 X122.967 Y125.885 E.01552
G1 X122.553 Y126.057 E.01377
G1 X122.084 Y126.126 E.01459
G1 X121.63 Y126.079 E.01402
G1 X121.492 Y126.035 E.00444
G2 X121.502 Y129.961 I6.362 J1.946 E.12244
G1 X121.69 Y129.904 E.00601
G1 X122.12 Y129.892 E.01323
G1 X122.648 Y129.974 E.01641
G1 X123.01 Y130.14 E.01224
G1 X123.363 Y130.414 E.01374
G3 X124.189 Y131.485 I-24.926 J20.073 E.04155
G1 X124.875 Y132.112 E.02857
G1 X125.579 Y132.631 E.02687
G1 X125.885 Y133.033 E.01552
G1 X126.057 Y133.447 E.01377
G1 X126.126 Y133.916 E.01459
G1 X126.079 Y134.371 E.01404
G1 X126.035 Y134.508 E.00442
G2 X129.961 Y134.498 I1.946 J-6.362 E.12244
G1 X129.904 Y134.31 E.00601
G1 X129.892 Y133.88 E.01323
G1 X129.974 Y133.352 E.01641
G1 X130.14 Y132.99 E.01224
G1 X130.414 Y132.637 E.01374
G3 X131.485 Y131.811 I20.022 J24.861 E.04155
G1 X132.112 Y131.125 E.02857
G1 X132.631 Y130.421 E.02687
G1 X133.033 Y130.115 E.01551
G1 X133.447 Y129.943 E.01377
G1 X133.916 Y129.874 E.01459
G1 X134.371 Y129.921 E.01404
G1 X134.508 Y129.965 E.00442
G2 X134.498 Y126.039 I-6.362 J-1.946 E.12244
G1 X134.304 Y126.097 E.0062
G1 X133.776 Y126.11 E.01624
G1 X133.355 Y126.027 E.01319
G1 X132.99 Y125.86 E.01232
G1 X132.637 Y125.586 E.01374
G3 X131.811 Y124.515 I24.874 J-20.033 E.04155
G1 X131.125 Y123.888 E.02857
G1 X130.421 Y123.369 E.02687
G1 X130.115 Y122.967 E.01552
G1 X129.943 Y122.553 E.01377
G1 X129.874 Y122.084 E.01458
G1 X129.921 Y121.629 E.01404
G1 X129.965 Y121.492 E.00442
G1 X129.329 Y121.331 E.02016
G1 X128.479 Y121.22 E.02636
G2 X126.902 Y121.287 I-.477 J7.341 E.04859
G1 X126.039 Y121.502 E.02731
G1 X126.096 Y121.69 E.00601
G1 X126.108 Y122.119 E.01319
G1 X126.026 Y122.648 E.01645
G1 X125.86 Y123.01 E.01224
G1 X125.586 Y123.363 E.01374
G1 X125.204 Y123.665 E.01495
M204 S10000
G1 X127.108 Y123.296 F42000
; LINE_WIDTH: 0.422994
G1 F3294
M204 S6000
G1 X127.96 Y123.205 E.02651
G1 X128.642 Y123.248 E.02119
G3 X129.96 Y123.61 I-.79 J5.46 E.04242
; LINE_WIDTH: 0.456778
G1 X130.178 Y123.699 E.00794
G1 X129.837 Y123.234 E.01944
; LINE_WIDTH: 0.420497
G1 X129.609 Y122.748 E.01652
G1 X129.503 Y122.191 E.01744
G1 X129.526 Y121.762 E.0132
G2 X127.893 Y121.577 I-1.727 J7.932 E.05065
G2 X126.482 Y121.78 I.265 J6.826 E.04391
G1 X126.482 Y122.172 E.01204
G1 X126.371 Y122.801 E.01966
G1 X126.161 Y123.238 E.01491
G1 X125.824 Y123.656 E.01654
G1 X125.563 Y123.873 E.01044
G3 X127.05 Y123.31 I2.503 J4.361 E.04914
M204 S10000
G1 X127.264 Y122.44 F42000
; LINE_WIDTH: 0.536883
G1 F3294
M204 S6000
G1 X127.902 Y122.392 E.02572
G1 X128.665 Y122.439 E.0308
M204 S10000
G1 X129.197 Y122.977 F42000
; LINE_WIDTH: 0.41999
G1 F3294
M204 S6000
G1 X129.308 Y123.001 E.00349
G3 X129.121 Y122.059 I2.783 J-1.041 E.02965
G1 X128.367 Y121.966 E.02336
G1 X127.49 Y121.974 E.02694
G1 X126.869 Y122.072 E.0193
G1 X126.787 Y122.704 E.01956
G1 X126.695 Y123 E.00955
G1 X127.197 Y122.891 E.01581
G1 X127.933 Y122.829 E.02267
G1 X128.669 Y122.872 E.02267
G1 X129.138 Y122.965 E.01469
M204 S10000
G1 X130.178 Y123.699 F42000
; LINE_WIDTH: 0.469515
G1 F3294
M204 S6000
G1 X130.4 Y123.842 E.00921
; LINE_WIDTH: 0.436225
G1 X130.623 Y123.986 E.00849
; LINE_WIDTH: 0.407367
G3 X132.093 Y125.513 I-3.164 J4.518 E.06335
M204 S10000
G1 X132.127 Y125.563 F42000
; LINE_WIDTH: 0.422416
G1 F3294
M204 S6000
G3 X132.74 Y127.278 I-4.593 J2.611 E.05661
G1 X132.795 Y127.96 E.02116
G1 X132.752 Y128.642 E.02116
G3 X132.39 Y129.96 I-5.461 J-.791 E.04235
; LINE_WIDTH: 0.456813
G1 X132.301 Y130.178 E.00794
G1 X132.766 Y129.837 E.01944
; LINE_WIDTH: 0.420237
G1 X133.252 Y129.609 E.01651
G1 X133.809 Y129.503 E.01743
G1 X134.238 Y129.526 E.01319
G1 X134.346 Y128.955 E.01787
G1 X134.417 Y128.128 E.02549
G2 X134.219 Y126.48 I-5.376 J-.191 E.05124
G1 X133.708 Y126.48 E.01572
G1 X133.202 Y126.372 E.01592
G1 X132.763 Y126.161 E.01498
G1 X132.344 Y125.824 E.01653
G1 X132.165 Y125.609 E.0086
M204 S10000
G1 X133.561 Y127.28 F42000
; LINE_WIDTH: 0.542268
G1 F3294
M204 S6000
G3 X133.566 Y128.662 I-6.743 J.712 E.0563
M204 S10000
G1 X133.143 Y128.457 F42000
; LINE_WIDTH: 0.41999
G1 F3294
M204 S6000
G3 X132.999 Y129.308 I-8.057 J-.928 E.02653
G3 X133.943 Y129.12 I1.05 J2.817 E.02969
G2 X133.929 Y126.877 I-5.688 J-1.088 E.06936
G1 X133.261 Y126.782 E.02074
G1 X133 Y126.695 E.00848
G1 X133.109 Y127.197 E.01581
G1 X133.171 Y127.933 E.02267
G1 X133.146 Y128.397 E.01429
M204 S10000
G1 X132.301 Y130.178 F42000
; LINE_WIDTH: 0.46956
G1 F3294
M204 S6000
G1 X132.158 Y130.4 E.00921
; LINE_WIDTH: 0.43624
G1 X132.014 Y130.623 E.00849
; LINE_WIDTH: 0.407368
G3 X130.487 Y132.093 I-4.517 J-3.163 E.06335
M204 S10000
G1 X128.892 Y132.704 F42000
; LINE_WIDTH: 0.423623
G1 F3294
M204 S6000
G1 X128.04 Y132.795 E.02656
G1 X127.358 Y132.752 E.02122
G3 X126.039 Y132.393 I.827 J-5.636 E.04249
; LINE_WIDTH: 0.459128
G1 X125.842 Y132.314 E.00723
G1 X126.163 Y132.766 E.01883
; LINE_WIDTH: 0.420496
G1 X126.391 Y133.252 E.01652
G1 X126.497 Y133.809 E.01744
G1 X126.474 Y134.238 E.0132
G1 X127.045 Y134.346 E.01788
G1 X127.872 Y134.417 E.02552
G2 X129.518 Y134.219 I.191 J-5.373 E.05121
G1 X129.519 Y133.827 E.01208
G1 X129.629 Y133.199 E.01962
G1 X129.839 Y132.763 E.01491
G1 X130.176 Y132.344 E.01654
G1 X130.437 Y132.127 E.01045
G3 X128.95 Y132.69 I-2.503 J-4.362 E.04914
M204 S10000
G1 X128.736 Y133.56 F42000
; LINE_WIDTH: 0.542117
G1 F3294
M204 S6000
G3 X127.338 Y133.566 I-.728 J-6.736 E.05693
M204 S10000
G1 X127.543 Y133.143 F42000
; LINE_WIDTH: 0.41999
G1 F3294
M204 S6000
G3 X126.692 Y132.999 I.926 J-8.042 E.02653
G3 X126.88 Y133.943 I-2.817 J1.05 E.02969
G2 X129.131 Y133.927 I1.088 J-5.68 E.06961
G1 X129.213 Y133.296 E.01956
G1 X129.305 Y133 E.00955
G1 X128.803 Y133.109 E.01581
G1 X128.067 Y133.171 E.02267
G1 X127.603 Y133.146 E.01429
M204 S10000
G1 X125.842 Y132.314 F42000
; LINE_WIDTH: 0.472175
G1 F3294
M204 S6000
G1 X125.609 Y132.164 E.00966
; LINE_WIDTH: 0.437125
G1 X125.377 Y132.014 E.00888
; LINE_WIDTH: 0.407393
G3 X123.907 Y130.487 I3.162 J-4.517 E.06336
; CHANGE_LAYER
; Z_HEIGHT: 1
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F9877.275
G1 X124.467 Y131.231 E-.35396
G1 X124.898 Y131.64 E-.22569
G1 X125.272 Y131.932 E-.18035
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 5/26
; update layer progress
M73 L5
M991 S0 P4 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z1.2 I1.138 J-.43 P1  F42000
G1 X124.6 Y130.155 Z1.2
G1 Z1
M73 P65 R3
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3540
M204 S6000
G1 X124.337 Y129.673 E.01822
G3 X127.427 Y124.014 I3.662 J-1.673 E.24796
G1 X127.646 Y123.999 E.00728
G1 X128 Y123.973 E.01178
G3 X124.632 Y130.206 I0 J4.026 E.55195
M204 S10000
G1 X124.944 Y129.964 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3540
M204 S5000
G3 X127.483 Y124.403 I3.056 J-1.965 E.2232
G1 X127.674 Y124.39 E.00588
G1 X128 Y124.366 E.01005
G3 X124.976 Y130.014 I0 J3.633 E.46047
; WIPE_START
G1 F9547.055
M204 S6000
G1 X124.695 Y129.509 E-.21971
G1 X124.513 Y129.024 E-.197
G1 X124.403 Y128.517 E-.197
G1 X124.376 Y128.133 E-.14629
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X125.711 Y134.183 Z1.4 F42000
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3540
M204 S6000
G1 X125.711 Y134.141 E.0014
G2 X125.733 Y133.903 I-2.207 J-.332 E.00793
G2 X125.081 Y132.732 I-1.485 J.06 E.04613
G3 X123.268 Y130.919 I3.141 J-4.954 E.08574
G2 X121.428 Y130.4 I-1.233 J.851 E.06878
G1 X121.067 Y130.569 E.01322
G3 X121.067 Y125.431 I6.966 J-2.569 E.17402
G2 X122.097 Y125.733 I1.125 J-1.927 E.03597
G2 X123.268 Y125.081 I-.06 J-1.485 E.04613
G3 X125.081 Y123.268 I4.954 J3.141 E.08574
G2 X125.6 Y121.428 I-.851 J-1.233 E.06879
G1 X125.431 Y121.067 E.01321
G3 X128.416 Y120.619 I2.623 J7.318 E.10075
G3 X130.569 Y121.067 I-.569 J8.146 E.07316
G2 X130.267 Y122.097 I1.927 J1.125 E.03597
G2 X130.919 Y123.268 I1.485 J-.06 E.04613
G3 X132.732 Y125.081 I-3.141 J4.954 E.08574
G2 X134.572 Y125.6 I1.233 J-.851 E.06878
G1 X134.933 Y125.431 E.01322
G3 X134.933 Y130.569 I-6.966 J2.569 E.17402
G2 X133.903 Y130.267 I-1.125 J1.927 E.03597
G2 X132.732 Y130.919 I.06 J1.485 E.04613
G3 X130.919 Y132.732 I-4.954 J-3.141 E.08574
G2 X130.4 Y134.572 I.851 J1.233 E.06878
G1 X130.569 Y134.933 E.01322
G3 X125.431 Y134.933 I-2.569 J-6.966 E.17402
G2 X125.649 Y134.424 I-1.927 J-1.125 E.01841
G1 X125.696 Y134.241 E.00627
M204 S10000
G1 X125.293 Y134.25 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3540
M204 S5000
G1 X125.326 Y134.098 E.00479
G2 X124.845 Y133.046 I-1.102 J-.133 E.03739
G3 X122.954 Y131.155 I3.35 J-5.241 E.08282
G2 X121.83 Y130.683 I-.918 J.612 E.03971
G1 X121.585 Y130.76 E.00787
G1 X121.005 Y131.03 E.01968
G1 F2040
G1 X120.86 Y131.098 E.0049
G3 X120.86 Y124.902 I7.122 J-3.098 E.1958
G1 F3158.835
G1 X121.005 Y124.97 E.0049
G1 F3540
G1 X121.679 Y125.275 E.02275
G2 X122.954 Y124.845 I.356 J-1.051 E.04443
G3 X124.845 Y122.954 I5.241 J3.35 E.08282
G2 X125.317 Y121.83 I-.612 J-.918 E.03971
G1 X125.24 Y121.585 E.00788
G1 X124.97 Y121.005 E.01968
G1 F2040
G1 X124.902 Y120.86 E.0049
G3 X128.436 Y120.228 I3.086 J7.052 E.11132
G3 X131.098 Y120.86 I-.461 J7.855 E.08449
G1 F3158.835
G1 X131.03 Y121.005 E.0049
G1 F3540
G1 X130.725 Y121.679 E.02275
G2 X131.155 Y122.954 I1.051 J.356 E.04443
G3 X133.046 Y124.845 I-3.35 J5.241 E.08282
G2 X134.17 Y125.317 I.918 J-.612 E.03971
G1 X134.415 Y125.24 E.00787
G1 X134.995 Y124.97 E.01968
G1 F2040
G1 X135.14 Y124.902 E.0049
G3 X135.14 Y131.098 I-7.122 J3.098 E.1958
G1 F3158.835
G1 X134.995 Y131.03 E.0049
G1 F3540
G1 X134.321 Y130.725 E.02275
G2 X133.046 Y131.155 I-.356 J1.051 E.04443
G3 X131.155 Y133.046 I-5.241 J-3.35 E.08282
G2 X130.683 Y134.17 I.612 J.918 E.03971
G1 X130.76 Y134.415 E.00787
G1 X131.03 Y134.995 E.01968
G1 F2040
G1 X131.098 Y135.14 E.0049
G3 X124.902 Y135.14 I-3.098 J-7.122 E.1958
G1 F3158.835
G1 X124.97 Y134.995 E.0049
G1 F3540
G1 X125.275 Y134.321 E.02275
G1 X125.279 Y134.308 E.0004
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.326 Y134.098 E-.08206
G1 X125.34 Y133.913 E-.07036
G1 X125.283 Y133.608 E-.11779
G1 X125.193 Y133.408 E-.08348
G1 X125.036 Y133.2 E-.0991
G1 X124.845 Y133.046 E-.09307
G1 X124.394 Y132.732 E-.20887
G1 X124.383 Y132.723 E-.00527
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z1.4 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z1.4
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z1.4 F4000
            G39.3 S1
            G0 Z1.4 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X123.686 Y125.842 F42000
G1 Z1
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.472195
G1 F3540
M204 S6000
G1 X123.836 Y125.609 E.00967
; LINE_WIDTH: 0.437145
G1 X123.986 Y125.377 E.00888
; LINE_WIDTH: 0.407387
G3 X125.513 Y123.907 I4.516 J3.162 E.06336
M204 S10000
G1 X123.504 Y126.361 F42000
; LINE_WIDTH: 0.437423
G1 F3540
M204 S6000
G1 X123.595 Y126.101 E.00884
; LINE_WIDTH: 0.460653
G1 X123.686 Y125.842 E.00936
G1 X123.236 Y126.162 E.01879
; LINE_WIDTH: 0.420364
G1 X122.712 Y126.399 E.01769
G1 X122.196 Y126.496 E.01615
G1 X121.701 Y126.474 E.01525
G1 X121.564 Y126.442 E.00431
G1 X121.457 Y127.013 E.01788
G1 X121.385 Y127.862 E.02621
G2 X121.566 Y129.551 I6.366 J.171 E.05239
G1 X122.081 Y129.499 E.01591
G1 X122.679 Y129.591 E.01864
G1 X123.239 Y129.84 E.01883
G1 X123.656 Y130.176 E.01649
G1 X123.873 Y130.437 E.01044
G3 X123.26 Y128.722 I4.593 J-2.611 E.0563
G1 X123.205 Y128.04 E.02104
G3 X123.487 Y126.418 I5.465 J.113 E.05083
M204 S10000
G1 X122.969 Y126.84 F42000
; LINE_WIDTH: 0.41999
G1 F3540
M204 S6000
G1 X123.002 Y126.687 E.00484
G3 X121.859 Y126.868 I-1.041 J-2.862 E.0358
G2 X121.863 Y129.136 I5.877 J1.122 E.0701
G1 X122.34 Y129.145 E.01466
G1 X123 Y129.304 E.02087
G1 X122.891 Y128.803 E.01578
G1 X122.829 Y128.067 E.02267
G3 X122.959 Y126.9 I5.597 J.034 E.03617
M204 S10000
G1 X122.493 Y127.515 F42000
; LINE_WIDTH: 0.393132
G1 F3540
M204 S6000
G1 X122.525 Y127.194 E.00922
G1 X122.174 Y127.235 E.0101
G2 X122.17 Y128.764 I6.734 J.783 E.04372
G1 X122.525 Y128.809 E.01022
G1 X122.467 Y128.093 E.0205
G1 X122.49 Y127.575 E.01479
M204 S10000
G1 X123.858 Y129.51 F42000
; LINE_WIDTH: 0.41999
G1 F3540
M204 S6000
G1 X123.676 Y128.863 E.02066
G1 X123.581 Y128.013 E.02627
G3 X125.033 Y124.732 I4.505 J.032 E.11341
G1 X125.6 Y124.29 E.02207
G3 X126.653 Y123.797 I2.623 J4.236 E.0358
G1 X127.358 Y123.628 E.02228
G1 X127.987 Y123.581 E.01937
G3 X131.268 Y125.033 I-.032 J4.505 E.11341
G1 X131.71 Y125.6 E.02207
G1 X131.955 Y126.043 E.01557
G1 X132.22 Y126.7 E.02175
G1 X132.372 Y127.358 E.02075
G1 X132.419 Y127.987 E.01937
G3 X130.967 Y131.268 I-4.505 J-.032 E.11341
G1 X130.4 Y131.71 E.02207
G3 X129.347 Y132.203 I-2.624 J-4.238 E.0358
G1 X128.642 Y132.372 E.02228
G1 X128.013 Y132.419 E.01937
G3 X124.732 Y130.967 I.032 J-4.506 E.11341
G1 X124.29 Y130.4 E.02207
G3 X123.881 Y129.566 I3.711 J-2.334 E.02861
M204 S10000
G1 X123.702 Y130.843 F42000
; LINE_WIDTH: 0.41999
G1 F3540
M204 S6000
G1 X124.189 Y131.485 E.02476
G1 X124.875 Y132.112 E.02857
G1 X125.579 Y132.631 E.02687
M73 P66 R3
G1 X125.885 Y133.033 E.0155
G1 X126.079 Y133.58 E.01785
G3 X126.107 Y134.214 I-1.492 J.382 E.01962
G1 X125.965 Y134.693 E.01535
G2 X130.042 Y134.69 I2.034 J-6.726 E.12709
G1 X129.903 Y134.299 E.01275
G1 X129.887 Y133.797 E.01543
G1 X129.975 Y133.347 E.01412
G1 X130.141 Y132.989 E.01211
G1 X130.414 Y132.637 E.0137
G3 X131.485 Y131.811 I19.999 J24.83 E.04155
G1 X132.112 Y131.125 E.02857
G1 X132.631 Y130.421 E.02687
G1 X133.033 Y130.115 E.0155
G1 X133.58 Y129.921 E.01785
G3 X134.214 Y129.893 I.382 J1.492 E.01962
G1 X134.693 Y130.035 E.01535
G2 X134.69 Y125.958 I-6.726 J-2.034 E.12709
G1 X134.307 Y126.095 E.01252
G3 X133.542 Y126.075 I-.304 J-2.977 E.02359
G1 X133.036 Y125.885 E.01658
G1 X132.637 Y125.586 E.01535
G3 X131.811 Y124.515 I24.83 J-19.999 E.04155
G1 X131.125 Y123.888 E.02857
G1 X130.421 Y123.369 E.02687
G1 X130.115 Y122.967 E.0155
G1 X129.921 Y122.42 E.01785
G3 X129.894 Y121.786 I1.491 J-.382 E.01963
G1 X130.035 Y121.307 E.01535
G2 X125.958 Y121.31 I-2.034 J6.719 E.12709
G1 X126.097 Y121.701 E.01275
G1 X126.114 Y122.203 E.01543
G1 X126.025 Y122.653 E.01412
G1 X125.859 Y123.011 E.01211
G1 X125.586 Y123.363 E.0137
G3 X124.515 Y124.189 I-20.017 J-24.854 E.04155
G1 X123.888 Y124.875 E.02857
G1 X123.369 Y125.579 E.02687
G1 X122.967 Y125.885 E.0155
G1 X122.42 Y126.079 E.01785
G3 X121.786 Y126.107 I-.382 J-1.492 E.01962
G1 X121.307 Y125.965 E.01535
G2 X121.31 Y130.042 I6.726 J2.034 E.12709
G1 X121.701 Y129.903 E.01275
G1 X122.203 Y129.887 E.01543
G1 X122.653 Y129.975 E.01412
G1 X123.011 Y130.141 E.01211
G1 X123.363 Y130.414 E.0137
G1 X123.665 Y130.796 E.01495
M204 S10000
G1 X125.842 Y132.314 F42000
; LINE_WIDTH: 0.472195
G1 F3540
M204 S6000
G1 X125.609 Y132.164 E.00967
; LINE_WIDTH: 0.437145
G1 X125.377 Y132.014 E.00888
; LINE_WIDTH: 0.407392
G3 X123.907 Y130.487 I3.162 J-4.517 E.06336
M204 S10000
G1 X126.361 Y132.496 F42000
; LINE_WIDTH: 0.437423
G1 F3540
M204 S6000
G1 X126.101 Y132.405 E.00884
; LINE_WIDTH: 0.460653
G1 X125.842 Y132.314 E.00936
G1 X126.162 Y132.764 E.01879
; LINE_WIDTH: 0.42032
G1 X126.399 Y133.288 E.01769
G1 X126.496 Y133.804 E.01615
G1 X126.474 Y134.299 E.01525
G1 X126.442 Y134.436 E.00431
G1 X127.013 Y134.543 E.01787
G1 X127.862 Y134.615 E.02621
G2 X129.551 Y134.434 I.171 J-6.366 E.05238
G1 X129.499 Y133.919 E.01591
G1 X129.591 Y133.321 E.01864
G1 X129.84 Y132.761 E.01882
G1 X130.176 Y132.344 E.01649
G1 X130.437 Y132.127 E.01044
G3 X128.722 Y132.74 I-2.611 J-4.592 E.05629
G1 X128.04 Y132.795 E.02104
G3 X126.418 Y132.513 I.113 J-5.465 E.05083
M204 S10000
G1 X126.84 Y133.031 F42000
; LINE_WIDTH: 0.41999
G1 F3540
M204 S6000
G1 X126.687 Y132.998 E.00484
G3 X126.868 Y134.141 I-2.861 J1.041 E.0358
G2 X129.136 Y134.137 I1.122 J-5.876 E.0701
G1 X129.145 Y133.66 E.01466
G1 X129.304 Y133 E.02087
G1 X128.803 Y133.109 E.01578
G1 X128.067 Y133.171 E.02267
G3 X126.9 Y133.041 I.034 J-5.598 E.03617
M204 S10000
G1 X127.515 Y133.507 F42000
; LINE_WIDTH: 0.393131
G1 F3540
M204 S6000
G1 X127.194 Y133.475 E.00922
G1 X127.235 Y133.826 E.0101
G2 X128.764 Y133.83 I.783 J-6.733 E.04372
G1 X128.809 Y133.475 E.01022
G1 X128.093 Y133.533 E.0205
G1 X127.575 Y133.51 E.01479
M204 S10000
G1 X132.301 Y130.178 F42000
; LINE_WIDTH: 0.46956
G1 F3540
M204 S6000
G1 X132.158 Y130.4 E.00921
; LINE_WIDTH: 0.43624
G1 X132.014 Y130.623 E.00849
; LINE_WIDTH: 0.407316
G3 X130.491 Y132.091 I-4.507 J-3.152 E.0632
M204 S10000
G1 X132.496 Y129.639 F42000
; LINE_WIDTH: 0.436548
G1 F3540
M204 S6000
G1 X132.399 Y129.909 E.00918
; LINE_WIDTH: 0.458619
G1 X132.301 Y130.178 E.0097
G1 X132.764 Y129.838 E.01942
; LINE_WIDTH: 0.420366
G1 X133.288 Y129.601 E.01769
G1 X133.804 Y129.504 E.01615
G1 X134.299 Y129.526 E.01525
G1 X134.436 Y129.558 E.00431
G1 X134.543 Y128.987 E.01788
G1 X134.615 Y128.138 E.02621
G2 X134.434 Y126.45 I-6.365 J-.171 E.05237
G1 X133.972 Y126.497 E.0143
G1 X133.409 Y126.428 E.01744
G1 X132.904 Y126.238 E.0166
G1 X132.442 Y125.918 E.01729
G1 X132.127 Y125.563 E.01461
G3 X132.74 Y127.278 I-4.592 J2.611 E.0563
G1 X132.795 Y127.96 E.02104
G3 X132.513 Y129.582 I-5.465 J-.113 E.05083
M204 S10000
G1 X133.031 Y129.16 F42000
; LINE_WIDTH: 0.41999
G1 F3540
M204 S6000
G1 X132.998 Y129.313 E.00484
G3 X134.141 Y129.132 I1.041 J2.861 E.0358
G2 X134.144 Y126.896 I-5.888 J-1.124 E.06909
G3 X132.995 Y126.675 I.041 J-3.314 E.03612
G1 X133.109 Y127.197 E.01641
G1 X133.171 Y127.933 E.02267
G3 X133.041 Y129.1 I-5.595 J-.034 E.03617
M204 S10000
G1 X133.507 Y128.485 F42000
; LINE_WIDTH: 0.393042
G1 F3540
M204 S6000
G1 X133.475 Y128.806 E.00922
G1 X133.826 Y128.765 E.01009
G2 X133.829 Y127.229 I-6.742 J-.783 E.04391
G1 X133.482 Y127.216 E.00993
G3 X133.51 Y128.425 I-4.992 J.721 E.03457
M204 S10000
G1 X130.178 Y123.699 F42000
; LINE_WIDTH: 0.469545
G1 F3540
M204 S6000
G1 X130.4 Y123.842 E.00921
; LINE_WIDTH: 0.436235
G1 X130.623 Y123.986 E.00849
; LINE_WIDTH: 0.407364
G3 X132.093 Y125.513 I-3.163 J4.517 E.06336
M204 S10000
G1 X129.639 Y123.504 F42000
; LINE_WIDTH: 0.436543
G1 F3540
M204 S6000
G1 X129.909 Y123.601 E.00918
; LINE_WIDTH: 0.458607
G1 X130.178 Y123.699 E.0097
G1 X129.838 Y123.236 E.01942
; LINE_WIDTH: 0.420364
G1 X129.601 Y122.712 E.01769
G1 X129.504 Y122.196 E.01616
G1 X129.526 Y121.701 E.01525
G1 X129.558 Y121.564 E.00431
G1 X128.987 Y121.458 E.01787
G1 X128.137 Y121.384 E.02623
G2 X126.449 Y121.566 I-.166 J6.393 E.05237
G1 X126.501 Y122.08 E.01591
G1 X126.409 Y122.679 E.01864
G1 X126.16 Y123.239 E.01882
G1 X125.824 Y123.656 E.01649
G1 X125.563 Y123.873 E.01044
G3 X127.278 Y123.26 I2.611 J4.593 E.0563
G1 X127.96 Y123.205 E.02104
G3 X129.582 Y123.487 I-.113 J5.465 E.05083
M204 S10000
G1 X129.16 Y122.969 F42000
; LINE_WIDTH: 0.41999
G1 F3540
M204 S6000
G1 X129.313 Y123.002 E.00483
G3 X129.132 Y121.859 I2.862 J-1.041 E.0358
G2 X126.864 Y121.863 I-1.122 J5.889 E.0701
G1 X126.855 Y122.34 E.01466
G1 X126.696 Y123 E.02087
G1 X127.198 Y122.891 E.01578
G1 X127.933 Y122.829 E.02267
G3 X129.1 Y122.959 I-.037 J5.621 E.03617
M204 S10000
G1 X128.48 Y122.492 F42000
; LINE_WIDTH: 0.393129
G1 F3540
M204 S6000
G1 X128.806 Y122.525 E.00935
G1 X128.765 Y122.174 E.0101
G2 X127.236 Y122.17 I-.782 J6.715 E.04372
G1 X127.191 Y122.525 E.01022
G1 X127.907 Y122.467 E.0205
G1 X128.42 Y122.49 E.01467
; CHANGE_LAYER
; Z_HEIGHT: 1.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F10279.578
G1 X127.907 Y122.467 E-.1953
G1 X127.191 Y122.525 E-.27295
G1 X127.236 Y122.17 E-.13604
G1 X127.494 Y122.139 E-.09878
G1 X127.644 Y122.135 E-.05694
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 6/26
; update layer progress
M73 L6
M991 S0 P5 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z1.4 I-1.14 J-.426 P1  F42000
G1 X124.627 Y130.197 Z1.4
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3659
M204 S6000
G1 X124.613 Y130.177 E.00083
G3 X127.427 Y124.014 I3.387 J-2.177 E.26704
G1 X127.576 Y124.003 E.00497
G1 X128 Y123.973 E.01409
G3 X124.957 Y130.637 I0 J4.027 E.53405
G1 X124.663 Y130.245 E.01624
M204 S10000
G1 X124.943 Y129.965 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3659
M204 S5000
G1 X124.943 Y129.964 E.00002
G3 X127.483 Y124.403 I3.056 J-1.965 E.22321
G1 X127.604 Y124.395 E.00375
G1 X128 Y124.366 E.01219
G3 X125.254 Y130.379 I0 J3.633 E.44638
G1 X124.979 Y130.013 E.01407
; WIPE_START
G1 F9547.055
M204 S6000
G1 X124.943 Y129.964 E-.02302
G1 X124.695 Y129.509 E-.19699
G1 X124.513 Y129.024 E-.19699
G1 X124.403 Y128.517 E-.19702
G1 X124.376 Y128.134 E-.14597
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X125.714 Y134.166 Z1.6 F42000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F3659
M204 S6000
G1 X125.722 Y134.128 E.0013
G2 X125.081 Y132.732 I-1.466 J-.172 E.05359
G3 X123.268 Y130.919 I3.141 J-4.954 E.08574
G2 X121.428 Y130.4 I-1.229 J.835 E.06889
G1 X120.885 Y130.653 E.01988
G3 X120.885 Y125.347 I7.168 J-2.653 E.17978
G2 X121.589 Y125.66 I2.248 J-4.1 E.02558
G2 X123.268 Y125.081 I.456 J-1.404 E.06324
G3 X125.081 Y123.268 I4.954 J3.141 E.08574
G2 X125.6 Y121.428 I-.835 J-1.229 E.06889
G1 X125.347 Y120.885 E.01988
G3 X128.377 Y120.417 I2.718 J7.554 E.10236
G3 X130.653 Y120.885 I-.538 J8.383 E.07733
G2 X130.34 Y121.589 I4.093 J2.245 E.02558
G2 X130.919 Y123.268 I1.404 J.456 E.06323
G3 X132.732 Y125.081 I-3.141 J4.954 E.08574
G2 X134.572 Y125.6 I1.229 J-.835 E.06888
G1 X135.115 Y125.347 E.01989
G3 X135.115 Y130.653 I-7.168 J2.653 E.17978
G2 X134.411 Y130.34 I-2.245 J4.093 E.02558
G2 X132.732 Y130.919 I-.456 J1.404 E.06323
G3 X130.919 Y132.732 I-4.954 J-3.141 E.08574
G2 X130.4 Y134.572 I.835 J1.229 E.06889
G1 X130.653 Y135.115 E.01988
G3 X125.347 Y135.115 I-2.653 J-7.168 E.17978
G2 X125.66 Y134.411 I-4.093 J-2.245 E.02558
G1 X125.701 Y134.225 E.00633
M204 S10000
G1 X125.28 Y134.275 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F3659
M204 S5000
G1 X125.332 Y134.085 E.00604
G2 X124.845 Y133.046 I-1.087 J-.125 E.03713
G3 X122.954 Y131.155 I3.35 J-5.241 E.08282
G2 X121.586 Y130.759 I-.915 J.6 E.04768
G1 X120.823 Y131.115 E.02584
G1 F2040
G1 X120.679 Y131.182 E.0049
G3 X120.679 Y124.818 I7.325 J-3.182 E.20114
G1 F3158.835
G1 X120.823 Y124.885 E.0049
G1 F3659
G1 X121.589 Y125.242 E.02595
G2 X122.954 Y124.845 I.451 J-.997 E.04757
G3 X124.845 Y122.954 I5.241 J3.35 E.08282
G2 X125.241 Y121.586 I-.6 J-.915 E.04768
G1 X124.885 Y120.823 E.02584
G1 F2040
G1 X124.818 Y120.679 E.0049
G3 X128.398 Y120.025 I3.174 J7.254 E.11282
G3 X131.182 Y120.679 I-.419 J8.046 E.08836
G1 F3158.835
G1 X131.115 Y120.823 E.0049
G1 F3659
G1 X130.758 Y121.589 E.02595
G2 X131.155 Y122.954 I.997 J.451 E.04757
G3 X133.046 Y124.845 I-3.35 J5.241 E.08282
G2 X134.414 Y125.241 I.915 J-.6 E.04768
G1 X135.177 Y124.885 E.02585
G1 F2040
G1 X135.321 Y124.818 E.0049
G3 X135.321 Y131.182 I-7.325 J3.182 E.20114
G1 F3158.835
G1 X135.177 Y131.115 E.0049
G1 F3659
G1 X134.411 Y130.758 E.02595
G2 X133.046 Y131.155 I-.451 J.997 E.04757
G3 X131.155 Y133.046 I-5.241 J-3.35 E.08282
G2 X130.759 Y134.414 I.6 J.915 E.04768
G1 X131.115 Y135.177 E.02584
G1 F2040
G1 X131.182 Y135.321 E.0049
G3 X124.818 Y135.321 I-3.182 J-7.325 E.20114
G1 F3158.835
G1 X124.885 Y135.177 E.0049
G1 F3659
G1 X125.242 Y134.411 E.02595
G1 X125.264 Y134.332 E.00251
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.332 Y134.085 E-.09745
G1 X125.34 Y133.912 E-.0658
G1 X125.298 Y133.657 E-.09843
M73 P67 R3
G1 X125.193 Y133.408 E-.10278
G1 X125.036 Y133.2 E-.09896
G1 X124.845 Y133.046 E-.09307
G1 X124.405 Y132.74 E-.20351
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z1.6 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z1.6
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z1.6 F4000
            G39.3 S1
            G0 Z1.6 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X128.474 Y122.445 F42000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.492339
G1 F3659
M204 S6000
G1 X128.749 Y122.469 E.0101
G1 X128.718 Y122.026 E.01625
G2 X127.276 Y122.015 I-.77 J6.194 E.05293
G1 X127.256 Y122.463 E.01644
G3 X128.414 Y122.442 I.664 J4.682 E.04253
M204 S10000
G1 X129.164 Y122.97 F42000
; LINE_WIDTH: 0.41999
G1 F3659
M204 S6000
G1 X129.313 Y123.002 E.0047
G3 X129.122 Y122.178 I2.874 J-1.101 E.02608
G1 X129.173 Y121.666 E.01579
G1 X128.304 Y121.562 E.02691
G1 X127.462 Y121.575 E.02588
G1 X126.846 Y121.664 E.01912
G3 X126.831 Y122.539 I-5.599 J.341 E.02694
G1 X126.674 Y123.005 E.0151
G1 X127.198 Y122.891 E.01646
G1 X127.933 Y122.829 E.02267
G3 X129.105 Y122.96 I-.042 J5.665 E.0363
M204 S10000
G1 X129.641 Y123.504 F42000
; LINE_WIDTH: 0.436538
G1 F3659
M204 S6000
G1 X129.909 Y123.601 E.00916
; LINE_WIDTH: 0.458595
G1 X130.178 Y123.699 E.00967
G1 X129.839 Y123.237 E.01938
; LINE_WIDTH: 0.420348
G1 X129.603 Y122.716 E.01761
G1 X129.504 Y122.2 E.01616
G3 X129.607 Y121.37 I4.812 J.177 E.02575
G2 X128.33 Y121.185 I-2.737 J14.395 E.0397
G1 X127.442 Y121.198 E.02731
G2 X126.39 Y121.374 I.442 J5.871 E.03285
G1 X126.489 Y121.865 E.01538
G1 X126.467 Y122.401 E.0165
G3 X126.159 Y123.24 I-3.598 J-.845 E.02755
G1 X125.824 Y123.656 E.01644
G1 X125.563 Y123.873 E.01044
G3 X127.278 Y123.26 I2.611 J4.593 E.0563
G1 X127.96 Y123.205 E.02104
G3 X129.583 Y123.487 I-.101 J5.393 E.05088
M204 S10000
G1 X130.178 Y123.699 F42000
; LINE_WIDTH: 0.46953
G1 F3659
M204 S6000
G1 X130.4 Y123.842 E.00921
; LINE_WIDTH: 0.43623
G1 X130.623 Y123.986 E.00849
; LINE_WIDTH: 0.413113
G3 X132.094 Y125.513 I-3.061 J4.42 E.06437
M204 S10000
G1 X133.559 Y128.465 F42000
; LINE_WIDTH: 0.494401
G1 F3659
M204 S6000
G1 X133.536 Y128.744 E.01029
G1 X133.982 Y128.714 E.01645
G2 X133.986 Y127.276 I-6.625 J-.735 E.05302
G1 X133.536 Y127.255 E.01654
G3 X133.561 Y128.405 I-5.226 J.689 E.04241
M204 S10000
G1 X133.145 Y128.436 F42000
; LINE_WIDTH: 0.41999
G1 F3659
M204 S6000
G3 X132.998 Y129.313 I-7.585 J-.819 E.02736
G3 X133.834 Y129.121 I1.096 J2.859 E.02645
G1 X134.336 Y129.174 E.01552
G2 X134.336 Y126.846 I-6.038 J-1.165 E.07196
G3 X133.461 Y126.831 I-.342 J-5.549 E.02694
G1 X132.995 Y126.674 E.0151
G1 X133.109 Y127.198 E.01646
G1 X133.171 Y127.933 E.02267
G1 X133.148 Y128.376 E.01363
M204 S10000
G1 X132.496 Y129.641 F42000
; LINE_WIDTH: 0.436543
G1 F3659
M204 S6000
G1 X132.399 Y129.909 E.00916
; LINE_WIDTH: 0.458607
G1 X132.301 Y130.178 E.00967
G1 X132.763 Y129.839 E.01938
; LINE_WIDTH: 0.420347
G1 X133.284 Y129.603 E.01761
G1 X133.8 Y129.504 E.01615
G3 X134.63 Y129.607 I-.181 J4.841 E.02575
G2 X134.626 Y126.39 I-6.864 J-1.599 E.09982
G1 X134.135 Y126.489 E.01538
G1 X133.599 Y126.467 E.01651
G3 X132.76 Y126.159 I.845 J-3.596 E.02755
G1 X132.344 Y125.824 E.01644
G1 X132.127 Y125.563 E.01044
G3 X132.74 Y127.278 I-4.592 J2.611 E.0563
G1 X132.795 Y127.96 E.02104
G3 X132.513 Y129.583 I-5.393 J-.101 E.05088
M204 S10000
G1 X132.301 Y130.178 F42000
; LINE_WIDTH: 0.469545
G1 F3659
M204 S6000
G1 X132.158 Y130.4 E.00921
; LINE_WIDTH: 0.436235
G1 X132.014 Y130.623 E.00849
; LINE_WIDTH: 0.413108
G3 X130.487 Y132.094 I-4.42 J-3.061 E.06437
M204 S10000
G1 X131.858 Y131.406 F42000
; LINE_WIDTH: 0.41999
G1 F3659
M204 S6000
G2 X132.631 Y130.421 I-8.944 J-7.821 E.03849
G1 X133.031 Y130.116 E.01545
G1 X133.582 Y129.921 E.01795
G1 X133.916 Y129.876 E.01035
G1 X134.495 Y129.958 E.01798
G1 X134.876 Y130.116 E.01268
G2 X135.198 Y128.193 I-7.968 J-2.322 E.06002
G2 X134.877 Y125.887 I-7.158 J-.18 E.07187
G1 X134.615 Y126.004 E.00883
G1 X134.151 Y126.112 E.01464
G1 X133.615 Y126.09 E.01649
G1 X133.078 Y125.9 E.0175
G1 X132.664 Y125.613 E.01548
G3 X131.923 Y124.655 I30.646 J-24.457 E.03721
G2 X130.421 Y123.369 I-7.598 J7.352 E.06085
G1 X130.116 Y122.969 E.01545
G1 X129.921 Y122.418 E.01795
G1 X129.876 Y122.084 E.01035
G1 X129.958 Y121.505 E.01798
G1 X130.116 Y121.124 E.01268
G2 X128.95 Y120.88 I-1.651 J4.987 E.03668
G2 X126.231 Y121.023 I-1.007 J6.781 E.08421
G1 X125.887 Y121.123 E.011
G1 X126.004 Y121.385 E.00883
G1 X126.112 Y121.849 E.01464
G1 X126.09 Y122.385 E.01649
G1 X125.9 Y122.922 E.0175
G1 X125.613 Y123.336 E.01548
G3 X124.655 Y124.077 I-24.5 J-30.703 E.03721
G2 X123.369 Y125.579 I7.348 J7.594 E.06085
G1 X122.969 Y125.884 E.01546
G1 X122.418 Y126.079 E.01795
G1 X122.084 Y126.124 E.01035
G1 X121.505 Y126.042 E.01798
G1 X121.124 Y125.884 E.01267
G2 X120.802 Y127.806 I7.97 J2.322 E.06002
G2 X121.123 Y130.113 I7.158 J.18 E.07187
G1 X121.385 Y129.996 E.00883
G1 X121.849 Y129.888 E.01464
G1 X122.385 Y129.91 E.01649
G1 X122.922 Y130.1 E.0175
G1 X123.336 Y130.387 E.01548
G3 X124.077 Y131.345 I-30.661 J24.468 E.03721
G2 X125.579 Y132.631 I7.595 J-7.349 E.06085
G1 X125.884 Y133.031 E.01546
G1 X126.079 Y133.582 E.01795
G1 X126.124 Y133.916 E.01035
G1 X126.042 Y134.495 E.01798
G1 X125.884 Y134.876 E.01268
G2 X127.807 Y135.198 I2.322 J-7.968 E.06002
G2 X130.113 Y134.877 I.18 J-7.158 E.07187
G1 X129.996 Y134.615 E.00883
G1 X129.888 Y134.151 E.01464
G1 X129.91 Y133.615 E.01649
G1 X130.1 Y133.078 E.0175
G1 X130.387 Y132.664 E.01548
G3 X131.345 Y131.923 I24.523 J30.733 E.03721
G1 X131.816 Y131.448 E.02054
M204 S10000
G1 X127.535 Y133.559 F42000
; LINE_WIDTH: 0.494404
G1 F3659
M204 S6000
G1 X127.256 Y133.536 E.01029
G1 X127.286 Y133.982 E.01645
G2 X128.724 Y133.986 I.735 J-6.625 E.05302
G1 X128.745 Y133.536 E.01655
G3 X127.595 Y133.561 I-.689 J-5.225 E.04241
M204 S10000
G1 X127.564 Y133.145 F42000
; LINE_WIDTH: 0.41999
G1 F3659
M204 S6000
G3 X126.687 Y132.998 I.82 J-7.59 E.02736
G3 X126.879 Y133.834 I-2.86 J1.096 E.02645
G1 X126.826 Y134.336 E.01552
G2 X128.6 Y134.419 I1.239 J-7.497 E.05467
G1 X129.154 Y134.336 E.01723
G3 X129.169 Y133.461 I5.55 J-.342 E.02694
G1 X129.326 Y132.995 E.01509
G1 X128.802 Y133.109 E.01646
G1 X128.067 Y133.171 E.02267
G1 X127.624 Y133.148 E.01363
M204 S10000
G1 X126.359 Y132.496 F42000
; LINE_WIDTH: 0.437418
G1 F3659
M204 S6000
G1 X126.1 Y132.405 E.00882
; LINE_WIDTH: 0.460642
G1 X125.842 Y132.314 E.00934
G1 X126.161 Y132.763 E.01875
; LINE_WIDTH: 0.420348
G1 X126.397 Y133.284 E.01761
G1 X126.496 Y133.8 E.01615
G3 X126.393 Y134.63 I-4.841 J-.181 E.02575
G2 X129.61 Y134.626 I1.599 J-6.864 E.09983
G1 X129.511 Y134.135 E.01538
G1 X129.533 Y133.599 E.0165
G3 X129.841 Y132.76 I3.597 J.845 E.02755
G1 X130.176 Y132.344 E.01644
G1 X130.437 Y132.127 E.01044
G3 X128.722 Y132.74 I-2.611 J-4.593 E.0563
G1 X128.04 Y132.795 E.02104
G3 X126.417 Y132.513 I.101 J-5.392 E.05088
M204 S10000
G1 X125.842 Y132.314 F42000
; LINE_WIDTH: 0.47218
G1 F3659
M204 S6000
G1 X125.609 Y132.164 E.00966
; LINE_WIDTH: 0.43714
G1 X125.377 Y132.014 E.00888
; LINE_WIDTH: 0.413143
G3 X123.906 Y130.487 I3.061 J-4.42 E.06438
M204 S10000
G1 X124.045 Y129.957 F42000
; LINE_WIDTH: 0.41999
G1 F3659
M204 S6000
G1 X123.78 Y129.3 E.02177
G1 X123.628 Y128.642 E.02074
G1 X123.581 Y128.013 E.01937
G3 X126.043 Y124.045 I4.405 J-.014 E.15124
G1 X126.7 Y123.78 E.02177
G1 X127.358 Y123.628 E.02074
G1 X127.987 Y123.581 E.01937
G1 X128.523 Y123.618 E.01652
G1 X129.232 Y123.756 E.0222
G3 X131.955 Y126.043 I-1.224 J4.221 E.11248
G1 X132.22 Y126.7 E.02177
G1 X132.372 Y127.358 E.02074
G1 X132.419 Y127.987 E.01937
G1 X132.382 Y128.523 E.01653
G1 X132.244 Y129.232 E.02219
G3 X129.957 Y131.955 I-4.221 J-1.224 E.11248
G1 X129.3 Y132.22 E.02177
G1 X128.642 Y132.372 E.02074
G1 X128.013 Y132.419 E.01937
G1 X127.477 Y132.382 E.01653
G1 X126.768 Y132.244 E.02219
G3 X124.074 Y130.009 I1.22 J-4.212 E.11062
M204 S10000
G1 X122.441 Y127.535 F42000
; LINE_WIDTH: 0.494411
G1 F3659
M204 S6000
G1 X122.464 Y127.256 E.01029
G1 X122.018 Y127.286 E.01645
G2 X122.014 Y128.724 I6.624 J.735 E.05302
G1 X122.464 Y128.745 E.01654
G3 X122.439 Y127.595 I5.226 J-.689 E.04241
M204 S10000
G1 X122.855 Y127.564 F42000
; LINE_WIDTH: 0.41999
G1 F3659
M204 S6000
G3 X123.002 Y126.687 I7.59 J.82 E.02736
G3 X122.166 Y126.879 I-1.097 J-2.862 E.02645
G1 X121.664 Y126.826 E.01552
G2 X121.581 Y128.6 I7.497 J1.239 E.05467
G1 X121.664 Y129.154 E.01723
G3 X122.539 Y129.169 I.342 J5.549 E.02694
G1 X123.005 Y129.326 E.0151
G1 X122.891 Y128.802 E.01646
G1 X122.829 Y128.067 E.02267
G1 X122.852 Y127.624 E.01363
M204 S10000
G1 X123.504 Y126.359 F42000
; LINE_WIDTH: 0.437418
G1 F3659
M204 S6000
G1 X123.595 Y126.1 E.00882
; LINE_WIDTH: 0.460642
G1 X123.686 Y125.841 E.00934
G1 X123.237 Y126.161 E.01875
; LINE_WIDTH: 0.420348
G1 X122.716 Y126.397 E.01761
G1 X122.2 Y126.496 E.01615
G3 X121.37 Y126.393 I.182 J-4.846 E.02575
G2 X121.374 Y129.61 I6.865 J1.599 E.09982
G1 X121.865 Y129.511 E.01538
G1 X122.401 Y129.533 E.0165
M73 P68 R3
G3 X123.24 Y129.841 I-.845 J3.597 E.02755
G1 X123.656 Y130.176 E.01644
G1 X123.873 Y130.437 E.01044
G3 X123.26 Y128.722 I4.593 J-2.611 E.0563
G1 X123.205 Y128.04 E.02104
G3 X123.487 Y126.417 I5.392 J.101 E.05088
M204 S10000
G1 X123.686 Y125.841 F42000
; LINE_WIDTH: 0.47218
G1 F3659
M204 S6000
G1 X123.836 Y125.609 E.00966
; LINE_WIDTH: 0.43714
G1 X123.986 Y125.377 E.00888
; LINE_WIDTH: 0.413148
G3 X125.513 Y123.906 I4.42 J3.061 E.06438
; CHANGE_LAYER
; Z_HEIGHT: 1.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F9723.74
G1 X125.103 Y124.19 E-.18915
G1 X124.716 Y124.518 E-.19293
G1 X124.36 Y124.898 E-.19787
G1 X124.068 Y125.271 E-.18004
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 7/26
; update layer progress
M73 L7
M991 S0 P6 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z1.6 I-1.196 J.223 P1  F42000
G1 X124.942 Y129.963 Z1.6
G1 Z1.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5688
M204 S5000
G1 X124.679 Y129.459 E.01747
G3 X127.483 Y124.403 I3.321 J-1.464 E.20553
G1 X127.535 Y124.4 E.00161
G1 X128 Y124.366 E.01432
G3 X124.978 Y130.005 I0 J3.629 E.46002
; WIPE_START
G1 F9547.055
M204 S6000
G1 X124.679 Y129.459 E-.23661
G1 X124.513 Y129.024 E-.17702
G1 X124.403 Y128.517 E-.19701
G1 X124.375 Y128.125 E-.14936
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X125.369 Y120.933 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5688
M204 S6000
G1 X125.262 Y120.703 E.00841
G3 X128.339 Y120.214 I2.817 J7.799 E.10398
G3 X130.738 Y120.703 I-.51 J8.629 E.08148
G1 X130.631 Y120.933 E.00841
G2 X125.425 Y120.912 I-2.631 J6.995 E.17638
; WIPE_START
G1 F8843.478
G1 X125.262 Y120.703 E-.10081
G1 X125.982 Y120.47 E-.28773
G1 X126.81 Y120.297 E-.32121
G1 X126.941 Y120.281 E-.05025
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X131.654 Y126.284 Z1.8 F42000
G1 X135.067 Y130.631 Z1.8
G1 Z1.4
G1 E.8 F1800
G1 F5688
M204 S6000
G2 X135.067 Y125.369 I-6.995 J-2.631 E.17837
G1 X135.297 Y125.262 E.00841
G1 X135.38 Y125.49 E.00804
G3 X135.297 Y130.738 I-7.398 J2.508 E.17757
G1 X135.121 Y130.656 E.00642
; WIPE_START
G1 F8843.478
G1 X135.222 Y130.189 E-.18167
G1 X135.416 Y129.394 E-.31096
G1 X135.511 Y128.734 E-.25325
G1 X135.513 Y128.697 E-.01412
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X129.049 Y132.756 Z1.8 F42000
G1 X125.369 Y135.067 Z1.8
G1 Z1.4
G1 E.8 F1800
G1 F5688
M204 S6000
G2 X130.631 Y135.067 I2.631 J-6.995 E.17836
G1 X130.738 Y135.297 E.00841
G3 X125.262 Y135.297 I-2.738 J-7.339 E.18558
G1 X125.344 Y135.121 E.00642
; WIPE_START
G1 F8843.478
G1 X125.811 Y135.222 E-.18156
G1 X126.606 Y135.416 E-.31103
G1 X127.266 Y135.511 E-.25325
G1 X127.303 Y135.513 E-.01416
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X121.245 Y130.87 Z1.8 F42000
G1 X120.933 Y130.631 Z1.8
G1 Z1.4
G1 E.8 F1800
G1 F5688
M204 S6000
G1 X120.703 Y130.738 E.00841
G3 X120.703 Y125.262 I7.339 J-2.738 E.18558
G1 X120.933 Y125.369 E.00841
G2 X120.912 Y130.575 I6.995 J2.631 E.17638
; WIPE_START
G1 F8843.478
G1 X120.703 Y130.738 E-.10081
G1 X120.47 Y130.018 E-.28773
G1 X120.297 Y129.19 E-.32121
G1 X120.281 Y129.059 E-.05026
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X125.272 Y134.3 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5688
M204 S5000
G1 X125.334 Y134.072 E.00724
G2 X124.845 Y133.046 I-1.089 J-.112 E.03673
G3 X122.954 Y131.155 I3.35 J-5.241 E.08282
G2 X121.585 Y130.76 I-.921 J.622 E.04753
G1 X121.004 Y131.031 E.0197
G1 F5311.374
G1 X120.642 Y131.2 E.01229
G1 F2040
G1 X120.497 Y131.267 E.0049
G3 X120.497 Y124.733 I7.506 J-3.267 E.20652
G1 F3159.08
G1 X120.642 Y124.8 E.0049
G1 F5688
G1 X121.004 Y124.969 E.01229
G1 X121.589 Y125.242 E.01982
G2 X122.954 Y124.845 I.451 J-.997 E.04756
G3 X124.845 Y122.954 I5.241 J3.35 E.08282
G2 X125.24 Y121.585 I-.622 J-.921 E.04753
G1 X124.969 Y121.004 E.0197
G1 F5311.374
G1 X124.8 Y120.642 E.01229
G1 F2040
G1 X124.733 Y120.497 E.0049
G3 X128.359 Y119.823 I3.264 J7.465 E.11433
G3 X131.267 Y120.497 I-.381 J8.246 E.09222
G1 F3159.08
G1 X131.2 Y120.642 E.0049
G1 F5688
G1 X131.031 Y121.004 E.01229
G1 X130.758 Y121.589 E.01982
G2 X131.155 Y122.954 I.997 J.451 E.04756
G3 X133.046 Y124.845 I-3.35 J5.241 E.08282
G2 X134.415 Y125.24 I.921 J-.622 E.04753
G1 X134.996 Y124.969 E.0197
G1 F5311.374
G1 X135.358 Y124.8 E.01229
G1 F2040
G1 X135.503 Y124.733 E.0049
G3 X135.503 Y131.267 I-7.506 J3.267 E.20652
G1 F3159.08
G1 X135.358 Y131.2 E.0049
G1 F5688
G1 X134.996 Y131.031 E.01229
G1 X134.411 Y130.758 E.01982
G2 X133.046 Y131.155 I-.451 J.997 E.04756
G3 X131.155 Y133.046 I-5.241 J-3.35 E.08282
G2 X130.76 Y134.415 I.622 J.921 E.04753
G1 X131.031 Y134.996 E.0197
G1 F5311.374
G1 X131.2 Y135.358 E.01229
G1 F2040
G1 X131.267 Y135.503 E.0049
G3 X124.733 Y135.503 I-3.267 J-7.506 E.20652
G1 F3159.08
G1 X124.8 Y135.358 E.0049
G1 F5688
G1 X124.969 Y134.996 E.01229
G1 X125.242 Y134.411 E.01982
G1 X125.257 Y134.358 E.0017
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.334 Y134.072 E-.11237
G1 X125.34 Y133.911 E-.06113
G1 X125.298 Y133.656 E-.09852
G1 X125.192 Y133.407 E-.10253
G1 X125.036 Y133.2 E-.0988
G1 X124.845 Y133.046 E-.09306
G1 X124.427 Y132.755 E-.19359
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z1.8 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z1.8
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z1.8 F4000
            G39.3 S1
            G0 Z1.8 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X134.3 Y125.501 F42000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Top surface
G1 F5688
M204 S2000
G1 X135.124 Y126.325 E.03579
G1 X135.245 Y126.98
G1 X133.803 Y125.537 E.06269
; WIPE_START
G1 F9547.055
M204 S6000
G1 X135.217 Y126.951 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.503 Y121.705 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
G1 F5688
M204 S2000
G1 X129.675 Y120.876 E.03599
G1 X129.02 Y120.755
G1 X130.463 Y122.197 E.06269
; WIPE_START
G1 F9547.055
M204 S6000
G1 X129.049 Y120.783 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X128.428 Y120.696 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
G1 F5688
M204 S2000
G1 X135.304 Y127.572 E.2988
G1 X135.32 Y128.121
G1 X127.879 Y120.68 E.32334
G1 X127.372 Y120.706
G1 X135.294 Y128.628 E.34425
G1 X135.234 Y129.101
G1 X126.899 Y120.766 E.36218
G1 X126.446 Y120.847
G1 X135.153 Y129.554 E.37837
G1 X135.048 Y129.982
G1 X131.509 Y126.443 E.15379
G1 X131.752 Y127.219
G1 X134.917 Y130.385 E.13757
G1 X134.631 Y130.631
G1 X131.83 Y127.83 E.12173
G1 X131.817 Y128.35
G1 X133.919 Y130.453 E.09135
G1 X133.479 Y130.547
G1 X131.745 Y128.812 E.07538
G1 X131.631 Y129.231
G1 X133.145 Y130.746 E.06582
G1 X132.887 Y131.021
G1 X131.483 Y129.617 E.06101
G1 X131.295 Y129.962
G1 X132.668 Y131.335 E.05968
M73 P69 R3
G1 X132.437 Y131.637
G1 X131.08 Y130.28 E.05896
G1 X130.843 Y130.576
G1 X132.19 Y131.923 E.05852
G1 X131.923 Y132.19
G1 X130.576 Y130.843 E.05852
G1 X130.28 Y131.08
G1 X131.637 Y132.437 E.05896
G1 X131.335 Y132.668
G1 X129.962 Y131.295 E.05968
G1 X129.617 Y131.483
G1 X131.021 Y132.887 E.06101
G1 X130.746 Y133.145
G1 X129.231 Y131.631 E.06583
G1 X128.812 Y131.745
G1 X130.547 Y133.48 E.07538
G1 X130.453 Y133.919
G1 X128.35 Y131.817 E.09137
G1 X127.83 Y131.829
G1 X130.632 Y134.631 E.12175
G1 X130.385 Y134.917
G1 X127.219 Y131.752 E.13757
G1 X126.443 Y131.509
G1 X129.982 Y135.048 E.1538
; WIPE_START
G1 F9547.055
M204 S6000
G1 X128.568 Y133.634 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X127.063 Y126.151 Z1.8 F42000
G1 X126.018 Y120.952 Z1.8
G1 Z1.4
G1 E.8 F1800
G1 F5688
M204 S2000
G1 X129.557 Y124.491 E.15379
G1 X128.781 Y124.248
G1 X125.615 Y121.083 E.13756
G1 X125.368 Y121.369
G1 X128.17 Y124.171 E.12173
G1 X127.65 Y124.183
G1 X125.547 Y122.081 E.09136
G1 X125.453 Y122.521
G1 X127.188 Y124.255 E.07538
G1 X126.769 Y124.369
G1 X125.254 Y122.855 E.06582
G1 X124.979 Y123.113
G1 X126.383 Y124.517 E.06101
G1 X126.038 Y124.705
G1 X124.665 Y123.332 E.05968
G1 X124.363 Y123.563
G1 X125.72 Y124.92 E.05896
G1 X125.424 Y125.157
G1 X124.077 Y123.81 E.05852
G1 X123.81 Y124.077
G1 X125.157 Y125.424 E.05852
G1 X124.92 Y125.72
G1 X123.563 Y124.363 E.05896
G1 X123.332 Y124.665
G1 X124.705 Y126.038 E.05968
G1 X124.517 Y126.383
G1 X123.113 Y124.979 E.06101
G1 X122.855 Y125.254
G1 X124.369 Y126.769 E.06583
G1 X124.255 Y127.188
G1 X122.52 Y125.453 E.07538
G1 X122.081 Y125.547
G1 X124.183 Y127.65 E.09136
G1 X124.171 Y128.17
G1 X121.369 Y125.368 E.12174
G1 X121.083 Y125.615
G1 X124.248 Y128.781 E.13757
G1 X124.491 Y129.557
G1 X120.952 Y126.018 E.1538
G1 X120.847 Y126.446
G1 X129.554 Y135.153 E.37837
G1 X129.101 Y135.234
G1 X120.766 Y126.899 E.36218
G1 X120.706 Y127.372
G1 X128.628 Y135.294 E.34425
G1 X128.121 Y135.32
G1 X120.68 Y127.879 E.32334
G1 X120.696 Y128.428
G1 X127.572 Y135.304 E.29879
G1 X126.98 Y135.245
G1 X125.537 Y133.803 E.06268
G1 X125.497 Y134.295
G1 X126.325 Y135.123 E.03598
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.497 Y134.295 E-.44502
G1 X125.537 Y133.803 E-.18784
G1 X125.774 Y134.039 E-.12714
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X122.197 Y130.463 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
G1 F5688
M204 S2000
G1 X120.755 Y129.02 E.06268
G1 X120.877 Y129.675
G1 X121.7 Y130.499 E.03579
; WIPE_START
G1 F9547.055
M204 S6000
G1 X120.877 Y129.675 E-.44256
G1 X120.755 Y129.02 E-.25317
G1 X120.874 Y129.14 E-.06428
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.576 Y132.604 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.0921754
G1 F5688
M204 S6000
G1 X124.524 Y132.561 E.00027
; LINE_WIDTH: 0.126722
G3 X123.439 Y131.476 I8.535 J-9.62 E.01049
; LINE_WIDTH: 0.0921707
G1 X123.396 Y131.424 E.00027
; WIPE_START
G1 F15000
G1 X123.439 Y131.476 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X125.615 Y133.725 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.0967758
G1 F5688
M204 S6000
G2 X125.452 Y133.478 I-4.187 J2.577 E.0013
M204 S10000
G1 X125.595 Y133.594 F42000
; LINE_WIDTH: 0.0942931
G1 F5688
M204 S6000
G1 X125.522 Y133.818 E.00098
M204 S10000
G1 X125.607 Y133.733 F42000
; LINE_WIDTH: 0.139799
G1 F5688
M204 S6000
G1 X125.458 Y133.474 E.00236
; WIPE_START
G1 F15000
G1 X125.607 Y133.733 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X125.939 Y135.029 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.0991033
G1 F5688
M204 S6000
G1 X125.329 Y134.672 E.00324
; WIPE_START
G1 F15000
G1 X125.939 Y135.029 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X126.38 Y131.572 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.194547
G1 F5688
M204 S6000
G1 X126.231 Y131.461 E.0023
; LINE_WIDTH: 0.151996
G1 X126.082 Y131.349 E.00165
; LINE_WIDTH: 0.109445
G1 X125.933 Y131.238 E.00101
; WIPE_START
G1 F15000
G1 X126.082 Y131.349 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.762 Y130.067 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.109451
G1 F5688
M204 S6000
G1 X124.651 Y129.918 E.00101
; LINE_WIDTH: 0.152004
G1 X124.539 Y129.769 E.00165
; LINE_WIDTH: 0.194557
G1 X124.428 Y129.62 E.0023
; WIPE_START
G1 F15000
G1 X124.539 Y129.769 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X122.009 Y125.619 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.137605
G1 F5688
M204 S6000
G1 X121.809 Y125.524 E.00171
; WIPE_START
M73 P70 R3
G1 F15000
G1 X122.009 Y125.619 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X121.328 Y130.671 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.0991271
G1 F5688
M204 S6000
G1 X120.971 Y130.061 E.00324
; WIPE_START
G1 F15000
G1 X121.328 Y130.671 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X122.407 Y130.406 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.099807
G1 F5688
M204 S6000
G1 X122.184 Y130.477 E.00109
M204 S10000
G1 X122.522 Y130.548 F42000
; LINE_WIDTH: 0.101948
G1 F5688
M204 S6000
G2 X122.272 Y130.388 I-1.776 J2.503 E.00143
; WIPE_START
G1 F15000
G1 X122.522 Y130.548 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X127.577 Y124.829 Z1.8 F42000
G1 X130.671 Y121.328 Z1.8
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.0991524
G1 F5688
M204 S6000
G1 X130.061 Y120.971 E.00324
M204 S10000
G1 X130.495 Y121.738 F42000
; LINE_WIDTH: 0.0938972
G1 F5688
M204 S6000
G2 X130.413 Y121.881 I1.865 J1.166 E.00069
M204 S10000
G1 X130.405 Y122.406 F42000
; LINE_WIDTH: 0.0941557
G1 F5688
M204 S6000
G1 X130.478 Y122.183 E.00098
M204 S10000
G1 X130.542 Y122.526 F42000
; LINE_WIDTH: 0.139886
G1 F5688
M204 S6000
G1 X130.393 Y122.267 E.00236
M204 S10000
G1 X130.548 Y122.522 F42000
; LINE_WIDTH: 0.0967819
G1 F5688
M204 S6000
G3 X130.385 Y122.275 I4.124 J-2.895 E.0013
; WIPE_START
G1 F15000
G1 X130.548 Y122.522 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X132.604 Y124.576 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.0922068
G1 F5688
M204 S6000
G1 X132.561 Y124.524 E.00027
; LINE_WIDTH: 0.1268
G2 X131.476 Y123.439 I-9.623 J8.537 E.0105
; LINE_WIDTH: 0.0922177
G1 X131.424 Y123.395 E.00027
; WIPE_START
G1 F15000
G1 X131.476 Y123.439 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.067 Y124.762 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.10944
G1 F5688
M204 S6000
G1 X129.918 Y124.651 E.00101
; LINE_WIDTH: 0.151981
G1 X129.769 Y124.539 E.00165
; LINE_WIDTH: 0.194523
G1 X129.62 Y124.428 E.0023
; WIPE_START
G1 F15000
G1 X129.769 Y124.539 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X131.572 Y126.38 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.194526
G1 F5688
M204 S6000
G1 X131.461 Y126.231 E.0023
; LINE_WIDTH: 0.151986
G1 X131.349 Y126.082 E.00165
; LINE_WIDTH: 0.109445
G1 X131.238 Y125.933 E.00101
; WIPE_START
G1 F15000
G1 X131.349 Y126.082 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X134.191 Y130.476 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.137525
G1 F5688
M204 S6000
G1 X133.991 Y130.381 E.00171
; WIPE_START
G1 F15000
G1 X134.191 Y130.476 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X135.029 Y125.939 Z1.8 F42000
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.0991369
G1 F5688
M204 S6000
G1 X134.672 Y125.329 E.00324
M204 S10000
G1 X133.728 Y125.612 F42000
; LINE_WIDTH: 0.102031
G1 F5688
M204 S6000
G3 X133.478 Y125.452 I1.516 J-2.648 E.00143
M204 S10000
G1 X133.817 Y125.523 F42000
; LINE_WIDTH: 0.0995992
G1 F5688
M204 S6000
G1 X133.593 Y125.594 E.00108
; CHANGE_LAYER
; Z_HEIGHT: 1.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X133.817 Y125.523 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 8/26
; update layer progress
M73 L8
M991 S0 P7 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z1.8 I-.902 J-.817 P1  F42000
G1 X125.57 Y134.633 Z1.8
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1402
M204 S6000
G1 X125.954 Y134.768 E.0135
G2 X130.429 Y134.633 I2.032 J-6.902 E.15102
G1 X130.823 Y135.478 E.03092
G3 X125.177 Y135.478 I-2.823 J-7.451 E.19145
G1 X125.545 Y134.687 E.02892
M204 S10000
G1 X125.504 Y134.194 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1402
M204 S5000
G1 X125.506 Y134.195 E.00007
G2 X130.672 Y134.115 I2.486 J-6.285 E.16292
G2 X130.76 Y134.415 I1.493 J-.272 E.00961
G1 X131.115 Y135.177 E.02586
G1 X131.284 Y135.54 E.01229
G1 X131.352 Y135.684 E.0049
G3 X124.648 Y135.684 I-3.352 J-7.64 E.21196
G1 X124.715 Y135.54 E.0049
G1 X124.884 Y135.177 E.01229
G1 X125.261 Y134.368 E.02741
G2 X125.326 Y134.114 I-1.287 J-.468 E.00808
G1 X125.449 Y134.169 E.00414
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.506 Y134.195 E-.02365
G1 X126.072 Y134.394 E-.228
G1 X126.756 Y134.561 E-.26761
G1 X127.35 Y134.647 E-.22808
G1 X127.383 Y134.648 E-.01267
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z2 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z2
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z2 F4000
            G39.3 S1
            G0 Z2 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.676 Y134.888 F42000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.560794
G1 F1402
M204 S6000
G1 X125.811 Y135.206 E.01458
G2 X130.042 Y135.249 I2.189 J-7.208 E.18098
G1 X130.188 Y135.206 E.0064
G1 X130.323 Y134.888 E.01459
; WIPE_START
G1 F6951.499
G1 X130.188 Y135.206 E-.13141
G1 X130.042 Y135.249 E-.05766
G1 X129.485 Y135.384 E-.21784
G1 X129.13 Y135.444 E-.13678
G1 X128.657 Y135.503 E-.18125
G1 X128.564 Y135.507 E-.03507
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X132.543 Y128.993 Z2 F42000
G1 X134.633 Y125.571 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1402
M204 S6000
G1 X135.478 Y125.177 E.03092
G1 X135.578 Y125.45 E.00965
G3 X135.478 Y130.823 I-7.628 J2.546 E.18175
G1 X134.633 Y130.43 E.03092
G2 X134.654 Y125.627 I-6.548 J-2.43 E.16264
M204 S10000
G1 X134.191 Y125.507 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1402
M204 S5000
G2 X134.115 Y125.328 I-6.143 J2.493 E.00599
G2 X134.415 Y125.24 I-.272 J-1.495 E.00961
G1 X135.177 Y124.885 E.02586
G1 X135.54 Y124.716 E.01229
G1 X135.685 Y124.648 E.00492
G1 X135.764 Y124.832 E.00614
G3 X135.684 Y131.352 I-7.743 J3.166 E.20581
G1 X135.54 Y131.285 E.0049
G1 X135.177 Y131.116 E.01229
G1 X134.368 Y130.739 E.02741
G2 X134.114 Y130.674 I-.468 J1.286 E.00808
G2 X134.213 Y125.563 I-6.066 J-2.674 E.16125
M204 S10000
G1 X134.889 Y125.677 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.560786
G1 F1402
M204 S6000
G1 X135.206 Y125.812 E.01456
G3 X135.249 Y130.042 I-7.207 J2.187 E.18093
G1 X135.206 Y130.189 E.00646
G1 X134.887 Y130.324 E.0146
; WIPE_START
G1 F6951.604
G1 X135.206 Y130.189 E-.13143
G1 X135.249 Y130.042 E-.05821
G1 X135.383 Y129.489 E-.21619
G1 X135.445 Y129.126 E-.14007
G1 X135.503 Y128.658 E-.17909
G1 X135.506 Y128.566 E-.03501
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X129.326 Y124.087 Z2 F42000
M73 P71 R3
G1 X125.571 Y121.367 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1402
M204 S6000
G1 X125.177 Y120.522 E.03092
G3 X128.301 Y120.012 I2.811 J7.399 E.10571
G3 X130.823 Y120.522 I-.28 J7.873 E.08574
G1 X130.43 Y121.367 E.03092
G2 X125.627 Y121.346 I-2.43 J6.547 E.16264
M204 S10000
G1 X125.507 Y121.809 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1402
M204 S5000
G2 X125.328 Y121.885 I2.493 J6.143 E.00599
G2 X125.24 Y121.585 I-1.493 J.272 E.00962
G1 X124.885 Y120.823 E.02586
G1 X124.716 Y120.46 E.01229
G1 X124.648 Y120.316 E.0049
G3 X128.321 Y119.62 I3.356 J7.682 E.11583
G3 X131.352 Y120.316 I-.345 J8.454 E.09609
G1 X131.285 Y120.46 E.0049
G1 X131.116 Y120.823 E.01229
G1 X130.739 Y121.632 E.02741
G2 X130.674 Y121.886 I1.287 J.468 E.00808
G2 X125.563 Y121.787 I-2.674 J6.066 E.16125
M204 S10000
G1 X125.677 Y121.111 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.560806
G1 F1402
M204 S6000
G1 X125.812 Y120.794 E.01456
G3 X130.042 Y120.751 I2.187 J7.19 E.18095
G1 X130.189 Y120.794 E.00646
G1 X130.324 Y121.113 E.0146
; WIPE_START
G1 F6951.345
G1 X130.189 Y120.794 E-.13142
G1 X130.042 Y120.751 E-.05821
G1 X129.485 Y120.616 E-.21781
G1 X129.13 Y120.556 E-.13678
G1 X128.655 Y120.497 E-.18197
G1 X128.566 Y120.493 E-.03381
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.053 Y126.649 Z2 F42000
G1 X121.24 Y130.488 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1402
M204 S6000
G1 X120.522 Y130.823 E.02627
G3 X120.522 Y125.177 I7.487 J-2.823 E.19141
G1 X121.367 Y125.57 E.03092
G2 X121.367 Y130.429 I6.548 J2.43 E.16463
G1 X121.294 Y130.463 E.00266
M204 S10000
G1 X121.405 Y130.843 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1402
M204 S5000
G1 X120.823 Y131.115 E.01976
G1 X120.46 Y131.284 E.01229
G1 X120.316 Y131.352 E.0049
G3 X120.316 Y124.648 I7.669 J-3.352 E.21192
G1 X120.46 Y124.716 E.0049
G1 X120.823 Y124.884 E.01229
G1 X121.632 Y125.261 E.02741
G2 X121.886 Y125.326 I.468 J-1.286 E.00808
G2 X121.885 Y130.672 I6.066 J2.674 E.16908
G2 X121.585 Y130.76 I.272 J1.495 E.00961
G1 X121.46 Y130.818 E.00426
M204 S10000
G1 X121.112 Y130.323 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.560738
G1 F1402
M204 S6000
G1 X120.794 Y130.188 E.01457
G3 X120.751 Y125.958 I7.206 J-2.188 E.18091
G1 X120.794 Y125.811 E.00646
G1 X121.112 Y125.676 E.01457
; CHANGE_LAYER
; Z_HEIGHT: 1.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6952.261
G1 X120.794 Y125.811 E-.13123
G1 X120.751 Y125.958 E-.05821
G1 X120.616 Y126.515 E-.2178
G1 X120.556 Y126.87 E-.13678
G1 X120.497 Y127.343 E-.18125
G1 X120.494 Y127.435 E-.03474
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 9/26
; update layer progress
M73 L9
M991 S0 P8 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z2 I-1.008 J.682 P1  F42000
G1 X125.486 Y134.817 Z2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1430
M204 S6000
G2 X130.514 Y134.817 I2.514 J-6.784 E.17037
G1 X130.907 Y135.66 E.03086
G3 X125.093 Y135.66 I-2.907 J-7.671 E.19718
G1 X125.46 Y134.871 E.02886
M204 S10000
G1 X125.278 Y134.313 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1430
M204 S5000
G1 X125.458 Y134.391 E.00603
G2 X130.72 Y134.313 I2.536 J-6.462 E.16584
G2 X130.76 Y134.415 I.67 J-.204 E.00335
G1 X131.031 Y134.996 E.01972
G1 X131.2 Y135.359 E.01229
G1 X131.369 Y135.722 E.01229
G1 X131.436 Y135.866 E.0049
G3 X124.564 Y135.866 I-3.436 J-7.86 E.21727
G1 X124.631 Y135.721 E.0049
G1 X124.798 Y135.358 E.01229
G1 X124.965 Y134.995 E.01229
G1 X125.253 Y134.367 E.02121
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.458 Y134.391 E-.0784
G1 X125.963 Y134.569 E-.20349
G1 X126.782 Y134.769 E-.32008
G1 X127.193 Y134.827 E-.15803
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z2.2 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z2.2
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z2.2 F4000
            G39.3 S1
            G0 Z2.2 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.719 Y135.371 F42000
G1 Z1.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.560809
G1 F1430
M204 S6000
G1 X125.727 Y135.389 E.00086
G2 X130.273 Y135.389 I2.273 J-7.408 E.19469
G1 X130.281 Y135.37 E.00087
; LINE_WIDTH: 0.50868
G1 X130.411 Y135.076 E.0122
M204 S10000
G1 X125.719 Y135.371 F42000
; LINE_WIDTH: 0.508771
G1 F1430
M204 S6000
G1 X125.589 Y135.076 E.01221
; WIPE_START
G1 F7727.804
G1 X125.719 Y135.371 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.887 Y129.755 Z2.2 F42000
G1 X134.817 Y125.486 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1430
M204 S6000
G1 X135.659 Y125.093 E.03084
G1 X135.79 Y125.457 E.01283
G3 X135.66 Y130.907 I-7.771 J2.541 E.18439
G1 X134.817 Y130.514 E.03085
G2 X134.837 Y125.542 I-6.784 J-2.514 E.16838
M204 S10000
G1 X134.313 Y125.28 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1430
M204 S5000
G2 X134.415 Y125.24 I-.204 J-.67 E.00335
G1 X134.997 Y124.969 E.01974
G1 X135.36 Y124.8 E.01229
G1 X135.722 Y124.631 E.01229
G1 X135.866 Y124.564 E.00489
G1 X135.967 Y124.798 E.00784
G3 X135.866 Y131.436 I-7.98 J3.198 E.20944
G1 X135.722 Y131.369 E.0049
M73 P72 R3
G1 X135.358 Y131.202 E.01229
G1 X134.995 Y131.035 E.01229
G1 X134.313 Y130.722 E.02306
G2 X134.337 Y125.335 I-6.298 J-2.722 E.17008
M204 S10000
M73 P72 R2
G1 X135.076 Y125.589 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.508698
G1 F1430
M204 S6000
G1 X135.371 Y125.719 E.0122
; LINE_WIDTH: 0.56065
G1 X135.389 Y125.727 E.00088
G3 X135.389 Y130.273 I-7.411 J2.272 E.19462
G1 X135.371 Y130.281 E.00086
; LINE_WIDTH: 0.508771
G1 X135.076 Y130.411 E.01221
; WIPE_START
G1 F7727.804
G1 X135.371 Y130.281 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X129.755 Y125.113 Z2.2 F42000
G1 X125.486 Y121.183 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1430
M204 S6000
G1 X125.093 Y120.34 E.03086
G3 X128.274 Y119.81 I2.924 J7.734 E.10769
G3 X130.907 Y120.34 I-.259 J8.092 E.08951
G1 X130.514 Y121.183 E.03085
G2 X125.542 Y121.163 I-2.514 J6.784 E.16838
M204 S10000
G1 X125.28 Y121.687 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1430
M204 S5000
G2 X125.24 Y121.585 I-.67 J.204 E.00335
G1 X124.969 Y121.004 E.01972
G1 X124.8 Y120.641 E.01229
G1 X124.631 Y120.278 E.01229
G1 X124.564 Y120.134 E.0049
G3 X128.287 Y119.418 I3.428 J7.787 E.11748
G3 X131.436 Y120.134 I-.314 J8.665 E.09983
G1 X131.369 Y120.278 E.0049
G1 X131.202 Y120.642 E.01229
G1 X131.035 Y121.005 E.01229
G1 X130.722 Y121.687 E.02306
G2 X125.335 Y121.663 I-2.722 J6.298 E.17008
M204 S10000
G1 X125.589 Y120.924 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.50868
G1 F1430
M204 S6000
G1 X125.719 Y120.629 E.0122
; LINE_WIDTH: 0.560739
G1 X125.727 Y120.611 E.00087
G3 X130.273 Y120.611 I2.273 J7.421 E.19466
G1 X130.281 Y120.629 E.00086
; LINE_WIDTH: 0.508771
G1 X130.411 Y120.924 E.01221
; WIPE_START
G1 F7727.804
G1 X130.281 Y120.629 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X125.113 Y126.245 Z2.2 F42000
G1 X121.183 Y130.514 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1430
M204 S6000
G1 X120.34 Y130.907 E.03086
G3 X120.34 Y125.093 I7.671 J-2.907 E.19718
G1 X121.183 Y125.486 E.03086
G2 X121.163 Y130.458 I6.784 J2.514 E.16838
M204 S10000
G1 X121.585 Y130.76 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1430
M204 S5000
G1 X121.004 Y131.031 E.01972
G1 X120.641 Y131.2 E.01229
G1 X120.278 Y131.369 E.01229
G1 X120.134 Y131.436 E.0049
G3 X120.134 Y124.564 I7.86 J-3.436 E.21727
G1 X120.279 Y124.631 E.0049
G1 X120.641 Y124.8 E.01229
G1 X121.004 Y124.969 E.01229
G1 X121.589 Y125.242 E.01984
G1 X121.687 Y125.278 E.00323
G2 X121.687 Y130.72 I6.298 J2.722 E.17193
G2 X121.64 Y130.736 I.204 J.67 E.0015
M204 S10000
G1 X120.924 Y130.411 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.50868
G1 F1430
M204 S6000
G1 X120.63 Y130.281 E.0122
; LINE_WIDTH: 0.560809
G1 X120.611 Y130.273 E.00087
G3 X120.611 Y125.727 I7.408 J-2.273 E.19469
G1 X120.63 Y125.719 E.00087
; LINE_WIDTH: 0.508685
G1 X120.924 Y125.589 E.0122
; CHANGE_LAYER
; Z_HEIGHT: 2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F7729.224
G1 X120.63 Y125.719 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 10/26
; update layer progress
M73 L10
M991 S0 P9 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z2.2 I-1.082 J.557 P1  F42000
G1 X125.402 Y134.997 Z2.2
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1456
M204 S6000
G2 X130.598 Y134.997 I2.598 J-7.009 E.17605
G1 X130.991 Y135.838 E.0308
G3 X125.009 Y135.838 I-2.991 J-7.853 E.20286
G1 X125.376 Y135.051 E.02881
M204 S10000
G1 X125.243 Y134.513 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1456
M204 S5000
G2 X130.797 Y134.496 I2.756 J-6.536 E.17534
G1 X131.115 Y135.178 E.02314
G1 X131.285 Y135.541 E.01229
G1 X131.454 Y135.903 E.01229
G1 X131.519 Y136.044 E.00479
M73 P73 R2
G3 X124.481 Y136.044 I-3.519 J-8.046 E.22254
G1 X124.546 Y135.903 E.00479
G1 X124.715 Y135.541 E.01229
G1 X124.885 Y135.178 E.01229
G1 X125.196 Y134.51 E.02265
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.863 Y134.744 E-.26844
G1 X126.327 Y134.874 E-.18332
G1 X126.8 Y134.972 E-.18338
G1 X127.125 Y135.017 E-.12486
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z2.4 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z2.4
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z2.4 F4000
            G39.3 S1
            G0 Z2.4 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.644 Y135.569 F42000
G1 Z2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.560992
G1 F1456
M204 S6000
G2 X130.356 Y135.569 I2.356 J-7.611 E.20196
G1 X130.366 Y135.547 E.00104
; LINE_WIDTH: 0.502202
G1 X130.377 Y135.524 E.00092
; LINE_WIDTH: 0.466913
G1 X130.495 Y135.256 E.01012
M204 S10000
G1 X125.644 Y135.569 F42000
; LINE_WIDTH: 0.539836
G1 F1456
M204 S6000
G1 X125.634 Y135.547 E.001
; LINE_WIDTH: 0.502218
G1 X125.623 Y135.524 E.00092
; LINE_WIDTH: 0.466935
G1 X125.505 Y135.256 E.01013
; WIPE_START
G1 F8490.275
G1 X125.623 Y135.524 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X121.003 Y130.598 Z2.4 F42000
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1456
M204 S6000
G1 X120.162 Y130.991 E.0308
G3 X120.162 Y125.009 I7.853 J-2.991 E.20286
G1 X121.003 Y125.402 E.0308
G2 X120.983 Y130.542 I7.009 J2.598 E.17406
M204 S10000
G1 X121.504 Y130.797 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1456
M204 S5000
G1 X120.822 Y131.115 E.02314
G1 X120.459 Y131.285 E.01229
G1 X120.097 Y131.454 E.01229
G1 X119.956 Y131.519 E.00479
G3 X119.956 Y124.481 I8.046 J-3.519 E.22254
G1 X120.097 Y124.546 E.00479
G1 X120.459 Y124.715 E.01229
G1 X120.822 Y124.884 E.01229
G1 X121.505 Y125.203 E.02315
G2 X121.481 Y130.742 I6.513 J2.798 E.17486
M204 S10000
G1 X120.744 Y130.495 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.466934
G1 F1456
M204 S6000
G1 X120.476 Y130.377 E.01013
; LINE_WIDTH: 0.502207
G1 X120.453 Y130.366 E.00092
; LINE_WIDTH: 0.539833
G1 X120.431 Y130.356 E.001
; LINE_WIDTH: 0.56099
G3 X120.431 Y125.644 I7.611 J-2.356 E.20196
G1 X120.453 Y125.633 E.00104
; LINE_WIDTH: 0.502144
G1 X120.476 Y125.623 E.00092
; LINE_WIDTH: 0.466832
G1 X120.744 Y125.505 E.01012
; WIPE_START
G1 F8492.338
G1 X120.476 Y125.623 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X125.402 Y121.003 Z2.4 F42000
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1456
M204 S6000
G1 X125.009 Y120.162 E.0308
G3 X128.654 Y119.635 I2.979 J7.746 E.12317
G3 X130.991 Y120.162 I-.603 J8.13 E.07975
G1 X130.598 Y121.003 E.0308
G2 X125.458 Y120.983 I-2.598 J7.009 E.17406
M204 S10000
G1 X125.203 Y121.504 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1456
M204 S5000
G1 X124.885 Y120.822 E.02314
G1 X124.715 Y120.459 E.01229
G1 X124.546 Y120.097 E.01229
G1 X124.481 Y119.956 E.00479
G3 X127.745 Y119.22 I3.551 J8.139 E.10343
G1 X128.255 Y119.22 E.01569
G1 X128.676 Y119.244 E.01296
G3 X131.519 Y119.956 I-.696 J8.817 E.09047
G1 X131.454 Y120.097 E.00479
G1 X131.285 Y120.459 E.01229
G1 X131.115 Y120.822 E.01229
G1 X130.797 Y121.505 E.02315
G2 X125.258 Y121.481 I-2.798 J6.513 E.17486
M204 S10000
G1 X125.505 Y120.744 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.466814
G1 F1456
M204 S6000
G1 X125.623 Y120.476 E.01012
; LINE_WIDTH: 0.502126
G1 X125.634 Y120.453 E.00092
; LINE_WIDTH: 0.539802
G1 X125.644 Y120.431 E.001
; LINE_WIDTH: 0.560991
G3 X130.356 Y120.431 I2.356 J7.537 E.20202
M73 P74 R2
G1 X130.367 Y120.453 E.00104
; LINE_WIDTH: 0.50212
G1 X130.377 Y120.476 E.00092
; LINE_WIDTH: 0.466818
G1 X130.495 Y120.744 E.01012
; WIPE_START
G1 F8492.612
G1 X130.377 Y120.476 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X134.997 Y125.402 Z2.4 F42000
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1456
M204 S6000
G1 X135.838 Y125.009 E.0308
G1 X135.966 Y125.36 E.01239
G3 X135.838 Y130.991 I-8.004 J2.635 E.19048
G1 X134.997 Y130.598 E.0308
G2 X135.017 Y125.458 I-7.009 J-2.598 E.17406
M204 S10000
G1 X134.496 Y125.203 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1456
M204 S5000
G1 X135.178 Y124.884 E.02315
G1 X135.541 Y124.715 E.01229
G1 X135.903 Y124.546 E.01229
G1 X136.044 Y124.481 E.00478
G1 X136.128 Y124.675 E.0065
G1 X136.164 Y124.757 E.00274
G1 X136.338 Y125.237 E.01571
G3 X136.702 Y129.184 I-8.315 J2.756 E.12287
G3 X136.603 Y129.777 I-5.131 J-.555 E.01846
G3 X136.044 Y131.519 I-8.384 J-1.725 E.05634
G1 X135.903 Y131.454 E.00479
G1 X135.541 Y131.285 E.01229
G1 X135.178 Y131.115 E.01229
G1 X134.495 Y130.797 E.02315
G2 X134.519 Y125.258 I-6.513 J-2.798 E.17486
M204 S10000
G1 X135.256 Y125.505 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.466804
G1 F1456
M204 S6000
G1 X135.524 Y125.623 E.01012
; LINE_WIDTH: 0.502108
G1 X135.547 Y125.634 E.00093
; LINE_WIDTH: 0.539805
G1 X135.569 Y125.644 E.001
; LINE_WIDTH: 0.560991
G3 X135.569 Y130.356 I-7.611 J2.356 E.20196
G1 X135.547 Y130.366 E.00104
; LINE_WIDTH: 0.50212
G1 X135.524 Y130.377 E.00092
; LINE_WIDTH: 0.466818
G1 X135.256 Y130.495 E.01012
; CHANGE_LAYER
; Z_HEIGHT: 2.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F8492.612
G1 X135.524 Y130.377 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 11/26
; update layer progress
M73 L11
M991 S0 P10 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z2.4 I-.516 J-1.102 P1  F42000
G1 X125.334 Y135.143 Z2.4
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1487
M204 S6000
G2 X130.666 Y135.143 I2.666 J-7.158 E.1807
G1 X131.059 Y135.984 E.0308
G3 X124.941 Y135.984 I-3.059 J-8.002 E.2075
G1 X125.308 Y135.197 E.02881
M204 S10000
G1 X125.192 Y134.662 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1487
M204 S5000
G1 X125.815 Y134.894 E.02043
G2 X130.865 Y134.64 I2.185 J-6.907 E.15869
G1 X131.049 Y135.035 E.01337
G1 X131.368 Y135.719 E.0232
G1 X131.537 Y136.082 E.01229
G1 X131.587 Y136.19 E.00367
G3 X126.921 Y136.875 I-3.585 J-8.174 E.14666
G3 X124.413 Y136.19 I1.082 J-8.888 E.08019
G1 X124.463 Y136.082 E.00367
G1 X124.632 Y135.719 E.01229
G1 X124.801 Y135.357 E.01229
G1 X125.135 Y134.64 E.02428
G1 X125.136 Y134.641 E.00002
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.815 Y134.894 E-.27546
G1 X126.289 Y135.03 E-.18743
G1 X126.772 Y135.13 E-.18754
G1 X127.058 Y135.169 E-.10958
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z2.6 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z2.6
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z2.6 F4000
            G39.3 S1
            G0 Z2.6 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.568 Y135.701 F42000
G1 Z2.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.560992
G1 F1487
M204 S6000
G1 X125.575 Y135.716 E.00071
G2 X130.425 Y135.716 I2.425 J-7.769 E.2079
G1 X130.432 Y135.701 E.00071
; LINE_WIDTH: 0.514332
G1 X130.563 Y135.403 E.01251
M204 S10000
G1 X125.568 Y135.701 F42000
; LINE_WIDTH: 0.514372
G1 F1487
M204 S6000
G1 X125.437 Y135.403 E.01251
; WIPE_START
G1 F7635.997
G1 X125.568 Y135.701 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.746 Y130.094 Z2.6 F42000
G1 X135.143 Y125.334 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1487
M204 S6000
G1 X135.984 Y124.941 E.0308
G1 X136.118 Y125.31 E.01302
G3 X135.984 Y131.059 I-8.158 J2.685 E.1945
G1 X135.143 Y130.666 E.0308
G2 X135.163 Y125.39 I-7.158 J-2.666 E.17871
M204 S10000
G1 X134.64 Y125.135 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1487
M204 S5000
G1 X135.357 Y124.801 E.02428
G1 X135.719 Y124.632 E.01229
G1 X136.082 Y124.463 E.01229
G1 X136.19 Y124.413 E.00367
G1 X136.226 Y124.497 E.0028
G3 X136.875 Y129.079 I-8.116 J3.488 E.14389
G3 X136.19 Y131.587 I-8.51 J-.979 E.08021
G1 X136.082 Y131.537 E.00367
G1 X135.719 Y131.368 E.01229
G1 X135.357 Y131.199 E.01229
G1 X134.64 Y130.865 E.02428
G2 X134.664 Y125.19 I-6.654 J-2.865 E.17915
M204 S10000
G1 X135.403 Y125.437 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.514321
G1 F1487
M204 S6000
G1 X135.701 Y125.568 E.01251
; LINE_WIDTH: 0.560993
M73 P75 R2
G1 X135.716 Y125.575 E.00071
G3 X135.716 Y130.425 I-7.769 J2.425 E.2079
G1 X135.701 Y130.432 E.00071
; LINE_WIDTH: 0.514387
G1 X135.403 Y130.563 E.01252
; WIPE_START
G1 F7635.743
G1 X135.701 Y130.432 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.094 Y125.254 Z2.6 F42000
G1 X125.334 Y120.857 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1487
M204 S6000
G1 X124.941 Y120.016 E.0308
G3 X128.538 Y119.468 I3.037 J7.856 E.12165
G3 X131.059 Y120.016 I-.479 J8.276 E.08591
G1 X130.666 Y120.857 E.0308
G2 X125.39 Y120.837 I-2.666 J7.158 E.17871
M204 S10000
G1 X125.135 Y121.36 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1487
M204 S5000
G1 X124.801 Y120.643 E.02428
G1 X124.632 Y120.281 E.01229
G1 X124.463 Y119.918 E.01229
G1 X124.413 Y119.81 E.00367
G3 X128.561 Y119.077 I3.588 J8.194 E.13067
G3 X131.587 Y119.81 I-.563 J8.93 E.09617
G1 X131.537 Y119.918 E.00367
G1 X131.368 Y120.281 E.01229
G1 X131.199 Y120.643 E.01229
G1 X130.865 Y121.36 E.02428
G2 X125.19 Y121.336 I-2.865 J6.654 E.17915
M204 S10000
G1 X125.437 Y120.597 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.514321
G1 F1487
M204 S6000
G1 X125.568 Y120.299 E.01251
; LINE_WIDTH: 0.560993
G1 X125.575 Y120.284 E.00071
G3 X130.425 Y120.284 I2.425 J7.779 E.20789
G1 X130.432 Y120.299 E.00071
; LINE_WIDTH: 0.514387
G1 X130.563 Y120.597 E.01252
; WIPE_START
G1 F7635.743
G1 X130.432 Y120.299 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X125.254 Y125.906 Z2.6 F42000
G1 X120.857 Y130.666 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1487
M204 S6000
G1 X120.016 Y131.059 E.0308
G3 X120.016 Y124.941 I7.947 J-3.059 E.20756
G1 X120.857 Y125.334 E.0308
G2 X120.837 Y130.61 I7.158 J2.666 E.17871
M204 S10000
G1 X121.36 Y130.865 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1487
M204 S5000
G1 X120.643 Y131.199 E.02428
G1 X120.281 Y131.368 E.01229
G1 X119.918 Y131.537 E.01229
G1 X119.81 Y131.587 E.00367
G3 X119.202 Y126.407 I8.193 J-3.587 E.16263
G3 X119.81 Y124.413 I8.816 J1.598 E.0642
G1 X119.878 Y124.444 E.00228
G1 X119.918 Y124.463 E.00139
G1 X120.281 Y124.632 E.01229
G1 X120.644 Y124.801 E.01229
G1 X121.36 Y125.135 E.02428
G2 X121.336 Y130.81 I6.654 J2.865 E.17915
M204 S10000
G1 X120.597 Y130.563 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.514332
G1 F1487
M204 S6000
G1 X120.299 Y130.432 E.01251
; LINE_WIDTH: 0.560993
G1 X120.284 Y130.425 E.00071
G3 X120.284 Y125.575 I7.769 J-2.425 E.2079
G1 X120.299 Y125.568 E.00071
; LINE_WIDTH: 0.514389
G1 X120.597 Y125.437 E.01252
; CHANGE_LAYER
; Z_HEIGHT: 2.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F7635.714
G1 X120.299 Y125.568 E-.76
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 12/26
; update layer progress
M73 L12
M991 S0 P11 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z2.6 I-1.082 J.557 P1  F42000
G1 X125.284 Y135.248 Z2.6
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1517
M204 S6000
G2 X130.716 Y135.248 I2.716 J-7.267 E.18406
G1 X131.108 Y136.09 E.0308
G3 X124.892 Y136.09 I-3.108 J-8.112 E.21087
G1 X125.259 Y135.303 E.02881
M204 S10000
G1 X125.307 Y134.84 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1517
M204 S5000
G2 X130.914 Y134.745 I2.689 J-6.827 E.1768
G1 X131.435 Y135.864 E.03794
G1 X131.605 Y136.227 E.01229
G1 X131.636 Y136.295 E.00231
G3 X129.073 Y136.993 I-3.536 J-7.929 E.08195
G3 X126.97 Y136.998 I-1.073 J-8.995 E.06476
G3 X124.364 Y136.295 I1.032 J-9.008 E.08327
G1 X124.395 Y136.227 E.00231
G1 X124.565 Y135.864 E.01229
G1 X125.086 Y134.745 E.03794
G1 X125.252 Y134.816 E.00553
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.779 Y135.008 E-.21314
G1 X126.262 Y135.143 E-.19048
G1 X126.753 Y135.245 E-.19054
G1 X127.185 Y135.304 E-.16583
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z2.8 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z2.8
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z2.8 F4000
            G39.3 S1
            G0 Z2.8 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.388 Y135.507 F42000
G1 Z2.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.55898
G1 F1517
M204 S6000
G1 X125.525 Y135.823 E.01447
G2 X130.47 Y135.824 I2.475 J-7.882 E.21119
G1 X130.612 Y135.507 E.01459
; WIPE_START
G1 F6975.934
G1 X130.47 Y135.824 E-.13184
G1 X129.932 Y135.974 E-.21252
M73 P76 R2
G1 X129.189 Y136.117 E-.28747
G1 X128.854 Y136.157 E-.12818
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X132.723 Y129.578 Z2.8 F42000
G1 X135.248 Y125.284 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1517
M204 S6000
G1 X136.09 Y124.892 E.0308
G1 X136.228 Y125.274 E.01347
G3 X136.09 Y131.108 I-8.27 J2.722 E.19741
G1 X135.248 Y130.716 E.0308
G2 X135.269 Y125.341 I-7.267 J-2.716 E.18207
M204 S10000
G1 X134.745 Y125.086 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1517
M204 S5000
G1 X135.864 Y124.565 E.03794
G1 X136.227 Y124.395 E.01229
G1 X136.295 Y124.364 E.00231
G1 X136.307 Y124.393 E.00097
G3 X136.998 Y129.03 I-8.193 J3.59 E.14576
G3 X136.295 Y131.636 I-8.64 J-.933 E.08329
G1 X136.227 Y131.605 E.00231
G1 X135.864 Y131.435 E.01229
G1 X134.745 Y130.914 E.03794
G2 X134.769 Y125.141 I-6.755 J-2.914 E.18226
M204 S10000
G1 X135.507 Y125.388 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.558979
G1 F1517
M204 S6000
G1 X135.823 Y125.525 E.01447
G3 X135.824 Y130.47 I-7.882 J2.475 E.21119
G1 X135.507 Y130.612 E.01459
; WIPE_START
G1 F6975.956
G1 X135.824 Y130.47 E-.13183
G1 X135.974 Y129.932 E-.21251
G1 X136.117 Y129.189 E-.28742
G1 X136.157 Y128.854 E-.12824
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.037 Y124.293 Z2.8 F42000
G1 X125.284 Y120.752 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1517
M204 S6000
G1 X124.892 Y119.91 E.0308
G3 X128.482 Y119.349 I3.084 J7.959 E.12146
G3 X131.108 Y119.91 I-.492 J8.717 E.08943
G1 X130.716 Y120.752 E.0308
G2 X125.341 Y120.731 I-2.716 J7.267 E.18207
M204 S10000
G1 X125.086 Y121.255 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1517
M204 S5000
G1 X124.565 Y120.136 E.03794
G1 X124.395 Y119.773 E.01229
G1 X124.364 Y119.705 E.00231
G3 X128.505 Y118.957 I3.637 J8.299 E.13049
G3 X131.636 Y119.705 I-.449 J8.813 E.09949
G1 X131.605 Y119.773 E.00231
G1 X131.435 Y120.136 E.01229
G1 X130.914 Y121.255 E.03794
G2 X125.141 Y121.231 I-2.914 J6.755 E.18226
M204 S10000
G1 X125.388 Y120.493 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.558979
G1 F1517
M204 S6000
G1 X125.525 Y120.177 E.01447
G3 X130.47 Y120.176 I2.475 J7.892 E.21118
G1 X130.612 Y120.493 E.01459
; WIPE_START
G1 F6975.954
G1 X130.47 Y120.176 E-.13182
G1 X129.932 Y120.026 E-.21251
G1 X129.189 Y119.883 E-.28746
G1 X128.854 Y119.843 E-.12821
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.293 Y125.963 Z2.8 F42000
G1 X120.752 Y130.716 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1517
M204 S6000
G1 X119.91 Y131.108 E.0308
G3 X119.91 Y124.892 I8.11 J-3.108 E.21087
G1 X120.752 Y125.284 E.0308
G2 X120.731 Y130.659 I7.267 J2.716 E.18207
M204 S10000
G1 X121.255 Y130.914 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1517
M204 S5000
G1 X120.136 Y131.435 E.03794
G1 X119.773 Y131.605 E.01229
G1 X119.705 Y131.636 E.00231
G3 X119.705 Y124.364 I8.297 J-3.636 E.22995
G1 X119.773 Y124.395 E.00231
G1 X119.853 Y124.433 E.0027
G1 X120.215 Y124.602 E.01229
G1 X121.255 Y125.086 E.03523
G2 X121.231 Y130.859 I6.755 J2.914 E.18226
M204 S10000
G1 X120.493 Y130.612 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.55898
G1 F1517
M204 S6000
G1 X120.177 Y130.475 E.01447
G3 X120.176 Y125.53 I7.892 J-2.475 E.21118
M73 P77 R2
G1 X120.493 Y125.388 E.01459
; CHANGE_LAYER
; Z_HEIGHT: 2.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6975.941
G1 X120.176 Y125.53 E-.13182
G1 X120.026 Y126.068 E-.21251
G1 X119.883 Y126.811 E-.28736
G1 X119.843 Y127.146 E-.12832
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 13/26
; update layer progress
M73 L13
M991 S0 P12 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z2.8 I-1.015 J.671 P1  F42000
G1 X125.25 Y135.322 Z2.8
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1531
M204 S6000
G2 X130.75 Y135.322 I2.75 J-7.271 E.18648
G1 X131.142 Y136.163 E.0308
G3 X124.858 Y136.163 I-3.142 J-8.185 E.21322
G1 X125.225 Y135.376 E.02881
M204 S10000
G1 X125.115 Y134.843 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1531
M204 S5000
G1 X125.755 Y135.083 E.02101
G2 X130.948 Y134.819 I2.245 J-7.041 E.16326
G1 X130.958 Y134.84 E.0007
G1 X131.654 Y136.332 E.0506
G1 X131.671 Y136.368 E.00123
G3 X126.458 Y137.007 I-3.694 J-8.558 E.16358
G3 X124.329 Y136.368 I1.547 J-9.026 E.06845
G1 X124.346 Y136.332 E.00123
G1 X125.052 Y134.819 E.0513
G1 X125.059 Y134.821 E.00022
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.755 Y135.083 E-.28264
G1 X126.243 Y135.222 E-.19256
G1 X126.739 Y135.325 E-.19263
G1 X126.979 Y135.358 E-.09217
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z3 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z3
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z3 F4000
            G39.3 S1
            G0 Z3 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.356 Y135.576 F42000
G1 Z2.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.560378
G1 F1531
M204 S6000
G1 X125.491 Y135.897 E.01467
G2 X130.495 Y135.901 I2.509 J-7.967 E.21429
G1 X130.644 Y135.576 E.01507
; WIPE_START
G1 F6957.086
G1 X130.495 Y135.901 E-.13582
G1 X129.951 Y136.052 E-.21461
G1 X129.201 Y136.197 E-.29022
G1 X128.889 Y136.234 E-.11935
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X132.746 Y129.648 Z3 F42000
G1 X135.322 Y125.25 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1531
M204 S6000
G1 X136.163 Y124.858 E.0308
G1 X136.305 Y125.248 E.01378
G3 X136.163 Y131.142 I-8.348 J2.748 E.19945
G1 X135.322 Y130.75 E.0308
G2 X135.343 Y125.306 I-7.271 J-2.75 E.18449
M204 S10000
G1 X134.819 Y125.052 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1531
M204 S5000
G1 X136.332 Y124.346 E.0513
G1 X136.372 Y124.339 E.00126
G3 X137.081 Y129.016 I-8.26 J3.644 E.14706
G3 X136.368 Y131.671 I-8.727 J-.92 E.08482
G1 X136.332 Y131.654 E.00123
G1 X134.819 Y130.948 E.0513
G2 X134.843 Y125.107 I-6.776 J-2.948 E.18451
M204 S10000
G1 X135.576 Y125.356 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.560374
G1 F1531
M204 S6000
G1 X135.901 Y125.505 E.01507
G3 X135.897 Y130.509 I-7.972 J2.495 E.21429
G1 X135.576 Y130.644 E.01467
; WIPE_START
G1 F6957.144
G1 X135.897 Y130.509 E-.13225
G1 X136.048 Y129.968 E-.21366
G1 X136.167 Y129.397 E-.22139
G1 X136.235 Y128.895 E-.19271
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.123 Y124.323 Z3 F42000
G1 X125.25 Y120.678 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1531
M204 S6000
G1 X124.858 Y119.837 E.03079
M73 P78 R2
G3 X128.463 Y119.266 I3.119 J8.035 E.12201
G3 X131.142 Y119.837 I-.409 J8.501 E.09126
G1 X130.75 Y120.678 E.0308
G2 X125.306 Y120.657 I-2.75 J7.271 E.18449
M204 S10000
G1 X125.052 Y121.181 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1531
M204 S5000
G1 X124.346 Y119.668 E.0513
G1 X124.329 Y119.632 E.00123
G3 X128.486 Y118.875 I3.671 J8.374 E.131
G3 X131.671 Y119.632 I-.488 J9.133 E.10112
G1 X131.654 Y119.668 E.00123
G1 X130.948 Y121.181 E.0513
G2 X125.107 Y121.157 I-2.948 J6.776 E.18451
M204 S10000
G1 X125.356 Y120.423 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.560375
G1 F1531
M204 S6000
G1 X125.491 Y120.103 E.01464
G3 X130.495 Y120.099 I2.509 J7.967 E.2143
G1 X130.644 Y120.424 E.01508
; WIPE_START
G1 F6957.138
G1 X130.495 Y120.099 E-.13592
G1 X129.951 Y119.948 E-.21468
G1 X129.201 Y119.803 E-.29024
G1 X128.889 Y119.766 E-.11916
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.319 Y125.879 Z3 F42000
G1 X120.678 Y130.75 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1531
M204 S6000
G1 X119.837 Y131.142 E.03079
G3 X119.837 Y124.858 I8.185 J-3.142 E.21321
G1 X120.678 Y125.25 E.0308
G2 X120.657 Y130.694 I7.271 J2.75 E.18449
M204 S10000
G1 X121.128 Y130.807 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1531
M204 S5000
G1 X121.181 Y130.948 E.00464
G1 X119.668 Y131.654 E.0513
G1 X119.632 Y131.671 E.00123
G3 X118.993 Y126.458 I8.558 J-3.694 E.16358
G3 X119.632 Y124.329 I9.026 J1.547 E.06845
G1 X119.668 Y124.346 E.00123
G1 X119.995 Y124.499 E.01108
G1 X121.181 Y125.052 E.04022
G2 X120.917 Y130.245 I6.776 J2.948 E.16326
G1 X121.107 Y130.751 E.0166
M204 S10000
G1 X120.423 Y130.644 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.56038
G1 F1531
M204 S6000
G1 X120.103 Y130.509 E.01464
G3 X120.099 Y125.505 I7.967 J-2.509 E.2143
G1 X120.424 Y125.356 E.01506
; CHANGE_LAYER
; Z_HEIGHT: 2.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6957.062
G1 X120.099 Y125.505 E-.13576
G1 X119.948 Y126.049 E-.21468
G1 X119.803 Y126.799 E-.29023
G1 X119.766 Y127.111 E-.11932
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 14/26
; update layer progress
M73 L14
M991 S0 P13 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z3 I-1.015 J.671 P1  F42000
G1 X125.228 Y135.369 Z3
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1535
M204 S6000
G1 X125.621 Y135.508 E.01381
G2 X130.772 Y135.369 I2.374 J-7.545 E.17411
G1 X131.164 Y136.21 E.03079
G3 X124.836 Y136.21 I-3.164 J-8.234 E.2147
G1 X125.203 Y135.423 E.0288
M204 S10000
G1 X125.093 Y134.889 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1535
M204 S5000
G1 X125.74 Y135.132 E.02122
G2 X130.97 Y134.865 I2.26 J-7.089 E.16444
G1 X130.977 Y134.881 E.00054
G1 X131.688 Y136.406 E.05168
G1 X131.692 Y136.415 E.00032
G3 X126.448 Y137.057 I-3.693 J-8.419 E.16466
G3 X124.308 Y136.415 I1.806 J-9.906 E.06881
G1 X124.312 Y136.406 E.00032
G1 X125.03 Y134.865 E.05222
G1 X125.037 Y134.868 E.00022
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.74 Y135.132 E-.28521
G1 X126.23 Y135.271 E-.19388
G1 X126.73 Y135.375 E-.19399
G1 X126.957 Y135.406 E-.08692
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z3.2 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z3.2
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z3.2 F4000
            G39.3 S1
            G0 Z3.2 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.223 Y135.862 F42000
G1 Z2.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.560831
G1 F1535
M204 S6000
G2 X130.527 Y135.945 I2.776 J-7.941 E.22779
G1 X130.778 Y135.863 E.01112
; WIPE_START
G1 F6951.007
G1 X130.527 Y135.945 E-.10014
G1 X129.963 Y136.102 E-.22263
G1 X129.208 Y136.248 E-.29209
G1 X128.829 Y136.293 E-.14515
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X132.712 Y129.722 Z3.2 F42000
G1 X135.369 Y125.228 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1535
M204 S6000
G1 X136.21 Y124.836 E.03079
G1 X136.354 Y125.232 E.01397
G3 X136.21 Y131.164 I-8.398 J2.764 E.20074
G1 X135.369 Y130.772 E.03079
G2 X135.39 Y125.285 I-7.39 J-2.772 E.1859
M204 S10000
G1 X134.865 Y125.03 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1535
M204 S5000
G1 X136.406 Y124.312 E.05222
G1 X136.42 Y124.319 E.00049
G3 X137.132 Y129.022 I-8.307 J3.663 E.14789
G3 X136.415 Y131.692 I-8.777 J-.927 E.08529
G1 X136.406 Y131.688 E.00032
G1 X134.865 Y130.97 E.05222
G2 X134.889 Y125.085 I-6.823 J-2.97 E.18589
M204 S10000
M73 P79 R2
G1 X135.863 Y125.222 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.560829
G1 F1535
M204 S6000
G3 X135.945 Y130.527 I-7.949 J2.776 E.22779
G1 X135.863 Y130.777 E.01112
; WIPE_START
G1 F6951.039
G1 X135.945 Y130.527 E-.10011
G1 X136.102 Y129.963 E-.22262
G1 X136.248 Y129.208 E-.29216
G1 X136.293 Y128.829 E-.14511
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.16 Y124.285 Z3.2 F42000
G1 X125.228 Y120.631 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1535
M204 S6000
G1 X124.836 Y119.79 E.03079
G3 X128.467 Y119.215 I3.141 J8.084 E.12288
G3 X131.164 Y119.79 I-.478 J8.861 E.09185
G1 X130.772 Y120.631 E.03079
G2 X125.285 Y120.61 I-2.772 J7.39 E.1859
M204 S10000
G1 X125.03 Y121.135 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1535
M204 S5000
G1 X124.312 Y119.594 E.05222
G1 X124.308 Y119.585 E.00032
G3 X128.49 Y118.824 I3.693 J8.421 E.1318
G3 X131.692 Y119.585 I-.436 J8.95 E.10172
G1 X131.688 Y119.594 E.00032
G1 X130.97 Y121.135 E.05222
G2 X125.085 Y121.111 I-2.97 J6.823 E.18589
M204 S10000
G1 X125.223 Y120.137 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.560831
G1 F1535
M204 S6000
G3 X130.527 Y120.055 I2.776 J7.933 E.22779
G1 X130.778 Y120.137 E.01112
; WIPE_START
G1 F6951.013
G1 X130.527 Y120.055 E-.10016
G1 X129.963 Y119.898 E-.22262
G1 X129.208 Y119.752 E-.2921
G1 X128.829 Y119.707 E-.14512
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.285 Y125.84 Z3.2 F42000
G1 X120.631 Y130.772 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1535
M204 S6000
G1 X119.79 Y131.164 E.03079
G3 X119.79 Y124.836 I8.214 J-3.164 E.21472
G1 X120.344 Y125.094 E.02027
G1 X120.631 Y125.228 E.01052
G2 X120.61 Y130.715 I7.39 J2.772 E.1859
M204 S10000
G1 X121.079 Y130.823 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1535
M204 S5000
G1 X121.135 Y130.97 E.00482
G1 X119.594 Y131.688 E.05222
G1 X119.585 Y131.692 E.00032
G3 X119.585 Y124.308 I8.401 J-3.692 E.23352
G1 X119.594 Y124.312 E.00032
G1 X120.51 Y124.739 E.03103
G1 X121.135 Y125.03 E.02119
G2 X120.868 Y130.26 I6.823 J2.97 E.16444
G1 X121.058 Y130.767 E.01661
M204 S10000
G1 X120.137 Y130.777 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.560831
G1 F1535
M204 S6000
G3 X120.055 Y125.473 I7.943 J-2.776 E.22779
G1 X120.137 Y125.222 E.01112
; CHANGE_LAYER
; Z_HEIGHT: 3
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6951.001
G1 X120.055 Y125.473 E-.10012
G1 X119.898 Y126.037 E-.22264
G1 X119.752 Y126.792 E-.2921
G1 X119.707 Y127.171 E-.14515
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 15/26
; update layer progress
M73 L15
M991 S0 P14 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z3.2 I-1.011 J.678 P1  F42000
G1 X125.218 Y135.391 Z3.2
G1 Z3
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1532
M204 S6000
G1 X125.613 Y135.531 E.01391
G2 X130.782 Y135.391 I2.382 J-7.524 E.17475
G1 X131.174 Y136.232 E.03079
G3 X124.826 Y136.232 I-3.174 J-8.364 E.2153
G1 X125.193 Y135.445 E.0288
M204 S10000
G1 X125.081 Y134.911 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1532
M204 S5000
G1 X125.733 Y135.153 E.02138
G2 X130.98 Y134.888 I2.267 J-7.189 E.16489
G1 X131.294 Y135.562 E.02286
G1 X131.703 Y136.437 E.02968
G3 X124.297 Y136.437 I-3.703 J-8.527 E.23403
G1 X125.02 Y134.888 E.05254
G1 X125.025 Y134.889 E.00016
; WIPE_START
G1 F9547.055
M204 S6000
M73 P80 R2
G1 X125.733 Y135.153 E-.28716
G1 X126.225 Y135.295 E-.19448
G1 X126.726 Y135.399 E-.19462
G1 X126.944 Y135.429 E-.08374
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z3.4 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z3.4
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z3.4 F4000
            G39.3 S1
            G0 Z3.4 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.212 Y135.885 F42000
G1 Z3
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.560839
G1 F1532
M204 S6000
G2 X130.535 Y135.968 I2.786 J-7.969 E.22856
G1 X130.788 Y135.885 E.01126
; WIPE_START
G1 F6950.903
G1 X130.535 Y135.968 E-.10134
G1 X129.969 Y136.126 E-.22328
G1 X129.212 Y136.272 E-.29289
G1 X128.84 Y136.316 E-.14249
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X132.719 Y129.744 Z3.4 F42000
G1 X135.391 Y125.218 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1532
M204 S6000
G1 X136.232 Y124.826 E.03079
G1 X136.377 Y125.224 E.01407
G3 X136.232 Y131.174 I-8.422 J2.772 E.20135
G1 X135.391 Y130.782 E.03079
G2 X135.412 Y125.274 I-7.341 J-2.782 E.18669
M204 S10000
G1 X134.888 Y125.02 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1532
M204 S5000
G1 X136.437 Y124.297 E.05254
G1 X136.448 Y124.323 E.00085
G3 X137.164 Y128.962 I-8.338 J3.661 E.14589
G3 X136.437 Y131.703 I-8.856 J-.882 E.08748
G1 X134.888 Y130.98 E.05254
G2 X134.911 Y125.075 I-6.845 J-2.98 E.18654
M204 S10000
G1 X135.885 Y125.212 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.560833
G1 F1532
M204 S6000
G3 X135.968 Y130.535 I-7.97 J2.786 E.22856
G1 X135.885 Y130.788 E.01125
; WIPE_START
G1 F6950.981
G1 X135.968 Y130.535 E-.10132
G1 X136.126 Y129.969 E-.22328
G1 X136.272 Y129.212 E-.29301
G1 X136.316 Y128.839 E-.14238
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.186 Y124.293 Z3.4 F42000
G1 X125.218 Y120.609 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1532
M204 S6000
G1 X124.826 Y119.768 E.03079
G3 X128.294 Y119.181 I3.164 J8.153 E.11751
G3 X131.174 Y119.768 I-.276 J8.71 E.09797
G1 X130.782 Y120.609 E.03079
G2 X125.274 Y120.588 I-2.782 J7.341 E.18669
M204 S10000
G1 X125.02 Y121.112 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1532
M204 S5000
G1 X124.297 Y119.563 E.05254
G3 X128.317 Y118.789 I3.719 J8.495 E.12683
G3 X131.703 Y119.563 I-.296 J9.087 E.10736
G1 X130.98 Y121.112 E.05254
G2 X125.075 Y121.089 I-2.98 J6.845 E.18654
M204 S10000
G1 X125.212 Y120.115 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.560757
G1 F1532
M204 S6000
G3 X130.535 Y120.032 I2.786 J7.979 E.22852
G1 X130.788 Y120.115 E.01125
; WIPE_START
G1 F6952.003
G1 X130.535 Y120.032 E-.10132
G1 X129.969 Y119.874 E-.22328
G1 X129.212 Y119.728 E-.29301
G1 X128.839 Y119.684 E-.14239
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.293 Y125.814 Z3.4 F42000
G1 X120.609 Y130.782 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1532
M204 S6000
G1 X119.768 Y131.174 E.03079
G3 X119.768 Y124.826 I8.272 J-3.174 E.21539
G1 X120.273 Y125.061 E.01848
M73 P81 R2
G1 X120.609 Y125.218 E.01232
G2 X120.588 Y130.726 I7.341 J2.782 E.18669
M204 S10000
G1 X121.055 Y130.829 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1532
M204 S5000
G1 X121.112 Y130.98 E.00495
G1 X119.563 Y131.703 E.05254
G3 X119.563 Y124.297 I8.401 J-3.703 E.23421
G1 X120.438 Y124.706 E.02968
G1 X121.112 Y125.02 E.02286
G2 X120.845 Y130.268 I6.845 J2.98 E.16499
G1 X121.034 Y130.773 E.01658
M204 S10000
G1 X120.115 Y130.788 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.560835
G1 F1532
M204 S6000
G3 X120.032 Y125.465 I7.969 J-2.786 E.22856
G1 X120.115 Y125.212 E.01125
; CHANGE_LAYER
; Z_HEIGHT: 3.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6950.947
G1 X120.032 Y125.465 E-.10131
G1 X119.874 Y126.031 E-.22328
G1 X119.728 Y126.788 E-.29295
G1 X119.684 Y127.161 E-.14246
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 16/26
; update layer progress
M73 L16
M991 S0 P15 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z3.4 I-1.01 J.678 P1  F42000
G1 X125.215 Y135.397 Z3.4
G1 Z3.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1540
M204 S6000
G2 X130.785 Y135.397 I2.785 J-7.433 E.18878
G1 X131.177 Y136.238 E.03079
G3 X124.823 Y136.238 I-3.177 J-8.274 E.21558
G1 X125.19 Y135.451 E.0288
M204 S10000
G1 X125.018 Y134.893 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1540
M204 S5000
G2 X130.982 Y134.893 I2.982 J-6.903 E.18846
G1 X130.993 Y134.915 E.00077
G1 X131.705 Y136.442 E.05177
G3 X124.295 Y136.442 I-3.705 J-8.445 E.23431
G1 X124.992 Y134.947 E.0507
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.707 Y135.155 E-.28274
G1 X126.22 Y135.3 E-.20289
G1 X126.742 Y135.408 E-.20242
G1 X126.93 Y135.433 E-.07195
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z3.6 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z3.6
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z3.6 F4000
            G39.3 S1
            G0 Z3.6 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.318 Y135.657 F42000
G1 Z3.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.558594
G1 F1540
M204 S6000
G1 X125.456 Y135.97 E.01439
G2 X130.544 Y135.971 I2.544 J-8.032 E.21719
G1 X130.682 Y135.657 E.0144
; WIPE_START
G1 F6981.155
G1 X130.544 Y135.971 E-.13023
G1 X129.973 Y136.131 E-.22539
G1 X129.187 Y136.282 E-.30392
M73 P81 R1
G1 X128.924 Y136.306 E-.10047
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X132.771 Y129.714 Z3.6 F42000
G1 X135.397 Y125.215 Z3.6
G1 Z3.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1540
M204 S6000
G1 X136.238 Y124.823 E.03078
G1 X136.395 Y125.262 E.01546
G3 X136.238 Y131.177 I-8.448 J2.735 E.20012
G1 X135.397 Y130.785 E.03079
G2 X135.418 Y125.271 I-7.433 J-2.785 E.18679
M204 S10000
G1 X134.893 Y125.018 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1540
M204 S5000
G1 X136.443 Y124.295 E.05255
G1 X136.55 Y124.545 E.00836
G3 X136.442 Y131.705 I-8.524 J3.452 E.22602
G1 X134.893 Y130.982 E.05254
G2 X134.916 Y125.073 I-6.903 J-2.982 E.18662
M204 S10000
G1 X135.657 Y125.318 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.558657
G1 F1540
M204 S6000
G1 X135.97 Y125.456 E.01439
G3 X135.971 Y130.544 I-8.033 J2.544 E.21721
G1 X135.657 Y130.682 E.0144
; WIPE_START
G1 F6980.312
G1 X135.971 Y130.544 E-.13024
G1 X136.131 Y129.973 E-.2254
G1 X136.281 Y129.187 E-.30394
G1 X136.313 Y128.925 E-.10041
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.207 Y124.346 Z3.6 F42000
G1 X125.215 Y120.603 Z3.6
G1 Z3.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1540
M204 S6000
G1 X124.823 Y119.762 E.03079
G3 X128.338 Y119.177 I3.165 J8.166 E.11904
G3 X131.177 Y119.762 I-.371 J8.984 E.09658
G1 X130.785 Y120.603 E.03079
G2 X125.271 Y120.582 I-2.785 J7.433 E.18679
M204 S10000
M73 P82 R1
G1 X125.018 Y121.107 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1540
M204 S5000
G1 X124.295 Y119.558 E.05254
G3 X128.361 Y118.786 I3.72 J8.497 E.12825
G3 X131.705 Y119.558 I-.382 J9.281 E.10606
G1 X130.982 Y121.107 E.05254
G2 X125.073 Y121.084 I-2.982 J6.903 E.18662
M204 S10000
G1 X125.318 Y120.343 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.558593
G1 F1540
M204 S6000
G1 X125.456 Y120.029 E.01439
G3 X130.544 Y120.029 I2.544 J8.022 E.21719
G1 X130.682 Y120.343 E.0144
; WIPE_START
G1 F6981.17
G1 X130.544 Y120.029 E-.13021
G1 X129.973 Y119.869 E-.22539
G1 X129.187 Y119.718 E-.30396
G1 X128.924 Y119.694 E-.10045
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.344 Y125.799 Z3.6 F42000
G1 X120.603 Y130.785 Z3.6
G1 Z3.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1540
M204 S6000
G1 X119.762 Y131.177 E.03079
G3 X119.762 Y124.823 I8.278 J-3.177 E.21558
G1 X120.603 Y125.215 E.03079
G2 X120.582 Y130.729 I7.433 J2.785 E.18679
M204 S10000
G1 X121.049 Y130.829 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1540
M204 S5000
G1 X121.107 Y130.982 E.00503
G1 X119.558 Y131.705 E.05254
G3 X119.558 Y124.295 I8.448 J-3.705 E.2343
G1 X121.085 Y125.007 E.05177
G1 X121.107 Y125.018 E.00077
G2 X120.849 Y130.292 I6.903 J2.982 E.1658
G1 X121.028 Y130.773 E.01577
M204 S10000
G1 X120.343 Y130.682 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.558587
G1 F1540
M204 S6000
G1 X120.03 Y130.544 E.01438
G3 X120.029 Y125.456 I8.032 J-2.544 E.21718
G1 X120.343 Y125.318 E.0144
; CHANGE_LAYER
; Z_HEIGHT: 3.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6981.259
G1 X120.029 Y125.456 E-.13024
G1 X119.869 Y126.027 E-.22539
G1 X119.719 Y126.807 E-.30179
G1 X119.694 Y127.076 E-.10258
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 17/26
; update layer progress
M73 L17
M991 S0 P16 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z3.6 I-1.014 J.673 P1  F42000
G1 X125.215 Y135.397 Z3.6
G1 Z3.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1536
M204 S6000
G2 X130.785 Y135.397 I2.785 J-7.425 E.18881
G1 X131.178 Y136.239 E.03079
G3 X124.823 Y136.239 I-3.178 J-8.295 E.21558
G1 X125.189 Y135.452 E.0288
M204 S10000
G1 X125.018 Y134.892 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1536
M204 S5000
G2 X130.982 Y134.892 I2.982 J-6.86 E.1885
G1 X131.172 Y135.298 E.01378
G1 X131.705 Y136.442 E.03877
G3 X124.295 Y136.442 I-3.705 J-8.446 E.23429
G1 X124.993 Y134.946 E.0507
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.662 Y135.14 E-.26493
G1 X126.216 Y135.299 E-.2189
G1 X126.774 Y135.413 E-.21657
G1 X126.93 Y135.432 E-.0596
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z3.8 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z3.8
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z3.8 F4000
            G39.3 S1
            G0 Z3.8 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.209 Y135.891 F42000
G1 Z3.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.561552
G1 F1536
M204 S6000
G2 X130.791 Y135.891 I2.791 J-8.016 E.24036
; WIPE_START
G1 F6941.34
G1 X130.209 Y136.07 E-.23139
G1 X129.679 Y136.196 E-.20698
G1 X128.966 Y136.311 E-.27419
G1 X128.842 Y136.32 E-.04744
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X132.722 Y129.747 Z3.8 F42000
G1 X135.398 Y125.215 Z3.8
M73 P83 R1
G1 Z3.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1536
M204 S6000
G1 X136.239 Y124.823 E.03079
G1 X136.35 Y125.129 E.01082
G3 X136.239 Y131.177 I-8.38 J2.871 E.20479
G1 X135.398 Y130.785 E.03079
G2 X135.418 Y125.271 I-7.425 J-2.785 E.18682
M204 S10000
G1 X134.892 Y125.018 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1536
M204 S5000
G1 X136.443 Y124.295 E.05257
G1 X136.507 Y124.445 E.00501
G3 X136.442 Y131.705 I-8.484 J3.554 E.22933
G1 X134.892 Y130.982 E.05255
G2 X134.916 Y125.073 I-6.86 J-2.982 E.18665
M204 S10000
G1 X135.892 Y125.209 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.561562
G1 F1536
M204 S6000
G3 X135.891 Y130.791 I-8.029 J2.789 E.24038
; WIPE_START
G1 F6941.215
G1 X136.07 Y130.207 E-.23188
G1 X136.195 Y129.68 E-.20611
G1 X136.288 Y129.14 E-.20789
G1 X136.314 Y128.841 E-.11412
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.185 Y124.292 Z3.8 F42000
G1 X125.215 Y120.602 Z3.8
G1 Z3.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1536
M204 S6000
G1 X124.823 Y119.761 E.03079
G3 X128.339 Y119.177 I3.185 J8.289 E.11906
G3 X131.178 Y119.761 I-.379 J9.021 E.09655
G1 X130.785 Y120.602 E.03079
G2 X125.271 Y120.582 I-2.785 J7.46 E.18678
M204 S10000
G1 X125.018 Y121.108 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1536
M204 S5000
G1 X124.295 Y119.558 E.05255
G3 X128.362 Y118.785 I3.728 J8.529 E.12826
G3 X131.705 Y119.558 I-.394 J9.317 E.10603
G1 X130.982 Y121.108 E.05255
G2 X125.073 Y121.085 I-2.982 J6.903 E.18659
M204 S10000
G1 X125.209 Y120.109 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.561245
G1 F1536
M204 S6000
G3 X130.791 Y120.109 I2.791 J7.927 E.24031
; WIPE_START
G1 F6945.459
G1 X130.207 Y119.93 E-.23193
G1 X129.68 Y119.805 E-.20607
G1 X128.966 Y119.689 E-.27457
G1 X128.842 Y119.68 E-.04743
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.294 Y125.809 Z3.8 F42000
G1 X120.602 Y130.785 Z3.8
G1 Z3.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1536
M204 S6000
G1 X119.761 Y131.177 E.03079
G3 X119.761 Y124.823 I8.295 J-3.177 E.21558
G1 X120.603 Y125.215 E.03079
G2 X120.582 Y130.729 I7.46 J2.785 E.18678
M204 S10000
G1 X120.988 Y130.688 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1536
M204 S5000
G2 X121.108 Y130.982 I7.023 J-2.688 E.00977
G1 X119.558 Y131.705 E.05255
G3 X119.558 Y124.295 I8.446 J-3.705 E.23429
G1 X120.702 Y124.828 E.03877
G1 X121.108 Y125.018 E.01378
G2 X120.967 Y130.631 I6.903 J2.982 E.17683
M204 S10000
G1 X120.109 Y130.791 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.56124
G1 F1536
M204 S6000
G3 X120.109 Y125.209 I8.008 J-2.791 E.24022
; CHANGE_LAYER
; Z_HEIGHT: 3.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6945.526
G1 X119.93 Y125.791 E-.23144
G1 X119.805 Y126.321 E-.20685
G1 X119.689 Y127.034 E-.27428
G1 X119.68 Y127.158 E-.04744
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 18/26
; update layer progress
M73 L18
M991 S0 P17 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z3.8 I-1.01 J.679 P1  F42000
G1 X125.214 Y135.398 Z3.8
G1 Z3.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1535
M204 S6000
G1 X125.356 Y135.448 E.00498
M73 P84 R1
G2 X130.786 Y135.398 I2.646 J-7.469 E.18385
G1 X131.178 Y136.239 E.03079
G3 X124.822 Y136.239 I-3.178 J-8.318 E.21558
G1 X125.189 Y135.453 E.0288
M204 S10000
G1 X125.018 Y134.891 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1535
M204 S5000
G2 X130.982 Y134.891 I2.982 J-6.858 E.18848
G1 X131.35 Y135.681 E.02679
G1 X131.705 Y136.441 E.02576
G3 X124.295 Y136.441 I-3.705 J-8.448 E.23427
G1 X124.993 Y134.946 E.05071
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.62 Y135.126 E-.24801
G1 X126.211 Y135.298 E-.23399
G1 X126.807 Y135.418 E-.23071
G1 X126.93 Y135.431 E-.04729
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z4 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z4
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z4 F4000
            G39.3 S1
            G0 Z4 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.209 Y135.891 F42000
G1 Z3.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.561883
G1 F1535
M204 S6000
G2 X130.791 Y135.891 I2.791 J-8.021 E.24049
; WIPE_START
G1 F6936.918
G1 X130.237 Y136.062 E-.22041
G1 X129.667 Y136.197 E-.22252
G1 X129.025 Y136.304 E-.24709
G1 X128.842 Y136.319 E-.06999
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X132.722 Y129.746 Z4 F42000
G1 X135.398 Y125.214 Z4
G1 Z3.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1535
M204 S6000
G1 X136.239 Y124.822 E.03079
G1 X136.327 Y125.064 E.00853
G3 X136.239 Y131.178 I-8.35 J2.938 E.2071
G1 X135.398 Y130.786 E.03079
G2 X135.419 Y125.271 I-7.428 J-2.786 E.18684
M204 S10000
G1 X134.891 Y125.018 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1535
M204 S5000
G1 X136.443 Y124.295 E.05259
G1 X136.464 Y124.345 E.00167
G3 X136.441 Y131.705 I-8.44 J3.654 E.23266
G1 X134.891 Y130.982 E.05255
G2 X134.915 Y125.073 I-6.858 J-2.982 E.18664
M204 S10000
G1 X135.891 Y125.209 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.561893
G1 F1535
M204 S6000
G3 X135.891 Y130.791 I-8.025 J2.79 E.2405
; WIPE_START
G1 F6936.781
G1 X136.062 Y130.236 E-.2208
G1 X136.197 Y129.668 E-.22171
G1 X136.293 Y129.096 E-.22051
G1 X136.315 Y128.841 E-.09698
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.187 Y124.292 Z4 F42000
G1 X125.214 Y120.602 Z4
G1 Z3.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1535
M204 S6000
G1 X124.822 Y119.761 E.03079
G3 X128.339 Y119.176 I3.202 J8.394 E.11905
G3 X131.178 Y119.761 I-.445 J9.346 E.09653
G1 X130.786 Y120.602 E.03079
G2 X125.271 Y120.581 I-2.786 J7.427 E.18684
M204 S10000
G1 X125.018 Y121.109 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1535
M204 S5000
G1 X124.295 Y119.559 E.05255
G3 X128.362 Y118.785 I3.736 J8.558 E.12826
G3 X131.705 Y119.559 I-.377 J9.233 E.10605
G1 X130.982 Y121.109 E.05255
G2 X125.073 Y121.085 I-2.982 J6.85 E.18665
M204 S10000
G1 X125.209 Y120.109 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.561432
G1 F1535
M204 S6000
M73 P85 R1
G3 X130.791 Y120.109 I2.791 J8.019 E.24028
; WIPE_START
G1 F6942.948
G1 X129.996 Y119.876 E-.31488
G1 X129.328 Y119.74 E-.25899
G1 X128.841 Y119.686 E-.18613
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.284 Y125.808 Z4 F42000
G1 X120.595 Y130.764 Z4
G1 Z3.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1535
M204 S6000
G1 X120.602 Y130.786 E.00074
G1 X119.761 Y131.178 E.03079
G3 X119.761 Y124.822 I8.317 J-3.178 E.21558
G1 X120.153 Y125.005 E.01436
G1 X120.602 Y125.214 E.01643
G2 X120.329 Y129.904 I7.427 J2.786 E.15821
G1 X120.577 Y130.707 E.02788
M204 S10000
G1 X120.972 Y130.646 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1535
M204 S5000
G2 X121.109 Y130.982 I6.986 J-2.646 E.01113
G1 X119.559 Y131.705 E.05255
G3 X119.559 Y124.295 I8.448 J-3.705 E.23427
G1 X120.319 Y124.65 E.02576
G1 X121.109 Y125.018 E.02679
G2 X120.951 Y130.59 I6.85 J2.982 E.17552
M204 S10000
G1 X120.109 Y130.791 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.561511
G1 F1535
M204 S6000
G3 X120.109 Y125.209 I8.012 J-2.791 E.24033
; CHANGE_LAYER
; Z_HEIGHT: 3.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6941.89
G1 X119.876 Y126.004 E-.31486
G1 X119.74 Y126.672 E-.25901
G1 X119.686 Y127.159 E-.18614
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 19/26
; update layer progress
M73 L19
M991 S0 P18 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z4 I-1.011 J.678 P1  F42000
G1 X125.214 Y135.399 Z4
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1533
M204 S6000
G1 X125.351 Y135.447 E.00481
G2 X130.786 Y135.399 I2.651 J-7.559 E.18395
G1 X131.178 Y136.24 E.03078
G3 X124.822 Y136.24 I-3.178 J-8.398 E.21552
G1 X125.189 Y135.453 E.0288
M204 S10000
G1 X125.018 Y134.891 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1533
M204 S5000
G2 X130.982 Y134.891 I2.982 J-6.847 E.18848
G1 X131.529 Y136.065 E.03979
G1 X131.704 Y136.441 E.01276
G3 X124.296 Y136.441 I-3.704 J-8.501 E.23419
G1 X124.993 Y134.945 E.05071
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.578 Y135.111 E-.23113
G1 X126.184 Y135.291 E-.23997
G1 X126.842 Y135.424 E-.25511
G1 X126.93 Y135.433 E-.03379
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z4.2 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z4.2
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z4.2 F4000
            G39.3 S1
            G0 Z4.2 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.21 Y135.89 F42000
G1 Z3.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.561855
G1 F1533
M204 S6000
G2 X130.79 Y135.89 I2.79 J-8.018 E.24044
; WIPE_START
G1 F6937.294
G1 X130.025 Y136.117 E-.30341
G1 X129.295 Y136.265 E-.28286
G1 X128.84 Y136.311 E-.17374
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X132.724 Y129.741 Z4.2 F42000
G1 X135.399 Y125.214 Z4.2
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1533
M204 S6000
G1 X136.24 Y124.822 E.03078
G1 X136.304 Y124.998 E.00623
G3 X136.24 Y131.178 I-8.321 J3.004 E.20942
G1 X135.399 Y130.786 E.03079
G2 X135.42 Y125.27 I-7.44 J-2.786 E.18686
M204 S10000
G1 X134.891 Y125.018 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1533
M204 S5000
G1 X136.442 Y124.295 E.05259
G1 X136.622 Y124.724 E.0143
G3 X136.441 Y131.704 I-8.6 J3.269 E.22006
G1 X134.891 Y130.982 E.05256
G2 X134.915 Y125.074 I-6.847 J-2.982 E.18664
M204 S10000
G1 X135.89 Y125.21 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.561844
G1 F1533
M204 S6000
G3 X135.89 Y130.79 I-8.018 J2.79 E.24044
; WIPE_START
G1 F6937.436
G1 X136.117 Y130.025 E-.30344
G1 X136.268 Y129.274 E-.2909
G1 X136.312 Y128.84 E-.16566
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.184 Y124.291 Z4.2 F42000
G1 X125.214 Y120.601 Z4.2
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
M73 P86 R1
G1 F1533
M204 S6000
G1 X124.822 Y119.76 E.03078
G3 X128.351 Y119.177 I3.225 J8.546 E.11942
G3 X131.178 Y119.76 I-.447 J9.311 E.09615
G1 X130.786 Y120.601 E.03079
G2 X125.27 Y120.58 I-2.786 J7.44 E.18686
M204 S10000
G1 X125.018 Y121.109 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1533
M204 S5000
G1 X124.296 Y119.559 E.05256
G3 X128.366 Y118.784 I3.703 J8.379 E.12842
G3 X131.704 Y119.559 I-.41 J9.347 E.1059
G1 X130.982 Y121.109 E.05256
G2 X125.074 Y121.085 I-2.982 J6.847 E.18664
M204 S10000
G1 X125.21 Y120.11 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.561319
G1 F1533
M204 S6000
G3 X130.79 Y120.11 I2.79 J8.014 E.2402
; WIPE_START
G1 F6944.467
G1 X130.025 Y119.883 E-.30339
G1 X129.295 Y119.735 E-.28289
G1 X128.84 Y119.689 E-.17372
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.267 Y125.799 Z4.2 F42000
G1 X120.581 Y130.724 Z4.2
G1 Z3.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1533
M204 S6000
G1 X120.601 Y130.786 E.00216
G1 X119.76 Y131.178 E.03078
G3 X119.76 Y124.822 I8.398 J-3.178 E.21552
G1 X120.601 Y125.214 E.03078
G2 X120.329 Y129.908 I7.44 J2.786 E.15833
G1 X120.564 Y130.667 E.02635
M204 S10000
G1 X121.046 Y130.828 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1533
M204 S5000
G1 X121.109 Y130.982 E.00509
G1 X119.559 Y131.704 E.05256
G3 X119.559 Y124.296 I8.501 J-3.704 E.23419
G1 X119.935 Y124.471 E.01276
G1 X121.109 Y125.018 E.03979
G2 X120.957 Y130.605 I6.847 J2.982 E.176
G1 X121.024 Y130.773 E.00555
M204 S10000
G1 X120.11 Y130.79 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.561427
G1 F1533
M204 S6000
G3 X120.11 Y125.21 I8.006 J-2.79 E.24025
; CHANGE_LAYER
; Z_HEIGHT: 4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6943.023
G1 X119.883 Y125.975 E-.30339
G1 X119.735 Y126.705 E-.28289
G1 X119.689 Y127.16 E-.17373
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 20/26
; update layer progress
M73 L20
M991 S0 P19 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z4.2 I-1.01 J.678 P1  F42000
G1 X125.216 Y135.394 Z4.2
G1 Z4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1534
M204 S6000
G1 X125.342 Y135.446 E.00452
G2 X130.787 Y135.401 I2.66 J-7.563 E.18427
G1 X131.179 Y136.243 E.0308
G3 X124.82 Y136.244 I-3.182 J-8.434 E.21559
G1 X125.191 Y135.449 E.02912
M204 S10000
G1 X125.019 Y134.89 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1534
M204 S5000
G1 X125.474 Y135.076 E.01511
G2 X130.981 Y134.89 I2.52 J-7.024 E.17343
G1 X131.704 Y136.441 E.05256
G3 X124.296 Y136.44 I-3.703 J-8.466 E.23422
G1 X124.994 Y134.944 E.05071
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.474 Y135.076 E-.18932
G1 X126.178 Y135.29 E-.2794
G1 X126.874 Y135.429 E-.26992
G1 X126.93 Y135.435 E-.02136
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
M73 P87 R1
G3 Z4.4 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z4.4
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z4.4 F4000
            G39.3 S1
            G0 Z4.4 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.211 Y135.887 F42000
G1 Z4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.561943
G1 F1534
M204 S6000
G2 X130.789 Y135.887 I2.789 J-7.864 E.24055
; WIPE_START
G1 F6936.115
G1 X130.289 Y136.046 E-.19925
G1 X129.646 Y136.201 E-.25125
G1 X129.017 Y136.303 E-.24226
G1 X128.841 Y136.318 E-.06724
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X132.723 Y129.747 Z4.4 F42000
G1 X135.401 Y125.213 Z4.4
G1 Z4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1534
M204 S6000
G1 X136.243 Y124.821 E.0308
G1 X136.486 Y125.557 E.02574
G3 X136.244 Y131.18 I-8.621 J2.446 E.1899
G1 X135.394 Y130.784 E.03111
G1 X135.446 Y130.658 E.00452
G2 X135.422 Y125.269 I-7.562 J-2.66 E.18228
M204 S10000
G1 X134.89 Y125.019 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1534
M204 S5000
G1 X136.441 Y124.296 E.05257
G1 X136.635 Y124.759 E.01543
G3 X136.44 Y131.704 I-8.626 J3.233 E.21891
G1 X134.89 Y130.981 E.05255
G2 X134.914 Y125.074 I-6.94 J-2.982 E.18649
M204 S10000
G1 X135.887 Y125.211 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.561789
G1 F1534
M204 S6000
G3 X135.887 Y130.789 I-7.861 J2.789 E.24048
; WIPE_START
G1 F6938.166
G1 X136.112 Y130.042 E-.29655
G1 X136.274 Y129.239 E-.31115
G1 X136.313 Y128.84 E-.1523
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.185 Y124.29 Z4.4 F42000
G1 X125.213 Y120.599 Z4.4
G1 Z4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1534
M204 S6000
G1 X124.82 Y119.756 E.03087
G3 X128.349 Y119.176 I3.252 J8.77 E.11938
G3 X131.18 Y119.756 I-.388 J9.1 E.09625
G1 X130.784 Y120.606 E.03111
G1 X130.658 Y120.554 E.00452
G2 X125.27 Y120.579 I-2.659 J7.624 E.18223
M204 S10000
G1 X125.019 Y121.11 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1534
M204 S5000
G1 X124.296 Y119.56 E.05254
G3 X128.365 Y118.784 I3.702 J8.355 E.12841
G3 X131.704 Y119.56 I-.449 J9.499 E.10589
G1 X130.981 Y121.11 E.05255
G2 X125.074 Y121.086 I-2.982 J6.918 E.18652
M204 S10000
G1 X125.211 Y120.112 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.561605
G1 F1534
M204 S6000
G3 X130.789 Y120.113 I2.789 J7.865 E.2404
; WIPE_START
G1 F6940.628
G1 X130.042 Y119.888 E-.29655
G1 X129.26 Y119.73 E-.30295
G1 X128.84 Y119.688 E-.16049
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.25 Y125.786 Z4.4 F42000
G1 X120.566 Y130.68 Z4.4
G1 Z4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1534
M204 S6000
G1 X120.599 Y130.787 E.0037
G1 X119.756 Y131.18 E.03087
G3 X119.758 Y124.821 I8.436 J-3.177 E.21559
G1 X120.606 Y125.216 E.03104
G1 X120.554 Y125.342 E.00452
G2 X120.326 Y129.884 I7.624 J2.659 E.15292
G1 X120.549 Y130.623 E.02559
M204 S10000
G1 X121.045 Y130.825 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P88 R1
G1 F1534
M204 S5000
G1 X121.11 Y130.981 E.00519
G1 X119.56 Y131.704 E.05254
G3 X119.559 Y124.296 I8.466 J-3.705 E.23422
G1 X121.11 Y125.019 E.05258
G2 X120.944 Y130.562 I6.918 J2.982 E.17451
G1 X121.024 Y130.769 E.00682
M204 S10000
G1 X120.112 Y130.789 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.561793
G1 F1534
M204 S6000
G3 X120.113 Y125.211 I7.989 J-2.788 E.24034
; CHANGE_LAYER
; Z_HEIGHT: 4.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6938.113
G1 X119.887 Y125.958 E-.29653
G1 X119.794 Y126.382 E-.16507
G1 X119.697 Y126.983 E-.23113
G1 X119.682 Y127.159 E-.06727
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 21/26
; update layer progress
M73 L21
M991 S0 P20 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z4.4 I-1.007 J.683 P1  F42000
G1 X125.238 Y135.348 Z4.4
G1 Z4.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1530
M204 S6000
G1 X125.355 Y135.396 E.00421
G2 X130.762 Y135.348 I2.638 J-7.372 E.18313
G1 X131.155 Y136.191 E.03085
G3 X124.845 Y136.191 I-3.155 J-8.378 E.21391
G1 X125.213 Y135.402 E.02886
M204 S10000
G1 X125.036 Y134.853 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1530
M204 S5000
G1 X125.487 Y135.026 E.01484
G2 X130.513 Y135.026 I2.513 J-7.183 E.15739
G1 X130.959 Y134.843 E.01482
G1 X130.964 Y134.853 E.00035
G1 X131.68 Y136.388 E.05203
G3 X128.409 Y137.155 I-3.737 J-8.58 E.10378
G1 X128.363 Y137.158 E.00141
G3 X124.32 Y136.388 I-.363 J-9.088 E.12757
G1 X125.011 Y134.907 E.05021
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.487 Y135.026 E-.18652
G1 X126.187 Y135.239 E-.27815
G1 X126.905 Y135.382 E-.27815
G1 X126.95 Y135.386 E-.01719
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z4.6 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z4.6
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z4.6 F4000
            G39.3 S1
            G0 Z4.6 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.234 Y135.837 F42000
G1 Z4.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.556111
G1 F1530
M204 S6000
G2 X130.766 Y135.837 I2.766 J-7.929 E.23571
; WIPE_START
G1 F7014.941
G1 X130.031 Y136.059 E-.29172
G1 X129.207 Y136.223 E-.31918
G1 X128.816 Y136.261 E-.1491
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X132.707 Y129.695 Z4.6 F42000
G1 X135.348 Y125.238 Z4.6
G1 Z4.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1530
M204 S6000
G1 X136.191 Y124.845 E.03085
G1 X136.437 Y125.595 E.0262
G3 X136.191 Y131.155 I-8.613 J2.404 E.18773
G1 X135.348 Y130.762 E.03085
G1 X135.396 Y130.645 E.00421
G2 X135.369 Y125.294 I-7.373 J-2.638 E.18114
M204 S10000
G1 X134.853 Y125.036 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1530
M204 S5000
G1 X136.388 Y124.32 E.05203
G1 X136.57 Y124.755 E.01447
G1 X136.588 Y124.797 E.00141
G3 X137.155 Y127.591 I-8.544 J3.189 E.08796
G1 X137.158 Y127.637 E.00141
G3 X136.388 Y131.68 I-9.088 J.363 E.12757
G1 X134.853 Y130.964 E.05205
G1 X134.843 Y130.959 E.00033
G2 X135.026 Y125.487 I-6.815 J-2.968 E.1723
G1 X134.861 Y125.086 E.01333
M204 S10000
G1 X135.837 Y125.234 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.556122
G1 F1530
M204 S6000
G3 X135.837 Y130.766 I-7.929 J2.766 E.23572
; WIPE_START
G1 F7014.784
G1 X135.991 Y130.278 E-.19441
G1 X136.146 Y129.637 E-.2505
G1 X136.251 Y128.986 E-.25045
G1 X136.265 Y128.817 E-.06464
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.131 Y124.275 Z4.6 F42000
G1 X125.238 Y120.652 Z4.6
G1 Z4.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1530
M204 S6000
G1 X124.845 Y119.809 E.03085
G3 X129.012 Y119.287 I3.167 J8.378 E.14061
G1 X129.042 Y119.289 E.001
G3 X131.155 Y119.809 I-1.344 J10.009 E.07234
G1 X130.762 Y120.652 E.03085
G1 X130.645 Y120.604 E.00421
G2 X125.294 Y120.631 I-2.638 J7.372 E.18114
M204 S10000
G1 X125.036 Y121.147 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1530
M204 S5000
G1 X124.32 Y119.612 E.05203
G3 X129.043 Y118.896 I3.702 J8.483 E.14844
M73 P89 R1
G1 X129.088 Y118.899 E.0014
G3 X131.68 Y119.612 I-1.059 J8.919 E.0829
G1 X130.964 Y121.147 E.05205
G1 X130.959 Y121.157 E.00033
G2 X125.487 Y120.974 I-2.968 J6.815 E.1723
G1 X125.086 Y121.139 E.01333
M204 S10000
G1 X125.234 Y120.163 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.556014
G1 F1530
M204 S6000
G3 X130.766 Y120.163 I2.766 J7.928 E.23567
; WIPE_START
G1 F7016.27
G1 X130.278 Y120.009 E-.1944
G1 X129.637 Y119.854 E-.25036
G1 X128.965 Y119.747 E-.25877
G1 X128.817 Y119.735 E-.05647
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.275 Y125.869 Z4.6 F42000
G1 X120.652 Y130.762 Z4.6
G1 Z4.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1530
M204 S6000
G1 X119.809 Y131.155 E.03085
G3 X119.809 Y124.845 I8.36 J-3.155 E.21393
G1 X120.516 Y125.174 E.02585
G1 X120.652 Y125.238 E.00499
G1 X120.604 Y125.355 E.00421
G2 X120.631 Y130.706 I7.373 J2.638 E.18114
M204 S10000
G1 X121.093 Y130.802 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1530
M204 S5000
G1 X121.157 Y130.959 E.00521
G1 X121.147 Y130.964 E.00035
G1 X119.612 Y131.68 E.05203
G3 X119.612 Y124.32 I8.403 J-3.68 E.23268
G1 X120.681 Y124.819 E.03625
G1 X121.147 Y125.036 E.0158
G1 X121.157 Y125.041 E.00033
G2 X120.974 Y130.513 I6.815 J2.968 E.1723
G1 X121.07 Y130.747 E.00777
M204 S10000
G1 X120.163 Y130.766 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.556116
G1 F1530
M204 S6000
G3 X120.163 Y125.234 I7.929 J-2.766 E.23572
; CHANGE_LAYER
; Z_HEIGHT: 4.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F7014.863
G1 X120.009 Y125.722 E-.19437
G1 X119.854 Y126.363 E-.25051
G1 X119.749 Y127.014 E-.25049
G1 X119.735 Y127.183 E-.06462
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 22/26
; update layer progress
M73 L22
M991 S0 P21 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z4.6 I-.998 J.697 P1  F42000
G1 X125.318 Y135.176 Z4.6
G1 Z4.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1520
M204 S6000
G1 X126.141 Y135.425 E.02851
G2 X130.682 Y135.176 I1.859 J-7.612 E.15308
G1 X131.106 Y136.085 E.03328
G3 X124.894 Y136.085 I-3.106 J-8.247 E.21058
G1 X125.293 Y135.23 E.03129
M204 S10000
G1 X125.058 Y134.806 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1520
M204 S5000
G1 X125.125 Y134.662 E.00488
G1 X125.554 Y134.838 E.01425
G2 X130.875 Y134.662 I2.437 J-6.81 E.16751
G1 X130.942 Y134.806 E.00488
G1 X131.111 Y135.168 E.01229
G1 X131.28 Y135.531 E.01229
G1 X131.631 Y136.283 E.02551
G3 X124.369 Y136.283 I-3.631 J-8.298 E.22959
G1 X125.033 Y134.86 E.04825
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.125 Y134.662 E-.0832
G1 X125.554 Y134.838 E-.17627
G1 X126.236 Y135.045 E-.27064
G1 X126.829 Y135.163 E-.2299
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z4.8 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z4.8
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z4.8 F4000
            G39.3 S1
            G0 Z4.8 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.301 Y135.693 F42000
G1 Z4.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.640622
G1 F1520
M204 S6000
G2 X130.699 Y135.693 I2.699 J-7.775 E.26782
; WIPE_START
G1 F6023.072
G1 X129.966 Y135.912 E-.29043
G1 X129.182 Y136.067 E-.3039
G1 X128.748 Y136.11 E-.16567
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X132.654 Y129.553 Z4.8 F42000
G1 X135.176 Y125.318 Z4.8
M73 P90 R1
G1 Z4.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1520
M204 S6000
G1 X136.085 Y124.894 E.03328
G1 X136.326 Y125.627 E.02558
G3 X136.085 Y131.106 I-8.496 J2.372 E.185
G1 X135.176 Y130.682 E.03328
G2 X135.196 Y125.375 I-7.425 J-2.682 E.17956
M204 S10000
G1 X134.806 Y125.058 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1520
M204 S5000
G1 X136.283 Y124.369 E.05009
G1 X136.42 Y124.696 E.01088
G3 X136.283 Y131.631 I-8.414 J3.303 E.21875
G1 X135.531 Y131.28 E.02551
G1 X135.168 Y131.111 E.01229
G1 X134.806 Y130.942 E.01229
G1 X134.662 Y130.875 E.00488
G2 X134.662 Y125.125 I-6.686 J-2.875 E.18161
G1 X134.751 Y125.083 E.00304
M204 S10000
G1 X135.693 Y125.301 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.640625
G1 F1520
M204 S6000
G3 X135.693 Y130.699 I-7.775 J2.699 E.26782
; WIPE_START
G1 F6023.042
G1 X135.905 Y129.994 E-.27941
G1 X136.067 Y129.182 E-.31497
G1 X136.11 Y128.748 E-.16562
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X129.958 Y124.231 Z4.8 F42000
G1 X125.318 Y120.824 Z4.8
G1 Z4.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1520
M204 S6000
G1 X124.894 Y119.915 E.03328
G3 X128.89 Y119.393 I3.106 J8.221 E.13489
G3 X131.106 Y119.915 I-.891 J8.745 E.07572
G1 X130.682 Y120.824 E.03328
G2 X125.375 Y120.804 I-2.682 J7.425 E.17955
M204 S10000
G1 X125.058 Y121.194 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1520
M204 S5000
G1 X124.369 Y119.717 E.05009
G3 X128.921 Y119.002 I3.641 J8.336 E.14315
G3 X131.631 Y119.717 I-.966 J9.151 E.08644
G1 X131.28 Y120.469 E.02551
G1 X131.111 Y120.832 E.01229
G1 X130.942 Y121.194 E.01229
G1 X130.875 Y121.338 E.00488
G2 X125.125 Y121.338 I-2.875 J6.686 E.18161
G1 X125.083 Y121.249 E.00304
M204 S10000
G1 X125.301 Y120.307 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.640621
G1 F1520
M204 S6000
G3 X130.699 Y120.307 I2.698 J7.659 E.26796
; WIPE_START
G1 F6023.078
G1 X130.235 Y120.16 E-.1848
G1 X129.606 Y120.008 E-.24585
G1 X128.968 Y119.905 E-.24566
G1 X128.748 Y119.887 E-.08369
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.185 Y126.005 Z4.8 F42000
G1 X120.787 Y130.561 Z4.8
M73 P90 R0
G1 Z4.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1520
M204 S6000
G1 X120.824 Y130.682 E.00421
G1 X119.915 Y131.106 E.03328
G3 X119.915 Y124.894 I8.247 J-3.106 E.21058
G1 X120.406 Y125.123 E.01797
G1 X120.824 Y125.318 E.01531
G2 X120.576 Y129.859 I7.425 J2.682 E.15302
G1 X120.77 Y130.503 E.02232
M204 S10000
G1 X121.276 Y130.724 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1520
M204 S5000
G1 X121.338 Y130.875 E.005
G1 X121.194 Y130.942 E.00488
G1 X120.832 Y131.111 E.01229
G1 X120.469 Y131.28 E.01229
G1 X119.717 Y131.631 E.02551
G3 X119.717 Y124.369 I8.298 J-3.631 E.22959
G1 X120.571 Y124.768 E.02897
G1 X121.194 Y125.058 E.02112
G1 X121.338 Y125.125 E.00488
G2 X121.169 Y130.443 I6.686 J2.875 E.16737
G1 X121.255 Y130.668 E.0074
M204 S10000
G1 X120.307 Y130.699 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.640363
G1 F1520
M204 S6000
M73 P91 R0
G3 X120.088 Y126.034 I7.655 J-2.697 E.23062
; LINE_WIDTH: 0.630451
G3 X120.216 Y125.59 I7.916 J2.04 E.02212
G1 X120.036 Y125.175 E.02161
; CHANGE_LAYER
; Z_HEIGHT: 4.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6127.337
G1 X120.216 Y125.59 E-.37556
G1 X120.088 Y126.034 E-.38444
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 23/26
; update layer progress
M73 L23
M991 S0 P22 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z4.8 I-1.052 J.613 P1  F42000
G1 X125.36 Y135.085 Z4.8
G1 Z4.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1545
M204 S6000
G1 X126.165 Y135.329 E.02789
G2 X130.64 Y135.085 I1.835 J-7.5 E.15082
G1 X131.057 Y135.98 E.03277
G3 X124.943 Y135.98 I-3.057 J-8.102 E.20728
G1 X125.335 Y135.139 E.03078
M204 S10000
G1 X125.142 Y134.624 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1545
M204 S5000
G1 X125.167 Y134.571 E.00181
G1 X125.588 Y134.744 E.01398
G2 X130.833 Y134.571 I2.404 J-6.716 E.16512
G1 X130.858 Y134.624 E.00181
G1 X131.582 Y136.179 E.05269
G3 X124.418 Y136.179 I-3.582 J-8.109 E.22662
G1 X125.117 Y134.679 E.05085
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.167 Y134.571 E-.04521
G1 X125.588 Y134.744 E-.17294
G1 X126.26 Y134.948 E-.2669
G1 X126.949 Y135.085 E-.26706
G1 X126.97 Y135.087 E-.00789
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z5 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z5
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z5 F4000
            G39.3 S1
            G0 Z5 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.347 Y135.595 F42000
G1 Z4.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.625126
G1 F1545
M204 S6000
G2 X130.653 Y135.595 I2.653 J-7.67 E.25643
; WIPE_START
G1 F6183.379
G1 X129.941 Y135.808 E-.28246
G1 X129.166 Y135.96 E-.29997
G1 X128.701 Y136.006 E-.17757
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X132.626 Y129.461 Z5 F42000
G1 X135.085 Y125.36 Z5
G1 Z4.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1545
M204 S6000
G1 X135.98 Y124.943 E.03277
G1 X136.215 Y125.658 E.02498
G3 X135.98 Y131.057 I-8.337 J2.342 E.1823
G1 X135.085 Y130.64 E.03277
G2 X135.105 Y125.417 I-7.324 J-2.64 E.17668
M204 S10000
G1 X134.624 Y125.142 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1545
M204 S5000
G1 X136.179 Y124.418 E.05269
G1 X136.27 Y124.637 E.00729
G3 X136.179 Y131.582 I-8.281 J3.364 E.2192
G1 X134.987 Y131.027 E.0404
G1 X134.624 Y130.858 E.01229
G1 X134.571 Y130.833 E.00181
G2 X134.571 Y125.168 I-6.594 J-2.833 E.17894
; WIPE_START
G1 F8400
M204 S6000
G1 X136.179 Y124.418 E-.67405
G1 X136.266 Y124.626 E-.08595
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X135.595 Y125.347 Z5 F42000
G1 Z4.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.625134
G1 F1545
M204 S6000
G3 X135.595 Y130.653 I-7.67 J2.653 E.25644
; WIPE_START
G1 F6183.293
G1 X135.808 Y129.941 E-.28254
G1 X135.96 Y129.166 E-.29994
G1 X136.006 Y128.701 E-.17753
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X129.846 Y124.196 Z5 F42000
G1 X125.36 Y120.915 Z5
G1 Z4.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1545
M204 S6000
G1 X124.943 Y120.02 E.03277
G3 X128.769 Y119.499 I3.049 J8.077 E.12919
G3 X131.057 Y120.02 I-.744 J8.545 E.07808
G1 X130.64 Y120.915 E.03277
G2 X125.417 Y120.895 I-2.64 J7.324 E.17668
M204 S10000
G1 X125.142 Y121.376 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1545
M204 S5000
G1 X124.418 Y119.821 E.05269
G3 X128.8 Y119.108 I3.585 J8.205 E.13787
G3 X131.582 Y119.821 I-.814 J8.954 E.08862
G1 X131.027 Y121.013 E.0404
G1 X130.858 Y121.376 E.01229
G1 X130.833 Y121.429 E.00181
G2 X125.168 Y121.429 I-2.833 J6.594 E.17894
; WIPE_START
G1 F8400
M204 S6000
G1 X124.418 Y119.821 E-.67405
G1 X124.627 Y119.734 E-.08595
; WIPE_END
M73 P92 R0
G1 E-.04 F1800
M204 S10000
G1 X125.347 Y120.405 Z5 F42000
G1 Z4.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.625126
G1 F1545
M204 S6000
G3 X130.653 Y120.405 I2.653 J7.555 E.25658
; WIPE_START
G1 F6183.38
G1 X130.205 Y120.264 E-.17839
G1 X129.585 Y120.114 E-.2426
G1 X128.955 Y120.012 E-.24244
G1 X128.702 Y119.991 E-.09657
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.197 Y126.152 Z5 F42000
G1 X120.915 Y130.64 Z5
G1 Z4.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1545
M204 S6000
G1 X120.02 Y131.057 E.03277
G3 X120.02 Y124.943 I8.135 J-3.057 E.20724
G1 X120.296 Y125.072 E.01009
G1 X120.915 Y125.36 E.02269
G2 X120.895 Y130.583 I7.324 J2.64 E.17668
M204 S10000
G1 X121.429 Y130.833 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1545
M204 S5000
G1 X121.376 Y130.858 E.00181
G1 X119.821 Y131.582 E.05269
G3 X119.821 Y124.418 I8.193 J-3.582 E.2265
G1 X120.461 Y124.716 E.02169
G1 X121.013 Y124.973 E.01871
G1 X121.376 Y125.142 E.01229
G1 X121.429 Y125.167 E.00181
G2 X121.406 Y130.778 I6.594 J2.833 E.17712
; WIPE_START
G1 F8400
M204 S6000
G1 X121.376 Y130.858 E-.03252
G1 X119.821 Y131.582 E-.65162
G1 X119.744 Y131.398 E-.07586
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X120.405 Y130.653 Z5 F42000
G1 Z4.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.625127
G1 F1545
M204 S6000
G3 X120.405 Y125.347 I7.67 J-2.653 E.25643
; CHANGE_LAYER
; Z_HEIGHT: 4.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F6183.371
G1 X120.192 Y126.059 E-.28245
G1 X120.04 Y126.834 E-.29993
G1 X119.994 Y127.299 E-.17762
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 24/26
; update layer progress
M73 L24
M991 S0 P23 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z5 I-1.003 J.689 P1  F42000
G1 X125.353 Y135.1 Z5
G1 Z4.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1453
M204 S6000
G1 X126.161 Y135.345 E.02799
G2 X130.647 Y135.1 I1.839 J-7.519 E.15121
G1 X131.008 Y135.875 E.02834
G3 X124.992 Y135.875 I-3.008 J-7.981 E.20394
G1 X125.328 Y135.155 E.02636
M204 S10000
G1 X125.16 Y134.587 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1453
M204 S5000
G1 X125.26 Y134.627 E.00331
G2 X130.84 Y134.587 I2.742 J-6.645 E.1761
G1 X131.533 Y136.074 E.05043
G3 X124.467 Y136.074 I-3.533 J-8.004 E.22352
G1 X125.135 Y134.641 E.04858
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.26 Y134.627 E-.04774
G1 X125.582 Y134.76 E-.13253
G1 X126.256 Y134.964 E-.26755
G1 X126.947 Y135.102 E-.26769
G1 X127.063 Y135.113 E-.0445
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z5.2 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z5.2
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z5.2 F4000
            G39.3 S1
            G0 Z5.2 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.368 Y135.55 F42000
G1 Z4.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.492502
G1 F1453
M204 S6000
G2 X130.632 Y135.55 I2.632 J-7.622 E.19644
; WIPE_START
G1 F8007.441
G1 X129.953 Y135.754 E-.26946
G1 X129.575 Y135.838 E-.14702
G1 X128.949 Y135.939 E-.24095
G1 X128.68 Y135.961 E-.10256
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X122.378 Y131.656 Z5.2 F42000
G1 X120.9 Y130.647 Z5.2
G1 Z4.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1453
M204 S6000
G1 X120.125 Y131.008 E.02834
G3 X120.125 Y124.992 I8.022 J-3.008 E.20389
G1 X120.9 Y125.353 E.02835
G2 X120.88 Y130.59 I7.341 J2.647 E.17716
M204 S10000
G1 X121.413 Y130.84 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1453
M204 S5000
G1 X119.926 Y131.533 E.05043
G3 X119.926 Y124.467 I8.087 J-3.533 E.2234
G1 X120.351 Y124.665 E.01441
G1 X121.413 Y125.16 E.03602
G2 X121.39 Y130.785 I6.61 J2.84 E.17757
M204 S10000
G1 X120.45 Y130.632 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.492504
G1 F1453
M204 S6000
G3 X120.45 Y125.368 I7.622 J-2.632 E.19643
; WIPE_START
G1 F8007.414
G1 X120.246 Y126.047 E-.26937
G1 X120.162 Y126.425 E-.14709
G1 X120.061 Y127.051 E-.24091
M73 P93 R0
G1 X120.039 Y127.32 E-.10263
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.906 Y121.44 Z5.2 F42000
G1 X125.353 Y120.9 Z5.2
G1 Z4.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1453
M204 S6000
G1 X124.992 Y120.125 E.02834
G3 X128.648 Y119.605 I2.996 J7.945 E.12349
G3 X131.008 Y120.125 I-.616 J8.404 E.08043
G1 X130.647 Y120.9 E.02834
G2 X125.41 Y120.88 I-2.647 J7.341 E.17717
M204 S10000
G1 X125.16 Y121.413 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1453
M204 S5000
G1 X124.467 Y119.926 E.05043
G3 X128.679 Y119.214 I3.534 J8.092 E.13259
G3 X131.533 Y119.926 I-.686 J8.825 E.0908
G1 X130.84 Y121.413 E.05043
G2 X125.215 Y121.39 I-2.84 J6.61 E.17757
M204 S10000
G1 X125.368 Y120.45 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.492507
G1 F1453
M204 S6000
G3 X130.632 Y120.45 I2.632 J7.645 E.19642
; WIPE_START
G1 F8007.354
G1 X129.932 Y120.241 E-.27764
G1 X129.162 Y120.089 E-.29815
G1 X128.68 Y120.041 E-.18421
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X134.56 Y124.906 Z5.2 F42000
G1 X135.1 Y125.353 Z5.2
G1 Z4.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1453
M204 S6000
G1 X135.875 Y124.992 E.02834
G1 X136.104 Y125.69 E.02436
G3 X135.875 Y131.008 I-8.264 J2.308 E.17953
G1 X135.1 Y130.647 E.02834
G2 X135.12 Y125.41 I-7.341 J-2.647 E.17717
M204 S10000
G1 X134.587 Y125.16 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1453
M204 S5000
G1 X136.074 Y124.467 E.05043
G1 X136.121 Y124.578 E.0037
G3 X136.074 Y131.533 I-8.043 J3.424 E.21981
G1 X134.587 Y130.84 E.05043
G2 X134.61 Y125.215 I-6.61 J-2.84 E.17757
M204 S10000
G1 X135.55 Y125.368 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.492507
G1 F1453
M204 S6000
G3 X135.55 Y130.632 I-7.622 J2.632 E.19644
; CHANGE_LAYER
; Z_HEIGHT: 5
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F8007.357
G1 X135.754 Y129.953 E-.26942
G1 X135.838 Y129.575 E-.14706
G1 X135.939 Y128.949 E-.24091
G1 X135.961 Y128.68 E-.10261
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 25/26
; update layer progress
M73 L25
M991 S0 P24 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z5.2 I-.635 J-1.038 P1  F42000
G1 X125.308 Y135.197 Z5.2
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1415
M204 S6000
G1 X125.411 Y135.238 E.00368
G2 X130.691 Y135.195 I2.581 J-7.212 E.17881
G1 X130.959 Y135.769 E.02102
G3 X125.041 Y135.769 I-2.959 J-7.909 E.20054
G1 X125.283 Y135.251 E.01897
M204 S10000
G1 X125.112 Y134.691 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1415
M204 S5000
G2 X130.888 Y134.691 I2.888 J-6.716 E.18249
G1 X130.988 Y134.904 E.0072
G1 X131.484 Y135.969 E.03613
G3 X124.516 Y135.969 I-3.484 J-7.982 E.2203
G1 X125.086 Y134.746 E.04149
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.543 Y134.869 E-.17993
G1 X126.228 Y135.076 E-.27184
G1 X126.93 Y135.216 E-.27199
G1 X127.025 Y135.225 E-.03624
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z5.4 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z5.4
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z5.4 F4000
            G39.3 S1
            G0 Z5.4 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X125.368 Y135.55 F42000
M73 P94 R0
G1 Z5
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.261555
G1 F1415
M204 S6000
G2 X130.632 Y135.55 I2.632 J-7.622 E.09552
; WIPE_START
G1 F15000
G1 X129.947 Y135.756 E-.27155
G1 X129.575 Y135.838 E-.14487
G1 X128.949 Y135.939 E-.24095
G1 X128.68 Y135.961 E-.10263
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X132.663 Y129.45 Z5.4 F42000
G1 X135.197 Y125.308 Z5.4
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1415
M204 S6000
G1 X135.769 Y125.041 E.02096
G1 X135.993 Y125.722 E.02375
G3 X135.769 Y130.959 I-8.085 J2.278 E.17683
G1 X135.197 Y130.692 E.02096
G1 X135.238 Y130.589 E.00368
G2 X135.218 Y125.365 I-7.221 J-2.584 E.17684
M204 S10000
G1 X134.691 Y125.112 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1415
M204 S5000
G1 X135.971 Y124.519 E.04333
G3 X135.969 Y131.484 I-7.983 J3.481 E.22019
G1 X134.691 Y130.888 E.04333
G2 X134.715 Y125.167 I-6.716 J-2.888 E.18064
M204 S10000
G1 X135.55 Y125.368 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.261556
G1 F1415
M204 S6000
G3 X135.55 Y130.632 I-7.622 J2.632 E.09552
; WIPE_START
G1 F15000
G1 X135.758 Y129.937 E-.27547
G1 X135.911 Y129.168 E-.29808
G1 X135.959 Y128.68 E-.18645
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X129.825 Y124.139 Z5.4 F42000
G1 X125.305 Y120.794 Z5.4
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1415
M204 S6000
G1 X125.041 Y120.231 E.02063
G3 X128.527 Y119.711 I2.949 J7.831 E.1178
G3 X130.959 Y120.231 I-.505 J8.315 E.08279
G1 X130.696 Y120.794 E.02063
G2 X125.361 Y120.774 I-2.696 J7.458 E.18047
M204 S10000
G1 X125.112 Y121.309 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1415
M204 S5000
G1 X124.516 Y120.031 E.04333
G3 X128.558 Y119.32 I3.491 J8.005 E.12731
G3 X131.484 Y120.031 I-.574 J8.747 E.09299
G1 X130.888 Y121.309 E.04333
G2 X125.167 Y121.285 I-2.888 J6.716 E.18064
M204 S10000
G1 X125.369 Y120.45 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.261555
G1 F1415
M204 S6000
G3 X130.632 Y120.45 I2.631 J7.646 E.09551
; WIPE_START
G1 F15000
G1 X129.947 Y120.245 E-.27151
G1 X129.575 Y120.162 E-.14491
G1 X128.949 Y120.061 E-.24091
G1 X128.68 Y120.039 E-.10267
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X124.142 Y126.176 Z5.4 F42000
G1 X120.803 Y130.692 Z5.4
G1 Z5
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1415
M204 S6000
G1 X120.231 Y130.959 E.02096
G3 X120.231 Y125.041 I7.902 J-2.959 E.20055
G1 X120.804 Y125.309 E.02099
G1 X120.761 Y125.412 E.0037
G2 X120.782 Y130.635 I7.22 J2.583 E.17682
M204 S10000
G1 X121.309 Y130.888 F42000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P95 R0
G1 F1415
M204 S5000
G1 X120.031 Y131.484 E.04333
G3 X120.031 Y124.516 I7.97 J-3.484 E.22032
G1 X120.241 Y124.613 E.00712
G1 X121.309 Y125.112 E.03621
G2 X121.285 Y130.833 I6.716 J2.888 E.18064
M204 S10000
G1 X120.45 Y130.632 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.261555
G1 F1415
M204 S6000
G3 X120.45 Y125.368 I7.622 J-2.632 E.09552
; CHANGE_LAYER
; Z_HEIGHT: 5.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X120.244 Y126.053 E-.27156
G1 X120.162 Y126.425 E-.14487
G1 X120.061 Y127.051 E-.24095
G1 X120.039 Y127.32 E-.10262
; WIPE_END
G1 E-.04 F1800
; layer num/total_layer_count: 26/26
; update layer progress
M73 L26
M991 S0 P25 ;notify layer change
; OBJECT_ID: 123
M204 S10000
G17
G3 Z5.4 I-1.01 J.679 P1  F42000
G1 X125.063 Y134.796 Z5.4
G1 Z5.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1555
M204 S5000
G2 X130.937 Y134.796 I2.937 J-6.822 E.18558
G1 X131.249 Y135.464 E.02265
G1 X131.436 Y135.865 E.01358
G3 X124.564 Y135.865 I-3.436 J-7.877 E.21721
G1 X125.037 Y134.85 E.03439
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.504 Y134.977 E-.18397
G1 X126.2 Y135.188 E-.27615
G1 X126.913 Y135.33 E-.27628
G1 X126.975 Y135.336 E-.02361
; WIPE_END
G1 E-.04 F1800
M204 S10000
G17
G3 Z5.6 I1.217 J0 P1  F42000
;===================== date: 20250206 =====================

; don't support timelapse gcode in spiral_mode and by object sequence for I3 structure printer
; SKIPPABLE_START
; SKIPTYPE: timelapse
M622.1 S1 ; for prev firware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
G92 E0
G1 Z5.6
G1 X0 Y128 F18000 ; move to safe pos
G1 X-48.2 F3000 ; move to safe pos
M400
M1004 S5 P1  ; external shutter
M400 P300
M971 S11 C11 O0
G92 E0
G1 X0 F18000
M623

; SKIPTYPE: head_wrap_detect
M622.1 S1
M1002 judge_flag g39_3rd_layer_detect_flag
M622 J1
    ; enable nozzle clog detect at 3rd layer
    


    M622.1 S1
    M1002 judge_flag g39_detection_flag
    M622 J1
      
        M622.1 S0
        M1002 judge_flag g39_mass_exceed_flag
        M622 J1
        
            G392 S0
            M400
            G90
            M83
            M204 S5000
            G0 Z5.6 F4000
            G39.3 S1
            G0 Z5.6 F4000
            G392 S0
          
        M623
    
    M623
M623
; SKIPPABLE_END


G1 X130.359 Y136.039 F42000
G1 Z5.2
G1 E.8 F1800
; FEATURE: Top surface
G1 F1555
M204 S2000
G1 X130.993 Y135.406 E.02753
G1 X130.781 Y135.084
G1 X129.648 Y136.217 E.0492
G1 X129.014 Y136.318
G1 X129.982 Y135.35 E.04209
G1 X129.299 Y135.499
G1 X128.433 Y136.366 E.03766
G1 X127.891 Y136.374
G1 X128.688 Y135.578 E.0346
G1 X128.123 Y135.609
G1 X127.381 Y136.351 E.03226
G1 X126.895 Y136.304
G1 X127.593 Y135.606 E.03034
G1 X127.108 Y135.558
G1 X126.435 Y136.23 E.02922
G1 X126.001 Y136.132
G1 X126.644 Y135.488 E.02797
G1 X126.199 Y135.4
G1 X125.58 Y136.019 E.02692
G1 X125.178 Y135.887
G1 X125.786 Y135.28 E.02641
; WIPE_START
G1 F9547.055
M204 S6000
G1 X125.178 Y135.887 E-.32664
G1 X125.58 Y136.019 E-.16055
G1 X126.088 Y135.512 E-.27281
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X131.138 Y135.673 Z5.6 F42000
G1 Z5.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.198313
G1 F1555
M204 S6000
G1 X130.966 Y135.789 E.00263
; LINE_WIDTH: 0.163729
G1 X130.794 Y135.904 E.00204
; WIPE_START
G1 F15000
G1 X130.966 Y135.789 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X125.363 Y135.123 Z5.6 F42000
G1 Z5.2
G1 E.8 F1800
; LINE_WIDTH: 0.397943
G1 F1555
M204 S6000
G1 X125.265 Y135.263 E.00493
; LINE_WIDTH: 0.355541
G1 X125.167 Y135.402 E.00434
; LINE_WIDTH: 0.31314
G1 X125.07 Y135.541 E.00375
; LINE_WIDTH: 0.266259
G2 X124.953 Y135.714 I.858 J.705 E.0038
; LINE_WIDTH: 0.219024
G1 X124.981 Y135.752 E.00068
; LINE_WIDTH: 0.170363
G1 X125.009 Y135.79 E.00049
; LINE_WIDTH: 0.130062
G1 X125.143 Y135.88 E.00115
; WIPE_START
G1 F15000
G1 X125.009 Y135.79 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.153 Y130.152 Z5.6 F42000
G1 X134.796 Y125.063 Z5.6
G1 Z5.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1555
M204 S5000
G1 X135.865 Y124.564 E.03624
G1 X136.047 Y124.999 E.01448
G3 X135.865 Y131.436 I-8.103 J2.992 E.20276
G1 X134.796 Y130.937 E.03624
G2 X134.819 Y125.118 I-6.822 J-2.937 E.18374
; WIPE_START
G1 F9547.055
M204 S6000
G1 X135.865 Y124.564 E-.44948
G1 X136.047 Y124.999 E-.17901
G1 X136.155 Y125.328 E-.13151
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X136.039 Y130.359 Z5.6 F42000
G1 Z5.2
M73 P96 R0
G1 E.8 F1800
; FEATURE: Top surface
G1 F1555
M204 S2000
G1 X135.406 Y130.993 E.02753
G1 X135.084 Y130.781
G1 X136.217 Y129.648 E.04921
G1 X136.318 Y129.014
G1 X135.35 Y129.982 E.04209
G1 X135.499 Y129.299
G1 X136.366 Y128.433 E.03766
G1 X136.374 Y127.891
G1 X135.578 Y128.688 E.0346
G1 X135.609 Y128.123
G1 X136.351 Y127.381 E.03226
G1 X136.299 Y126.9
G1 X135.606 Y127.593 E.03013
G1 X135.558 Y127.108
G1 X136.229 Y126.436 E.02919
G1 X136.132 Y126.001
G1 X135.488 Y126.644 E.02797
G1 X135.4 Y126.199
G1 X136.019 Y125.58 E.02692
G1 X135.887 Y125.178
G1 X135.28 Y125.786 E.02641
M204 S10000
G1 X135.88 Y125.143 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.13004
G1 F1555
M204 S6000
G1 X135.791 Y125.009 E.00114
; LINE_WIDTH: 0.17036
G1 X135.752 Y124.981 E.00049
; LINE_WIDTH: 0.219019
G1 X135.714 Y124.953 E.00068
; LINE_WIDTH: 0.246443
G1 X135.681 Y124.972 E.00064
; LINE_WIDTH: 0.270739
G1 X135.542 Y125.07 E.00316
; LINE_WIDTH: 0.313142
G1 X135.402 Y125.167 E.00375
; LINE_WIDTH: 0.355545
G1 X135.263 Y125.265 E.00434
; LINE_WIDTH: 0.397949
G1 X135.123 Y125.363 E.00493
; WIPE_START
G1 F10140.041
G1 X135.263 Y125.265 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X135.904 Y130.794 Z5.6 F42000
G1 Z5.2
G1 E.8 F1800
; LINE_WIDTH: 0.163742
G1 F1555
M204 S6000
G1 X135.789 Y130.966 E.00204
; LINE_WIDTH: 0.198314
G1 X135.673 Y131.138 E.00263
; WIPE_START
G1 F15000
G1 X135.789 Y130.966 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.144 Y125.829 Z5.6 F42000
G1 X125.063 Y121.204 Z5.6
G1 Z5.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1555
M204 S5000
G1 X124.564 Y120.135 E.03624
G3 X128.437 Y119.426 I3.457 J7.952 E.12204
G3 X131.436 Y120.135 I-.476 J8.706 E.09518
G1 X130.937 Y121.204 E.03624
G2 X125.118 Y121.181 I-2.937 J6.822 E.18374
; WIPE_START
G1 F9547.055
M204 S6000
G1 X124.564 Y120.135 E-.44948
G1 X124.999 Y119.953 E-.17901
G1 X125.328 Y119.845 E-.1315
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.214 Y120.72 Z5.6 F42000
G1 Z5.2
G1 E.8 F1800
; FEATURE: Top surface
G1 F1555
M204 S2000
G1 X130.821 Y120.113 E.02641
G1 X130.42 Y119.981
G1 X129.8 Y120.6 E.02692
G1 X129.356 Y120.512
G1 X129.999 Y119.868 E.02797
G1 X129.564 Y119.77
G1 X128.892 Y120.442 E.02922
G1 X128.407 Y120.394
G1 X129.105 Y119.696 E.03034
G1 X128.619 Y119.649
G1 X127.876 Y120.391 E.03226
G1 X127.312 Y120.422
G1 X128.104 Y119.63 E.03441
G1 X127.567 Y119.634
G1 X126.701 Y120.501 E.03766
G1 X126.018 Y120.65
G1 X126.986 Y119.682 E.04209
G1 X126.351 Y119.783
G1 X125.219 Y120.916 E.04921
G1 X125.007 Y120.594
G1 X125.641 Y119.961 E.02753
M204 S10000
G1 X125.206 Y120.096 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.163654
G1 F1555
M204 S6000
G1 X125.034 Y120.211 E.00204
; LINE_WIDTH: 0.19825
G1 X124.862 Y120.327 E.00262
; WIPE_START
G1 F15000
G1 X125.034 Y120.211 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X130.177 Y119.957 Z5.6 F42000
G1 Z5.2
G1 E.8 F1800
; LINE_WIDTH: 0.0928936
G1 F1555
M204 S6000
G1 X130.027 Y119.872 E.0007
M204 S10000
G1 X130.857 Y120.12 F42000
; LINE_WIDTH: 0.130081
G1 F1555
M204 S6000
G1 X130.991 Y120.209 E.00115
; LINE_WIDTH: 0.170403
G1 X131.019 Y120.248 E.00049
; LINE_WIDTH: 0.219111
G1 X131.047 Y120.286 E.00068
; LINE_WIDTH: 0.246551
G1 X131.028 Y120.319 E.00064
; LINE_WIDTH: 0.270845
G1 X130.93 Y120.459 E.00316
; LINE_WIDTH: 0.313242
G1 X130.833 Y120.598 E.00375
; LINE_WIDTH: 0.355639
G1 X130.735 Y120.737 E.00434
; LINE_WIDTH: 0.398035
G1 X130.637 Y120.877 E.00493
; WIPE_START
G1 F10137.56
G1 X130.735 Y120.737 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X125.524 Y126.314 Z5.6 F42000
G1 X121.204 Y130.937 Z5.6
G1 Z5.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1555
M204 S5000
G1 X120.135 Y131.436 E.03624
G3 X120.135 Y124.564 I7.833 J-3.436 E.21727
G1 X121.204 Y125.063 E.03624
G2 X121.181 Y130.882 I6.822 J2.937 E.18374
M204 S10000
G1 X120.72 Y130.214 F42000
; FEATURE: Top surface
G1 F1555
M204 S2000
G1 X120.113 Y130.821 E.02641
G1 X119.981 Y130.42
G1 X120.6 Y129.8 E.02692
G1 X120.512 Y129.356
G1 X119.868 Y129.999 E.02797
G1 X119.77 Y129.564
G1 X120.442 Y128.892 E.02922
G1 X120.394 Y128.407
G1 X119.696 Y129.105 E.03034
G1 X119.649 Y128.619
G1 X120.391 Y127.876 E.03226
G1 X120.422 Y127.312
G1 X119.626 Y128.108 E.0346
G1 X119.634 Y127.567
G1 X120.501 Y126.701 E.03766
G1 X120.65 Y126.018
G1 X119.682 Y126.986 E.04209
G1 X119.783 Y126.351
G1 X120.916 Y125.219 E.04921
G1 X120.594 Y125.007
G1 X119.961 Y125.641 E.02753
M204 S10000
G1 X120.327 Y124.862 F42000
; FEATURE: Gap infill
; LINE_WIDTH: 0.198239
G1 F1555
M204 S6000
G1 X120.211 Y125.034 E.00262
; LINE_WIDTH: 0.163657
G1 X120.096 Y125.206 E.00204
; WIPE_START
G1 F15000
G1 X120.211 Y125.034 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S10000
G1 X120.877 Y130.637 Z5.6 F42000
G1 Z5.2
M73 P97 R0
G1 E.8 F1800
; LINE_WIDTH: 0.398031
G1 F1555
M204 S6000
G1 X120.737 Y130.735 E.00493
; LINE_WIDTH: 0.355637
G1 X120.598 Y130.833 E.00434
; LINE_WIDTH: 0.313242
G1 X120.459 Y130.93 E.00375
; LINE_WIDTH: 0.266371
G3 X120.286 Y131.047 I-.706 J-.859 E.0038
; LINE_WIDTH: 0.219101
G1 X120.248 Y131.019 E.00068
; LINE_WIDTH: 0.170397
G1 X120.209 Y130.991 E.00049
; LINE_WIDTH: 0.130076
G1 X120.12 Y130.857 E.00115
; close powerlost recovery
M1003 S0
; WIPE_START
G1 F15000
G1 X120.209 Y130.991 E-.76
; WIPE_END
G1 E-.04 F1800
M106 S0
M106 P2 S0
M981 S0 P20000 ; close spaghetti detector
; FEATURE: Custom
; MACHINE_END_GCODE_START
; filament end gcode 
M106 P3 S0
;===== date: 20231229 =====================
G392 S0 ;turn off nozzle clog detect

M400 ; wait for buffer to clear
G92 E0 ; zero the extruder
G1 E-0.8 F1800 ; retract
G1 Z5.7 F900 ; lower z a little
G1 X0 Y128 F18000 ; move to safe pos
G1 X-13.0 F3000 ; move to safe pos

M1002 judge_flag timelapse_record_flag
M622 J1
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M400 P100
M971 S11 C11 O0
M991 S0 P-1 ;end timelapse at safe pos
M623


M140 S0 ; turn off bed
M106 S0 ; turn off fan
M106 P2 S0 ; turn off remote part cooling fan
M106 P3 S0 ; turn off chamber cooling fan

;G1 X27 F15000 ; wipe

; pull back filament to AMS
M620 S255
G1 X267 F15000
T255
G1 X-28.5 F18000
G1 X-48.2 F3000
G1 X-28.5 F18000
G1 X-48.2 F3000
M621 S255

M104 S0 ; turn off hotend

M400 ; wait all motion done
M17 S
M17 Z0.4 ; lower z motor current to reduce impact if there is something in the bottom

    G1 Z105.2 F600
    G1 Z103.2

M400 P100
M17 R ; restore z current

G90
G1 X-48 Y180 F3600

M220 S100  ; Reset feedrate magnitude
M201.2 K1.0 ; Reset acc magnitude
M73.2   R1.0 ;Reset left time magnitude
M1002 set_gcode_claim_speed_level : 0

;=====printer finish  sound=========
M17
M400 S1
M1006 S1
M1006 A0 B20 L100 C37 D20 M40 E42 F20 N60
M1006 A0 B10 L100 C44 D10 M60 E44 F10 N60
M1006 A0 B10 L100 C46 D10 M80 E46 F10 N80
M1006 A44 B20 L100 C39 D20 M60 E48 F20 N60
M1006 A0 B10 L100 C44 D10 M60 E44 F10 N60
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N60
M1006 A0 B10 L100 C39 D10 M60 E39 F10 N60
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N60
M1006 A0 B10 L100 C44 D10 M60 E44 F10 N60
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N60
M1006 A0 B10 L100 C39 D10 M60 E39 F10 N60
M1006 A0 B10 L100 C0 D10 M60 E0 F10 N60
M1006 A0 B10 L100 C48 D10 M60 E44 F10 N80
M1006 A0 B10 L100 C0 D10 M60 E0 F10  N80
M1006 A44 B20 L100 C49 D20 M80 E41 F20 N80
M1006 A0 B20 L100 C0 D20 M60 E0 F20 N80
M1006 A0 B20 L100 C37 D20 M30 E37 F20 N60
M1006 W
;=====printer finish  sound=========

;M17 X0.8 Y0.8 Z0.5 ; lower motor current to 45% power
M400
M18 X Y Z

M73 P100 R0
; EXECUTABLE_BLOCK_END

