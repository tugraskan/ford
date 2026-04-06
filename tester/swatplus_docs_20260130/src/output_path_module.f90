      module output_path_module
      
      implicit none
      
      !! [path] output directory prefix applied to generated output files
      character(len=256) :: out_path = ""
      
      contains
      
      subroutine init_output_path(path_in)

!!    ~ ~ ~ PURPOSE ~ ~ ~
!!    initialize and validate the configured output directory path, normalize
!!    path separators by operating system, and create the directory if needed.
      
      implicit none
      
      character(len=*), intent(in) :: path_in                              !! [path] raw path string from file.cio out_path setting
      character(len=256) :: path_work, path_mkdir                          !! [path] normalized path value and mkdir-safe path
      character(len=512) :: cmd                                            !! [n/a] shell command used for path existence checks/creation
      character(len=32) :: os_env                                          !! [n/a] OS environment variable string used for OS detection
      integer :: i, path_len, stat                                         !! [count] loop index, trimmed path length, and command status code
      logical :: is_windows                                                !! [flag] true when running on Windows
      logical :: dir_exists                                                !! [flag] true when target output directory exists
      
      !! Detect OS - Runtime check is more robust if preprocessor fails
      is_windows = .false.
      call get_environment_variable("OS", os_env, status=stat)
      if (stat == 0 .and. index(os_env, "Windows") > 0) then
         is_windows = .true.
      end if
      
      !! If null or empty, use current directory (no prefix needed)
      if (trim(path_in) == "null" .or. trim(path_in) == "" .or. &
          trim(path_in) == "NULL" .or. trim(path_in) == " ") then
        out_path = ""
        return
      end if
      
      !! Copy and process the path
      path_work = trim(adjustl(path_in))
      path_len = len_trim(path_work)
      
      !! Handle path separators based on OS
      if (is_windows) then
        !! On Windows: convert forward slashes to backslashes
        do i = 1, path_len
          if (path_work(i:i) == '/') path_work(i:i) = '\'
        end do
        
        !! Check if this looks like a Unix absolute path on Windows (starts with /)
        !! If so, prepend C:
        if (path_in(1:1) == '/') then
          path_work = 'C:' // trim(path_work)
          path_len = len_trim(path_work)
        end if
        
        !! Remove trailing backslash(es) for consistent processing
        do while (path_len > 0 .and. path_work(path_len:path_len) == '\')
          path_work(path_len:path_len) = ' '
          path_len = path_len - 1
        end do
      else
        !! On Unix: convert backslashes to forward slashes
        do i = 1, path_len
          if (path_work(i:i) == '\') path_work(i:i) = '/'
        end do
        
        !! Check if this looks like a Windows path on Unix
        if (index(path_work, ':') > 0) then
          write (*,*) "! ERROR: cannot create path specified in file.cio (out_path)"
          write (*,*) "  > Windows-style path detected on Unix system: ", trim(path_in)
          stop 1
        end if
        
        !! Remove trailing slash(es) for consistent processing
        do while (path_len > 1 .and. path_work(path_len:path_len) == '/')
          path_work(path_len:path_len) = ' '
          path_len = path_len - 1
        end do
      end if
      
      !! Store path for mkdir (without trailing separator)
      path_mkdir = trim(path_work)
      
      !! Add trailing separator for out_path (used when building file paths)
      if (is_windows) then
        out_path = trim(path_work) // '\'
      else
        out_path = trim(path_work) // '/'
      end if
      
      !! Create the directory
      if (is_windows) then
        !! Windows: use cmd /c to run mkdir and suppress output
        cmd = 'cmd /c mkdir "' // trim(path_mkdir) // '" 2>NUL'
      else
        !! Unix: use mkdir -p (creates parent directories, no error if exists)
        cmd = 'mkdir -p "' // trim(path_mkdir) // '" 2>/dev/null'
      end if
      call execute_command_line(trim(cmd), wait=.true., exitstat=stat)
      
      !! Verify directory exists using INQUIRE
      inquire(file=trim(path_mkdir), exist=dir_exists)
      
      !! If inquire failed, try alternate method - check via directory listing
      if (.not. dir_exists) then
        if (is_windows) then
           !! Windows check
           cmd = 'cmd /c "if exist "' // trim(path_mkdir) // '" (exit 0) else (exit 1)"'
        else
           !! Unix check
           cmd = 'test -d "' // trim(path_mkdir) // '"'
        end if
        call execute_command_line(trim(cmd), wait=.true., exitstat=stat)
        
        if (stat /= 0) then
          write (*,*) "! ERROR: cannot create or access path specified in file.cio (out_path)"
          write (*,*) "  > Path: ", trim(path_in)
          stop 1
        end if
      end if
      
      !! Write confirmation
      write (*,*) "Output path set to: ", trim(out_path)
      
      return
      end subroutine init_output_path
      
      function get_output_filename(filename) result(full_path)

!!    ~ ~ ~ PURPOSE ~ ~ ~
!!    return the resolved output filename by prepending the configured output
!!    path when an output directory prefix is active.
      
      implicit none
      
      character(len=*), intent(in) :: filename                             !! [path] base output filename from caller
      character(len=512) :: full_path                                      !! [path] resolved output path written by caller
      
      if (len_trim(out_path) > 0) then
        full_path = trim(out_path) // trim(filename)
      else
        full_path = trim(filename)
      end if
      
      return
      end function get_output_filename
      
      subroutine open_output_file(iunit, filename, recl_val)

!!    ~ ~ ~ PURPOSE ~ ~ ~
!!    open an output file using the configured output directory prefix and
!!    optional record length for formatted file writing.
      
      implicit none
      
      integer, intent(in) :: iunit                   !! [count] Fortran I/O unit number
      character(len=*), intent(in) :: filename       !! [path] output filename (without optional out_path prefix)
      integer, intent(in), optional :: recl_val      !! [count] optional record length passed to OPEN
      character(len=512) :: full_path                !! [path] resolved filename with output path prefix
      
      !! Get full path
      full_path = get_output_filename(filename)
      
      !! Open with or without recl
      if (present(recl_val)) then
        open (iunit, file=trim(full_path), recl=recl_val)
      else
        open (iunit, file=trim(full_path))
      end if
      
      return
      end subroutine open_output_file
      
      end module output_path_module
