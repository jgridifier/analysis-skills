# partykit application 2 -- model-based tree (MOB / lmtree): does the sensitivity of credit-spread
# changes to VIX and 10y-yield shocks depend on the financial-conditions regime or on calendar time?
# Ported from the scout's analysis A3. Deterministic (no RNG in lmtree); new checks are appended.
a <- commandArgs(trailingOnly = FALSE); source(file.path(dirname(sub("^--file=", "", a[grep("^--file=", a)])), "..", "..", "lib.R"))
suppressMessages(library(strucchange)); set.seed(SEED); res <- list()
M <- read.csv(file.path(WORK, "monthly_panel.csv")); M$date <- as.Date(M$date)
d3 <- M[complete.cases(M[, c("dGZ","dVIX","dDGS10","T10Y2Y","NFCI","DGS2")]), ]
d3$time <- as.numeric(format(d3$date, "%Y")) + (as.numeric(format(d3$date, "%m")) - 0.5) / 12
fm <- dGZ ~ dVIX + dDGS10 | T10Y2Y + NFCI + DGS2 + time
mb <- lmtree(fm, data = d3, minsize = 36, alpha = 0.01, bonferroni = TRUE)
png(file.path(FIG, "partykit_app2_mob.png"), width = 1500, height = 750, res = 110); plot(mb, gp = gpar(fontsize = 9)); dev.off()
cf <- coef(mb); cf <- if (is.null(dim(cf))) t(as.matrix(cf)) else cf
nodes <- nodeids(mb, terminal = TRUE); d3$leaf <- predict(mb, type = "node")
res$A3_leaves <- data.frame(leaf = nodes, n = as.integer(table(factor(d3$leaf, levels = nodes))), round(cf, 4), rule = rules_of(mb)[as.character(nodes)], row.names = NULL)
pooled <- lm(dGZ ~ dVIX + dDGS10, data = d3)
res$A3_pooled <- round(coef(pooled), 4); res$A3_BIC <- c(pooled = BIC(pooled), mob = BIC(mb)); res$A3_n <- nrow(d3)
res$A3_root_tests <- round(sctest.modelparty(mb, node = 1), 5)
# ---- new robustness checks ----
# (a) windows: refit on 1990-2007 and 2008-2026
res$R_windows <- lapply(list(pre2008 = d3[d3$date < as.Date("2008-01-01"), ], post2008 = d3[d3$date >= as.Date("2008-01-01"), ]), function(w) {
  m <- lmtree(fm, data = w, minsize = 36, alpha = 0.01, bonferroni = TRUE); r <- root_of(m)
  list(n = nrow(w), leaves = n_leaves(m), root_var = r[["var"]], root_thr = r[["thr"]]) })
# (b) leave-crisis-out: drop 2008-09 and 2020-03..2020-06, refit
keep <- !(format(d3$date, "%Y") %in% c("2008", "2009") | (d3$date >= as.Date("2020-03-01") & d3$date <= as.Date("2020-06-30")))
m2 <- lmtree(fm, data = d3[keep, ], minsize = 36, alpha = 0.01, bonferroni = TRUE); r2 <- root_of(m2)
res$R_ex_crises <- list(n = sum(keep), leaves = n_leaves(m2), root_var = r2[["var"]], root_thr = r2[["thr"]])
# (c) null: circularly shift the partitioning variables (keeps their persistence, breaks their link to time t)
hits <- 0; B <- 100
for (b in 1:B) { dd <- d3; k <- sample(24:(nrow(d3) - 24), 1); idx <- c((k + 1):nrow(d3), 1:k)
  for (v in c("T10Y2Y","NFCI","DGS2")) dd[[v]] <- d3[[v]][idx]
  dd$time <- d3$time  # time itself stays aligned
  m <- lmtree(dGZ ~ dVIX + dDGS10 | T10Y2Y + NFCI + DGS2, data = dd, minsize = 36, alpha = 0.01, bonferroni = TRUE)
  if (n_leaves(m) > 1) hits <- hits + 1 }
res$R_null_shift_split_rate <- hits / B
# (d) baseline: OLS with a full interaction on an NFCI>0.057 dummy vs MOB BIC, and an OLS with a 2008 time break
d3$hi <- as.numeric(d3$NFCI > 0.057); d3$post08 <- as.numeric(d3$date >= as.Date("2008-01-01"))
res$R_baseline_BIC <- c(ols_nfci_dummy_interact = BIC(lm(dGZ ~ (dVIX + dDGS10) * hi, data = d3)),
                        ols_2008_break_interact = BIC(lm(dGZ ~ (dVIX + dDGS10) * post08, data = d3)))
write_results(res)
