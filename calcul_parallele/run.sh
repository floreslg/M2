#!/bin/bash

# Coding experiences in functions:
# --------------------------------

function run_pi_omp()
{
    echo "### RUNNING EXPERIENCES V$1"
    
    for val_n in 30000 300000 3000000 30000000
    do 
        echo "... cleaning"
        rm a.out
        
        echo "... compiling"
        gfortran v$1_pi.F90 -DVAL_N=$val_n -fopenmp
        
        echo "... Running experiences "
        
        for n_threads in 1 2 3 4 5 6 8 10 16
        do
            echo "[DATA] V$1 | threads = $n_threads"
            export OMP_NUM_THREADS=$n_threads
            ./a.out
        done
        echo "... done"
    done
}



function run_pi_mpi()
{
    echo "### RUNNING EXPERIENCES V$1"
    
    for val_n in 30000 300000 3000000 30000000
    do 
        echo "... cleaning"
        rm a.out
        
        echo "... compiling"
        mpif90 -o a.out v$1_pi.F90 -DVAL_N=$val_n
        
        echo "... Running experiences "
        
        for n_threads in 1 2 3 4 5 6 8 10 16
        do
            echo "[DATA] V$1 | threads = $n_threads"
            export OMP_NUM_THREADS=$n_threads
            mpiexec --mca btl_base_warn_component_unused 0 -n $n_threads ./a.out
        done
        echo "... done"
    done
}



function run_jacobi_omp()
{
    gfortran jacobi_omp.F90 -o jacobi_omp.exe -fopenmp

    export OMP_SCHEDULE="STATIC"

    echo 1 2 3 4 5 6 8
    for n_threads in 16
    do
        export OMP_NUM_THREADS=$n_threads
        ./jacobi_omp.exe
    done
}



function run_jacobi_mat_size()
{
    for val_n in 800 1201 1600 2000 
    do
        for val_d in 400 800 1600
        do
            gfortran jacobi.F90 -o jacobi_mono.exe -DVAL_N=$val_n -DVAL_D=$val_d
            ./jacobi_mono.exe
        done
    done
}



# Executing experiences:
# ----------------------

run_pi_omp 1
#run_pi_omp 2
#run_pi_omp 3
#run_pi_mpi 4
#run_pi_omp 5
#run_pi_omp 6

#run_jacobi_mat_size
#run_jacobi_omp