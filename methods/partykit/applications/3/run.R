# partykit application 3 -- cross-sectional subgroup discovery on the county panel:
# which pre-shock county traits mark the counties hit hardest by the 2007-10 and 2019-20 unemployment shocks?
# Ported from the scout's analysis A4. The scout drew its CV folds after other analyses consumed RNG,
# so fold-dependent numbers (CV RMSE/R2) are compared with a tolerance, plus a 10-seed spread.
a <- commandArgs(trailingOnly = FALSE); source(file.path(dirname(sub("^--file=", "", a[grep("^--file=", a)])), "..", "..", "lib.R"))
set.seed(SEED); res <- list()
P <- read.csv(file.path(WORK, "county_panel.csv"), check.names = TRUE); E <- read.csv(file.path(WORK, "county_edu.csv"))
w <- function(yr, col) { z <- P[P$year == yr, c("fips", col)]; names(z)[2] <- paste0(col, "_", yr); z }
G <- Reduce(function(a, b) merge(a, b, by = "fips"), list(w(2007,"unemp_rate"), w(2010,"unemp_rate"), w(2019,"unemp_rate"), w(2020,"unemp_rate"),
   w(2001,"gdp_.M"), w(2007,"gdp_.M"), w(2014,"gdp_.M"), w(2019,"gdp_.M"), w(2007,"labor_force"), w(2019,"labor_force")))
G <- merge(G, unique(P[P$year == 2023, c("fips","rucc","metro")]), by = "fips")
e00 <- E[E$period == "2000", c("fips","pct_bachelor_plus")]; names(e00)[2] <- "bach_2000"
e08 <- E[grepl("^2008", E$period), c("fips","pct_bachelor_plus")]; names(e08)[2] <- "bach_2008_12"
G <- merge(merge(G, e00, by = "fips"), e08, by = "fips")
G$gr_shock <- G$unemp_rate_2010 - G$unemp_rate_2007; G$cv_shock <- G$unemp_rate_2020 - G$unemp_rate_2019
G$gdp_g_01_07 <- 100 * log(G$gdp_.M_2007 / G$gdp_.M_2001); G$gdp_g_14_19 <- 100 * log(G$gdp_.M_2019 / G$gdp_.M_2014)
G$log_lf07 <- log(G$labor_force_2007); G$log_lf19 <- log(G$labor_force_2019)
G$metro <- factor(G$metro); G$rucc <- as.numeric(G$rucc)
cvrun <- function(fm, dat, K = 5) {
  dat <- dat[complete.cases(dat[, all.vars(fm)]), ]; fold <- sample(rep(1:K, length.out = nrow(dat))); e <- matrix(NA, nrow(dat), 4)
  colnames(e) <- c("mean","ctree","cart","ols")
  for (k in 1:K) { tr <- dat[fold != k, ]; te <- dat[fold == k, ]
    c1 <- ctree(fm, data = tr, control = ctree_control(alpha = 0.01, minbucket = 50, maxdepth = 4))
    rp <- rpart(fm, data = tr, control = rpart.control(cp = 0.001, minbucket = 50)); rp <- prune(rp, cp = rp$cptable[which.min(rp$cptable[, "xerror"]), "CP"])
    y <- te[[all.vars(fm)[1]]]
    e[fold == k, ] <- cbind(mean(tr[[all.vars(fm)[1]]]), predict(c1, te), predict(rp, te), predict(lm(fm, tr), te)) - y }
  rmse <- sqrt(colMeans(e^2)); list(n = nrow(dat), rmse = round(rmse, 4), R2 = round(1 - rmse^2 / rmse[["mean"]]^2, 4)) }
f_gr <- gr_shock ~ unemp_rate_2007 + gdp_g_01_07 + rucc + metro + bach_2000 + log_lf07
f_cv <- cv_shock ~ unemp_rate_2019 + gdp_g_14_19 + rucc + metro + bach_2008_12 + log_lf19
ctl4 <- ctree_control(alpha = 0.01, minbucket = 50, maxdepth = 3)
for (nm in c("gr", "cv")) {
  fm4 <- get(paste0("f_", nm)); dd <- G[complete.cases(G[, all.vars(fm4)]), ]
  t4 <- ctree(fm4, data = dd, control = ctl4)
  png(file.path(FIG, paste0("partykit_app3_", nm, ".png")), width = 1500, height = 700, res = 110); plot(t4, terminal_panel = node_boxplot, gp = gpar(fontsize = 9)); dev.off()
  dd$leaf <- predict(t4, type = "node"); yv <- all.vars(fm4)[1]
  lt <- do.call(rbind, lapply(split(dd, dd$leaf), function(z) data.frame(leaf = z$leaf[1], n = nrow(z), mean_shock = round(mean(z[[yv]]), 2), sd = round(sd(z[[yv]]), 2))))
  lt$rule <- rules_of(t4)[as.character(lt$leaf)]
  res[[paste0("A4_", nm, "_leaves")]] <- lt; res[[paste0("A4_", nm, "_cv")]] <- cvrun(fm4, G); res[[paste0("A4_", nm, "_root")]] <- root_of(t4)
  # ---- new robustness checks ----
  res[[paste0("R_", nm, "_cv_10seeds")]] <- t(sapply(1:10, function(s) { set.seed(SEED + s); cvrun(fm4, G)$R2 }))
  set.seed(SEED + 200); res[[paste0("R_", nm, "_null_iid_split_rate")]] <- null_split_rate(fm4, dd, ctl4, 50, "iid")
}
write_results(res)
