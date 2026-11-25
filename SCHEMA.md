# Knowledge Graph Extraction Schema

Output one JSON file per extraction job:

```json
{
  "entities": [
    {
      "id": "launchxl_f280025c",
      "label": "LAUNCHXL-F280025C",
      "type": "EvaluationKit",
      "description": "One or two sentences, factual, from the source.",
      "aliases": ["F280025C LaunchPad"],
      "properties": {"cpu_freq": "100 MHz"},
      "sources": [{"doc": "spruj26a", "page": 27}]
    }
  ],
  "relations": [
    {
      "source": "launchxl_f280025c",
      "target": "f280025c",
      "type": "based_on",
      "evidence": "Short quote or close paraphrase from the source (<= 25 words).",
      "sources": [{"doc": "spruj26a", "page": 27}]
    }
  ]
}
```

## Entity types (use exactly these)

| type | what it covers | examples |
|---|---|---|
| `Device` | MCU device or device family / series | F280025C, F2800137, F280013x, F2838x, F2837x, C2000 |
| `EvaluationKit` | LaunchPad, controlCARD, docking station, EVM, BoosterPack, adapter, TI design | LAUNCHXL-F280025C, TMDSCNCD280039C, BOOSTXL-DRV8323RH, DRV8329AEVM |
| `Component` | Other ICs / hardware parts / boards that are not kits | DRV8323RH gate driver, Arm Cortex-M4, custom inverter board |
| `Peripheral` | On-chip peripheral / module | ADC, ePWM, CMPSS, eQEP, eCAP, CLB, CAN, EtherCAT, FSI, SCI |
| `Software` | SDK, library, project, tool, GUI, file, framework | MotorControl SDK, C2000Ware, Universal Motor Control Lab, Code Composer Studio, FAST, InstaSPIN-FOC, SFRA, DCL |
| `Algorithm` | Control / estimation algorithm or transform | FOC, eSMO, PLL, Clarke transform, Park transform, SVPWM, MTPA, field weakening, PI controller |
| `Motor` | Motor type or specific motor | PMSM, BLDC, ACIM, LVSERVOMTR |
| `Concept` | Physical / control concept or quantity | back-EMF, rotor flux angle, d-axis current, dead time, overcurrent protection |
| `Feature` | Software/system feature or operating mode | flying start, rs online recalibration, sensored/sensorless mode, motor parameter identification, DATALOG |
| `BuildLevel` | Incremental build level of the lab | BUILDLEVEL_LEVEL1 .. LEVEL4 |
| `Parameter` | Named code symbol, macro, variable, or tunable | USER_MOTOR_RS_Ohm, motorVars.speedRef_Hz, MOTOR1_FAST, ADC sampling period |
| `Application` | End application / market | industrial drives, appliances, robotics, HVAC compressor, grid |
| `Document` | Referenced document / user guide / datasheet | SPRUJ26A, Technical Reference Manual |

## ID convention (critical for merging across jobs)

- lowercase, `[a-z0-9_]` only; replace `-`, `.`, `/`, spaces with `_`; drop ™ ® etc.
- Device parts: bare part number, no TMS320 prefix: `f280025c`, `f280039c`, `f2800137`, `f280013x` (family), `f2838x`, `f2837x`, `c2000` (platform).
- Kits: full orderable name: `launchxl_f280025c`, `tmdscncd280039c`, `boostxl_drv8323rh`, `drv8329aevm`, `tmdsadap180to100`.
- Peripherals: generic name, not instance: `adc`, `epwm`, `cmpss`, `eqep`, `ecap`, `clb`, `can`, `mcan`, `ethercat`, `fsi`, `sci`, `spi`, `i2c`, `pga`, `dac`, `cla`, `tmu`, `ethernet`, `usb`.
- Algorithms: `foc`, `esmo`, `pll`, `fast_estimator` (FAST), `clarke_transform`, `park_transform`, `inverse_park_transform`, `svpwm`, `pi_controller`, `mtpa`, `field_weakening`, `hall_sensor` (Concept), `encoder` (Concept).
- Software: `motorcontrol_sdk`, `c2000ware`, `universal_motor_control_lab`, `code_composer_studio`, `instaspin_foc`, `universal_gui`, `sysconfig`, `dcl`, `sfra`, `datalog`.
- Motors: `pmsm`, `bldc`, `acim`. Build levels: `build_level_1` .. `build_level_4`.
- Documents: literature number: `spruj26a`, `spruio7a`, `sprt755`, `sszt350`, `sszt464`.
- Code symbols: lowercase the exact symbol: `user_motor_rs_ohm`, `motorvars_speedref_hz`; put the exact spelling in `label`.

## Relation types (use exactly these, direction source -> target)

`is_a`, `part_of`, `contains`, `based_on`, `runs_on`, `supports`, `uses`, `implements`, `requires`,
`compatible_with`, `connects_to`, `estimates`, `controls`, `configures`, `measures`, `protects`,
`produces`, `input_to`, `enables`, `precedes`, `extends`, `targets` (-> Application),
`documented_in` (-> Document), `alternative_to`, `related_to` (last resort).

## Rules

- Extract only what the source states. No outside knowledge in descriptions.
- `page` = the PDF page number, i.e. the number in the file name `pNNN.txt`.
- Prefer specific, useful facts: what runs on what, what estimates what, which kit pairs with which, which
  parameters configure which feature, the build-level progression, protection mechanisms, specs (put specs in `properties`).
- Every entity must be connected by at least one relation. Every relation's endpoints must appear in `entities`
  (repeat shared entities like `foc` or `c2000` in your file with at least id/label/type).
- Each doc gets a `Document` entity, and its key entities are linked with `documented_in`.
- Aim for density over breadth: ~40–120 entities and ~60–200 relations per 30 pages, depending on content.
