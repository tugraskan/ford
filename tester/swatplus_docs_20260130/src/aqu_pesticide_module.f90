      module aqu_pesticide_module

      implicit none
              
      type aqu_pesticide_processes
        real :: tot_in = 0.             !! [kg] total pesticide mass entering the aquifer
        real :: sol_flo = 0.            !! [kg] soluble pesticide mass leaving the aquifer
        real :: sor_flo = 0.            !! [kg] sorbed pesticide mass leaving the aquifer
        real :: sol_perc = 0.           !! [kg] soluble pesticide mass percolating from the aquifer
        real :: react = 0.              !! [kg] pesticide mass lost through reactions
        real :: metab = 0.              !! [kg] pesticide mass metabolized from the parent compound
        real :: stor_ave = 0.           !! [kg] average end-of-day pesticide mass in aquifer over the period
        real :: stor_init = 0.          !! [kg] pesticide mass in aquifer at the start of the day
        real :: stor_final = 0.         !! [kg] pesticide mass in aquifer at the end of the day
      end type aqu_pesticide_processes
      
      type aqu_pesticide_output
        type (aqu_pesticide_processes), dimension (:), allocatable :: pest         !! [n/a] pesticide output records by pesticide index
      end type aqu_pesticide_output
      type (aqu_pesticide_processes) :: aqu_pestbz
           
      type (aqu_pesticide_output), dimension(:), allocatable, save :: aqupst_d
      type (aqu_pesticide_output), dimension(:), allocatable, save :: aqupst_m
      type (aqu_pesticide_output), dimension(:), allocatable, save :: aqupst_y
      type (aqu_pesticide_output), dimension(:), allocatable, save :: aqupst_a
      type (aqu_pesticide_output) :: baqupst_d
      type (aqu_pesticide_output) :: baqupst_m
      type (aqu_pesticide_output) :: baqupst_y
      type (aqu_pesticide_output) :: baqupst_a
      type (aqu_pesticide_output) :: aqupst, aqupstz
                 
      type aqu_pesticide_header
          character (len=6) :: day =        "  jday"
          character (len=6) :: mo =         "   mon"
          character (len=6) :: day_mo =     "   day"
          character (len=6) :: yrc =        "    yr"
          character (len=8) :: isd =        "   unit "
          character (len=8) :: id =         " gis_id "
          character (len=16) :: name =      " name           "
          character (len=16) :: pest =      " pesticide      "
          character(len=13) :: tot_in =     "  tot_in_kg "          !! [n/a] output column label for total pesticide mass (kg)
          character(len=13) :: sol_out =    "  sol_flo_kg"          !! [n/a] output column label for soluble pesticide outflow (kg)
          character(len=13) :: sor_out =    "  sor_flo_kg"          !! [n/a] output column label for sorbed pesticide outflow (kg)
          character(len=13) :: sol_perc =   "sol_perc_kg"           !! [n/a] output column label for soluble pesticide percolation (kg)
          character(len=13) :: react =      "react_kg"              !! [n/a] output column label for reacted pesticide mass (kg)
          character(len=13) :: metab =      "metab_kg"              !! [n/a] output column label for metabolized pesticide mass (kg)
          character(len=13) :: stor_ave  =  "stor_ave_kg"           !! [n/a] output column label for average storage mass (kg)
          character(len=13) :: stor_init =  "stor_init_kg"          !! [n/a] output column label for initial storage mass (kg)
          character(len=13) :: stor_final=  "stor_final_kg"         !! [n/a] output column label for final storage mass (kg)
      end type aqu_pesticide_header
      type (aqu_pesticide_header) :: aqupest_hdr
     
      interface operator (+)
        module procedure aqupest_add
      end interface
           
      interface operator (.sum.)
        module procedure aqupest_add_all
      end interface
      
      interface operator (/)
        module procedure aqupest_div
      end interface
        
      interface operator (//)
        module procedure aqupest_ave
      end interface 
             
      contains
!! routines for swatdeg_hru module

      function aqupest_add(aqu1, aqu2) result (aqu3)
      !!    ~ ~ ~ PURPOSE ~ ~ ~
      !!    combine two aquifer pesticide process records by summing flow/process terms
      !!    and carrying initial/final storage from the first record.
        type (aqu_pesticide_processes),  intent (in) :: aqu1
        type (aqu_pesticide_processes),  intent (in) :: aqu2
        type (aqu_pesticide_processes) :: aqu3
        aqu3%tot_in = aqu1%tot_in + aqu2%tot_in
        aqu3%sol_flo = aqu1%sol_flo + aqu2%sol_flo
        aqu3%sor_flo = aqu1%sor_flo + aqu2%sor_flo
        aqu3%sol_perc = aqu1%sol_perc + aqu2%sol_perc
        aqu3%react = aqu1%react + aqu2%react
        aqu3%metab = aqu1%metab + aqu2%metab
        aqu3%stor_ave = aqu1%stor_ave + aqu2%stor_ave
        aqu3%stor_init = aqu1%stor_init
        aqu3%stor_final = aqu1%stor_final
      end function aqupest_add
      
      function aqupest_add_all(aqu1, aqu2) result (aqu3)
      !!    ~ ~ ~ PURPOSE ~ ~ ~
      !!    combine two aquifer pesticide process records by summing all terms,
      !!    including initial and final storage.
        type (aqu_pesticide_processes),  intent (in) :: aqu1
        type (aqu_pesticide_processes),  intent (in) :: aqu2
        type (aqu_pesticide_processes) :: aqu3
        aqu3%tot_in = aqu1%tot_in + aqu2%tot_in
        aqu3%sol_flo = aqu1%sol_flo + aqu2%sol_flo
        aqu3%sor_flo = aqu1%sor_flo + aqu2%sor_flo
        aqu3%sol_perc = aqu1%sol_perc + aqu2%sol_perc
        aqu3%react = aqu1%react + aqu2%react
        aqu3%metab = aqu1%metab + aqu2%metab
        aqu3%stor_ave = aqu1%stor_ave + aqu2%stor_ave
        aqu3%stor_init = aqu1%stor_init + aqu2%stor_init
        aqu3%stor_final = aqu1%stor_final + aqu2%stor_final
      end function aqupest_add_all
            
      function aqupest_div (aqu1, const) result (aqu2)
      !!    ~ ~ ~ PURPOSE ~ ~ ~
      !!    scale selected aquifer pesticide process terms by a divisor while
      !!    preserving storage terms unchanged.
        type (aqu_pesticide_processes), intent (in) :: aqu1
        real, intent (in) :: const
        type (aqu_pesticide_processes) :: aqu2
          aqu2%tot_in = aqu1%tot_in / const
          aqu2%sol_flo = aqu1%sol_flo / const
          aqu2%sor_flo = aqu1%sor_flo / const
          aqu2%sol_perc = aqu1%sol_perc / const
          aqu2%react = aqu1%react / const
          aqu2%metab = aqu1%metab / const
          aqu2%stor_ave = aqu1%stor_ave
          aqu2%stor_init = aqu1%stor_init
          aqu2%stor_final = aqu1%stor_final
      end function aqupest_div
      
      function aqupest_ave (aqu1, const) result (aqu2)
      !!    ~ ~ ~ PURPOSE ~ ~ ~
      !!    compute an average-storage variant of an aquifer pesticide process record
      !!    by dividing only the average storage term by the provided divisor.
        type (aqu_pesticide_processes), intent (in) :: aqu1
        real, intent (in) :: const
        type (aqu_pesticide_processes) :: aqu2
          aqu2%tot_in = aqu1%tot_in
          aqu2%sol_flo = aqu1%sol_flo
          aqu2%sor_flo = aqu1%sor_flo
          aqu2%sol_perc = aqu1%sol_perc
          aqu2%react = aqu1%react
          aqu2%metab = aqu1%metab
          aqu2%stor_ave = aqu1%stor_ave / const
          aqu2%stor_init = aqu1%stor_init
          aqu2%stor_final = aqu1%stor_final
      end function aqupest_ave
      
      end module aqu_pesticide_module
