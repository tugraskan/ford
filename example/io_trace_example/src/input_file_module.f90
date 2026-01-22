!> Module defining input file names and paths for hydrological model
!! @author Example Author
!! @date 2026-01-22
module input_file_module
  implicit none
  
  !> Derived type containing all input filenames
  type :: input_files_type
    character(len=25) :: aqu = "aquifer.aqu"  !< Aquifer input file (hydraulic properties, initial conditions)
    character(len=25) :: obj = "object.cnt"   !< Object count file (number of spatial objects in simulation)
  end type input_files_type
  
  !> Global instance of input filenames
  type(input_files_type) :: in_aqu
  type(input_files_type) :: in_obj
  
contains

  !> Initialize input file names from configuration
  !! This routine can override default filenames from control file or command line
  subroutine init_input_files(config_file)
    character(len=*), intent(in), optional :: config_file  !< Optional configuration file path
    
    ! Default initialization already done in type definition
    ! This routine could read from config_file to override defaults
    
    if (present(config_file)) then
      ! Read overrides from config file (implementation omitted for brevity)
      ! Example: in_aqu%aqu might be set to "custom_aquifer.aqu"
    end if
    
  end subroutine init_input_files

end module input_file_module
