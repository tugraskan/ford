!> Module for writing model output files
!! @author Example Author
!! @date 2026-01-22
module output_module
  use aquifer_database
  implicit none
  
  !> Output file names
  type :: output_files_type
    character(len=25) :: mgt = "mgt.out"          !< Management operations output
    character(len=25) :: aquifer = "aquifer.out"  !< Aquifer water balance output
  end type output_files_type
  
  !> Global output file names
  type(output_files_type) :: out_files
  
  !> Management operation data for output
  type :: mgt_operation_type
    integer :: year = 0         !< Simulation year
    integer :: day = 0          !< Day of year
    integer :: hru_id = 0       !< HRU identifier
    character(len=16) :: op_type = ""  !< Operation type (e.g., "PLANT", "HARVEST", "IRRIGATE")
    real :: amount = 0.0        !< Operation amount (units vary by operation)
  end type mgt_operation_type
  
contains

  !> Initialize output files and write headers
  subroutine output_init
    
    ! Open management output file on unit 201
    open(unit=201, file=out_files%mgt, status='replace', action='write')
    
    ! Write header for mgt.out
    write(201, '(a)') "YEAR  DAY  HRU_ID  OPERATION  AMOUNT"
    
    ! Open aquifer output file on unit 202
    open(unit=202, file=out_files%aquifer, status='replace', action='write')
    
    ! Write header for aquifer.out
    write(202, '(a)') "YEAR  DAY  AQU_ID  AQU_NAME  STORAGE_M3  SEEPAGE_M3  REVAP_M3  RECHARGE_M3"
    
  end subroutine output_init
  
  !> Write management operation to mgt.out
  !! @param mgt_op Management operation data structure
  !! @note Unit 201 must be opened via output_init before calling this routine
  subroutine write_mgt_operation(mgt_op)
    type(mgt_operation_type), intent(in) :: mgt_op  !< Management operation to write
    
    ! Write management operation record
    write(201, '(i5, i5, i8, 2x, a16, f12.3)') &
      mgt_op%year, mgt_op%day, mgt_op%hru_id, mgt_op%op_type, mgt_op%amount
    
  end subroutine write_mgt_operation
  
  !> Write daily aquifer water balance to aquifer.out
  !! @param year Simulation year
  !! @param day Day of year
  !! @param aqu_id Aquifer index
  !! @note Unit 202 must be opened via output_init before calling this routine
  subroutine write_aquifer_output(year, day, aqu_id)
    integer, intent(in) :: year     !< Simulation year
    integer, intent(in) :: day      !< Day of year
    integer, intent(in) :: aqu_id   !< Aquifer index
    
    real :: storage      !< Current storage [m^3]
    real :: seepage      !< Seepage loss [m^3]
    real :: revap        !< Revaporation [m^3]
    real :: recharge     !< Groundwater recharge [m^3]
    
    ! These would normally be calculated by the model
    ! Here we just use placeholder values from the database
    storage = aqudb(aqu_id)%initial_storage
    seepage = 0.0
    revap = 0.0
    recharge = 0.0
    
    ! Write aquifer output record
    write(202, '(i5, i5, i5, 2x, a16, 4f15.3)') &
      year, day, aqu_id, aqudb(aqu_id)%name, &
      storage, seepage, revap, recharge
    
  end subroutine write_aquifer_output
  
  !> Close all output files
  subroutine output_close
    
    ! Close management output file
    close(201)
    
    ! Close aquifer output file
    close(202)
    
  end subroutine output_close

end module output_module
