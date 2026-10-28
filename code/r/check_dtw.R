# Parity check for distances.R. Run from the repository root:
#   uv run python scripts/parity_dtw.py && Rscript code/r/check_dtw.R
# Checks: hand cases, every fixture pair against the dtw package (w = 4 and
# no window), and the whole R matrix against the Python matrix.

for (f in c("code/r/distances.R", "fixtures/demand-12.csv")) {
  if (!file.exists(f)) {
    cat("Missing", f, "- run from the repository root: Rscript code/r/check_dtw.R\n")
    quit(status = 1)
  }
}
source("code/r/distances.R")
library(dtw)

cat("R", as.character(getRversion()), "| dtw", as.character(packageVersion("dtw")), "\n")

failures <- 0
fail <- function(msg) {
  cat("FAIL:", msg, "\n")
  failures <<- failures + 1
}
close_enough <- function(x, ref) abs(x - ref) <= 1e-12 + 1e-10 * abs(ref)
worst <- 0
track <- function(x, ref) worst <<- max(worst, abs(x - ref))

# 1. Hand cases (same literal values as the Python tests)
h1 <- dtw_distance(c(0, 1, 2), c(0, 1, 1, 2))
if (h1 != 0) fail(paste("hand case 1: got", h1))
h2 <- dtw_distance(c(0, 2), c(1))
if (!close_enough(h2, sqrt(2))) fail(paste("hand case 2: got", h2))

# 2. Fixture, read with base R: columns id, hour_group, shape_group, v00...
fx <- read.csv("fixtures/demand-12.csv", stringsAsFactors = FALSE)
ids <- fx$id
X <- as.matrix(fx[, grepl("^v", names(fx))])
n <- nrow(X)

# Reference: the dtw package on the squared local cost matrix
reference <- function(a, b, w) {
  cm <- outer(a, b, function(u, v) (u - v)^2)
  r <- if (is.null(w)) {
    dtw::dtw(cm, step.pattern = dtw::symmetric1, window.type = "none")
  } else {
    dtw::dtw(cm, step.pattern = dtw::symmetric1,
             window.type = "sakoechiba", window.size = w)
  }
  sqrt(r$distance)
}

R_w4 <- matrix(0, n, n, dimnames = list(ids, ids))
for (i in seq_len(n - 1)) {
  for (j in (i + 1):n) {
    for (w in list(4, NULL)) {
      mine <- dtw_distance(X[i, ], X[j, ], w)
      ref <- reference(X[i, ], X[j, ], w)
      track(mine, ref)
      if (!close_enough(mine, ref)) {
        fail(sprintf("%s vs %s, w = %s: R %.17g, dtw %.17g",
                     ids[i], ids[j], if (is.null(w)) "none" else w, mine, ref))
      }
    }
    R_w4[i, j] <- R_w4[j, i] <- dtw_distance(X[i, ], X[j, ], 4)
  }
}

# 3. R matrix against the Python matrix, matched by ids
py_file <- "tests/output/py-dtw-w4.csv"
if (!file.exists(py_file)) {
  fail("missing tests/output/py-dtw-w4.csv: run scripts/parity_dtw.py first")
} else {
  py <- read.csv(py_file, stringsAsFactors = FALSE, check.names = FALSE)
  py_ids <- py$id
  PY <- as.matrix(py[, -1])
  rownames(PY) <- py_ids
  if (!setequal(py_ids, ids) || !setequal(colnames(PY), ids)) {
    fail("ids in the Python matrix differ from the fixture")
  } else {
    PY <- PY[ids, ids]
    for (i in seq_len(n)) for (j in seq_len(n)) {
      track(R_w4[i, j], PY[i, j])
      if (!close_enough(R_w4[i, j], PY[i, j])) {
        fail(sprintf("R vs Python, %s vs %s: R %.17g, Python %.17g",
                     ids[i], ids[j], R_w4[i, j], PY[i, j]))
      }
    }
  }
}

cat(sprintf("worst absolute difference: %.3g\n", worst))
if (failures > 0) {
  cat(failures, "check(s) failed\n")
  quit(status = 1)
}
cat("ok\n")
