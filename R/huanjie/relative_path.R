
##. determine the path of this script
relative.file.path <- function() {
  cmdArgs <- commandArgs(trailingOnly = FALSE)
  needle <- "--file="
  match <- grep(needle, cmdArgs)
  if (length(match) > 0) {
    # Rscript
    return(dirname(sub(needle, "", cmdArgs[match])))
  } else {
    # 'source'd via R console
    currentPath <- paste0(getwd(), "/")
    scriptPath <- dirname(sys.frames()[[1]]$ofile)
    relativePath <- gsub(currentPath, "", scriptPath)
    return(relativePath)
  }
}
