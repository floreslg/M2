#ifndef VAL_N
#define VAL_N 30000000
#endif



PROGRAM PI
    
    use mpi
    

    INTEGER, PARAMETER :: version=4
    INTEGER            :: n=VAL_N
    INTEGER            :: N_threads
    LOGICAL            :: exist
    
    INTEGER :: ierr
    INTEGER :: nproc
    INTEGER :: iproc
    INTEGER :: master=0
    
    DOUBLE PRECISION   :: f
    DOUBLE PRECISION   :: x
    DOUBLE PRECISION   :: a
    DOUBLE PRECISION   :: h
    DOUBLE PRECISION   :: Pi_estime
    DOUBLE PRECISION   :: Pi_calcule
    DOUBLE PRECISION   :: iproc_pi
    DOUBLE PRECISION   :: ecart
    DOUBLE PRECISION   :: temps
    DOUBLE PRECISION   :: t_cpu_0
    DOUBLE PRECISION   :: t_cpu_1
    DOUBLE PRECISION   :: t_cpu

    INTEGER            :: i
    INTEGER            :: ir
    INTEGER            :: t1
    INTEGER            :: t2
    INTEGER            :: k
    
    INTRINSIC ABS, DBLE
    

    ! Fonction instruction a integrer
    f(a) = 4.0_8/(1.0_8 + a*a)

    ! Valeur estimée de Pi
    Pi_estime = ACOS(-1.0_8)

    ! Longueur de l'intervalle d'integration
    h = 1.0_8/DBLE(n)
    
    
    IF (iproc==master) THEN
        
        ! Temps CPU de calcul initial
        CALL CPU_TIME(t_cpu_0)

        ! Temps elapsed de reference
        CALL SYSTEM_CLOCK(count=t1, count_rate=ir)
        
    END IF

    
    CALL MPI_INIT(ierr)
    CALL MPI_COMM_SIZE(MPI_COMM_WORLD, nproc, ierr)
    CALL MPI_COMM_RANK(MPI_COMM_WORLD, iproc, ierr)
    
    ! Boucle artificielle
    DO k=1,100
        ! PRINT '(3x, "Iteration k : ", i3)', k
        
        CALL MPI_BCAST(n, 1, MPI_INTEGER, master, MPI_COMM_WORLD, ierr)
        sum = 0.0_8
        DO i = iproc+1, n, nproc
            x = h*(DBLE(i) - 0.5_8)
            !$OMP ATOMIC
            sum = sum + f(x)
        END DO
        iproc_pi = h * sum
        
        CALL MPI_REDUCE(iproc_pi, Pi_calcule, 1, &
                        MPI_DOUBLE_PRECISION, MPI_SUM, &
                        master,MPI_COMM_WORLD, ierr)
        
        N_threads = nproc
        
    END DO
    
    CALL MPI_FINALIZE(ierr)
    
    
    
    IF (iproc==master) THEN
    
        ! Temps elapsed final
        CALL SYSTEM_clock(count=t2, count_rate=ir)
        temps = REAL(t2 - t1, KIND=8)/REAL(ir, KIND=8)

        ! Temps CPU de calcul final
        CALL CPU_TIME(t_cpu_1)
        t_cpu = t_cpu_1 - t_cpu_0


        ! Ecart entre la valeur estimee et la valeur calculee de Pi.
        ecart = ABS(Pi_estime - Pi_calcule)


        ! Impression du resultat
        PRINT '(3x, "Nombre d intervalles       : ", i10, / &
                   &, 3x, "Pi_estime                  : ", 1pe15.8, / &
                   &, 3x, "Pi_calcule                 : ", 1pe15.8, / &
                   &, 3x, "| Pi_estime - Pi_calcule | : ", 1pe10.3, / &
                   &, 3x, "Temps elapsed (sec.)       : ", 1pe10.3, / &
                   &, 3x, "Temps CPU (sec.)           : ", 1pe10.3)', &
                   n, Pi_estime, Pi_calcule, ecart, temps, t_cpu



        ! Ecrire une rapport csv
        INQUIRE(file="report.csv", exist=exist)

        IF (exist) THEN
            OPEN(1, file="report.csv", &
                    status="old", &
                    position="append", &
                    action="write")
        ELSE
            OPEN(1, file="report.csv", status="new", action="write")
            WRITE(1, '(*(A10,:,","))') "N_val", &
                    "Pi_estime", &
                    "Pi_calcule", &
                    "ecart", &
                    "temps", &
                    "t_cpu", &
                    "N_threads", &
                    "Version"
        END IF


        WRITE(1, '(*(G0.15,:,","))') n, &
                    Pi_estime, &
                    Pi_calcule, &
                    ecart, &
                    temps, &
                    t_cpu, &
                    N_threads, &
                    version
        CLOSE(1)
    
    END IF

END PROGRAM PI
