# Enhanced Dynamic Modular Database Generation Summary

## Overall Statistics
- **Total Parameters**: 330
- **Total Files**: 148
- **Data Source**: input_file_module.f90 + pattern inference

## Classification Distribution
- **BASIN**: 4 parameters
- **CHANNEL**: 32 parameters
- **CLIMATE**: 20 parameters
- **CONDITIONAL**: 8 parameters
- **CONNECT**: 26 parameters
- **EXCO**: 12 parameters
- **GENERAL**: 102 parameters
- **HERD**: 6 parameters
- **HRU**: 8 parameters
- **HYDROLOGY**: 6 parameters
- **LINK**: 4 parameters
- **PLANT**: 22 parameters
- **REGIONAL**: 34 parameters
- **RESERVOIR**: 18 parameters
- **SOIL**: 12 parameters
- **STRUCTURAL**: 10 parameters
- **WATER**: 6 parameters

## Top Files by Parameter Count
- **initial.cha**: 4 parameters
- **channel.cha**: 4 parameters
- **hydrology.cha**: 4 parameters
- **sediment.cha**: 4 parameters
- **nutrients.cha**: 4 parameters
- **channel-lte.cha**: 4 parameters
- **hyd-sed-lte.cha**: 4 parameters
- **temperature.cha**: 4 parameters
- **hru-data.hru**: 4 parameters
- **hru-lte.hru**: 4 parameters
- **plants.plt**: 4 parameters
- **soils.sol**: 4 parameters
- **nutrients.sol**: 4 parameters
- **soils_lte.sol**: 4 parameters
- **initial.res**: 3 parameters
- **reservoir.res**: 3 parameters
- **hydrology.res**: 3 parameters
- **sediment.res**: 3 parameters
- **nutrients.res**: 3 parameters
- **weir.res**: 3 parameters

## All Files Discovered

### SIM (5 files)
- `time.sim` (2 parameters)
- `print.prt` (2 parameters)
- `object.prt` (2 parameters)
- `object.cnt` (2 parameters)
- `constituents.cs` (2 parameters)

### BASIN (2 files)
- `codes.bsn` (2 parameters)
- `parameters.bsn` (2 parameters)

### CLI (10 files)
- `weather-sta.cli` (2 parameters)
- `weather-wgn.cli` (2 parameters)
- `pet.cli` (2 parameters)
- `wind-dir.cli` (2 parameters)
- `pcp.cli` (2 parameters)
- `tmp.cli` (2 parameters)
- `slr.cli` (2 parameters)
- `hmd.cli` (2 parameters)
- `wnd.cli` (2 parameters)
- `atmodep.cli` (2 parameters)

### CON (13 files)
- `hru.con` (2 parameters)
- `hru-lte.con` (2 parameters)
- `rout_unit.con` (2 parameters)
- `gwflow.con` (2 parameters)
- `aquifer.con` (2 parameters)
- `aquifer2d.con` (2 parameters)
- `channel.con` (2 parameters)
- `reservoir.con` (2 parameters)
- `recall.con` (2 parameters)
- `exco.con` (2 parameters)
- `delratio.con` (2 parameters)
- `outlet.con` (2 parameters)
- `chandeg.con` (2 parameters)

### CHA (8 files)
- `initial.cha` (4 parameters)
- `channel.cha` (4 parameters)
- `hydrology.cha` (4 parameters)
- `sediment.cha` (4 parameters)
- `nutrients.cha` (4 parameters)
- `channel-lte.cha` (4 parameters)
- `hyd-sed-lte.cha` (4 parameters)
- `temperature.cha` (4 parameters)

### RES (8 files)
- `initial.res` (3 parameters)
- `reservoir.res` (3 parameters)
- `hydrology.res` (3 parameters)
- `sediment.res` (3 parameters)
- `nutrients.res` (3 parameters)
- `weir.res` (3 parameters)
- `wetland.wet` (2 parameters)
- `hydrology.wet` (2 parameters)

### RU (4 files)
- `rout_unit.def` (2 parameters)
- `rout_unit.ele` (2 parameters)
- `rout_unit.rtu` (2 parameters)
- `rout_unit.dr` (2 parameters)

### HRU (2 files)
- `hru-data.hru` (4 parameters)
- `hru-lte.hru` (4 parameters)

### EXCO (6 files)
- `exco.exc` (2 parameters)
- `exco_om.exc` (2 parameters)
- `exco_pest.exc` (2 parameters)
- `exco_path.exc` (2 parameters)
- `exco_hmet.exc` (2 parameters)
- `exco_salt.exc` (2 parameters)

### REC (1 files)
- `recall.rec` (2 parameters)

### DELR (6 files)
- `delratio.del` (2 parameters)
- `dr_om.del` (2 parameters)
- `dr_pest.del` (2 parameters)
- `dr_path.del` (2 parameters)
- `dr_hmet.del` (2 parameters)
- `dr_salt.del` (2 parameters)

### AQU (2 files)
- `initial.aqu` (2 parameters)
- `aquifer.aqu` (2 parameters)

### HERD (3 files)
- `animal.hrd` (2 parameters)
- `herd.hrd` (2 parameters)
- `ranch.hrd` (2 parameters)

### WATER_RIGHTS (3 files)
- `water_allocation.wro` (2 parameters)
- `element.wro` (2 parameters)
- `water_rights.wro` (2 parameters)

### LINK (2 files)
- `chan-surf.lin` (2 parameters)
- `aqu_cha.lin` (2 parameters)

### HYDROLOGY (3 files)
- `hydrology.hyd` (2 parameters)
- `topography.hyd` (2 parameters)
- `field.fld` (2 parameters)

### STRUCTURAL (5 files)
- `tiledrain.str` (2 parameters)
- `septic.str` (2 parameters)
- `filterstrip.str` (2 parameters)
- `grassedww.str` (2 parameters)
- `bmpuser.str` (2 parameters)

### PARAMETER_DATABASES (10 files)
- `plants.plt` (4 parameters)
- `fertilizer.frt` (2 parameters)
- `tillage.til` (2 parameters)
- `pesticide.pes` (2 parameters)
- `pathogens.pth` (2 parameters)
- `metals.mtl` (2 parameters)
- `salt.slt` (2 parameters)
- `urban.urb` (2 parameters)
- `septic.sep` (2 parameters)
- `snow.sno` (2 parameters)

### OPS (6 files)
- `harv.ops` (2 parameters)
- `graze.ops` (2 parameters)
- `irr.ops` (2 parameters)
- `chem_app.ops` (2 parameters)
- `fire.ops` (2 parameters)
- `sweep.ops` (2 parameters)

### LUM (5 files)
- `landuse.lum` (2 parameters)
- `management.sch` (2 parameters)
- `cntable.lum` (2 parameters)
- `cons_practice.lum` (2 parameters)
- `ovn_table.lum` (2 parameters)

### CHG (9 files)
- `cal_parms.cal` (2 parameters)
- `calibration.cal` (2 parameters)
- `codes.sft` (2 parameters)
- `wb_parms.sft` (2 parameters)
- `water_balance.sft` (2 parameters)
- `ch_sed_budget.sft` (2 parameters)
- `ch_sed_parms.sft` (2 parameters)
- `plant_parms.sft` (2 parameters)
- `plant_gro.sft` (2 parameters)

### INIT (11 files)
- `plant.ini` (2 parameters)
- `soil_plant.ini` (2 parameters)
- `om_water.ini` (2 parameters)
- `pest_hru.ini` (2 parameters)
- `pest_water.ini` (2 parameters)
- `path_hru.ini` (2 parameters)
- `path_water.ini` (2 parameters)
- `hmet_hru.ini` (2 parameters)
- `hmet_water.ini` (2 parameters)
- `salt_hru.ini` (2 parameters)
- `salt_water.ini` (2 parameters)

### SOILS (3 files)
- `soils.sol` (4 parameters)
- `nutrients.sol` (4 parameters)
- `soils_lte.sol` (4 parameters)

### CONDITION (4 files)
- `lum.dtl` (2 parameters)
- `res_rel.dtl` (2 parameters)
- `scen_lu.dtl` (2 parameters)
- `flo_con.dtl` (2 parameters)

### REGIONS (17 files)
- `ls_unit.ele` (2 parameters)
- `ls_unit.def` (2 parameters)
- `ls_reg.ele` (2 parameters)
- `ls_reg.def` (2 parameters)
- `ls_cal.reg` (2 parameters)
- `ch_catunit.ele` (2 parameters)
- `ch_catunit.def` (2 parameters)
- `ch_reg.def` (2 parameters)
- `aqu_catunit.ele` (2 parameters)
- `aqu_catunit.def` (2 parameters)
- `aqu_reg.def` (2 parameters)
- `res_catunit.ele` (2 parameters)
- `res_catunit.def` (2 parameters)
- `res_reg.def` (2 parameters)
- `rec_catunit.ele` (2 parameters)
- `rec_catunit.def` (2 parameters)
- `rec_reg.def` (2 parameters)

### PATH_PCP (0 files)

### PATH_TMP (0 files)

### PATH_SLR (0 files)

### PATH_HMD (0 files)

### PATH_WND (0 files)

### PATH_PET (0 files)
