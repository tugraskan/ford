!> Test module for code folding
module folding_test
  implicit none
  
contains

  !> Test subroutine with nested blocks
  subroutine test_nested()
    integer :: i, j, k
    
    ! Test nested do loops
    do i = 1, 10
      print *, "Outer loop:", i
      
      do j = 1, 5
        print *, "  Inner loop:", j
        
        if (j > 2) then
          print *, "    j is greater than 2"
        else
          print *, "    j is not greater than 2"
        end if
      end do
    end do
    
    ! Test select case
    select case (i)
      case (1)
        print *, "One"
      case (2)
        print *, "Two"
      case (3:5)
        print *, "Three to Five"
      case default
        print *, "Other"
    end select
    
    ! Test if with multiple branches
    if (i < 5) then
      print *, "Less than 5"
    else if (i == 5) then
      print *, "Equal to 5"
    else
      print *, "Greater than 5"
    end if
    
  end subroutine test_nested

end module folding_test
