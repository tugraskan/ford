      subroutine test_variable_defaults
      
      implicit none
       
      character (len=100) :: filename = "" !              |filename
      integer :: unit_num = 107            !              |unit number
      integer :: eof = 0                   !              |end of file
      logical :: i_exist                   !              |check to determine if file exists
       
      ! Set default file names
      filename = "test_data.txt"
      
      eof = 0

      !! read test data
      inquire (file=filename, exist=i_exist)
      if (i_exist) then
        open (107,file=filename)
        read (107,*,iostat=eof) unit_num
        if (eof < 0) then
          write(*,*) 'End of file reached'
        end if
        close (107)
      end if
       
      end subroutine test_variable_defaults