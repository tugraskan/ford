# Dynamic Modular Database Generation Report

## Overview

This database was generated using **dynamic template analysis** of FORD JSON outputs.
Instead of static templates, parameters were extracted directly from source code I/O operations.

**Total Parameters**: 801
**Files Analyzed**: 60
**I/O Procedures**: 262

## Dynamic Template Discovery

### Files with Dynamic Templates

- **reservoir.res**: 3 parameters, 3 lines
- **satbuffer.str**: 3 parameters, 3 lines
- **initial.aqu_cs**: 3 parameters, 3 lines
- **res_conds.dat**: 13 parameters, 7 lines
- **cs_channel.ini**: 4 parameters, 3 lines
- **channel.cha**: 6 parameters, 4 lines
- **gwflow.input**: 73 parameters, 44 lines
- **gwflow.pumpex**: 7 parameters, 4 lines
- **gwflow.tiles**: 10 parameters, 10 lines
- **gwflow.solutes**: 13 parameters, 12 lines
- **gwflow.hru_pump_observe**: 2 parameters, 2 lines
- **gwflow.rescells**: 7 parameters, 6 lines
- **gwflow.floodplain**: 6 parameters, 3 lines
- **gwflow.canals**: 20 parameters, 10 lines
- **gwflow.solutes.minerals**: 6 parameters, 6 lines
- **gwflow.lsucell**: 9 parameters, 6 lines
- **out.key**: 2 parameters, 1 lines
- **gwflow.hrucell**: 6 parameters, 3 lines
- **gwflow.huc12cell**: 5 parameters, 3 lines
- **gwflow.cellhru**: 7 parameters, 4 lines
- **gwflow.streamobs**: 5 parameters, 5 lines
- **hru-data.hru**: 4 parameters, 3 lines
- **cs_recall.rec**: 6 parameters, 3 lines
- **gwflow.chancells**: 2 parameters, 2 lines
- **file.cio**: 61 parameters, 31 lines
- **cs_atmo.cli**: 7 parameters, 7 lines
- **nutrients.rte**: 3 parameters, 3 lines
- **sed_nut.cha**: 3 parameters, 3 lines
- **salt_atmo.cli**: 13 parameters, 7 lines
- **carb_coefs.cbn', iostat=eof**: 51 parameters, 20 lines
- **co2_yr.dat**: 4 parameters, 4 lines
- **pest_metabolite.pes**: 11 parameters, 5 lines
- **salt_channel.ini**: 4 parameters, 3 lines
- **soil_lyr_depths.sol**: 4 parameters, 4 lines
- **salt_recall.rec**: 6 parameters, 3 lines
- **manure_allo.mnu**: 20 parameters, 6 lines
- **cs_aqu.ini**: 4 parameters, 3 lines
- **soil_plant.ini_cs**: 8 parameters, 3 lines
- **salt_fertilizer.frt**: 3 parameters, 3 lines
- **scen_dtl.upd**: 6 parameters, 4 lines
- **transplant.plt**: 3 parameters, 3 lines
- **cs.res**: 3 parameters, 3 lines
- **salt_hru.ini**: 5 parameters, 5 lines
- **wetland.wet_cs**: 3 parameters, 2 lines
- **cs_hru.ini**: 5 parameters, 5 lines
- **basins_carbon.tes**: 3 parameters, 3 lines
- **gwflow.wetland**: 3 parameters, 2 lines
- **print.prt**: 289 parameters, 114 lines
- **pest.com**: 7 parameters, 4 lines
- **salt_aqu.ini**: 5 parameters, 3 lines
- **puddle.ops**: 3 parameters, 3 lines
- **initial.cha_cs**: 3 parameters, 3 lines
- **plants.plt**: 6 parameters, 4 lines
- **fertilizer.frt_cs**: 3 parameters, 3 lines
- **treatment.trt**: 5 parameters, 4 lines
- **element.ccu**: 9 parameters, 3 lines
- **pet.cli**: 2 parameters, 2 lines
- **time.sim**: 7 parameters, 3 lines
- **reservoir.res_cs**: 4 parameters, 3 lines
- **manure.frt**: 3 parameters, 3 lines

### Parameters by Classification

- **CHANNEL**: 22 parameters
- **CLIMATE**: 22 parameters
- **GENERAL**: 317 parameters
- **HRU**: 29 parameters
- **PLANT**: 17 parameters
- **RESERVOIR**: 30 parameters
- **SIMULATION**: 360 parameters
- **SOIL**: 4 parameters

### Parameters by File

- **basins_carbon.tes**: 3 parameters
- **carb_coefs.cbn', iostat=eof**: 51 parameters
- **channel.cha**: 6 parameters
- **co2_yr.dat**: 4 parameters
- **cs.res**: 3 parameters
- **cs_aqu.ini**: 4 parameters
- **cs_atmo.cli**: 7 parameters
- **cs_channel.ini**: 4 parameters
- **cs_hru.ini**: 5 parameters
- **cs_recall.rec**: 6 parameters
- **element.ccu**: 9 parameters
- **fertilizer.frt_cs**: 3 parameters
- **file.cio**: 61 parameters
- **gwflow.canals**: 20 parameters
- **gwflow.cellhru**: 7 parameters
- **gwflow.chancells**: 2 parameters
- **gwflow.floodplain**: 6 parameters
- **gwflow.hru_pump_observe**: 2 parameters
- **gwflow.hrucell**: 6 parameters
- **gwflow.huc12cell**: 5 parameters
- **gwflow.input**: 73 parameters
- **gwflow.lsucell**: 9 parameters
- **gwflow.pumpex**: 7 parameters
- **gwflow.rescells**: 7 parameters
- **gwflow.solutes**: 13 parameters
- **gwflow.solutes.minerals**: 6 parameters
- **gwflow.streamobs**: 5 parameters
- **gwflow.tiles**: 10 parameters
- **gwflow.wetland**: 3 parameters
- **hru-data.hru**: 4 parameters
- **initial.aqu_cs**: 3 parameters
- **initial.cha_cs**: 3 parameters
- **manure.frt**: 3 parameters
- **manure_allo.mnu**: 20 parameters
- **nutrients.rte**: 3 parameters
- **out.key**: 2 parameters
- **pest.com**: 7 parameters
- **pest_metabolite.pes**: 11 parameters
- **pet.cli**: 2 parameters
- **plants.plt**: 6 parameters
- **print.prt**: 289 parameters
- **puddle.ops**: 3 parameters
- **res_conds.dat**: 13 parameters
- **reservoir.res**: 3 parameters
- **reservoir.res_cs**: 4 parameters
- **salt_aqu.ini**: 5 parameters
- **salt_atmo.cli**: 13 parameters
- **salt_channel.ini**: 4 parameters
- **salt_fertilizer.frt**: 3 parameters
- **salt_hru.ini**: 5 parameters
- **salt_recall.rec**: 6 parameters
- **satbuffer.str**: 3 parameters
- **scen_dtl.upd**: 6 parameters
- **sed_nut.cha**: 3 parameters
- **soil_lyr_depths.sol**: 4 parameters
- **soil_plant.ini_cs**: 8 parameters
- **time.sim**: 7 parameters
- **transplant.plt**: 3 parameters
- **treatment.trt**: 5 parameters
- **wetland.wet_cs**: 3 parameters

## Advantages of Dynamic Templates

✅ **Source Code Accuracy**: Parameters extracted from actual file reading operations
✅ **Automatic Discovery**: No manual template maintenance required
✅ **Real Structure Mapping**: Reflects actual file formats and line positions
✅ **Comprehensive Coverage**: Captures all parameters the source code actually reads
✅ **Type Intelligence**: Smart inference of data types, units, and ranges

## Template Generation Process

1. **JSON Analysis**: Load FORD I/O analysis files (`*.io.json`)
2. **File Discovery**: Identify input files from procedure names and units
3. **Parameter Extraction**: Parse data_reads sections for column information
4. **Type Inference**: Apply intelligent patterns for data types and units
5. **Structure Mapping**: Map parameters to file positions and lines
6. **Database Generation**: Create SWAT+-compatible parameter database
