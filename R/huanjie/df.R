cbind_lists <- function(list_of_lists, empty=NA){
  names <- names(list_of_lists)
  list_of_lists <- lapply(list_of_lists, as.data.frame)
  cols <- sapply(list_of_lists, ncol)
  ncols <- sum(cols)
  rows <- sapply(list_of_lists, nrow)
  max_nrow <- max(rows)
  df <- data.frame(matrix(empty, ncol = ncols, nrow = max_nrow), stringsAsFactors=FALSE)
  idx <- 1
  df_colnames <- character(length=ncols)
  for(i in 1:length(list_of_lists)){
    if(cols[i]==0 || rows[i]==0) next
    df[1:rows[i], idx:idx+cols[i]-1] <- as.character(list_of_lists[[i]][[1]])
    df_colnames[idx:idx+cols[i]-1] <- rep(names[i], cols[i])
    idx <- idx + cols[i]
  }
  colnames(df) <- df_colnames
  return(df)
}

cbind_fill <- function(..., fill=NA){
    nm <- list(...)
    nm <- lapply(nm, as.matrix)
    n <- max(sapply(nm, nrow))
    do.call(cbind, lapply(nm, function (x)
        rbind(x, matrix(fill, n-nrow(x), ncol(x)))))
}
