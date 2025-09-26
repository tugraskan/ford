!> A simple test module for CSV generation
module test_module
    implicit none
    private
    
    public :: test_subroutine, test_function
    
    !> A test integer parameter
    integer, parameter :: test_param = 42
    
contains

    !> A simple test subroutine
    !! @param[in] input_value Input integer value
    !! @param[out] output_value Output integer value
    subroutine test_subroutine(input_value, output_value)
        integer, intent(in) :: input_value
        integer, intent(out) :: output_value
        
        ! Local variables
        integer :: temp_var
        
        temp_var = input_value * 2
        output_value = temp_var + test_param
        
        write(*,*) 'Processing value:', input_value
    end subroutine test_subroutine
    
    !> A simple test function
    !! @param[in] x Input value
    !! @return Result of computation
    function test_function(x) result(y)
        real, intent(in) :: x
        real :: y
        
        y = x ** 2 + 1.0
    end function test_function

end module test_module

!> A simple test program
program test_program
    use test_module
    implicit none
    
    integer :: input, output
    real :: value, result
    
    input = 10
    call test_subroutine(input, output)
    
    value = 3.0
    result = test_function(value)
    
    write(*,*) 'Final output:', output
    write(*,*) 'Function result:', result
end program test_program