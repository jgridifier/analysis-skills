# Shared helpers for the partykit applications. Sourced by applications/*/run.R.
suppressMessages({library(partykit); library(rpart); library(jsonlite)})
args_dir <- function() {
  a <- commandArgs(trailingOnly = FALSE); f <- sub("^--file=", "", a[grep("^--file=", a)])
  normalizePath(dirname(f))
}
HERE <- args_dir()
ROOT <- normalizePath(file.path(HERE, "..", "..", "..", ".."))
WORK <- Sys.getenv("AS_WORK_DIR", file.path(ROOT, ".work", "panels"))
OUT  <- file.path(HERE, "out"); dir.create(OUT, showWarnings = FALSE)
FIG  <- Sys.getenv("AS_FIG_DIR", OUT); dir.create(FIG, showWarnings = FALSE, recursive = TRUE)
SEED <- 20261110L
root_of <- function(t) { n <- node_party(t); if (is.terminal(n)) return(c(var="(none)", thr=NA))
  s <- split_node(n); c(var=names(t$data)[varid_split(s)], thr=if (is.null(breaks_split(s))) NA else round(breaks_split(s), 3)) }
n_leaves <- function(t) length(nodeids(t, terminal = TRUE))
rules_of <- function(t) partykit:::.list.rules.party(t)
write_results <- function(res) {
  res$versions <- list(R = R.version.string, partykit = as.character(packageVersion("partykit")),
                       rpart = as.character(packageVersion("rpart")))
  writeLines(toJSON(res, auto_unbox = TRUE, pretty = TRUE, digits = 5), file.path(OUT, "results.json"))
  cat("wrote", file.path(OUT, "results.json"), "\n")
}
# Null checks: how often does a tree split when the response carries no information?
#  iid   = permute y across rows (destroys all structure, incl. autocorrelation)
#  shift = circularly shift y by a random offset (keeps y's own autocorrelation; the honest null
#          for time series, where ctree's exchangeability assumption fails)
null_split_rate <- function(fm, d, ctl, B = 100, kind = c("iid", "shift")) {
  kind <- match.arg(kind); y <- all.vars(fm)[1]; n <- nrow(d); hit <- 0
  for (b in 1:B) { dd <- d
    dd[[y]] <- if (kind == "iid") sample(d[[y]]) else { k <- sample(12:(n - 12), 1); d[[y]][c((k + 1):n, 1:k)] }
    if (n_leaves(ctree(fm, data = dd, control = ctl)) > 1) hit <- hit + 1 }
  hit / B
}
