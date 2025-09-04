module test_module
  !! Test module with procedures that have local variables and I/O operations
  use iso_fortran_env, only: output_unit
  implicit none
  
  integer, parameter :: dp = selected_real_kind(15, 307)
  
contains

  subroutine test_io_procedure(filename, num_records)
    !! Subroutine that demonstrates I/O operations and local variables
    character(len=*), intent(in) :: filename
    !! Name of the file to write
    integer, intent(in) :: num_records
    !! Number of records to write
    
    ! Local variables
    integer :: unit_num = 10
    integer :: i, j
    real(dp) :: local_var = 3.14159
    character(len=100) :: buffer
    logical :: file_exists
    
    ! Check if file exists
    inquire(file=filename, exist=file_exists)
    
    ! Open file for writing
    open(unit=unit_num, file=filename, status='unknown', action='write')
    
    ! Write header
    write(unit_num, '(A)') 'Test data file'
    write(unit_num, '(A,I0)') 'Number of records: ', num_records
    
    ! Write data records
    do i = 1, num_records
      do j = 1, 3
        local_var = local_var + real(i*j, dp)
      end do
      write(unit_num, '(I5,F15.6)') i, local_var
    end do
    
    ! Close file
    close(unit_num)
    
    ! Write status to output
    write(output_unit, '(A,A)') 'Wrote data to file: ', filename
    
  end subroutine test_io_procedure

end module test_module