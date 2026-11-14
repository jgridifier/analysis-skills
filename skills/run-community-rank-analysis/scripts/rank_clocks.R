#!/usr/bin/env Rscript
# Community dynamics and rank clocks (codyn).
#   Rscript rank_clocks.R --synthetic
#   Rscript rank_clocks.R --csv panel.csv --time t --unit species --value y --out results.json
#
# Raw amounts for variance_ratio / synchrony; shares for rank_shift and rate_change.

args <- commandArgs(trailingOnly = TRUE)
opt <- list(synthetic = FALSE, csv = NULL, time = "t", unit = "species", value = "y", out = NULL, boots = "29")
i <- 1
while (i <= length(args)) {
  k <- sub("^--", "", args[i])
  if (k == "synthetic") { opt$synthetic <- TRUE; i <- i + 1; next }
  if (i == length(args)) stop("missing value for --", k)
  opt[[k]] <- args[i + 1]; i <- i + 2
}

suppressMessages(library(codyn))
suppressMessages(library(jsonlite))

# Point variance ratio (Loreau / Schluter): var(sum of units) / sum(var of units).
# This is the VR column that codyn::variance_ratio reports; we compute it
# directly so the CI self-test does not need a long cyclic-shift bootstrap.
vr_point <- function(td, time.var, species.var, abundance.var) {
  wide <- reshape(td[, c(time.var, species.var, abundance.var)],
                  idvar = time.var, timevar = species.var, direction = "wide")
  mat <- as.matrix(wide[, setdiff(names(wide), time.var), drop = FALSE])
  as.numeric(stats::var(rowSums(mat)) / sum(apply(mat, 2, stats::var)))
}

cyclic_shift_one <- function(td, time.var, species.var, abundance.var) {
  out <- td
  spp <- unique(td[[species.var]])
  for (s in spp) {
    ix <- which(td[[species.var]] == s)
    ix <- ix[order(td[[time.var]][ix])]
    n <- length(ix)
    lag <- sample(0:(n - 1), 1)
    if (lag) out[[abundance.var]][ix] <- td[[abundance.var]][ix][c((lag + 1):n, seq_len(lag))]
  }
  out
}

synthetic <- function() {
  set.seed(20261113)
  Tm <- 40; S <- 8
  t <- seq_len(Tm)
  # Co-moving community: shared factor + small idiosyncratic noise (raw amounts).
  common <- 10 + 3 * sin(2 * pi * t / 16) + 0.15 * t
  co <- do.call(rbind, lapply(seq_len(S), function(s) {
    data.frame(t = t, species = paste0("c", s),
               y = pmax(0.1, common + rnorm(Tm, 0, 0.4) + s * 0.2))
  }))
  # Independent community: each series has its own unrelated trend + noise.
  ind <- do.call(rbind, lapply(seq_len(S), function(s) {
    phase <- runif(1, 0, 2 * pi)
    data.frame(t = t, species = paste0("i", s),
               y = pmax(0.1, 10 + 3 * sin(2 * pi * t / (8 + s) + phase) + rnorm(Tm, 0, 1.2)))
  }))

  vr_co <- vr_point(co, "t", "species", "y")
  vr_ind <- vr_point(ind, "t", "species", "y")
  # Short cyclic-shift null on the co-moving set (CI, not 999 draws).
  B <- 19
  set.seed(20261113 + 1)
  null_co <- replicate(B, vr_point(cyclic_shift_one(co, "t", "species", "y"), "t", "species", "y"))
  set.seed(20261113 + 2)
  null_ind <- replicate(B, vr_point(cyclic_shift_one(ind, "t", "species", "y"), "t", "species", "y"))

  stopifnot(is.finite(vr_co) && vr_co > 1)
  stopifnot(vr_co > max(null_co))
  # Independent series should not be as synchronized; VR should sit inside or below the high end of its null.
  stopifnot(is.finite(vr_ind))
  stopifnot(vr_ind < vr_co)
  stopifnot(vr_ind <= max(null_ind) * 1.05)

  # Designed rank swap on shares: species A starts first, ends last; B the reverse.
  # Four species, deterministic shares so rank_shift must see the swap.
  ranks <- data.frame()
  for (tt in 1:20) {
    # linear swap of A and B; C and D stay in the middle
    a <- 0.40 - 0.02 * (tt - 1)   # 0.40 -> 0.02
    b <- 0.10 + 0.02 * (tt - 1)   # 0.10 -> 0.48
    c <- 0.30
    d <- 1 - a - b - c
    ranks <- rbind(ranks,
                   data.frame(t = tt, species = c("A", "B", "C", "D"),
                              y = c(a, b, c, d)))
  }
  rs <- rank_shift(ranks, time.var = "t", species.var = "species", abundance.var = "y")
  mrs <- mean(rs[[ncol(rs)]])
  stopifnot(mrs > 0)
  # End ranks: A last (4), B first (1)
  end <- ranks[ranks$t == 20, ]
  end$rank <- rank(-end$y, ties.method = "first")
  start <- ranks[ranks$t == 1, ]
  start$rank <- rank(-start$y, ties.method = "first")
  stopifnot(start$rank[start$species == "A"] == 1)
  stopifnot(end$rank[end$species == "A"] == 4)
  stopifnot(start$rank[start$species == "B"] == 4)
  stopifnot(end$rank[end$species == "B"] == 1)

  # Stored-original lock when the aggregate file is in the repo.
  args_cmd <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args_cmd, value = TRUE)
  if (length(file_arg)) {
    script_dir <- dirname(normalizePath(sub("^--file=", "", file_arg)))
    agg_path <- file.path(script_dir, "..", "..", "..", "methods", "codyn", "original", "scout_aggregates.json")
    if (file.exists(agg_path)) {
      orig <- fromJSON(agg_path, simplifyVector = FALSE)
      stopifnot(abs(orig$A$vr$VR - 4.4536782878) < 1e-9)
      stopifnot(abs(orig$A$vr$lowerCI - 0.43762295713) < 1e-9)
      stopifnot(abs(orig$A$vr$upperCI - 2.0025608176) < 1e-9)
      stopifnot(abs(orig$A$leaveout$foreign_only$VR - 0.72921075224) < 1e-9)
      stopifnot(abs(orig$A$rate_null$p_ge - 0.001) < 1e-12)
      cat("original aggregates lock: PASS\n")
    }
  }

  cat("synthetic OK: VR_co", signif(vr_co, 4), "null_co max", signif(max(null_co), 4),
      "VR_ind", signif(vr_ind, 4), "MRS_swap", signif(mrs, 4), "\n")
  invisible(list(vr_co = vr_co, vr_ind = vr_ind, mrs = mrs))
}

if (isTRUE(opt$synthetic)) {
  synthetic()
  quit(status = 0)
}

if (is.null(opt$csv)) stop("pass --csv or --synthetic")
dat <- read.csv(opt$csv, stringsAsFactors = FALSE)
for (col in c(opt$time, opt$unit, opt$value)) {
  if (!(col %in% names(dat))) stop("csv must have column ", col)
}
td <- dat[, c(opt$time, opt$unit, opt$value)]
names(td) <- c("t", "species", "y")
# shares for rank metrics
tot <- ave(td$y, td$t, FUN = sum)
td$share <- td$y / tot
vr <- vr_point(td, "t", "species", "y")
rs <- rank_shift(td, time.var = "t", species.var = "species", abundance.var = "share")
rc <- rate_change(td, time.var = "t", species.var = "species", abundance.var = "share")
syn <- tryCatch(synchrony(td, time.var = "t", species.var = "species", abundance.var = "y", metric = "Loreau"), error = function(e) NA)
res <- list(
  n_times = length(unique(td$t)),
  n_units = length(unique(td$species)),
  variance_ratio = vr,
  rank_shift_mean = mean(rs[[ncol(rs)]]),
  rate_change = as.numeric(rc),
  synchrony = as.numeric(syn),
  note = "VR and synchrony used raw y; rank_shift and rate_change used shares. Run a cyclic-shift null before reporting co-movement or a directional walk."
)
cat(toJSON(res, auto_unbox = TRUE, pretty = TRUE, digits = NA), "\n")
if (!is.null(opt$out)) write_json(res, opt$out, auto_unbox = TRUE, digits = NA)
