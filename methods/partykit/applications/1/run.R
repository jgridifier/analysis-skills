# partykit application 1 -- credit-spread regimes with a conditional inference tree (ctree).
# Question: which macro-financial states precede large 6-month moves in the GZ credit spread?
# Ported from the 2026-11-10 scout (m1_partykit.R, analyses A1 + A2). Order of RNG use is kept
# identical to the scout so the bootstrap reproduces exactly; new checks run afterwards.
a <- commandArgs(trailingOnly = FALSE); source(file.path(dirname(sub("^--file=", "", a[grep("^--file=", a)])), "..", "..", "lib.R"))
set.seed(SEED); res <- list()
M <- read.csv(file.path(WORK, "monthly_panel.csv")); M$date <- as.Date(M$date)
feats <- c("VIXCLS","T10Y2Y","NFCI","DGS2","dDGS2_12","ebp","dMORT_12","dGZ_3")
fm <- as.formula(paste("y_fwd6 ~", paste(feats, collapse = "+")))
d <- M[complete.cases(M[, c("y_fwd6", feats)]), ]
res$A1_sample <- list(n = nrow(d), start = as.character(min(d$date)), end = as.character(max(d$date)))
ctl <- ctree_control(alpha = 0.05, minbucket = 24, maxdepth = 3)
ct <- ctree(fm, data = d, control = ctl)
png(file.path(FIG, "partykit_app1_ctree.png"), width = 1500, height = 750, res = 110)
plot(ct, terminal_panel = node_boxplot, gp = gpar(fontsize = 9)); dev.off()
d$leaf <- predict(ct, type = "node")
lt <- do.call(rbind, lapply(split(d, d$leaf), function(z) data.frame(leaf = z$leaf[1], n = nrow(z),
  mean_fwd6 = mean(z$y_fwd6), sd_fwd6 = sd(z$y_fwd6), p_widen_gt50bp = mean(z$y_fwd6 > 0.5),
  first = as.character(min(z$date)), last = as.character(max(z$date)))))
lt$rule <- rules_of(ct)[as.character(lt$leaf)]; res$A1_leaves <- lt
# walk-forward (annual refits from 2004; training window ends 6 months before the refit date)
refits <- seq(as.Date("2004-01-31"), max(d$date), by = "12 months"); pred <- data.frame()
for (i in seq_along(refits)) {
  r <- refits[i]; nxt <- if (i < length(refits)) refits[i + 1] else max(d$date) + 1
  tr <- d[d$date <= seq(r, by = "-6 months", length.out = 2)[2], ]; te <- d[d$date >= r & d$date < nxt, ]
  if (nrow(te) == 0) next
  c1 <- ctree(fm, data = tr, control = ctl)
  rp <- rpart(fm, data = tr, control = rpart.control(cp = 0.001, minbucket = 24, xval = 10))
  rp <- prune(rp, cp = rp$cptable[which.min(rp$cptable[, "xerror"]), "CP"]); ol <- lm(fm, data = tr)
  pred <- rbind(pred, data.frame(date = te$date, y = te$y_fwd6, mean = mean(tr$y_fwd6), ctree = predict(c1, te),
    cart = predict(rp, te), ols = predict(ol, te), ctree_leaves = n_leaves(c1)))
}
oos <- function(p) c(R2_vs_hist_mean = 1 - sum((pred$y - p)^2) / sum((pred$y - pred$mean)^2), MAE = mean(abs(pred$y - p)), corr = cor(pred$y, p))
res$A1_walkforward <- list(n_oos = nrow(pred), period = c(as.character(min(pred$date)), as.character(max(pred$date))),
  ctree = oos(pred$ctree), cart = oos(pred$cart), ols = oos(pred$ols), hist_mean = oos(pred$mean), ctree_leaves_range = range(pred$ctree_leaves))
# A2 stability: split windows + 24-month block bootstrap of the root split
win <- list(`1990-2007` = d[d$date < as.Date("2008-01-01"), ], `2008-2026` = d[d$date >= as.Date("2008-01-01"), ], full = d)
res$A2_windows <- do.call(rbind, lapply(names(win), function(k) { t <- ctree(fm, data = win[[k]], control = ctl); r <- root_of(t)
  data.frame(window = k, n = nrow(win[[k]]), root_var = r[["var"]], root_thr = r[["thr"]], leaves = n_leaves(t)) }))
boot_roots <- function(B = 300, L = 24) { nb <- ceiling(nrow(d) / L); roots <- character(B); thr <- numeric(B); lv <- integer(B)
  for (b in 1:B) { st <- sample(1:(nrow(d) - L + 1), nb, replace = TRUE); idx <- unlist(lapply(st, function(s) s:(s + L - 1)))[1:nrow(d)]
    t <- ctree(fm, data = d[idx, ], control = ctl); r <- root_of(t); roots[b] <- r[["var"]]; thr[b] <- as.numeric(r[["thr"]]); lv[b] <- n_leaves(t) }
  list(roots = roots, thr = thr, lv = lv) }
bb <- boot_roots()
res$A2_boot_root_freq <- as.list(sort(table(bb$roots), decreasing = TRUE) / 300)
res$A2_boot_thr_by_var <- lapply(split(bb$thr, bb$roots), function(x) round(quantile(x, c(.1, .5, .9), na.rm = TRUE), 3))
res$A2_boot_leaves <- as.list(table(bb$lv) / 300)
# ---- new robustness checks (Stage 3), after the scout's RNG stream ----
res$R_boot_seeds_VIX_root_freq <- sapply(1:5, function(s) { set.seed(SEED + s); mean(boot_roots()$roots == "VIXCLS") })
set.seed(SEED + 100)
res$R_null_split_rate <- list(iid = null_split_rate(fm, d, ctl, 100, "iid"), circular_shift = null_split_rate(fm, d, ctl, 100, "shift"))
write_results(res)
