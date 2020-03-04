
tempoRatio <- function(t1, t2, harmonics = c(2,3)) {
     lograts <- sapply(harmonics,
                       function(h) {
                            diff(log(c(t1, t2), h)) %% 1
                       })

     lograts <- pmin(lograts, 1 - lograts)

     min(harmonics ^ lograts)


}
