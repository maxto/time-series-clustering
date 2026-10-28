# Reference distances for the course: Euclidean and DTW (R version).
#
# Same contracts as code/python/tsc/distances.py. The loops are plain on
# purpose: this is the version to read and study next to the Python one.
# Invalid input stops with an error (Python raises ValueError).

# Return x as a numeric vector, or stop if it is empty or not finite.
as_series <- function(x) {
  if (!is.numeric(x) || !is.null(dim(x)) || length(x) == 0) {
    stop("a series must be a non-empty 1-D numeric vector")
  }
  if (!all(is.finite(x))) {
    stop("a series must contain only finite numbers")
  }
  as.numeric(x)
}

# Subtract the mean and divide by the population std (divide by n, not n - 1).
# A constant series becomes all zeros.
znorm <- function(x) {
  x <- as_series(x)
  s <- sqrt(mean((x - mean(x))^2))
  if (s == 0) {
    return(rep(0, length(x)))
  }
  (x - mean(x)) / s
}

# Straight-line distance between two series of equal length.
euclidean <- function(x, y) {
  x <- as_series(x)
  y <- as_series(y)
  if (length(x) != length(y)) {
    stop("euclidean needs series of equal length")
  }
  sqrt(sum((x - y)^2))
}

# DTW distance: square root of the accumulated squared cost.
# w is the Sakoe-Chiba half-width in samples (NULL means no window).
# Named dtw_distance so it does not clash with the dtw package.
dtw_distance <- function(x, y, w = NULL) {
  x <- as_series(x)
  y <- as_series(y)
  n <- length(x)
  m <- length(y)

  if (is.null(w)) {
    w <- max(n, m)  # wide enough to never bind
  } else {
    if (!is.numeric(w) || length(w) != 1 || is.na(w) || w < 0 || w != round(w)) {
      stop("w must be a non-negative integer or NULL")
    }
    if (w < abs(n - m)) {
      stop("no admissible path: w < |length(x) - length(y)|")
    }
  }

  # D[i, j] = cheapest cost of reaching cell (i, j). R indexes from 1, so the
  # window |i - j| <= w is the same test as in Python. Outside it D stays Inf.
  D <- matrix(Inf, n, m)
  for (i in 1:n) {
    for (j in max(1, i - w):min(m, i + w)) {
      local <- (x[i] - y[j])^2
      if (i == 1 && j == 1) {
        D[i, j] <- local  # closed start
      } else {
        # cheapest way in: from above, from the left, or diagonally
        up <- if (i > 1) D[i - 1, j] else Inf
        left <- if (j > 1) D[i, j - 1] else Inf
        diag <- if (i > 1 && j > 1) D[i - 1, j - 1] else Inf
        D[i, j] <- local + min(up, left, diag)
      }
    }
  }
  sqrt(D[n, m])  # closed end, no length normalisation
}
