# I/O Trace Documentation: Aquifer Model File Operations

This document provides a comprehensive analysis of all I/O operations involving the four target files in the example hydrological model:
- `aquifer.aqu` (input)
- `object.cnt` (input)
- `mgt.out` (output)
- `aquifer.out` (output)

---

## 1. Filename Resolution Map

### 1.1 aquifer.aqu

**Target filename:** `aquifer.aqu`

**Resolution chain:**
- **Expression:** `in_aqu%aqu`
- **Type:** Component of `input_files_type` derived type
- **Default value:** `"aquifer.aqu"` (character(len=25))
- **Defined at:** `example/io_trace_example/src/input_file_module.f90:9`
- **Instance declaration:** `example/io_trace_example/src/input_file_module.f90:14`
- **Potential override:** `example/io_trace_example/src/input_file_module.f90:24-28` (via `init_input_files` subroutine)

**Usage sites:**
- Read operations in `aqu_read`: `example/io_trace_example/src/aquifer_module.f90:20-57`

---

### 1.2 object.cnt

**Target filename:** `object.cnt`

**Resolution chain:**
- **Expression:** `in_obj%obj`
- **Type:** Component of `input_files_type` derived type
- **Default value:** `"object.cnt"` (character(len=25))
- **Defined at:** `example/io_trace_example/src/input_file_module.f90:10`
- **Instance declaration:** `example/io_trace_example/src/input_file_module.f90:14`
- **Potential override:** `example/io_trace_example/src/input_file_module.f90:24-28` (via `init_input_files` subroutine)

**Usage sites:**
- Read operations in `object_cnt_read`: `example/io_trace_example/src/object_module.f90:28-50`

---

### 1.3 mgt.out

**Target filename:** `mgt.out`

**Resolution chain:**
- **Expression:** `out_files%mgt`
- **Type:** Component of `output_files_type` derived type
- **Default value:** `"mgt.out"` (character(len=25))
- **Defined at:** `example/io_trace_example/src/output_module.f90:10`
- **Instance declaration:** `example/io_trace_example/src/output_module.f90:15`
- **No runtime override:** Default value used throughout execution

**Usage sites:**
- Opened in `output_init`: `example/io_trace_example/src/output_module.f90:28`
- Written in `write_mgt_operation`: `example/io_trace_example/src/output_module.f90:45`
- Closed in `output_close`: `example/io_trace_example/src/output_module.f90:80`

---

### 1.4 aquifer.out

**Target filename:** `aquifer.out`

**Resolution chain:**
- **Expression:** `out_files%aquifer`
- **Type:** Component of `output_files_type` derived type
- **Default value:** `"aquifer.out"` (character(len=25))
- **Defined at:** `example/io_trace_example/src/output_module.f90:11`
- **Instance declaration:** `example/io_trace_example/src/output_module.f90:15`
- **No runtime override:** Default value used throughout execution

**Usage sites:**
- Opened in `output_init`: `example/io_trace_example/src/output_module.f90:34`
- Written in `write_aquifer_output`: `example/io_trace_example/src/output_module.f90:72`
- Closed in `output_close`: `example/io_trace_example/src/output_module.f90:83`

---

## 2. I/O Sites and Unit Mappings

### 2.1 aquifer.aqu

#### Routine: aqu_read
**Location:** `example/io_trace_example/src/aquifer_module.f90:20-57`

**File expression:** `in_aqu%aqu` → `"aquifer.aqu"`

**Unit mapping:** Unit 107 → `in_aqu%aqu` → `aquifer.aqu`

**I/O Sites:**

1. **inquire** — `example/io_trace_example/src/aquifer_module.f90:26`
   ```fortran
   inquire(file=in_aqu%aqu, exist=file_exists)
   ```

2. **open** — `example/io_trace_example/src/aquifer_module.f90:32`
   ```fortran
   open(unit=107, file=in_aqu%aqu, status='old', action='read')
   ```

3. **read (header)** — `example/io_trace_example/src/aquifer_module.f90:35`
   ```fortran
   read(107, *)
   ```

4. **read (num_aquifers)** — `example/io_trace_example/src/aquifer_module.f90:38`
   ```fortran
   read(107, *) num_aquifers
   ```

5. **read (aquifer records)** — `example/io_trace_example/src/aquifer_module.f90:47`
   ```fortran
   read(107, *, iostat=eof) k, aqudb(i)
   ```

6. **close** — `example/io_trace_example/src/aquifer_module.f90:55`
   ```fortran
   close(107)
   ```

---

### 2.2 object.cnt

#### Routine: object_cnt_read
**Location:** `example/io_trace_example/src/object_module.f90:28-50`

**File expression:** `in_obj%obj` → `"object.cnt"`

**Unit mapping:** Unit 108 → `in_obj%obj` → `object.cnt`

**I/O Sites:**

1. **open** — `example/io_trace_example/src/object_module.f90:32`
   ```fortran
   open(unit=108, file=in_obj%obj, status='old', action='read', iostat=ios)
   ```

2. **read (header)** — `example/io_trace_example/src/object_module.f90:39`
   ```fortran
   read(108, *)
   ```

3. **read (subbasins)** — `example/io_trace_example/src/object_module.f90:42`
   ```fortran
   read(108, *) obj_cnt%subbasins
   ```

4. **read (hrus)** — `example/io_trace_example/src/object_module.f90:43`
   ```fortran
   read(108, *) obj_cnt%hrus
   ```

5. **read (aquifers)** — `example/io_trace_example/src/object_module.f90:44`
   ```fortran
   read(108, *) obj_cnt%aquifers
   ```

6. **read (channels)** — `example/io_trace_example/src/object_module.f90:45`
   ```fortran
   read(108, *) obj_cnt%channels
   ```

7. **read (reservoirs)** — `example/io_trace_example/src/object_module.f90:46`
   ```fortran
   read(108, *) obj_cnt%reservoirs
   ```

8. **read (point_sources)** — `example/io_trace_example/src/object_module.f90:47`
   ```fortran
   read(108, *) obj_cnt%point_sources
   ```

9. **close** — `example/io_trace_example/src/object_module.f90:50`
   ```fortran
   close(108)
   ```

---

### 2.3 mgt.out

#### Routine: output_init
**Location:** `example/io_trace_example/src/output_module.f90:24-37`

**File expression:** `out_files%mgt` → `"mgt.out"`

**Unit mapping:** Unit 201 → `out_files%mgt` → `mgt.out`

**I/O Sites:**

1. **open** — `example/io_trace_example/src/output_module.f90:28`
   ```fortran
   open(unit=201, file=out_files%mgt, status='replace', action='write')
   ```

2. **write (header)** — `example/io_trace_example/src/output_module.f90:31`
   ```fortran
   write(201, '(a)') "YEAR  DAY  HRU_ID  OPERATION  AMOUNT"
   ```

#### Routine: write_mgt_operation
**Location:** `example/io_trace_example/src/output_module.f90:41-48`

**I/O Sites:**

3. **write (data record)** — `example/io_trace_example/src/output_module.f90:45`
   ```fortran
   write(201, '(i5, i5, i8, 2x, a16, f12.3)') &
     mgt_op%year, mgt_op%day, mgt_op%hru_id, mgt_op%op_type, mgt_op%amount
   ```

#### Routine: output_close
**Location:** `example/io_trace_example/src/output_module.f90:77-86`

**I/O Sites:**

4. **close** — `example/io_trace_example/src/output_module.f90:80`
   ```fortran
   close(201)
   ```

---

### 2.4 aquifer.out

#### Routine: output_init
**Location:** `example/io_trace_example/src/output_module.f90:24-37`

**File expression:** `out_files%aquifer` → `"aquifer.out"`

**Unit mapping:** Unit 202 → `out_files%aquifer` → `aquifer.out`

**I/O Sites:**

1. **open** — `example/io_trace_example/src/output_module.f90:34`
   ```fortran
   open(unit=202, file=out_files%aquifer, status='replace', action='write')
   ```

2. **write (header)** — `example/io_trace_example/src/output_module.f90:37`
   ```fortran
   write(202, '(a)') "YEAR  DAY  AQU_ID  AQU_NAME  STORAGE_M3  SEEPAGE_M3  REVAP_M3  RECHARGE_M3"
   ```

#### Routine: write_aquifer_output
**Location:** `example/io_trace_example/src/output_module.f90:52-75`

**I/O Sites:**

3. **write (data record)** — `example/io_trace_example/src/output_module.f90:72`
   ```fortran
   write(202, '(i5, i5, i5, 2x, a16, 4f15.3)') &
     year, day, aqu_id, aqudb(aqu_id)%name, &
     storage, seepage, revap, recharge
   ```

#### Routine: output_close
**Location:** `example/io_trace_example/src/output_module.f90:77-86`

**I/O Sites:**

4. **close** — `example/io_trace_example/src/output_module.f90:83`
   ```fortran
   close(202)
   ```

---

## 3. Read/Write Payload Map

### 3.1 aquifer.aqu (Input)

#### READ in aqu_read — `example/io_trace_example/src/aquifer_module.f90:35`
**Statement:**
```fortran
read(107, *)
```
**Purpose:** Skip header line (column names)

**Payload:** None (format-free skip)

---

#### READ in aqu_read — `example/io_trace_example/src/aquifer_module.f90:38`
**Statement:**
```fortran
read(107, *) num_aquifers
```

**Payload items:**

##### Variable: num_aquifers

- **Name:** `num_aquifers`
- **Scope:** Module variable (from `aquifer_database`)
- **Declaration:** `integer :: num_aquifers = 0`
- **Type/Kind:** Integer, default kind
- **Dimensions:** Scalar
- **Default:** 0
- **Units:** Count (dimensionless)
- **Description:** Number of aquifers in the simulation
- **Declared at:** `example/io_trace_example/src/aquifer_database.f90:21`

---

#### READ in aqu_read — `example/io_trace_example/src/aquifer_module.f90:47`
**Statement:**
```fortran
read(107, *, iostat=eof) k, aqudb(i)
```

**Payload items (in order):**

##### 1. Variable: k

- **Name:** `k`
- **Scope:** Local variable (declared in `aqu_read`)
- **Declaration:** `integer :: k`
- **Type/Kind:** Integer, default kind
- **Dimensions:** Scalar
- **Default:** Undefined (not initialized)
- **Units:** Index (dimensionless)
- **Description:** Counter/index variable for aquifer record number
- **Declared at:** `example/io_trace_example/src/aquifer_module.f90:14`

##### 2. Variable: aqudb(i)

- **Name/Expression:** `aqudb(i)` (array element access)
- **Scope:** Module variable, allocated array (from `aquifer_database`)
- **Declaration:** `type(aquifer_db_type), allocatable :: aqudb(:)`
- **Type:** Derived type `aquifer_db_type`
- **Dimensions:** 1D allocatable array, indexed by `i`
- **Default:** Not initialized until read
- **Declared at:** `example/io_trace_example/src/aquifer_database.f90:19`

**Derived Type: aquifer_db_type**

- **Type name:** `aquifer_db_type`
- **Defined at:** `example/io_trace_example/src/aquifer_database.f90:8-17`
- **Has user-defined I/O:** No (uses Fortran list-directed I/O)

**Components (in declaration order):**

1. **name**
   - Type: `character(len=16)`
   - Default: `""` (empty string)
   - Units: N/A (text identifier)
   - Description: Aquifer name/ID
   - Location: `example/io_trace_example/src/aquifer_database.f90:9`

2. **area**
   - Type: `real` (default kind)
   - Default: `0.0`
   - Units: hectares [ha]
   - Description: Surface area
   - Location: `example/io_trace_example/src/aquifer_database.f90:10`

3. **hydraulic_cond**
   - Type: `real` (default kind)
   - Default: `0.0`
   - Units: meters per day [m/day]
   - Description: Hydraulic conductivity
   - Location: `example/io_trace_example/src/aquifer_database.f90:11`

4. **specific_yield**
   - Type: `real` (default kind)
   - Default: `0.0`
   - Units: dimensionless (0-1)
   - Description: Specific yield
   - Location: `example/io_trace_example/src/aquifer_database.f90:12`

5. **alpha**
   - Type: `real` (default kind)
   - Default: `0.0`
   - Units: per day [1/day]
   - Description: Baseflow recession coefficient
   - Location: `example/io_trace_example/src/aquifer_database.f90:13`

6. **initial_storage**
   - Type: `real` (default kind)
   - Default: `0.0`
   - Units: cubic meters [m^3]
   - Description: Initial water storage
   - Location: `example/io_trace_example/src/aquifer_database.f90:14`

7. **min_storage**
   - Type: `real` (default kind)
   - Default: `0.0`
   - Units: cubic meters [m^3]
   - Description: Minimum storage threshold
   - Location: `example/io_trace_example/src/aquifer_database.f90:15`

8. **max_storage**
   - Type: `real` (default kind)
   - Default: `0.0`
   - Units: cubic meters [m^3]
   - Description: Maximum storage capacity
   - Location: `example/io_trace_example/src/aquifer_database.f90:16`

**I/O Mapping:** Since no user-defined I/O is specified, Fortran's list-directed I/O reads components in declaration order. Each `read(107, *, iostat=eof) k, aqudb(i)` statement reads:
1. An integer value into `k`
2. A string into `aqudb(i)%name`
3. A real value into `aqudb(i)%area`
4. A real value into `aqudb(i)%hydraulic_cond`
5. A real value into `aqudb(i)%specific_yield`
6. A real value into `aqudb(i)%alpha`
7. A real value into `aqudb(i)%initial_storage`
8. A real value into `aqudb(i)%min_storage`
9. A real value into `aqudb(i)%max_storage`

---

### 3.2 object.cnt (Input)

#### READ in object_cnt_read — `example/io_trace_example/src/object_module.f90:39`
**Statement:**
```fortran
read(108, *)
```
**Purpose:** Skip header line

**Payload:** None (format-free skip)

---

#### READ in object_cnt_read — `example/io_trace_example/src/object_module.f90:42`
**Statement:**
```fortran
read(108, *) obj_cnt%subbasins
```

**Payload items:**

##### Variable: obj_cnt%subbasins

- **Name:** `obj_cnt%subbasins`
- **Scope:** Module variable component (from `object_module`)
- **Parent type:** `object_count_type`
- **Declaration:** `integer :: subbasins = 0`
- **Type/Kind:** Integer, default kind
- **Dimensions:** Scalar
- **Default:** 0
- **Units:** Count (dimensionless)
- **Description:** Number of subbasins
- **Component declared at:** `example/io_trace_example/src/object_module.f90:10`
- **Instance declared at:** `example/io_trace_example/src/object_module.f90:17`

---

#### READ in object_cnt_read — `example/io_trace_example/src/object_module.f90:43`
**Statement:**
```fortran
read(108, *) obj_cnt%hrus
```

**Payload items:**

##### Variable: obj_cnt%hrus

- **Name:** `obj_cnt%hrus`
- **Scope:** Module variable component
- **Parent type:** `object_count_type`
- **Declaration:** `integer :: hrus = 0`
- **Type/Kind:** Integer, default kind
- **Dimensions:** Scalar
- **Default:** 0
- **Units:** Count (dimensionless)
- **Description:** Number of hydrologic response units
- **Component declared at:** `example/io_trace_example/src/object_module.f90:11`
- **Instance declared at:** `example/io_trace_example/src/object_module.f90:17`

---

#### READ in object_cnt_read — `example/io_trace_example/src/object_module.f90:44`
**Statement:**
```fortran
read(108, *) obj_cnt%aquifers
```

**Payload items:**

##### Variable: obj_cnt%aquifers

- **Name:** `obj_cnt%aquifers`
- **Scope:** Module variable component
- **Parent type:** `object_count_type`
- **Declaration:** `integer :: aquifers = 0`
- **Type/Kind:** Integer, default kind
- **Dimensions:** Scalar
- **Default:** 0
- **Units:** Count (dimensionless)
- **Description:** Number of aquifers
- **Component declared at:** `example/io_trace_example/src/object_module.f90:12`
- **Instance declared at:** `example/io_trace_example/src/object_module.f90:17`

---

#### READ in object_cnt_read — `example/io_trace_example/src/object_module.f90:45`
**Statement:**
```fortran
read(108, *) obj_cnt%channels
```

**Payload items:**

##### Variable: obj_cnt%channels

- **Name:** `obj_cnt%channels`
- **Scope:** Module variable component
- **Parent type:** `object_count_type`
- **Declaration:** `integer :: channels = 0`
- **Type/Kind:** Integer, default kind
- **Dimensions:** Scalar
- **Default:** 0
- **Units:** Count (dimensionless)
- **Description:** Number of stream channels
- **Component declared at:** `example/io_trace_example/src/object_module.f90:13`
- **Instance declared at:** `example/io_trace_example/src/object_module.f90:17`

---

#### READ in object_cnt_read — `example/io_trace_example/src/object_module.f90:46`
**Statement:**
```fortran
read(108, *) obj_cnt%reservoirs
```

**Payload items:**

##### Variable: obj_cnt%reservoirs

- **Name:** `obj_cnt%reservoirs`
- **Scope:** Module variable component
- **Parent type:** `object_count_type`
- **Declaration:** `integer :: reservoirs = 0`
- **Type/Kind:** Integer, default kind
- **Dimensions:** Scalar
- **Default:** 0
- **Units:** Count (dimensionless)
- **Description:** Number of reservoirs
- **Component declared at:** `example/io_trace_example/src/object_module.f90:14`
- **Instance declared at:** `example/io_trace_example/src/object_module.f90:17`

---

#### READ in object_cnt_read — `example/io_trace_example/src/object_module.f90:47`
**Statement:**
```fortran
read(108, *) obj_cnt%point_sources
```

**Payload items:**

##### Variable: obj_cnt%point_sources

- **Name:** `obj_cnt%point_sources`
- **Scope:** Module variable component
- **Parent type:** `object_count_type`
- **Declaration:** `integer :: point_sources = 0`
- **Type/Kind:** Integer, default kind
- **Dimensions:** Scalar
- **Default:** 0
- **Units:** Count (dimensionless)
- **Description:** Number of point source inputs
- **Component declared at:** `example/io_trace_example/src/object_module.f90:15`
- **Instance declared at:** `example/io_trace_example/src/object_module.f90:17`

---

### 3.3 mgt.out (Output)

#### WRITE in output_init — `example/io_trace_example/src/output_module.f90:31`
**Statement:**
```fortran
write(201, '(a)') "YEAR  DAY  HRU_ID  OPERATION  AMOUNT"
```

**Payload items:**

- **Literal string:** Header text for management output file
- **Format:** Character string with column labels

---

#### WRITE in write_mgt_operation — `example/io_trace_example/src/output_module.f90:45-46`
**Statement:**
```fortran
write(201, '(i5, i5, i8, 2x, a16, f12.3)') &
  mgt_op%year, mgt_op%day, mgt_op%hru_id, mgt_op%op_type, mgt_op%amount
```

**Payload items (in order):**

##### 1. Variable: mgt_op%year

- **Name:** `mgt_op%year`
- **Scope:** Dummy argument component (intent(in))
- **Parent variable:** `mgt_op` (type `mgt_operation_type`)
- **Declaration:** `integer :: year = 0`
- **Type/Kind:** Integer, default kind
- **Dimensions:** Scalar
- **Default:** 0
- **Units:** Year (YYYY)
- **Description:** Simulation year
- **Component declared at:** `example/io_trace_example/src/output_module.f90:19`
- **Argument declared at:** `example/io_trace_example/src/output_module.f90:42`

##### 2. Variable: mgt_op%day

- **Name:** `mgt_op%day`
- **Scope:** Dummy argument component (intent(in))
- **Parent variable:** `mgt_op`
- **Declaration:** `integer :: day = 0`
- **Type/Kind:** Integer, default kind
- **Dimensions:** Scalar
- **Default:** 0
- **Units:** Day of year (1-365/366)
- **Description:** Day of year
- **Component declared at:** `example/io_trace_example/src/output_module.f90:20`

##### 3. Variable: mgt_op%hru_id

- **Name:** `mgt_op%hru_id`
- **Scope:** Dummy argument component (intent(in))
- **Parent variable:** `mgt_op`
- **Declaration:** `integer :: hru_id = 0`
- **Type/Kind:** Integer, default kind
- **Dimensions:** Scalar
- **Default:** 0
- **Units:** ID number (dimensionless)
- **Description:** HRU identifier
- **Component declared at:** `example/io_trace_example/src/output_module.f90:21`

##### 4. Variable: mgt_op%op_type

- **Name:** `mgt_op%op_type`
- **Scope:** Dummy argument component (intent(in))
- **Parent variable:** `mgt_op`
- **Declaration:** `character(len=16) :: op_type = ""`
- **Type/Kind:** Character, length 16
- **Dimensions:** Scalar string
- **Default:** `""` (empty string)
- **Units:** N/A (text identifier)
- **Description:** Operation type (e.g., "PLANT", "HARVEST", "IRRIGATE")
- **Component declared at:** `example/io_trace_example/src/output_module.f90:22`

##### 5. Variable: mgt_op%amount

- **Name:** `mgt_op%amount`
- **Scope:** Dummy argument component (intent(in))
- **Parent variable:** `mgt_op`
- **Declaration:** `real :: amount = 0.0`
- **Type/Kind:** Real, default kind
- **Dimensions:** Scalar
- **Default:** 0.0
- **Units:** Variable (depends on operation type: kg/ha for fertilizer, mm for irrigation, etc.)
- **Description:** Operation amount
- **Component declared at:** `example/io_trace_example/src/output_module.f90:23`

**Derived Type: mgt_operation_type**

- **Type name:** `mgt_operation_type`
- **Defined at:** `example/io_trace_example/src/output_module.f90:18-24`
- **Has user-defined I/O:** No
- **Purpose:** Container for management operation data to be written to output

---

### 3.4 aquifer.out (Output)

#### WRITE in output_init — `example/io_trace_example/src/output_module.f90:37`
**Statement:**
```fortran
write(202, '(a)') "YEAR  DAY  AQU_ID  AQU_NAME  STORAGE_M3  SEEPAGE_M3  REVAP_M3  RECHARGE_M3"
```

**Payload items:**

- **Literal string:** Header text for aquifer output file
- **Format:** Character string with column labels

---

#### WRITE in write_aquifer_output — `example/io_trace_example/src/output_module.f90:72-74`
**Statement:**
```fortran
write(202, '(i5, i5, i5, 2x, a16, 4f15.3)') &
  year, day, aqu_id, aqudb(aqu_id)%name, &
  storage, seepage, revap, recharge
```

**Payload items (in order):**

##### 1. Variable: year

- **Name:** `year`
- **Scope:** Dummy argument (intent(in))
- **Declaration:** `integer, intent(in) :: year`
- **Type/Kind:** Integer, default kind
- **Dimensions:** Scalar
- **Default:** N/A (must be provided by caller)
- **Units:** Year (YYYY)
- **Description:** Simulation year
- **Declared at:** `example/io_trace_example/src/output_module.f90:53`

##### 2. Variable: day

- **Name:** `day`
- **Scope:** Dummy argument (intent(in))
- **Declaration:** `integer, intent(in) :: day`
- **Type/Kind:** Integer, default kind
- **Dimensions:** Scalar
- **Default:** N/A (must be provided by caller)
- **Units:** Day of year (1-365/366)
- **Description:** Day of year
- **Declared at:** `example/io_trace_example/src/output_module.f90:54`

##### 3. Variable: aqu_id

- **Name:** `aqu_id`
- **Scope:** Dummy argument (intent(in))
- **Declaration:** `integer, intent(in) :: aqu_id`
- **Type/Kind:** Integer, default kind
- **Dimensions:** Scalar
- **Default:** N/A (must be provided by caller)
- **Units:** Index (dimensionless)
- **Description:** Aquifer index
- **Declared at:** `example/io_trace_example/src/output_module.f90:55`

##### 4. Variable: aqudb(aqu_id)%name

- **Name/Expression:** `aqudb(aqu_id)%name`
- **Scope:** Module variable component (from `aquifer_database`)
- **Declaration (aqudb):** `type(aquifer_db_type), allocatable :: aqudb(:)`
- **Declaration (name component):** `character(len=16) :: name = ""`
- **Type/Kind:** Character, length 16
- **Dimensions:** Accessed from array element
- **Default:** `""` (empty string)
- **Units:** N/A (text identifier)
- **Description:** Aquifer name/ID
- **Array declared at:** `example/io_trace_example/src/aquifer_database.f90:19`
- **Component declared at:** `example/io_trace_example/src/aquifer_database.f90:9`

##### 5. Variable: storage

- **Name:** `storage`
- **Scope:** Local variable
- **Declaration:** `real :: storage`
- **Type/Kind:** Real, default kind
- **Dimensions:** Scalar
- **Default:** Computed at runtime (initialized from `aqudb(aqu_id)%initial_storage`)
- **Units:** cubic meters [m^3]
- **Description:** Current storage
- **Declared at:** `example/io_trace_example/src/output_module.f90:57`

##### 6. Variable: seepage

- **Name:** `seepage`
- **Scope:** Local variable
- **Declaration:** `real :: seepage`
- **Type/Kind:** Real, default kind
- **Dimensions:** Scalar
- **Default:** Computed at runtime
- **Units:** cubic meters [m^3]
- **Description:** Seepage loss
- **Declared at:** `example/io_trace_example/src/output_module.f90:58`

##### 7. Variable: revap

- **Name:** `revap`
- **Scope:** Local variable
- **Declaration:** `real :: revap`
- **Type/Kind:** Real, default kind
- **Dimensions:** Scalar
- **Default:** Computed at runtime
- **Units:** cubic meters [m^3]
- **Description:** Revaporation
- **Declared at:** `example/io_trace_example/src/output_module.f90:59`

##### 8. Variable: recharge

- **Name:** `recharge`
- **Scope:** Local variable
- **Declaration:** `real :: recharge`
- **Type/Kind:** Real, default kind
- **Dimensions:** Scalar
- **Default:** Computed at runtime
- **Units:** cubic meters [m^3]
- **Description:** Groundwater recharge
- **Declared at:** `example/io_trace_example/src/output_module.f90:60`

---

## 4. Worked Example: aqu_read (aquifer.aqu)

This section provides a complete walkthrough of the `aqu_read` subroutine, demonstrating how aquifer data is read from `aquifer.aqu`.

### 4.1 Filename Resolution

**Filename variable:** `in_aqu%aqu`

**Definition chain:**
1. Type definition at `example/io_trace_example/src/input_file_module.f90:7-12`:
   ```fortran
   type :: input_files_type
     character(len=25) :: aqu = "aquifer.aqu"  !< Aquifer input file
     character(len=25) :: obj = "object.cnt"   !< Object count file
   end type input_files_type
   ```

2. Instance declaration at `example/io_trace_example/src/input_file_module.f90:15`:
   ```fortran
   type(input_files_type) :: in_aqu
   ```

**Default value:** `"aquifer.aqu"` is assigned when the type is instantiated.

**Potential override:** The `init_input_files` subroutine (`example/io_trace_example/src/input_file_module.f90:21-32`) can override this default at runtime by reading from a configuration file.

### 4.2 File Opening and Unit Association

**Location:** `example/io_trace_example/src/aquifer_module.f90:32`

**Statement:**
```fortran
open(unit=107, file=in_aqu%aqu, status='old', action='read')
```

**Unit number:** 107  
**File:** `in_aqu%aqu` → `"aquifer.aqu"`  
**Status:** `'old'` (file must already exist)  
**Action:** `'read'` (read-only access)

This establishes the association: **Unit 107 ↔ aquifer.aqu**

All subsequent reads using unit 107 will read from the aquifer.aqu file.

### 4.3 Read Operations

#### Read #1: Skip Header (Line 35)

**Statement:**
```fortran
read(107, *)
```

**Purpose:** Skip the first line of the file (column headers)  
**Payload:** None (list-directed skip)

---

#### Read #2: Number of Aquifers (Line 38)

**Statement:**
```fortran
read(107, *) num_aquifers
```

**Variable: num_aquifers**

- **Declared at:** `example/io_trace_example/src/aquifer_database.f90:21`
- **Declaration:**
  ```fortran
  integer :: num_aquifers = 0
  ```
- **Type:** Integer, default kind
- **Scope:** Module variable (public, available throughout program)
- **Default:** 0
- **Units:** Count (dimensionless)
- **Description:** Number of aquifers in the simulation
- **Usage:** Determines loop iteration count and array allocation size

---

#### Read #3: Aquifer Records Loop (Line 47)

**Statement:**
```fortran
read(107, *, iostat=eof) k, aqudb(i)
```

This statement is executed `num_aquifers` times (controlled by the do-loop at line 44).

**Variable 1: k**

- **Declared at:** `example/io_trace_example/src/aquifer_module.f90:15`
- **Declaration:**
  ```fortran
  integer :: k  !< Counter/index variable
  ```
- **Type:** Integer, default kind
- **Scope:** Local to subroutine `aqu_read`
- **Default:** Uninitialized
- **Units:** Index (dimensionless)
- **Description:** Counter/index variable for aquifer record number
- **Purpose:** Stores the sequential record number from the input file (may differ from array index `i`)

**Variable 2: aqudb(i)**

- **Array declared at:** `example/io_trace_example/src/aquifer_database.f90:19`
- **Array declaration:**
  ```fortran
  type(aquifer_db_type), allocatable :: aqudb(:)
  ```
- **Element type:** Derived type `aquifer_db_type`
- **Scope:** Module variable (public)
- **Allocation:** Performed at line 43: `allocate(aqudb(max_aqu))`
- **Index:** `i` (loop variable, ranges from 1 to `num_aquifers`)

### 4.4 Derived Type: aquifer_db_type

**Defined at:** `example/io_trace_example/src/aquifer_database.f90:8-17`

**Full definition:**
```fortran
type :: aquifer_db_type
  character(len=16) :: name = ""           !< Aquifer name/ID
  real :: area = 0.0                        !< Surface area [ha]
  real :: hydraulic_cond = 0.0              !< Hydraulic conductivity [m/day]
  real :: specific_yield = 0.0              !< Specific yield (dimensionless, 0-1)
  real :: alpha = 0.0                       !< Baseflow recession coefficient [1/day]
  real :: initial_storage = 0.0             !< Initial water storage [m^3]
  real :: min_storage = 0.0                 !< Minimum storage threshold [m^3]
  real :: max_storage = 0.0                 !< Maximum storage capacity [m^3]
end type aquifer_db_type
```

**User-defined I/O:** None. The type uses Fortran's default list-directed I/O.

### 4.5 Input Record to Variable Mapping

When Fortran executes:
```fortran
read(107, *, iostat=eof) k, aqudb(i)
```

The input record format is expected to be:
```
index  name  area  K  Sy  alpha  storage_init  storage_min  storage_max
```

**Mapping to variables (in order):**

1. **First field** → `k` (integer)
   - Record index number

2. **Second field** → `aqudb(i)%name` (character(len=16))
   - Aquifer name/identifier

3. **Third field** → `aqudb(i)%area` (real)
   - Surface area in hectares [ha]

4. **Fourth field** → `aqudb(i)%hydraulic_cond` (real)
   - Hydraulic conductivity in meters per day [m/day]

5. **Fifth field** → `aqudb(i)%specific_yield` (real)
   - Specific yield, dimensionless (0-1)

6. **Sixth field** → `aqudb(i)%alpha` (real)
   - Baseflow recession coefficient in per day [1/day]

7. **Seventh field** → `aqudb(i)%initial_storage` (real)
   - Initial water storage in cubic meters [m³]

8. **Eighth field** → `aqudb(i)%min_storage` (real)
   - Minimum storage threshold in cubic meters [m³]

9. **Ninth field** → `aqudb(i)%max_storage` (real)
   - Maximum storage capacity in cubic meters [m³]

**Example input record:**
```
1  Shallow_GW  250.5  2.5  0.15  0.05  10000.0  500.0  50000.0
```

This would be read as:
- `k = 1`
- `aqudb(1)%name = "Shallow_GW"`
- `aqudb(1)%area = 250.5` ha
- `aqudb(1)%hydraulic_cond = 2.5` m/day
- `aqudb(1)%specific_yield = 0.15` (dimensionless)
- `aqudb(1)%alpha = 0.05` 1/day
- `aqudb(1)%initial_storage = 10000.0` m³
- `aqudb(1)%min_storage = 500.0` m³
- `aqudb(1)%max_storage = 50000.0` m³

### 4.6 Error Handling

**IOSTAT variable:** `eof` (declared at line 16)

```fortran
integer :: eof  !< End-of-file status indicator
```

The `iostat=eof` clause captures any I/O errors:
- `eof = 0`: Successful read
- `eof < 0`: End-of-file reached
- `eof > 0`: Error occurred during read

Error check at lines 49-52:
```fortran
if (eof /= 0) then
  print *, "Error reading aquifer data at record", i
  exit
end if
```

If an error occurs, the routine prints an error message and exits the loop early.

### 4.7 File Closure

**Location:** Line 55

**Statement:**
```fortran
close(107)
```

This closes unit 107 and releases the file association with `aquifer.aqu`.

### 4.8 Complete Routine Flow Summary

1. **File existence check** (line 26): Verify `aquifer.aqu` exists
2. **Open file** (line 32): Associate unit 107 with `aquifer.aqu`
3. **Skip header** (line 35): Read and discard first line
4. **Read count** (line 38): Read total number of aquifers
5. **Allocate array** (line 43): Allocate `aqudb` to hold all aquifer data
6. **Loop** (lines 44-53): For each aquifer:
   - Read record index `k` and all aquifer properties into `aqudb(i)`
   - Check for errors
7. **Close file** (line 55): Release unit 107

**Result:** The module variable `aqudb(:)` is populated with all aquifer hydraulic properties and state variables, ready for use by the simulation model.

---

## Summary

This document has provided a comprehensive trace of all I/O operations involving the four target files:

- **aquifer.aqu**: Input file with aquifer hydraulic parameters, read by `aqu_read`
- **object.cnt**: Input file with object counts, read by `object_cnt_read`  
- **mgt.out**: Output file for management operations, written by `output_init` and `write_mgt_operation`
- **aquifer.out**: Output file for aquifer water balance, written by `output_init` and `write_aquifer_output`

Each file operation has been documented with:
- Exact source locations (file:line format)
- Variable definitions with types, defaults, units, and descriptions
- Unit number associations
- Complete I/O statement listings
- Derived type component expansions

The worked example for `aqu_read` demonstrates the level of detail required for understanding how Fortran I/O operations map input file records to program variables, including the automatic component-by-component reading of derived types using list-directed I/O.
