#!/usr/bin/env Rscript
# General regime / subgroup tree analysis, following run-regime-tree-analysis/SKILL.md.
#
#   Rscript regime_tree.R --csv panel.csv --formula "y ~ x1 + x2" [--mode ctree|mob] [--time-col date]
#                         [--alpha 0.05] [--minbucket 24] [--maxdepth 3] [--B 200] [--block 24] [--gap h] [--out report.json]
#   --gap h: drop the last h training rows at each walk-forward origin (set h = forecast horizon so targets do not overlap)
#   Rscript regime_tree.R --synthetic        # self-test (used by CI)
#
# mode ctree: conditional inference tree on the formula.  mode mob: lmtree, formula "y ~ x | z1 + z2".
# With --time-col the data are treated as a time series: block bootstrap, circular-shift null, walk-forward
# comparison against the historical mean.  Without it: case bootstrap, iid-permutation null, K-fold CV vs CART/OLS.
suppressMessages({library(partykit); library(rpart); library(jsonlite)})
opt <- list(mode = "ctree", alpha = 0.05, minbucket = 24, maxdepth = 3, B = 200, block = 24, seed = 20261110, nulls = 100, gap = 0)
a <- commandArgs(trailingOnly = TRUE); i <- 1
while (i <= length(a)) { k <- sub("^--", "", a[i]); if (k == "synthetic") { opt$synthetic <- TRUE; i <- i + 1; next }
  opt[[gsub("-", "_", k)]] <- a[i + 1]; i <- i + 2 }
for (k in c("alpha","minbucket","maxdepth","B","block","seed","nulls","gap")) opt[[k]] <- as.numeric(opt[[k]])

n_leaves <- function(t) length(nodeids(t, terminal = TRUE))
root_var <- function(t) { n <- node_party(t); if (is.terminal(n)) "(none)" else names(t$data)[varid_split(split_node(n))] }
fit <- function(fm, d) if (opt$mode == "mob") lmtree(fm, data = d, minsize = opt$minbucket, alpha = opt$alpha, maxdepth = opt$maxdepth + 1) else
  ctree(fm, data = d, control = ctree_control(alpha = opt$alpha, minbucket = opt$minbucket, maxdepth = opt$maxdepth))

analyse <- function(d, fm, ts) {
  set.seed(opt$seed); y <- all.vars(fm)[1]; t0 <- fit(fm, d); res <- list(n = nrow(d), mode = opt$mode, time_series = ts)
  d$.leaf <- predict(t0, newdata = d, type = "node"); rl <- partykit:::.list.rules.party(t0)
  res$leaves <- do.call(rbind, lapply(split(d, d$.leaf), function(z) data.frame(leaf = z$.leaf[1], n = nrow(z),
    mean_y = mean(z[[y]]), sd_y = sd(z[[y]]))))
  res$leaves$rule <- rl[as.character(res$leaves$leaf)]
  if (opt$mode == "mob") res$leaf_coefs <- coef(t0)
  # stability: (block) bootstrap of the root variable
  roots <- replicate(opt$B, { idx <- if (ts) { nb <- ceiling(nrow(d) / opt$block); st <- sample(1:(nrow(d) - opt$block + 1), nb, TRUE)
      unlist(lapply(st, function(s) s:(s + opt$block - 1)))[1:nrow(d)] } else sample(nrow(d), replace = TRUE)
    root_var(fit(fm, d[idx, ])) })
  res$bootstrap_root_freq <- as.list(sort(table(roots), decreasing = TRUE) / opt$B); res$root <- root_var(t0)
  # null: iid permutation (cross-section) or circular shift (time series) of the response
  hit <- 0; for (b in 1:opt$nulls) { dd <- d; dd[[y]] <- if (ts) { k <- sample(12:(nrow(d) - 12), 1); d[[y]][c((k + 1):nrow(d), 1:k)] } else sample(d[[y]])
    if (n_leaves(fit(fm, dd)) > 1) hit <- hit + 1 }
  res$null_kind <- if (ts) "circular shift of y" else "iid permutation of y"; res$null_split_rate <- hit / opt$nulls
  # baseline: walk-forward vs historical mean (ts) or 5-fold CV vs mean / CART / OLS (cross-section)
  fm_flat <- if (opt$mode == "mob") as.formula(paste(y, "~", paste(setdiff(all.vars(fm), y), collapse = "+"))) else fm
  if (ts) { cut <- seq(floor(nrow(d) * .5), nrow(d) - 1, by = max(1, floor(nrow(d) * .05))); e <- NULL
    for (j in seq_along(cut)) { tr <- d[1:(cut[j] - opt$gap), ]; te <- d[(cut[j] + 1):min(nrow(d), if (j < length(cut)) cut[j + 1] else nrow(d)), ]
      e <- rbind(e, cbind(y = te[[y]], mean = mean(tr[[y]]), tree = predict(fit(fm, tr), newdata = te))) }
    res$walkforward_R2_vs_hist_mean <- 1 - sum((e[, "y"] - e[, "tree"])^2) / sum((e[, "y"] - e[, "mean"])^2)
  } else { fold <- sample(rep(1:5, length.out = nrow(d))); e <- matrix(NA, nrow(d), 4, dimnames = list(NULL, c("mean","tree","cart","ols")))
    for (k in 1:5) { tr <- d[fold != k, ]; te <- d[fold == k, ]; rp <- rpart(fm_flat, data = tr, control = rpart.control(cp = 0.001, minbucket = opt$minbucket))
      rp <- prune(rp, cp = rp$cptable[which.min(rp$cptable[, "xerror"]), "CP"])
      e[fold == k, ] <- cbind(mean(tr[[y]]), predict(fit(fm, tr), newdata = te), predict(rp, te), predict(lm(fm_flat, tr), te)) - te[[y]] }
    rmse <- sqrt(colMeans(e^2)); res$cv_R2 <- as.list(round(1 - rmse^2 / rmse[["mean"]]^2, 4)) }
  res$verdict <- if (n_leaves(t0) == 1) "no split" else if (res$null_split_rate > 2 * opt$alpha) "NOT distinguishable from the null: describe as exploratory only" else "splits clear the null"
  res
}

if (isTRUE(opt$synthetic)) {
  set.seed(1); n <- 600; x1 <- runif(n); x2 <- runif(n); x3 <- runif(n)
  d <- data.frame(y = ifelse(x1 > 0.5, 2, 0) + rnorm(n), x1, x2, x3)
  opt$B <- 30; opt$nulls <- 20; opt$minbucket <- 30
  r <- analyse(d, y ~ x1 + x2 + x3, FALSE)
  stopifnot(r$root == "x1", r$null_split_rate <= 0.2, r$cv_R2$tree > 0.3)
  opt$mode <- "mob"; d$z <- runif(n); d$y2 <- ifelse(d$z > 0.5, 2, 0.2) * d$x2 + rnorm(n, sd = .3)
  r2 <- analyse(d, y2 ~ x2 | z + x3, FALSE); stopifnot(r2$root == "z")
  cat("synthetic OK: ctree root", r$root, "| null split rate", r$null_split_rate, "| CV R2", r$cv_R2$tree, "| mob root", r2$root, "\n")
  quit(status = 0)
}
d <- read.csv(opt$csv); ts <- !is.null(opt$time_col)
if (ts) d <- d[order(d[[opt$time_col]]), ]
fm <- as.formula(opt$formula); d <- d[complete.cases(d[, all.vars(fm)]), ]
r <- analyse(d, fm, ts)
txt <- toJSON(r, auto_unbox = TRUE, pretty = TRUE, digits = 5)
if (!is.null(opt$out)) writeLines(txt, opt$out) else cat(txt, "\n")
