#ifndef VAL_N
#define VAL_N 30000000
#endif



PROGRAM PI
    
    !$ use OMP_LIB

    INTEGER, PARAMETER :: version=5
    INTEGER, PARAMETER :: n=VAL_N
    INTEGER            :: N_threads
    LOGICAL            :: exist
    
    REAL(KIND=8)       :: f
    REAL(KIND=8)       :: x
    REAL(KIND=8)       :: a
    REAL(KIND=8)       :: h
    REAL(KIND=8)       :: Pi_estime
    REAL(KIND=8)       :: Pi_calcule
    REAL(KIND=8)       :: ecart
    REAL(KIND=8)       :: temps
    REAL(KIND=8)       :: t_cpu_0
    REAL(KIND=8)       :: t_cpu_1
    REAL(KIND=8)       :: t_cpu

    INTEGER            :: i
    INTEGER            :: ir
    INTEGER            :: t1
    INTEGER            :: t2
    INTEGER            :: k


    ! Fonction instruction a integrer
    f(a) = 4.0_8/(1.0_8 + a*a)

    ! Valeur estimée de Pi
    Pi_estime = ACOS(-1.0_8)

    ! Longueur de l'intervalle d'integration
    h = 1.0_8/REAL(n, KIND=8)

    ! Temps CPU de calcul initial
    CALL CPU_TIME(t_cpu_0)

    ! Temps elapsed de reference
    CALL SYSTEM_CLOCK(count=t1, count_rate=ir)


    ! Boucle artificielle
    DO k=1,100
        ! PRINT '(3x, "Iteration k : ", i3)', k
        
        Pi_calcule = 0.0_8
        !$OMP PARALLEL PRIVATE(N_thread)
        N_threads=OMP_GET_NUM_THREADS()
        !$OMP DO REDUCTION(+:Pi_calcule) PRIVATE(i,x) SCHEDULE(DYNAMIC)
        DO i=1,n
            x = h*(REAL(i, kind=8) - 0.5_8)
            pi_calcule = pi_calcule + f(x)
        END DO
        !$OMP END DO
        !$OMP END PARALLEL
        Pi_calcule = h * Pi_calcule
        
    END DO

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


END PROGRAM PI
