
      subroutine test_procedure
      use input_file_module
      use basin_module, only: pco, wb_bsn
      use time_module
      implicit none
      
      character(len=16) :: name
      integer :: unit_num = 107
      
      open(unit_num, file='test.dat')
      read(unit_num, *) name
      write(unit_num, '(A)') 'Hello'
      close(unit_num)
      
      end subroutine test_procedure
