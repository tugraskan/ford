!> Module for reading and managing aquifer data
!! @author Example Author
!! @date 2026-01-22
module aquifer_module
  use input_file_module
  use aquifer_database
  implicit none
  
contains

  !> Read aquifer parameters from aquifer.aqu file
  !! This subroutine reads hydraulic properties for all aquifers
  !! File format: Header lines followed by one record per aquifer
  !! Each record contains: name, area, K, Sy, alpha, storage_init, storage_min, storage_max
  subroutine aqu_read
    integer :: i                  !< Loop counter for aquifers
    integer :: k                  !< Counter/index variable
    integer :: eof                !< End-of-file status indicator
    integer :: max_aqu            !< Maximum number of aquifers to allocate
    logical :: file_exists        !< File existence check flag
    
    ! Inquire if file exists before opening
    inquire(file=in_aqu%aqu, exist=file_exists)
    if (.not. file_exists) then
      print *, "Warning: ", trim(in_aqu%aqu), " not found"
      return
    end if
    
    ! Open aquifer input file on unit 107
    open(unit=107, file=in_aqu%aqu, status='old', action='read')
    
    ! Read header line (skip first line with column names)
    read(107, *)
    
    ! Read number of aquifers from second line
    read(107, *) num_aquifers
    
    ! Allocate aquifer database array
    max_aqu = num_aquifers
    allocate(aqudb(max_aqu))
    
    ! Read each aquifer record
    do i = 1, num_aquifers
      ! Read aquifer index and database entry
      ! Format: k, name, area, hydraulic_cond, specific_yield, alpha, 
      !         initial_storage, min_storage, max_storage
      read(107, *, iostat=eof) k, aqudb(i)
      
      if (eof /= 0) then
        print *, "Error reading aquifer data at record", i
        exit
      end if
    end do
    
    ! Close the file
    close(107)
    
  end subroutine aqu_read

end module aquifer_module
