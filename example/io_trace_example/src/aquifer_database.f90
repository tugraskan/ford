!> Module defining aquifer database structures
!! @author Example Author
!! @date 2026-01-22
module aquifer_database
  implicit none
  
  !> Aquifer hydraulic properties and state variables
  !! This type stores all parameters for a single aquifer
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
  
  !> Array of all aquifers in the simulation
  type(aquifer_db_type), allocatable :: aqudb(:)
  
  !> Number of aquifers
  integer :: num_aquifers = 0
  
end module aquifer_database
