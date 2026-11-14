#!/usr/bin/env Rscript
# Empirical Bayes shrinkage for many noisy observations (ebnm).
#   Rscript shrinkage.R --synthetic          # self-test (used by CI)
#   Rscript shrinkage.R --csv data.csv --x x --s s --out results.json

args <- commandArgs(trailingOnly = TRUE)
opt <- list(synthetic = FALSE, csv = NULL, x = "x", s = "s", prior = "normal_scale_mixture", out = NULL)
i <- 1
while (i <= length(args)) {
  k <- sub("^--", "", args[i])
  if (k == "synthetic") { opt$synthetic <- TRUE; i <- i + 1; next }
  if (i == length(args)) stop("missing value for --", k)
  opt[[k]] <- args[i + 1]; i <- i + 2
}

suppressMessages(library(ebnm))
suppressMessages(library(jsonlite))

analyse <- function(x, s, prior_family = "normal_scale_mixture", mode = 0) {
  raw_rmse <- function(est, truth) sqrt(mean((est - truth)^2))
  fit <- ebnm(x, s, prior_family = prior_family, mode = mode, output = ebnm_output_all())
  list(
    n = length(x),
    prior_family = prior_family,
    loglik = as.numeric(fit$log_likelihood),
    posterior_mean = as.numeric(fit$posterior$mean),
    posterior_sd = as.numeric(fit$posterior$sd),
    lfsr = as.numeric(fit$posterior$lfsr),
    n_calls_lfsr_05 = as.integer(sum(fit$posterior$lfsr < 0.05, na.rm = TRUE))
  )
}

synthetic <- function() {
  set.seed(20261113)
  n <- 400
  # Spike-and-slab: 70% exact zeros, 30% N(0, 2^2); observation noise s = 0.5
  z <- rbinom(n, 1, 0.3)
  theta <- z * rnorm(n, 0, 2)
  s <- rep(0.5, n)
  x <- theta + rnorm(n, 0, s)

  fit <- ebnm(x, s, prior_family = "normal_scale_mixture", mode = 0, output = ebnm_output_all())
  pm <- fit$posterior$mean
  lfsr <- fit$posterior$lfsr
  rmse_raw <- sqrt(mean((x - theta)^2))
  rmse_eb <- sqrt(mean((pm - theta)^2))
  # calls
  call <- lfsr < 0.05
  n_calls <- sum(call)
  # false sign: called, and sign of posterior mean disagrees with true theta (zeros count as wrong if called)
  false_sign <- call & (sign(pm) != sign(theta) | theta == 0)
  fsr <- if (n_calls == 0) NA_real_ else mean(false_sign[call])
  true_pos <- sum(call & theta != 0 & sign(pm) == sign(theta))

  # also the complete-pooled and unpooled comparisons used on the scout
  rmse_pool <- sqrt(mean((mean(x) - theta)^2))

  stopifnot(rmse_eb < rmse_raw)
  stopifnot(rmse_eb < rmse_pool)
  stopifnot(n_calls >= 20)
  stopifnot(is.finite(fsr) && fsr <= 0.05)
  stopifnot(true_pos >= 20)

  # Consistency lock on the scout aggregates that RESULTS.md quotes, when present.
  args_cmd <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args_cmd, value = TRUE)
  if (length(file_arg)) {
    script_dir <- dirname(normalizePath(sub("^--file=", "", file_arg)))
    agg_path <- file.path(script_dir, "..", "..", "..", "methods", "ebnm", "original", "scout_aggregates.json")
    if (file.exists(agg_path)) {
      orig <- fromJSON(agg_path, simplifyVector = FALSE)
      ash <- Filter(function(r) identical(r$estimator, "ebnm: ash"), orig$Corning_mock$A1$table)[[1]]
      raw <- Filter(function(r) identical(r$estimator, "Own 2025 actual (no pooling)"), orig$Corning_mock$A1$table)[[1]]
      stopifnot(abs(raw$rmse_all - 0.145504738140438) < 1e-12)
      stopifnot(abs(ash$rmse_all - 0.107888611153387) < 1e-12)
      ms_ash <- Filter(function(r) identical(r$estimator, "ebnm: ash"), orig$MorganStanley_mock$A1$table)[[1]]
      stopifnot(abs(ms_ash$rmse_all - 0.109302219686466) < 1e-12)
      cor_calls <- Filter(function(r) identical(r$`_row`, "ebnm ash, lfsr<0.05"), orig$Corning_mock$A2$calls)[[1]]
      stopifnot(as.integer(cor_calls$n_calls) == 91L)
      stopifnot(all.equal(as.numeric(cor_calls$false_sign_rate), 0))
      stopifnot(as.integer(cor_calls$true_pos) == 91L)
      cat("original aggregates lock: PASS\n")
    }
  }

  out <- list(
    rmse_raw = rmse_raw, rmse_eb = rmse_eb, rmse_pool = rmse_pool,
    n_calls_lfsr_05 = as.integer(n_calls), false_sign_rate = fsr, true_pos = as.integer(true_pos)
  )
  cat("synthetic OK: rmse_raw", signif(rmse_raw, 4), "rmse_eb", signif(rmse_eb, 4),
      "calls", n_calls, "fsr", signif(fsr, 3), "true_pos", true_pos, "\n")
  invisible(out)
}

if (isTRUE(opt$synthetic)) {
  synthetic()
  quit(status = 0)
}

if (is.null(opt$csv)) stop("pass --csv or --synthetic")
dat <- read.csv(opt$csv, stringsAsFactors = FALSE)
if (!(opt$x %in% names(dat) && opt$s %in% names(dat))) {
  stop("csv must have columns ", opt$x, " and ", opt$s)
}
x <- dat[[opt$x]]; s <- dat[[opt$s]]
ok <- is.finite(x) & is.finite(s) & s > 0
res <- analyse(x[ok], s[ok], prior_family = opt$prior)
# do not dump every posterior in the default print; write full if --out
summary <- list(
  n = res$n, prior_family = res$prior_family, loglik = res$loglik,
  n_calls_lfsr_05 = res$n_calls_lfsr_05,
  posterior_mean_mean = mean(res$posterior_mean),
  posterior_mean_sd = sd(res$posterior_mean)
)
cat(toJSON(summary, auto_unbox = TRUE, pretty = TRUE), "\n")
if (!is.null(opt$out)) {
  write_json(res, opt$out, auto_unbox = TRUE, digits = NA)
}
