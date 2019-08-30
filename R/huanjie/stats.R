benjamini_hochberg <- function(pvalues, FDR=0.05){
    if(length(pvalues)==0)
        return(NA)
    real_pvalues <- pvalues[!(is.infinite(pvalues) | is.nan(pvalues) | is.na(pvalues))]
    sorted_values = sort(real_pvalues)
    critical_values = seq(1, length(sorted_values)) / length(sorted_values) * FDR
    idx = sorted_values < critical_values
    if(sum(idx)==0)
        return(NaN)
    else
        return(max(which(idx)))
}
