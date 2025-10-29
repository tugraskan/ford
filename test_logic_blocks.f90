module test_logic_module
  implicit none
contains

  subroutine test_logic_blocks(x, y, z)
    !! Test subroutine with various control flow structures
    integer, intent(in) :: x
    !! Input value
    integer, intent(inout) :: y
    !! Value to modify
    integer, intent(out) :: z
    !! Output value
    integer :: i
    
    ! Simple IF-THEN
    if (x > 0) then
      y = y + 1
    end if
    
    ! IF-THEN-ELSE
    if (x > 10) then
      y = y * 2
    else
      y = y + 5
    end if
    
    ! DO loop
    do i = 1, x
      z = z + i
    end do
    
    ! SELECT CASE
    select case (x)
    case (1)
      z = 1
    case (2)
      z = 2
    case default
      z = 0
    end select
    
  end subroutine test_logic_blocks

end module test_logic_module
