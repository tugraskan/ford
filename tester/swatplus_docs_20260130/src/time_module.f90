      module time_module
    
      implicit none

      character (len=29) :: cal_sim = " Original Simulation"              !! [n/a] calibration simulation label
      real :: cal_adj = 0.0                                                !! [unitless] calibration adjustment factor
      real :: yrs_print = 0.                                               !! [yr] print interval length in years
      integer, dimension (13) :: ndays = (/0,31,60,91,121,152,182,213,244,274,305,335,366/)              !! [day] cumulative day index (leap-year convention)
      integer, dimension (13) :: ndays_leap = (/0,31,60,91,121,152,182,213,244,274,305,335,366/)         !! [day] cumulative day index for leap years
      integer, dimension (13) :: ndays_noleap = (/0,31,59,90,120,151,181,212,243,273,304,334,365/)       !! [day] cumulative day index for non-leap years
      integer, dimension (12) :: ndmo = (/0,0,0,0,0,0,0,0,0,0,0,0/)      !! [day] cumulative days accrued in each month since simulation start

      
      type time_current
        character (len=1)  :: day_print = "n"                              !! [n/a] daily print toggle
        integer :: day = 0            !! [day] current simulation day (Julian day-of-year)
        integer :: mo = 0             !! [month] current simulation month
        integer :: mo_start = 0       !! [month] simulation start month
        integer :: yrc = 0            !! [yr] current calendar year
        integer :: yrc_start = 0      !! [yr] simulation start year
        integer :: yrc_end = 0        !! [yr] simulation end year
        integer :: yrs = 0            !! [yr] sequential simulation year counter
        integer :: day_mo = 0         !! [day] day of month (1-31)
        integer :: end_mo = 0         !! [flag] end-of-month indicator (1=yes)
        integer :: end_yr = 0         !! [flag] end-of-year indicator (1=yes)
        integer :: end_sim = 0        !! [flag] end-of-simulation indicator (1=yes)
        integer :: end_aa_prt = 0     !! [flag] end-of-average-annual print interval indicator (1=yes)
        integer :: day_start = 0      !! [day] starting Julian day of simulation
        integer :: day_end_yr = 0     !! [day] ending Julian day for current year
        integer :: day_end = 0        !! [day] input ending Julian day of simulation
        integer :: nbyr = 3           !! [yr] number of simulation years
        integer :: step = 0           !! [count/day] time steps per day (0=daily, 1=12-hr, 24=hourly, 96=15-min, 1440=minutely)
        real :: dtm = 0.              !! [min] routing and rainfall time-step size
        real :: days_prt = 0.         !! [day] days represented in average-annual output period
        real :: yrs_prt = 0.          !! [yr] years represented in average-annual output period
        real :: yrs_prt_int = 0.      !! [yr] years represented in current average-annual print interval
        integer :: num_leap = 0       !! [count] number of leap years included in simulation period
        integer :: prt_int_cur = 1    !! [count] current average-annual print interval index
        integer :: yrc_tot = 0        !! [yr] total number of calendar years represented
      end type time_current
      type (time_current) :: time                                          !! [n/a] mutable simulation time state
      type (time_current) :: time_init                                     !! [n/a] initial simulation time state snapshot

      !elapsed simulation time
      !real :: sim_start,sim_finish
      
      end module time_module
