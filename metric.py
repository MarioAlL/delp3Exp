def getMetric(aprox, exact):
    # aprox = [l,u]
    # exact = [l,u]
    width_aprox = aprox[1] - aprox[0]
    width_exact = exact[1] - exact[0]
    remainder_aprox = 1 - width_aprox
    remainder_exact = 1 - width_exact
    if remainder_exact == 0:
        metric = 0
    else:
        metric = remainder_aprox / remainder_exact
    return "{:.4f}".format(metric) 
