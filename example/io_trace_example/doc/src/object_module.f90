!> Module for reading object counts
!! @author Example Author
!! @date 2026-01-22
module object_module
  use input_file_module
  implicit none
  
  !> Derived type for object counts in the simulation domain
  type :: object_count_type
    integer :: subbasins = 0      !< Number of subbasins
    integer :: hrus = 0           !< Number of hydrologic response units
    integer :: aquifers = 0       !< Number of aquifers
    integer :: channels = 0       !< Number of stream channels
    integer :: reservoirs = 0     !< Number of reservoirs
    integer :: point_sources = 0  !< Number of point source inputs
  end type object_count_type
  
  !> Global object counts
  type(object_count_type) :: obj_cnt
  
contains

  !> Read object counts from object.cnt file
  !! This file defines the size of various spatial objects
  subroutine object_cnt_read
    integer :: ios  !< I/O status code
    
    ! Open object count file on unit 108
    open(unit=108, file=in_obj%obj, status='old', action='read', iostat=ios)
    
    if (ios /= 0) then
      print *, "Error opening", trim(in_obj%obj)
      return
    end if
    
    ! Read header
    read(108, *)
    
    ! Read object counts - each on a separate line with label
    read(108, *) obj_cnt%subbasins
    read(108, *) obj_cnt%hrus
    read(108, *) obj_cnt%aquifers
    read(108, *) obj_cnt%channels
    read(108, *) obj_cnt%reservoirs
    read(108, *) obj_cnt%point_sources
    
    ! Close file
    close(108)
    
  end subroutine object_cnt_read

end module object_module
