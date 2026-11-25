# Knowledge graph build report

- Extraction files: 5
- Documents: sprt755, spruio7a, spruj26a, sszt350, sszt464, sszt496
- Entities: 589
- Relations: 1519
- Isolated entities: 0

## Entity types

- Parameter: 173
- Software: 100
- Concept: 59
- Feature: 55
- Peripheral: 40
- Component: 33
- Algorithm: 29
- Device: 24
- Application: 21
- Document: 21
- EvaluationKit: 20
- Motor: 10
- BuildLevel: 4

## Relation types

- part_of: 223
- configures: 190
- uses: 181
- contains: 173
- supports: 144
- documented_in: 125
- related_to: 52
- input_to: 51
- compatible_with: 47
- controls: 43
- implements: 40
- precedes: 39
- enables: 32
- targets: 27
- connects_to: 22
- requires: 21
- estimates: 20
- runs_on: 17
- based_on: 14
- is_a: 14
- produces: 13
- measures: 10
- extends: 8
- alternative_to: 8
- protects: 5

## Top hubs

- Universal Motor Control Lab (universal_motor_control_lab): 124
- SPRUJ26A (spruj26a): 91
- user_mtr1.h (user_mtr1_h): 90
- FAST Software Encoder (fast_estimator): 50
- F280013x (f280013x): 48
- eSMO (esmo): 42
- C2000Ware MotorControl SDK (motorcontrol_sdk): 41
- Field-oriented control (FOC) (foc): 35
- C2000 (c2000): 34
- TMDSHVMTRINSPIN (tmdshvmtrinspin): 34
- F2838x (f2838x): 33
- F28002x (f28002x): 32
- InstaSPIN-FOC (instaspin_foc): 30
- ADC (adc): 29
- BOOSTXL-DRV8323RS (boostxl_drv8323rs): 28
- Motor identification (motor_parameter_identification): 26
- DRV8329AEVM (drv8329aevm): 26
- ePWM (epwm): 25
- LAUNCHXL-F280025C (launchxl_f280025c): 24
- Build Level 2 (build_level_2): 24
- DRV8353RS-EVM (drv8353rs_evm): 23
- TMS320F2800137 LaunchPad (launchxl_f2800137): 22
- Encoder (encoder): 22
- hal.h (hal_h): 22
- CLB (clb): 21

## Merge issues

- type conflict for datalog: {'Software': 5, 'Feature': 2} -> Software
- type conflict for pwmdac: {'Software': 3, 'Feature': 2} -> Software
- type conflict for sensorless_foc: {'Algorithm': 5, 'Feature': 2} -> Algorithm
- type conflict for hal_writepwmdata: {'Parameter': 3, 'Software': 2} -> Parameter
- type conflict for hal_readadcdata: {'Parameter': 3, 'Software': 2} -> Parameter
- type conflict for est_run: {'Parameter': 3, 'Software': 2} -> Parameter
- type conflict for single_shunt_current_sensing: {'Concept': 7, 'Feature': 2} -> Concept
- type conflict for overcurrent_protection: {'Concept': 7, 'Feature': 2} -> Concept
