!! This module handles Hydrologic Response Unit (HRU) data processing
!! for the SWAT+ model
module hru_module
  implicit none
  
  !! Maximum number of HRUs
  integer, parameter :: max_hrus = 10000
  
  !! HRU data structure
  type :: hru_type
    integer :: id              !! HRU identification number
    real :: area               !! HRU area in hectares
    real :: slope              !! Average slope in percent
    integer :: soil_type       !! Soil type code
    integer :: land_use        !! Land use classification
  end type hru_type
  
contains

  !! Read HRU data from input file
  !! @param filename Path to HRU data file
  !! @param hru_array Array to store HRU data
  !! @param num_hrus Number of HRUs read
  subroutine read_hru_data(filename, hru_array, num_hrus)
    character(len=*), intent(in) :: filename
    type(hru_type), intent(out) :: hru_array(:)
    integer, intent(out) :: num_hrus
    
    integer :: unit_num, i, io_status
    
    ! Open input file
    unit_num = 10
    open(unit=unit_num, file=filename, status='old', action='read', iostat=io_status)
    
    if (io_status /= 0) then
      print *, "Error opening file: ", filename
      num_hrus = 0
      return
    end if
    
    ! Read HRU data
    num_hrus = 0
    do i = 1, size(hru_array)
      read(unit_num, *, iostat=io_status) hru_array(i)%id, &
                                           hru_array(i)%area, &
                                           hru_array(i)%slope, &
                                           hru_array(i)%soil_type, &
                                           hru_array(i)%land_use
      if (io_status /= 0) exit
      num_hrus = num_hrus + 1
    end do
    
    close(unit_num)
    
  end subroutine read_hru_data
  
  !! Calculate total watershed area
  !! @param hru_array Array of HRU data
  !! @param num_hrus Number of HRUs
  !! @return Total area in hectares
  function calculate_total_area(hru_array, num_hrus) result(total_area)
    type(hru_type), intent(in) :: hru_array(:)
    integer, intent(in) :: num_hrus
    real :: total_area
    
    integer :: i
    
    total_area = 0.0
    do i = 1, num_hrus
      total_area = total_area + hru_array(i)%area
    end do
    
  end function calculate_total_area

end module hru_module
