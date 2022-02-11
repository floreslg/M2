#####################################################################
# TP4 - Analyse de sensibilité, Criblage
# Bertrand Iooss
# Polytech Nice Sophia
# 
# Etudiant: Gabriel Flores Lipa
#####################################################################


# Prép. enviro. et librairies
# ---------------------------
rm(list=ls())
graphics.off()

library(sensitivity)
library(mlbench)
library(parcoords)
library(car)



#####################################################################
# 1 Méthode de Morris


# wing weight function :
wingweight <- function(xx)
{
  # y  = wing weight
  # xx = c(Sw, Wfw, A, Lam, q, lam, tc, Nz, Wdg, Wp)
  
  # on met les entrees dans leur domaine de variation
  Sw      <- xx[,1]*50+150
  Wfw     <- xx[,2]*80+220
  A       <- xx[,3]*4+6
  Lam     <- (xx[,4]*20-10)*pi/180
  q       <- xx[,5]*29+16
  lam     <- xx[,6]*0.5+0.5
  tc      <- xx[,7]*0.1+0.08
  Nz      <- xx[,8]*3.5+2.5
  Wdg     <- xx[,9]*800+1700
  Wp      <- xx[,10]*0.055+0.025
  fact1 <- 0.036 * Sw^0.758 * Wfw^0.0035
  fact2 <- (A / ((cos(Lam))^2))^0.6
  fact3 <- q^0.006 * lam^0.04
  fact4 <- (100*tc / cos(Lam))^(-0.3)
  fact5 <- (Nz*Wdg)^0.49
  term1 <- Sw * Wp
  y <- fact1*fact2*fact3*fact4*fact5 + term1
  
  return(y)
}

namesWW <- c("Sw", "Wfw", "A", "Lam", "q",
             "lam", "tc", "Nz", "Wdg", "Wp")



# Methode de Morris :
mor1 <- morris(model=wingweight,
               factors=namesWW,
               r=10,
               design=list(type="oat",
                           levels=5,
                           grid.jump=3))


# Visualisation de résultats :
x11()
plot(mor1, xlim=c(0,120))




#####################################################################
# 2 Outils graphiques d'analyse de sensibilité



# 2a Selection des entrées et sortie à étudier :
# ---------------------------------------------

data(BostonHousing2)
a <- BostonHousing2
b <- a[,-c(1,2,3,4,5,10)]
yBH <- b$cmedv # sortie
xBH <- b[,-1] # entrées (on enleve cmedv)

dataBH <- data.frame(xBH, yBH)



# 2b Analyses uni- et bi-dimensionelles et de correlation :
# ---------------------------------------------

panel.hist <- function(x, ...){
  usr <- par("usr"); on.exit(par(usr))
  par(usr = c(usr[1:2], 0, 1.5) )
  h <- hist(x, plot = FALSE)
  breaks <- h$breaks; nB <- length(breaks)
  y <- h$counts; y <- y/max(y)
  rect(breaks[-nB], 0, breaks[-1], y, col = "cyan", ...)
}

panel.cor <- function(x, y, digits = 2,
                      prefix = "", cex.cor, ...){
  usr <- par("usr"); on.exit(par(usr))
  par(usr = c(0, 1, 0, 1))
  r <- cor(x, y, use="pairwise.complete.obs")
  txt <- format(c(r, 0.123456789), digits = digits)[1]
  txt <- paste0(prefix, txt)
  if(missing(cex.cor)) cex.cor <- 0.8/strwidth(txt)
  text(0.5, 0.5, txt, cex = cex.cor * abs(r)+1)
}


# visualisation de résultats :
x11()
pairs(dataBH,
      panel=panel.smooth,
      diag.panel=panel.hist,
      upper.panel=panel.cor,
      horOdd=F, verOdd=T,
      cex=.7, pch=24, bg="light blue",
      cex.labels=1.5, font.labels=2, cex.axis=1)




# 2c Visualisation avec Cobweb plot :
# ---------------------------------------------

# sur les données brutes :
parcoords(data = dataBH, brushMode = "1D-axes-multi",
          rownames = FALSE, alphaOnBrushed = 0.2)


# transformation des rangs :
dataBHr <- data.frame(lapply(dataBH,rank))


# sur les données transformées :
parcoords(data = dataBHr, brushMode = "1D-axes-multi",
          rownames = FALSE, alphaOnBrushed = 0.2)





#####################################################################
# 3 Calcul d'indices de sensibilité 
set.seed(123456)



# 3a Indices SRC, R2 sur Wing weight function :
# ---------------------------------------------

# generation des donnnées :
n <- 100
d <- length(namesWW)
x <- matrix(runif(n=n*d), nrow=n, ncol=d)
colnames(x) = namesWW
y = wingweight(x)


# calcul des indices SRC :
srcWW <- src(x, y, nboot=20)
print(srcWW)

# visualisation :
x11(); plot(srcWW); abline(h=0)

print(srcWW$SRC$original^2)
sum(srcWW$SRC$original^2)



# validation du modele lineaire :
formule <- as.formula( y ~ Sw + Wfw + A + Lam +
                            q + lam + tc + Nz + Wdg + Wp)
modele <- lm(formule, data.frame(x, y))
summary(modele)$r.squared




# 3b Indices SRC, R2 sur les données BostonHousing2 :
# ---------------------------------------------


# calcule d'indices SRC :
srcBH <- src(xBH, yBH, nboot=20)
x11(); plot(srcBH); abline(h=0)

print(srcBH)
print(srcBH$SRC$original^2)
sum(srcBH$SRC$original^2)


# Validation du modele (R^2) :
formule <- as.formula( yBH ~ .)
modele <- lm(formule, data.frame(xBH, yBH))
summary(modele)




# 3c métrique de multicollinéarité VIF, et LMG :
# ---------------------------------------------


# calcul metrique VIF :
vif(modele)


# calcul indice LMG :
lmgBH <- lmg(xBH, yBH, nboot=8)

x11() ; plot(lmgBH)
print(lmgBH)




# 3d réduction du nombre d'entrées, R2 of SRC vs LMG :
# ---------------------------------------------


# R2 du modeles apres reduction selon SRC2 :
formule <- as.formula( yBH ~ dis + rad + lstat)
modele <- lm(formule, data.frame(xBH, yBH))
summary(modele)$r.squared


# R2 du modeles apres reduction selon LMG :
formule <- as.formula( yBH ~ rm + ptratio + lstat)
modele <- lm(formule, data.frame(xBH, yBH))
summary(modele)$r.squared
