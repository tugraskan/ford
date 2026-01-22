# Makefile for I/O Trace Example
# Demonstrates compilation and execution of the Fortran I/O example

FC = gfortran
FFLAGS = -Wall -std=f2008 -J./mod
SRCDIR = src
DATADIR = data
MODDIR = mod
OBJDIR = obj

# Create directories
$(shell mkdir -p $(MODDIR) $(OBJDIR))

# Source files
SOURCES = $(SRCDIR)/input_file_module.f90 \
          $(SRCDIR)/aquifer_database.f90 \
          $(SRCDIR)/aquifer_module.f90 \
          $(SRCDIR)/object_module.f90 \
          $(SRCDIR)/output_module.f90 \
          $(SRCDIR)/io_trace_demo.f90

# Object files
OBJECTS = $(OBJDIR)/input_file_module.o \
          $(OBJDIR)/aquifer_database.o \
          $(OBJDIR)/aquifer_module.o \
          $(OBJDIR)/object_module.o \
          $(OBJDIR)/output_module.o \
          $(OBJDIR)/io_trace_demo.o

# Executable
TARGET = io_trace_demo

.PHONY: all clean run

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(FC) $(FFLAGS) -o $@ $(OBJECTS)

# Compilation rules with dependencies
$(OBJDIR)/input_file_module.o: $(SRCDIR)/input_file_module.f90
	$(FC) $(FFLAGS) -c $< -o $@

$(OBJDIR)/aquifer_database.o: $(SRCDIR)/aquifer_database.f90
	$(FC) $(FFLAGS) -c $< -o $@

$(OBJDIR)/aquifer_module.o: $(SRCDIR)/aquifer_module.f90 $(OBJDIR)/input_file_module.o $(OBJDIR)/aquifer_database.o
	$(FC) $(FFLAGS) -c $< -o $@

$(OBJDIR)/object_module.o: $(SRCDIR)/object_module.f90 $(OBJDIR)/input_file_module.o
	$(FC) $(FFLAGS) -c $< -o $@

$(OBJDIR)/output_module.o: $(SRCDIR)/output_module.f90 $(OBJDIR)/aquifer_database.o
	$(FC) $(FFLAGS) -c $< -o $@

$(OBJDIR)/io_trace_demo.o: $(SRCDIR)/io_trace_demo.f90 $(OBJDIR)/input_file_module.o $(OBJDIR)/aquifer_module.o $(OBJDIR)/object_module.o $(OBJDIR)/output_module.o
	$(FC) $(FFLAGS) -c $< -o $@

run: $(TARGET)
	@echo "===== Running I/O Trace Demo ====="
	@cp $(DATADIR)/aquifer.aqu .
	@cp $(DATADIR)/object.cnt .
	./$(TARGET)
	@echo ""
	@echo "===== Output Files Created ====="
	@ls -lh mgt.out aquifer.out
	@echo ""
	@echo "===== mgt.out Contents ====="
	@cat mgt.out
	@echo ""
	@echo "===== aquifer.out Contents ====="
	@cat aquifer.out

clean:
	rm -rf $(OBJDIR) $(MODDIR) $(TARGET) *.o *.mod
	rm -f aquifer.aqu object.cnt mgt.out aquifer.out

help:
	@echo "I/O Trace Example Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  all    - Build the demo program (default)"
	@echo "  run    - Build and run the demo program"
	@echo "  clean  - Remove build artifacts and output files"
	@echo "  help   - Display this help message"
	@echo ""
	@echo "Requirements:"
	@echo "  - gfortran compiler"
	@echo ""
	@echo "Usage:"
	@echo "  make        # Build the program"
	@echo "  make run    # Build and run with sample data"
	@echo "  make clean  # Clean up"
