!> Main program demonstrating I/O operations
!! This program demonstrates reading from input files and writing to output files
!! @author Example Author
!! @date 2026-01-22
program io_trace_demo
  use input_file_module
  use aquifer_module
  use object_module
  use output_module
  implicit none
  
  integer :: i
  type(mgt_operation_type) :: test_op
  
  print *, "===== I/O Trace Demonstration Program ====="
  print *
  
  ! Initialize input file names
  print *, "Initializing input file names..."
  call init_input_files()
  print *, "  Aquifer input file: ", trim(in_aqu%aqu)
  print *, "  Object count file:  ", trim(in_obj%obj)
  print *
  
  ! Read aquifer data
  print *, "Reading aquifer data from ", trim(in_aqu%aqu), "..."
  call aqu_read()
  print *, "  Successfully read", num_aquifers, "aquifers"
  
  ! Display aquifer information
  do i = 1, num_aquifers
    print *, "  Aquifer", i, ":", trim(aqudb(i)%name)
    print *, "    Area:", aqudb(i)%area, "ha"
    print *, "    Hydraulic conductivity:", aqudb(i)%hydraulic_cond, "m/day"
    print *, "    Initial storage:", aqudb(i)%initial_storage, "m^3"
  end do
  print *
  
  ! Read object counts
  print *, "Reading object counts from ", trim(in_obj%obj), "..."
  call object_cnt_read()
  print *, "  Subbasins:", obj_cnt%subbasins
  print *, "  HRUs:", obj_cnt%hrus
  print *, "  Aquifers:", obj_cnt%aquifers
  print *, "  Channels:", obj_cnt%channels
  print *, "  Reservoirs:", obj_cnt%reservoirs
  print *, "  Point sources:", obj_cnt%point_sources
  print *
  
  ! Initialize output files
  print *, "Initializing output files..."
  call output_init()
  print *, "  Management output: ", trim(out_files%mgt)
  print *, "  Aquifer output:    ", trim(out_files%aquifer)
  print *
  
  ! Write sample management operation
  print *, "Writing sample management operation..."
  test_op%year = 2024
  test_op%day = 100
  test_op%hru_id = 1
  test_op%op_type = "IRRIGATE"
  test_op%amount = 50.0
  call write_mgt_operation(test_op)
  print *, "  Written: IRRIGATE operation on day 100"
  print *
  
  ! Write aquifer output for all aquifers
  print *, "Writing aquifer output for day 1..."
  do i = 1, num_aquifers
    call write_aquifer_output(2024, 1, i)
  end do
  print *, "  Written output for", num_aquifers, "aquifers"
  print *
  
  ! Close output files
  print *, "Closing output files..."
  call output_close()
  print *
  
  print *, "===== Demonstration Complete ====="
  print *, "Check mgt.out and aquifer.out for results"
  
end program io_trace_demo
