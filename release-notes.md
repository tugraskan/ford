# Release Notes

## Version: test

Sources: compare_inputs_schema_diffs_lite.csv, compare_inputs_schema_diffs.csv (deduplicated)

### aqu_catunit.def
- Changed (6):
  - titldum (line 1, pos 1)
  - mreg (line 2, pos 1)
  - header (line 3, pos 1)
  - k (line 4, pos 1)
  - area_ha (line 4, pos 3)
  - nspu (line 4, pos 4)

### aqu_catunit.ele
- Changed (5):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - name (line 3, pos 2)
  - obtyp (line 3, pos 3)

### aqu_cha.lin
- Changed (5):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - numb (line 3, pos 1)
  - name (line 3, pos 2)
  - nspu (line 3, pos 3)

### aquifer.aqu
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)

### aquifer.con
- Changed (9):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - constit (line 3, pos 10)
  - props2 (line 3, pos 11)
  - ruleset (line 3, pos 12)
  - gis_id (line 3, pos 3)
  - lat (line 3, pos 5)
  - long (line 3, pos 6)
  - wst_c (line 3, pos 9)

### atmodep.cli
- Changed (6):
  - titldum (line 1, pos 1)
  - name (line 14, pos 1)
  - header (line 2, pos 1)
  - timestep (line 3, pos 2)
  - name (line 4, pos 1)
  - name (line 9, pos 1)

### basins_carbon.tes
- Added (37):
  - er_POC_para (line 3, pos 1)
  - ABCO2_para_sur (line 3, pos 10)
  - ABCO2_para_sub (line 3, pos 11)
  - ABP_para_sur (line 3, pos 12)
  - ABP_para_sub (line 3, pos 13)
  - ALMCO2_para_sur (line 3, pos 14)
  - ALMCO2_para_sub (line 3, pos 15)
  - ALSLNCO2_para_sur (line 3, pos 16)
  - ALSLNCO2_para_sub (line 3, pos 17)
  - ASP_para_sur (line 3, pos 18)
  - ...and 27 more
- Removed (1):
  - cbn_tes (line 3, pos 1)
- Changed (40):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - cbn_tes (line 3, pos 1)
  - er_POC_para (line 3, pos 1)
  - ABCO2_para_sur (line 3, pos 10)
  - ABCO2_para_sub (line 3, pos 11)
  - ABP_para_sur (line 3, pos 12)
  - ABP_para_sub (line 3, pos 13)
  - ALMCO2_para_sur (line 3, pos 14)
  - ALMCO2_para_sub (line 3, pos 15)
  - ...and 30 more

### bmpuser.str
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### cal_parms.cal
- Changed (3):
  - titldum (line 1, pos 1)
  - mchg_par (line 2, pos 1)
  - header (line 3, pos 1)

### calibration.cal
- Added (5):
  - range (line 5, pos 1)
  - var (line 5, pos 2)
  - val1 (line 5, pos 3)
  - val2 (line 5, pos 4)
  - cond (line 6, pos 1)
- Removed (1):
  - cond (line 5, pos 1)
- Changed (19):
  - titldum (line 1, pos 1)
  - mcal (line 2, pos 1)
  - header (line 3, pos 1)
  - name (line 4, pos 1)
  - day2 (line 4, pos 10)
  - chg_typ (line 4, pos 2)
  - val (line 4, pos 3)
  - conds (line 4, pos 4)
  - lyr1 (line 4, pos 5)
  - lyr2 (line 4, pos 6)
  - ...and 9 more

### ch_catunit.def
- Changed (6):
  - titldum (line 1, pos 1)
  - mreg (line 2, pos 1)
  - header (line 3, pos 1)
  - k (line 4, pos 1)
  - area_ha (line 4, pos 3)
  - nspu (line 4, pos 4)

### ch_reg.def
- Changed (6):
  - titldum (line 1, pos 1)
  - mreg (line 2, pos 1)
  - header (line 3, pos 1)
  - k (line 4, pos 1)
  - area_ha (line 4, pos 3)
  - nspu (line 4, pos 4)

### ch_sed_budget.sft
- Changed (6):
  - titldum (line 1, pos 1)
  - mreg (line 2, pos 1)
  - header (line 3, pos 1)
  - ord_num (line 4, pos 2)
  - nspu (line 4, pos 3)
  - header (line 5, pos 1)

### ch_sed_parms.sft
- Changed (9):
  - titldum (line 1, pos 1)
  - mchp (line 2, pos 1)
  - header (line 3, pos 1)
  - name (line 4, pos 1)
  - chg_typ (line 4, pos 2)
  - neg (line 4, pos 3)
  - pos (line 4, pos 4)
  - lo (line 4, pos 5)
  - up (line 4, pos 6)

### chan-surf.lin
- Changed (4):
  - titldum (line 1, pos 1)
  - mcha_sp (line 2, pos 1)
  - header (line 3, pos 1)
  - numb (line 4, pos 1)

### chandeg.con
- Changed (9):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - constit (line 3, pos 10)
  - props2 (line 3, pos 11)
  - ruleset (line 3, pos 12)
  - gis_id (line 3, pos 3)
  - lat (line 3, pos 5)
  - long (line 3, pos 6)
  - wst_c (line 3, pos 9)

### channel-lte.cha
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)

### channel.cha
- Changed (7):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - init (line 3, pos 3)
  - hyd (line 3, pos 4)
  - sed (line 3, pos 5)
  - nut (line 3, pos 6)

### channel.con
- Changed (9):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - constit (line 3, pos 10)
  - props2 (line 3, pos 11)
  - ruleset (line 3, pos 12)
  - gis_id (line 3, pos 3)
  - lat (line 3, pos 5)
  - long (line 3, pos 6)
  - wst_c (line 3, pos 9)

### chem_app.ops
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### cntable.lum
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### co2_yr.dat
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 3, pos 1)

### codes.bsn
- Added (3):
  - qual2e (line 3, pos 24)
  - idc_till (line 3, pos 26)
  - nam1 (line 3, pos 4)
- Removed (2):
  - i_fpwet (line 3, pos 24)
  - event (line 3, pos 4)
- Changed (19):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - wq (line 3, pos 10)
  - cfac (line 3, pos 13)
  - sed_ch (line 3, pos 17)
  - tdrn (line 3, pos 18)
  - wtdn (line 3, pos 19)
  - wwqfile (line 3, pos 2)
  - sol_p_model (line 3, pos 20)
  - atmo (line 3, pos 22)
  - ...and 9 more

### codes.sft
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### cons_practice.lum
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### constituents.cs
- Changed (1):
  - titldum (line 1, pos 1)

### cs_aqu.ini
- Changed (4):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - header (line 3, pos 1)
  - name (line 4, pos 1)

### cs_atmo.cli
- Changed (3):
  - station_name (line 10, pos 1)
  - station_name (line 4, pos 1)
  - station_name (line 7, pos 1)

### cs_channel.ini
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### cs_hru.ini
- Changed (6):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - header (line 3, pos 1)
  - header (line 4, pos 1)
  - header (line 5, pos 1)
  - name (line 6, pos 1)

### cs_irrigation
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### cs_plants_boron
- Changed (7):
  - titldum (line 1, pos 1)
  - bor_tol_sim (line 3, pos 1)
  - header (line 4, pos 1)
  - header (line 5, pos 1)
  - header (line 6, pos 1)
  - header (line 7, pos 1)
  - plant_name (line 8, pos 1)

### cs_reactions
- Changed (14):
  - titldum (line 1, pos 1)
  - header (line 10, pos 1)
  - aqu_dum (line 11, pos 1)
  - group (line 11, pos 2)
  - shale_fractions(ishale) (line 11, pos 3)
  - header (line 2, pos 1)
  - num_rct (line 3, pos 1)
  - num_groups (line 3, pos 2)
  - header (line 5, pos 1)
  - num_geol_shale (line 6, pos 1)
  - ...and 4 more

### cs_recall.rec
- Changed (6):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - name (line 3, pos 2)
  - typ (line 3, pos 3)
  - filename (line 3, pos 4)

### cs_res
- Changed (4):
  - titldum (line 1, pos 1)
  - titldum (line 2, pos 1)
  - header (line 4, pos 1)
  - name (line 5, pos 1)

### cs_streamobs
- Changed (1):
  - cs_str_nobs (line 2, pos 1)

### cs_uptake
- Changed (4):
  - header (line 1, pos 1)
  - header (line 2, pos 1)
  - header (line 3, pos 1)
  - name (line 4, pos 1)

### cs_urban
- Changed (3):
  - header (line 1, pos 1)
  - header (line 2, pos 1)
  - urb_type (line 3, pos 1)

### delratio.con
- Changed (9):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - constit (line 3, pos 10)
  - props2 (line 3, pos 11)
  - ruleset (line 3, pos 12)
  - gis_id (line 3, pos 3)
  - lat (line 3, pos 5)
  - long (line 3, pos 6)
  - wst_c (line 3, pos 9)

### delratio.del
- Changed (24):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - mdr_sp (line 2, pos 1)
  - header (line 3, pos 1)
  - name (line 3, pos 1)
  - om_file (line 3, pos 2)
  - pest_file (line 3, pos 3)
  - path_file (line 3, pos 4)
  - hmet_file (line 3, pos 5)
  - salts_file (line 3, pos 6)
  - ...and 14 more

### dr_hmet.del
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### dr_om.del
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### dr_path.del
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### dr_pest.del
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### dr_salt.del
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### element.ccu
- Changed (5):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - name (line 3, pos 2)
  - obtyp (line 3, pos 3)

### exco.con
- Changed (9):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - constit (line 3, pos 10)
  - props2 (line 3, pos 11)
  - ruleset (line 3, pos 12)
  - gis_id (line 3, pos 3)
  - lat (line 3, pos 5)
  - long (line 3, pos 6)
  - wst_c (line 3, pos 9)

### exco.exc
- Added (6):
  - name (line 3, pos 1)
  - om_file (line 3, pos 2)
  - pest_file (line 3, pos 3)
  - path_file (line 3, pos 4)
  - hmet_file (line 3, pos 5)
  - salts_file (line 3, pos 6)
- Removed (19):
  - namedum (line 3, pos 1)
  - no2 (line 3, pos 10)
  - cbod (line 3, pos 11)
  - dox (line 3, pos 12)
  - san (line 3, pos 13)
  - sil (line 3, pos 14)
  - cla (line 3, pos 15)
  - sag (line 3, pos 16)
  - lag (line 3, pos 17)
  - grv (line 3, pos 18)
  - ...and 9 more
- Changed (8):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)
  - om_file (line 3, pos 2)
  - pest_file (line 3, pos 3)
  - path_file (line 3, pos 4)
  - hmet_file (line 3, pos 5)
  - salts_file (line 3, pos 6)

### exco_hmet.exc
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### exco_om.exc
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### exco_path.exc
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### exco_pest.exc
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### exco_salt.exc
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### fertilizer.frt
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### fertilizer.frt_cs
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### field.fld
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### file.cio
- Added (1):
  - line_buffer (line 32, pos 1)
- Changed (32):
  - titldum (line 1, pos 1)
  - name (line 10, pos 1)
  - name (line 11, pos 1)
  - name (line 12, pos 1)
  - name (line 13, pos 1)
  - name (line 14, pos 1)
  - name (line 15, pos 1)
  - name (line 16, pos 1)
  - name (line 17, pos 1)
  - name (line 18, pos 1)
  - ...and 22 more

### filterstrip.str
- Changed (5):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)
  - vfscon (line 3, pos 4)
  - vfsch (line 3, pos 5)

### fire.ops
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### flo_con.dtl
- Changed (10):
  - name (line 5, pos 1)
  - titldum (line 1, pos 1)
  - mdtbl (line 2, pos 1)
  - header (line 4, pos 1)
  - name (line 5, pos 1)
  - conds (line 5, pos 2)
  - alts (line 5, pos 3)
  - acts (line 5, pos 4)
  - header (line 6, pos 1)
  - header (line 8, pos 1)

### grassedww.str
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### graze.ops
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### gwflow.canals
- Changed (13):
  - header (line 1, pos 1)
  - header (line 10, pos 1)
  - cell_num (line 11, pos 1)
  - canal (line 11, pos 2)
  - length (line 11, pos 3)
  - stage (line 11, pos 4)
  - K_zone (line 11, pos 5)
  - gw_ncanal (line 2, pos 1)
  - header (line 3, pos 1)
  - header (line 5, pos 1)
  - ...and 3 more

### gwflow.cellhru
- Changed (5):
  - num_unique (line 3, pos 1)
  - cell_num (line 5, pos 1)
  - hru_id (line 5, pos 2)
  - cell_area (line 5, pos 3)
  - poly_area (line 5, pos 4)

### gwflow.chancells
- Changed (10):
  - cell_ID (line 4, pos 1)
  - bed_elev (line 4, pos 2)
  - channel (line 4, pos 3)
  - chan_length (line 4, pos 4)
  - chan_zone (line 4, pos 5)
  - cell_ID (line 4, pos 1)
  - bed_elev (line 4, pos 2)
  - channel (line 4, pos 3)
  - chan_length (line 4, pos 4)
  - chan_zone (line 4, pos 5)

### gwflow.floodplain
- Changed (3):
  - header (line 1, pos 1)
  - gw_fp_ncells (line 2, pos 1)
  - header (line 3, pos 1)

### gwflow.hru_pump_observe
- Changed (1):
  - num_hru_pump_obs (line 2, pos 1)

### gwflow.hrucell
- Changed (5):
  - nhru_connected (line 4, pos 1)
  - hru_id (line 5, pos 1)
  - hru_id (line 8, pos 1)
  - hru_area (line 8, pos 2)
  - poly_area (line 8, pos 4)

### gwflow.huc12cell
- Changed (4):
  - huc12_dum (line 4, pos 1)
  - huc12_connect(k) (line 4, pos 2)
  - huc12_id (line 7, pos 1)
  - cell_num (line 7, pos 2)

### gwflow.input
- Added (1):
  - gw_bed_change (line 63, pos 1)
- Removed (1):
  - bed_change (line 63, pos 1)
- Changed (77):
  - gw_satx_flag (line 10, pos 1)
  - gw_pumpex_flag (line 11, pos 1)
  - gw_tile_flag (line 12, pos 1)
  - gw_res_flag (line 13, pos 1)
  - gw_wet_flag (line 14, pos 1)
  - gw_fp_flag (line 15, pos 1)
  - gw_canal_flag (line 16, pos 1)
  - gw_solute_flag (line 17, pos 1)
  - gw_time_step (line 18, pos 1)
  - gwflag_day (line 19, pos 1)
  - ...and 67 more

### gwflow.lsucell
- Changed (9):
  - header (line 1, pos 1)
  - nlsu (line 2, pos 1)
  - nlsu_connected (line 3, pos 1)
  - lsu_id (line 4, pos 1)
  - header (line 5, pos 1)
  - header (line 6, pos 1)
  - lsu (line 7, pos 1)
  - lsu_area (line 7, pos 2)
  - poly_area (line 7, pos 4)

### gwflow.pumpex
- Added (1):
  - pumpex_cell (line 4, pos 1)
- Removed (1):
  - gw_pumpex_cell(i) (line 4, pos 1)
- Changed (10):
  - gw_pumpex_dates(i,1,j) (line 5, pos 1)
  - gw_pumpex_dates(i,2,j) (line 5, pos 2)
  - gw_pumpex_rates(i,j) (line 5, pos 3)
  - header (line 1, pos 1)
  - gw_npumpex (line 2, pos 1)
  - gw_pumpex_cell(i) (line 4, pos 1)
  - pumpex_cell (line 4, pos 1)
  - gw_pumpex_dates(i,1,j) (line 5, pos 1)
  - gw_pumpex_dates(i,2,j) (line 5, pos 2)
  - gw_pumpex_rates(i,j) (line 5, pos 3)

### gwflow.rescells
- Changed (9):
  - header (line 1, pos 1)
  - header (line 2, pos 1)
  - res_thick (line 3, pos 1)
  - res_K (line 4, pos 1)
  - num_res_cells (line 5, pos 1)
  - header (line 6, pos 1)
  - res_cell (line 7, pos 1)
  - res_id (line 7, pos 2)
  - res_stage (line 7, pos 3)

### gwflow.solutes
- Changed (13):
  - header (line 1, pos 1)
  - single_value (line 10, pos 1)
  - header (line 16, pos 1)
  - header (line 2, pos 1)
  - num_ts_transport (line 3, pos 1)
  - gw_long_disp (line 4, pos 1)
  - header (line 5, pos 1)
  - name (line 6, pos 1)
  - gwsol_sorb(s) (line 6, pos 2)
  - gwsol_rctn(s) (line 6, pos 3)
  - ...and 3 more

### gwflow.streamobs
- Changed (2):
  - gw_num_obs_chan (line 2, pos 1)
  - gw_flow_cal_yrs (line 6, pos 1)

### gwflow.tiles
- Changed (13):
  - header (line 10, pos 1)
  - gw_tile_num_group (line 6, pos 1)
  - num_tile_cells(i) (line 8, pos 1)
  - gw_tile_groups(i,j) (line 9, pos 1)
  - header (line 1, pos 1)
  - header (line 10, pos 1)
  - gw_tile_depth (line 2, pos 1)
  - gw_tile_drain_area (line 3, pos 1)
  - gw_tile_K (line 4, pos 1)
  - gw_tile_group_flag (line 5, pos 1)
  - ...and 3 more

### gwflow.wetland
- Changed (6):
  - header (line 1, pos 1)
  - header (line 2, pos 1)
  - header (line 3, pos 1)
  - header (line 4, pos 1)
  - header (line 5, pos 1)
  - dum1 (line 6, pos 1)

### harv.ops
- Changed (4):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)
  - typ (line 3, pos 2)

### hmd(i)%filename
- Changed (11):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - nbyr (line 3, pos 1)
  - tstep (line 3, pos 2)
  - lat (line 3, pos 3)
  - long (line 3, pos 4)
  - elev (line 3, pos 5)
  - iyr (line 4, pos 1)
  - istep (line 4, pos 2)
  - iyr (line 5, pos 1)
  - ...and 1 more

### hmd.cli
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - filename (line 3, pos 1)

### hmet_hru.ini
- Changed (5):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)
  - titldum (line 4, pos 1)
  - titldum (line 5, pos 1)

### hru-data.hru
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)

### hru-lte.con
- Changed (9):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - constit (line 3, pos 10)
  - props2 (line 3, pos 11)
  - ruleset (line 3, pos 12)
  - gis_id (line 3, pos 3)
  - lat (line 3, pos 5)
  - long (line 3, pos 6)
  - wst_c (line 3, pos 9)

### hru-lte.hru
- Changed (9):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - name (line 3, pos 2)
  - text (line 3, pos 22)
  - tropical (line 3, pos 23)
  - igrow1 (line 3, pos 24)
  - igrow2 (line 3, pos 25)
  - plant (line 3, pos 26)

### hru.con
- Changed (29):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - hru_id (line 3, pos 1)
  - num (line 3, pos 1)
  - constit (line 3, pos 10)
  - props2 (line 3, pos 11)
  - ruleset (line 3, pos 12)
  - src_tot (line 3, pos 13)
  - obtyp_out (line 3, pos 14)
  - obtypno_out (line 3, pos 15)
  - ...and 19 more

### hyd-sed-lte.cha
- Added (2):
  - vcr_coef (line 3, pos 12)
  - bank_exp (line 3, pos 9)
- Removed (2):
  - chseq (line 3, pos 12)
  - cherod (line 3, pos 9)
- Changed (10):
  - order (line 3, pos 2)
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)
  - sinu (line 3, pos 11)
  - chseq (line 3, pos 12)
  - vcr_coef (line 3, pos 12)
  - order (line 3, pos 2)
  - bank_exp (line 3, pos 9)
  - cherod (line 3, pos 9)

### hydrology.cha
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### hydrology.hyd
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### hydrology.res
- Changed (13):
  - name (line 3, pos 1)
  - br1 (line 3, pos 10)
  - br2 (line 3, pos 11)
  - iyres (line 3, pos 2)
  - mores (line 3, pos 3)
  - psa (line 3, pos 4)
  - pvol (line 3, pos 5)
  - esa (line 3, pos 6)
  - evol (line 3, pos 7)
  - k (line 3, pos 8)
  - ...and 3 more

### hydrology.wet
- Changed (13):
  - name (line 3, pos 1)
  - ccoef (line 3, pos 10)
  - frac (line 3, pos 11)
  - psa (line 3, pos 2)
  - pdep (line 3, pos 3)
  - esa (line 3, pos 4)
  - edep (line 3, pos 5)
  - k (line 3, pos 6)
  - evrsv (line 3, pos 7)
  - acoef (line 3, pos 8)
  - ...and 3 more

### initial.aqu
- Changed (8):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)
  - org_min (line 3, pos 2)
  - pest (line 3, pos 3)
  - path (line 3, pos 4)
  - hmet (line 3, pos 5)
  - salt (line 3, pos 6)

### initial.aqu_cs
- Changed (8):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)
  - pest (line 3, pos 2)
  - path (line 3, pos 3)
  - hmet (line 3, pos 4)
  - salt (line 3, pos 5)
  - cs (line 3, pos 6)

### initial.cha
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### initial.cha_cs
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### initial.res
- Changed (8):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - init (line 3, pos 1)
  - org_min (line 3, pos 2)
  - pest (line 3, pos 3)
  - path (line 3, pos 4)
  - hmet (line 3, pos 5)
  - salt (line 3, pos 6)

### irr.ops
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### landuse.lum
- Changed (16):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)
  - tiledrain (line 3, pos 10)
  - septic (line 3, pos 11)
  - fstrip (line 3, pos 12)
  - grassww (line 3, pos 13)
  - bmpuser (line 3, pos 14)
  - cal_group (line 3, pos 2)
  - plant_cov (line 3, pos 3)
  - ...and 6 more

### ls_reg.def
- Changed (7):
  - titldum (line 1, pos 1)
  - i (line 2, pos 1)
  - num (line 2, pos 2)
  - header (line 3, pos 1)
  - k (line 4, pos 1)
  - area_ha (line 4, pos 3)
  - nspu (line 4, pos 4)

### ls_reg.ele
- Changed (6):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - name (line 3, pos 2)
  - ha (line 3, pos 3)
  - obtyp (line 3, pos 4)

### ls_unit.def
- Changed (6):
  - titldum (line 1, pos 1)
  - mlsu (line 2, pos 1)
  - header (line 3, pos 1)
  - k (line 4, pos 1)
  - area_ha (line 4, pos 3)
  - nspu (line 4, pos 4)

### ls_unit.ele
- Changed (5):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - name (line 3, pos 2)
  - obtyp (line 3, pos 3)

### lsu_elem_upd
- Changed (5):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - name (line 3, pos 2)
  - obtyp (line 3, pos 3)

### lum.dtl
- Changed (10):
  - name (line 5, pos 1)
  - titldum (line 1, pos 1)
  - mdtbl (line 2, pos 1)
  - header (line 4, pos 1)
  - name (line 5, pos 1)
  - conds (line 5, pos 2)
  - alts (line 5, pos 3)
  - acts (line 5, pos 4)
  - header (line 6, pos 1)
  - header (line 8, pos 1)

### manure_allo.mnu
- Added (1):
  - trn_obs (line 4, pos 4)
- Removed (1):
  - dmd_obs (line 4, pos 4)
- Changed (12):
  - titldum (line 1, pos 1)
  - imax (line 2, pos 1)
  - header (line 3, pos 1)
  - name (line 4, pos 1)
  - rule_typ (line 4, pos 2)
  - src_obs (line 4, pos 3)
  - dmd_obs (line 4, pos 4)
  - trn_obs (line 4, pos 4)
  - header (line 5, pos 1)
  - k (line 6, pos 1)
  - ...and 2 more

### nutrients.cha
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### nutrients.res
- Added (2):
  - nsolr (line 3, pos 8)
  - psolr (line 3, pos 9)
- Removed (2):
  - chlar (line 3, pos 8)
  - seccir (line 3, pos 9)
- Changed (13):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)
  - ires1 (line 3, pos 2)
  - ires2 (line 3, pos 3)
  - nsetlr1 (line 3, pos 4)
  - nsetlr2 (line 3, pos 5)
  - psetlr1 (line 3, pos 6)
  - psetlr2 (line 3, pos 7)
  - chlar (line 3, pos 8)
  - ...and 3 more

### nutrients.rte
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### nutrients.sol
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### object.cnt
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### object.prt
- Changed (9):
  - obtyp (line 3, pos 2)
  - hydtyp (line 3, pos 4)
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - obtyp (line 3, pos 2)
  - obtypno (line 3, pos 3)
  - hydtyp (line 3, pos 4)
  - filename (line 3, pos 5)

### om_water.ini
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### outlet.con
- Changed (9):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - constit (line 3, pos 10)
  - props2 (line 3, pos 11)
  - ruleset (line 3, pos 12)
  - gis_id (line 3, pos 3)
  - lat (line 3, pos 5)
  - long (line 3, pos 6)
  - wst_c (line 3, pos 9)

### ovn_table.lum
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### parameters.bsn
- Changed (6):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - cdn (line 3, pos 23)
  - rsd_covco (line 3, pos 33)
  - eros_spl (line 3, pos 37)
  - eros_expo (line 3, pos 39)

### path_hru.ini
- Added (1):
  - plt (line 4, pos 3)
- Removed (2):
  - titldum (line 5, pos 1)
  - plt (line 5, pos 2)
- Changed (7):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)
  - titldum (line 4, pos 1)
  - plt (line 4, pos 3)
  - titldum (line 5, pos 1)
  - plt (line 5, pos 2)

### path_water.ini
- Added (1):
  - benthic (line 4, pos 3)
- Removed (2):
  - titldum (line 5, pos 1)
  - benthic (line 5, pos 2)
- Changed (6):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - titldum (line 4, pos 1)
  - benthic (line 4, pos 3)
  - titldum (line 5, pos 1)
  - benthic (line 5, pos 2)

### pathogens.pth
- Added (1):
  - conc_min (line 3, pos 18)
- Removed (2):
  - swf (line 3, pos 18)
  - conc_min (line 3, pos 19)
- Changed (8):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - pathnm (line 3, pos 1)
  - det_thrshd (line 3, pos 13)
  - conc_min (line 3, pos 18)
  - swf (line 3, pos 18)
  - conc_min (line 3, pos 19)
  - kd (line 3, pos 6)

### pcp(i)%filename
- Changed (16):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - nbyr (line 3, pos 1)
  - tstep (line 3, pos 2)
  - lat (line 3, pos 3)
  - long (line 3, pos 4)
  - elev (line 3, pos 5)
  - iyr (line 4, pos 1)
  - istep (line 4, pos 2)
  - mo (line 4, pos 3)
  - ...and 6 more

### pcp.cli
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - filename (line 3, pos 1)

### pest.com
- Changed (7):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - ipestcom_db (line 3, pos 1)
  - k (line 4, pos 1)
  - name (line 4, pos 2)
  - typ (line 4, pos 3)
  - filename (line 4, pos 4)

### pest_hru.ini
- Changed (4):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)
  - titldum (line 4, pos 1)

### pest_metabolite.pes
- Changed (4):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - parent_name (line 3, pos 1)
  - num_metab (line 3, pos 2)

### pest_water.ini
- Added (1):
  - benthic (line 4, pos 3)
- Removed (2):
  - titldum (line 5, pos 1)
  - benthic (line 5, pos 2)
- Changed (6):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - titldum (line 4, pos 1)
  - benthic (line 4, pos 3)
  - titldum (line 5, pos 1)
  - benthic (line 5, pos 2)

### pesticide.pes
- Changed (5):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)
  - descrip (line 3, pos 16)
  - mol_wt (line 3, pos 9)

### pet.cli
- Changed (4):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - filename (line 3, pos 1)
  - titldum (line 3, pos 1)

### petm(i)%filename
- Changed (11):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - nbyr (line 3, pos 1)
  - tstep (line 3, pos 2)
  - lat (line 3, pos 3)
  - long (line 3, pos 4)
  - elev (line 3, pos 5)
  - iyr (line 4, pos 1)
  - istep (line 4, pos 2)
  - iyr (line 5, pos 1)
  - ...and 1 more

### plant_gro.sft
- Changed (6):
  - titldum (line 1, pos 1)
  - mreg (line 2, pos 1)
  - header (line 3, pos 1)
  - lum_num (line 4, pos 2)
  - nspu (line 4, pos 3)
  - header (line 5, pos 1)

### plant_parms.sft
- Changed (6):
  - titldum (line 1, pos 1)
  - mreg (line 2, pos 1)
  - header (line 3, pos 1)
  - lum_num (line 4, pos 2)
  - nspu (line 4, pos 3)
  - header (line 5, pos 1)

### plants.plt
- Added (60):
  - meta_frac (line 3, pos 54)
  - str_frac (line 3, pos 55)
  - lig_frac (line 3, pos 56)
  - plantnm (line 4, pos 1)
  - laimx1 (line 4, pos 10)
  - frgrw2 (line 4, pos 11)
  - laimx2 (line 4, pos 12)
  - dlai (line 4, pos 13)
  - dlai_rate (line 4, pos 14)
  - chtmx (line 4, pos 15)
  - ...and 50 more
- Changed (164):
  - plantnm (line 3, pos 1)
  - laimx1 (line 3, pos 10)
  - frgrw2 (line 3, pos 11)
  - laimx2 (line 3, pos 12)
  - dlai (line 3, pos 13)
  - dlai_rate (line 3, pos 14)
  - chtmx (line 3, pos 15)
  - rdmx (line 3, pos 16)
  - t_opt (line 3, pos 17)
  - t_base (line 3, pos 18)
  - ...and 154 more

### print.prt
- Added (214):
  - d (line 11, pos 2)
  - m (line 11, pos 3)
  - y (line 11, pos 4)
  - a (line 11, pos 5)
  - d (line 12, pos 2)
  - m (line 12, pos 3)
  - y (line 12, pos 4)
  - a (line 12, pos 5)
  - d (line 13, pos 2)
  - m (line 13, pos 3)
  - ...and 204 more
- Removed (53):
  - wb_bsn (line 11, pos 2)
  - nb_bsn (line 12, pos 2)
  - ls_bsn (line 13, pos 2)
  - pw_bsn (line 14, pos 2)
  - aqu_bsn (line 15, pos 2)
  - res_bsn (line 16, pos 2)
  - chan_bsn (line 17, pos 2)
  - sd_chan_bsn (line 18, pos 2)
  - recall_bsn (line 19, pos 2)
  - wb_reg (line 20, pos 2)
  - ...and 43 more
- Changed (384):
  - name (line 11, pos 1)
  - name (line 12, pos 1)
  - name (line 13, pos 1)
  - name (line 14, pos 1)
  - name (line 15, pos 1)
  - name (line 16, pos 1)
  - name (line 17, pos 1)
  - name (line 18, pos 1)
  - name (line 19, pos 1)
  - name (line 20, pos 1)
  - ...and 374 more

### puddle.ops
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### rec_catunit.def
- Changed (6):
  - titldum (line 1, pos 1)
  - mreg (line 2, pos 1)
  - header (line 3, pos 1)
  - k (line 4, pos 1)
  - area_ha (line 4, pos 3)
  - nspu (line 4, pos 4)

### rec_catunit.ele
- Changed (5):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - name (line 3, pos 2)
  - obtyp (line 3, pos 3)

### rec_cs(i)%filename
- Changed (13):
  - titldum (line 1, pos 1)
  - nbyr (line 2, pos 1)
  - header (line 3, pos 1)
  - jday (line 4, pos 1)
  - mo (line 4, pos 2)
  - day_mo (line 4, pos 3)
  - iyr (line 4, pos 4)
  - ob_typ (line 4, pos 5)
  - ob_name (line 4, pos 6)
  - jday (line 5, pos 1)
  - ...and 3 more

### rec_pest(i)%filename
- Changed (5):
  - titldum (line 1, pos 1)
  - nbyr (line 2, pos 1)
  - header (line 3, pos 1)
  - iyr (line 4, pos 1)
  - istep (line 4, pos 2)

### rec_reg.def
- Changed (6):
  - titldum (line 1, pos 1)
  - mreg (line 2, pos 1)
  - header (line 3, pos 1)
  - k (line 4, pos 1)
  - area_ha (line 4, pos 3)
  - nspu (line 4, pos 4)

### rec_salt(i)%filename
- Changed (13):
  - titldum (line 1, pos 1)
  - nbyr (line 2, pos 1)
  - header (line 3, pos 1)
  - jday (line 4, pos 1)
  - mo (line 4, pos 2)
  - day_mo (line 4, pos 3)
  - iyr (line 4, pos 4)
  - ob_typ (line 4, pos 5)
  - ob_name (line 4, pos 6)
  - jday (line 5, pos 1)
  - ...and 3 more

### recall(i)%filename
- Added (21):
  - hd (line 4, pos 7)
  - sedp (line 6, pos 10)
  - no3 (line 6, pos 11)
  - solp (line 6, pos 12)
  - chla (line 6, pos 13)
  - nh3 (line 6, pos 14)
  - no2 (line 6, pos 15)
  - cbod (line 6, pos 16)
  - dox (line 6, pos 17)
  - san (line 6, pos 18)
  - ...and 11 more
- Removed (18):
  - sedp (line 4, pos 10)
  - no3 (line 4, pos 11)
  - solp (line 4, pos 12)
  - chla (line 4, pos 13)
  - nh3 (line 4, pos 14)
  - no2 (line 4, pos 15)
  - cbod (line 4, pos 16)
  - dox (line 4, pos 17)
  - san (line 4, pos 18)
  - sil (line 4, pos 19)
  - ...and 8 more
- Changed (79):
  - titldum (line 1, pos 1)
  - nbyr (line 2, pos 1)
  - header (line 3, pos 1)
  - jday (line 4, pos 1)
  - mo (line 4, pos 2)
  - day_mo (line 4, pos 3)
  - iyr (line 4, pos 4)
  - ob_typ (line 4, pos 5)
  - ob_name (line 4, pos 6)
  - jday (line 5, pos 1)
  - ...and 69 more

### recall.con
- Changed (9):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - constit (line 3, pos 10)
  - props2 (line 3, pos 11)
  - ruleset (line 3, pos 12)
  - gis_id (line 3, pos 3)
  - lat (line 3, pos 5)
  - long (line 3, pos 6)
  - wst_c (line 3, pos 9)

### recall.rec
- Changed (5):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - name (line 3, pos 2)
  - filename (line 3, pos 4)

### res_catunit.def
- Changed (6):
  - titldum (line 1, pos 1)
  - mreg (line 2, pos 1)
  - header (line 3, pos 1)
  - k (line 4, pos 1)
  - area_ha (line 4, pos 3)
  - nspu (line 4, pos 4)

### res_catunit.ele
- Changed (5):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - name (line 3, pos 2)
  - obtyp (line 3, pos 3)

### res_conds.dat
- Changed (8):
  - title (line 1, pos 1)
  - max_table (line 2, pos 1)
  - name (line 3, pos 1)
  - num_conds (line 3, pos 2)
  - num_modules (line 3, pos 3)
  - num_conds (line 4, pos 1)
  - tnum_conds (line 5, pos 1)
  - num_conds (line 6, pos 1)

### res_reg.def
- Changed (6):
  - titldum (line 1, pos 1)
  - mreg (line 2, pos 1)
  - header (line 3, pos 1)
  - k (line 4, pos 1)
  - area_ha (line 4, pos 3)
  - nspu (line 4, pos 4)

### res_rel.dtl
- Changed (10):
  - name (line 5, pos 1)
  - titldum (line 1, pos 1)
  - mdtbl (line 2, pos 1)
  - header (line 4, pos 1)
  - name (line 5, pos 1)
  - conds (line 5, pos 2)
  - alts (line 5, pos 3)
  - acts (line 5, pos 4)
  - header (line 6, pos 1)
  - header (line 8, pos 1)

### reservoir.con
- Changed (9):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - constit (line 3, pos 10)
  - props2 (line 3, pos 11)
  - ruleset (line 3, pos 12)
  - gis_id (line 3, pos 3)
  - lat (line 3, pos 5)
  - long (line 3, pos 6)
  - wst_c (line 3, pos 9)

### reservoir.res
- Changed (8):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - init (line 3, pos 3)
  - hyd (line 3, pos 4)
  - release (line 3, pos 5)
  - sed (line 3, pos 6)
  - nut (line 3, pos 7)

### reservoir.res_cs
- Changed (7):
  - header (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - pst (line 3, pos 2)
  - weir (line 3, pos 3)
  - salt (line 3, pos 4)
  - cs (line 3, pos 5)

### rout_unit.con
- Changed (9):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - constit (line 3, pos 10)
  - props2 (line 3, pos 11)
  - ruleset (line 3, pos 12)
  - gis_id (line 3, pos 3)
  - lat (line 3, pos 5)
  - long (line 3, pos 6)
  - wst_c (line 3, pos 9)

### rout_unit.def
- Changed (5):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - numb (line 3, pos 1)
  - name (line 3, pos 2)
  - nspu (line 3, pos 3)

### rout_unit.ele
- Changed (6):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - name (line 3, pos 2)
  - obtyp (line 3, pos 3)
  - dr_name (line 3, pos 6)

### rout_unit.rtu
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)

### ru_elem_upd
- Changed (6):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - name (line 3, pos 2)
  - obtyp (line 3, pos 3)
  - dr_name (line 3, pos 6)

### salt_aqu.ini
- Changed (5):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - header (line 3, pos 1)
  - header (line 4, pos 1)
  - name (line 5, pos 1)

### salt_atmo.cli
- Changed (9):
  - station_name (line 10, pos 1)
  - salt_ion (line 11, pos 1)
  - salt_ion (line 12, pos 1)
  - station_name (line 13, pos 1)
  - salt_ion (line 14, pos 1)
  - salt_ion (line 15, pos 1)
  - station_name (line 7, pos 1)
  - salt_ion (line 8, pos 1)
  - salt_ion (line 9, pos 1)

### salt_channel.ini
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### salt_fertilizer.frt
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### salt_hru.ini
- Added (6):
  - header (line 3, pos 1)
  - header (line 4, pos 1)
  - header (line 5, pos 1)
  - name (line 6, pos 1)
  - soil (line 7, pos 1)
  - plt (line 8, pos 1)
- Removed (5):
  - name (line 3, pos 1)
  - titldum (line 4, pos 1)
  - soil (line 4, pos 2)
  - titldum (line 5, pos 1)
  - plt (line 5, pos 2)
- Changed (6):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - header (line 3, pos 1)
  - header (line 4, pos 1)
  - header (line 5, pos 1)
  - name (line 6, pos 1)

### salt_irrigation
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### salt_plants
- Changed (8):
  - titldum (line 1, pos 1)
  - header (line 12, pos 1)
  - plant_name (line 13, pos 1)
  - header (line 2, pos 1)
  - salt_tds_ec (line 3, pos 1)
  - salt_tol_sim (line 5, pos 1)
  - salt_soil_type (line 6, pos 1)
  - salt_effect (line 7, pos 1)

### salt_recall.rec
- Changed (6):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - name (line 3, pos 2)
  - typ (line 3, pos 3)
  - filename (line 3, pos 4)

### salt_res
- Changed (4):
  - titldum (line 1, pos 1)
  - titldum (line 2, pos 1)
  - header (line 4, pos 1)
  - name (line 5, pos 1)

### salt_road
- Changed (6):
  - salt_ion (line 10, pos 1)
  - station_name (line 5, pos 1)
  - salt_ion (line 6, pos 1)
  - station_name (line 7, pos 1)
  - salt_ion (line 8, pos 1)
  - station_name (line 9, pos 1)

### salt_uptake
- Changed (4):
  - header (line 1, pos 1)
  - header (line 2, pos 1)
  - header (line 3, pos 1)
  - name (line 4, pos 1)

### salt_urban
- Changed (3):
  - header (line 1, pos 1)
  - header (line 2, pos 1)
  - urb_type (line 3, pos 1)

### scen_dtl.upd
- Changed (5):
  - titldum (line 1, pos 1)
  - num_dtls (line 2, pos 1)
  - header (line 3, pos 1)
  - typ (line 4, pos 2)
  - dtbl (line 4, pos 3)

### scen_lu.dtl
- Changed (10):
  - name (line 5, pos 1)
  - titldum (line 1, pos 1)
  - mdtbl (line 2, pos 1)
  - header (line 4, pos 1)
  - name (line 5, pos 1)
  - conds (line 5, pos 2)
  - alts (line 5, pos 3)
  - acts (line 5, pos 4)
  - header (line 6, pos 1)
  - header (line 8, pos 1)

### sediment.cha
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### sediment.res
- Changed (9):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)
  - nsed (line 3, pos 2)
  - d50 (line 3, pos 3)
  - carbon (line 3, pos 4)
  - bd (line 3, pos 5)
  - sed_stlr (line 3, pos 6)
  - velsetlr (line 3, pos 7)

### septic.sep
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - sepnm (line 3, pos 1)

### septic.str
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - bod_conv (line 3, pos 14)

### slr(i)%filename
- Changed (11):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - nbyr (line 3, pos 1)
  - tstep (line 3, pos 2)
  - lat (line 3, pos 3)
  - long (line 3, pos 4)
  - elev (line 3, pos 5)
  - iyr (line 4, pos 1)
  - istep (line 4, pos 2)
  - iyr (line 5, pos 1)
  - ...and 1 more

### slr.cli
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - filename (line 3, pos 1)

### snow.sno
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### soil_plant.ini
- Added (8):
  - name (line 4, pos 1)
  - sw_frac (line 4, pos 2)
  - nutc (line 4, pos 3)
  - pestc (line 4, pos 4)
  - pathc (line 4, pos 5)
  - saltc (line 4, pos 6)
  - hmetc (line 4, pos 7)
  - csc (line 4, pos 8)
- Changed (24):
  - name (line 3, pos 1)
  - sw_frac (line 3, pos 2)
  - nutc (line 3, pos 3)
  - pestc (line 3, pos 4)
  - pathc (line 3, pos 5)
  - saltc (line 3, pos 6)
  - hmetc (line 3, pos 7)
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)
  - ...and 14 more

### soils_lte.sol
- Changed (6):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - texture (line 3, pos 1)
  - awc (line 3, pos 2)
  - por (line 3, pos 3)
  - scon (line 3, pos 4)

### sweep.ops
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### temperature.cha
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### tiledrain.str
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### tillage.til
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - ridge_sp (line 3, pos 6)

### time.sim
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### tmp(i)%filename
- Changed (11):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - nbyr (line 3, pos 1)
  - tstep (line 3, pos 2)
  - lat (line 3, pos 3)
  - long (line 3, pos 4)
  - elev (line 3, pos 5)
  - iyr (line 4, pos 1)
  - istep (line 4, pos 2)
  - iyr (line 5, pos 1)
  - ...and 1 more

### tmp.cli
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - filename (line 3, pos 1)

### topography.hyd
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### transplant.plt
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - pop (line 3, pos 6)

### urban.urb
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - urbnm (line 3, pos 1)

### usgs_annual_head
- Changed (4):
  - usgs_site_id (line 2, pos 1)
  - usgs_lat (line 2, pos 2)
  - usgs_long (line 2, pos 3)
  - head_vals(j) (line 2, pos 4)

### water_allocation.wro
- Added (21):
  - pipe (line 4, pos 10)
  - canal (line 4, pos 11)
  - pump (line 4, pos 12)
  - cha_ob (line 4, pos 13)
  - trn_obs (line 4, pos 4)
  - out_src (line 4, pos 5)
  - out_rcv (line 4, pos 6)
  - wtp (line 4, pos 7)
  - uses (line 4, pos 8)
  - stor (line 4, pos 9)
  - ...and 11 more
- Removed (16):
  - div_delay (line 10, pos 1)
  - dmd_obs (line 4, pos 4)
  - cha_ob (line 4, pos 5)
  - limit_mon (line 6, pos 4)
  - rcv_num (line 8, pos 10)
  - rcv_dtl (line 8, pos 11)
  - dmd_src_obs (line 8, pos 12)
  - src (line 8, pos 13)
  - ob_typ (line 8, pos 2)
  - ob_num (line 8, pos 3)
  - ...and 6 more
- Changed (49):
  - header (line 7, pos 1)
  - k (line 8, pos 1)
  - titldum (line 1, pos 1)
  - div_delay (line 10, pos 1)
  - imax (line 2, pos 1)
  - header (line 3, pos 1)
  - name (line 4, pos 1)
  - pipe (line 4, pos 10)
  - canal (line 4, pos 11)
  - pump (line 4, pos 12)
  - ...and 39 more

### water_balance.sft
- Changed (5):
  - titldum (line 1, pos 1)
  - mreg (line 2, pos 1)
  - header (line 3, pos 1)
  - nlum (line 4, pos 2)
  - header (line 5, pos 1)

### wb_parms.sft
- Changed (9):
  - titldum (line 1, pos 1)
  - mlsp (line 2, pos 1)
  - header (line 3, pos 1)
  - name (line 4, pos 1)
  - chg_typ (line 4, pos 2)
  - neg (line 4, pos 3)
  - pos (line 4, pos 4)
  - lo (line 4, pos 5)
  - up (line 4, pos 6)

### weather-sta.cli
- Changed (2):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)

### weather-wgn.cli
- Changed (16):
  - titldum (line 1, pos 1)
  - header (line 3, pos 1)
  - tmpmx (line 4, pos 1)
  - pcpd (line 4, pos 10)
  - rainhmx (line 4, pos 11)
  - solarav (line 4, pos 12)
  - dewpt (line 4, pos 13)
  - windav (line 4, pos 14)
  - tmpmn (line 4, pos 2)
  - tmpstdmx (line 4, pos 3)
  - ...and 6 more

### weir.res
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - name (line 3, pos 1)

### wetland.wet
- Changed (8):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - init (line 3, pos 3)
  - hyd (line 3, pos 4)
  - release (line 3, pos 5)
  - sed (line 3, pos 6)
  - nut (line 3, pos 7)

### wetland.wet_cs
- Changed (7):
  - header (line 1, pos 1)
  - header (line 2, pos 1)
  - k (line 3, pos 1)
  - pst (line 3, pos 2)
  - weir (line 3, pos 3)
  - salt (line 3, pos 4)
  - cs (line 3, pos 5)

### wnd(i)%filename
- Changed (11):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - nbyr (line 3, pos 1)
  - tstep (line 3, pos 2)
  - lat (line 3, pos 3)
  - long (line 3, pos 4)
  - elev (line 3, pos 5)
  - iyr (line 4, pos 1)
  - istep (line 4, pos 2)
  - iyr (line 5, pos 1)
  - ...and 1 more

### wnd.cli
- Changed (3):
  - titldum (line 1, pos 1)
  - header (line 2, pos 1)
  - filename (line 3, pos 1)
