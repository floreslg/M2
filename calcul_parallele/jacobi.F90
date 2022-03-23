PROGRAM JACOBI
  
  IMPLICIT NONE

! Dimension parn defaut de la taille des matrices
#ifndef VAL_N
#define VAL_N 1201
#endif
#ifndef VAL_D
#define VAL_D 800
#endif


  INTEGER, PARAMETER           :: n=VAL_N, diag=VAL_D
  INTEGER                      :: i, j, ir, t0, t1, iteration=0
  LOGICAL                      :: exist
  REAL(KIND=8), DIMENSION(n,n) :: a
  REAL(KIND=8), DIMENSION(n)   :: x, x_courant, b
  REAL(KIND=8)                 :: norme, temps, t_cpu_0, t_cpu_1, t_cpu

  ! Initialisation de la matrice et du second membre
  CALL RANDOM_NUMBER(a)
  CALL RANDOM_NUMBER(b)

  ! On muscle la diagonale principale de la matrice
  FORALL (i=1:n) a(i,i) = a(i,i) + diag

  ! Solution initiale
  x(:) = 1.0_8
  
  
  INQUIRE(file="hist.csv", exist=exist)
    
    IF (exist) THEN
        OPEN(1, file="hist.csv", &
                status="old", &
                position="append", &
                action="write")
    ELSE
        OPEN(1, file="hist.csv", status="new", action="write")
        WRITE(1, '(*(A10,:,","))') "taille", "diag", "iters", "norme"
    END IF
  

  ! Temps CPU de calcul initial
  CALL CPU_TIME(t_cpu_0)

  ! Temps elapsed de reference
  CALL SYSTEM_CLOCK(count=t0, count_rate=ir)

  ! Resolution par la methode de Jacobi
  Jaco : DO
     iteration = iteration + 1
     
     DO i=1,n
        x_courant(i) = 0.0
        !
        DO j=1,i-1
           x_courant(i) = x_courant(i) + a(i,j)*x(j)
        ENDDO
        !
        DO j=i+1,n
           x_courant(i) = x_courant(i) + a(i,j)*x(j)
        ENDDO
        !
        x_courant(i) = (b(i) - x_courant(i))/a(i,i)
     ENDDO

     ! Test de convergence
     norme = MAXVAL(ABS(x(:) - x_courant(:)) )/REAL(n, KIND=8)
     
     WRITE(1, '(*(G0.15,:,","))') n, diag, iteration, norme

     IF ((norme <= epsilon(1.0_8)) .OR. (iteration >= n)) EXIT Jaco

     x(:) = x_courant(:)
     
  ENDDO Jaco

  ! Temps elapsed final
  CALL SYSTEM_CLOCK(count=t1, count_rate=ir)

  temps = REAL(t1 - t0, KIND=8)/REAL(ir, KIND=8)

  ! Temps CPU de calcul final
  CALL CPU_TIME(t_cpu_1)

  t_cpu = t_cpu_1 - t_cpu_0

  ! Impression du resultat
  PRINT '(//, 3x, "Taille du systeme   : ", i5, /       &
           &, 3x, "Iterations          : ", i4, /       &
           &, 3x, "Norme               : ", 1pe10.3, /  &
           &, 3x, "Temps elapsed       : ", 1pe10.3, " sec.", / &
           &, 3x, "Temps CPU           : ", 1pe10.3, " sec.", //)', n, iteration, norme, temps, t_cpu
           
   
   CLOSE(1)
           

END PROGRAM JACOBI
 
