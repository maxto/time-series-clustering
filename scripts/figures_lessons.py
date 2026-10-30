"""The lesson figures beyond the pilot: one per lesson, each a different form.

Called by scripts/figures.py, same rules: every number from the frozen fixture, classes of
site/theme.css only, deterministic bytes. lesson_figures() returns the SVGs and the numbers the
lessons quote. Colours: the first series or group in ink, the second in accent, noise as an empty box.
"""

import csv

import numpy as np
from scipy.cluster.hierarchy import dendrogram

import figure_measures as fm
from figures import ROOT, W_DTW, WIDTH, document, f, hour_hints, line, polyline, text
from tsc.distances import dtw, euclidean, sbd, znorm
from tsc.group import average_linkage, distance_matrix
from tsc.validity import silhouette_from_matrix

SEMANTIC_ORDER = ["mon", "tue", "sat", "sun", "d08", "d09", "wed", "thu", "fri", "d10", "d11", "d12"]
LCSS_EPS, LCSS_DELTA = 0.25, W_DTW
DBSCAN_EPS, DBSCAN_MIN_PTS = (1.25, 2.0, 2.35), 3
WINDOWS = (0, 2, 4, 6, 10, None)
SHAPELET_LEN = 9
PROFILE_LEN = 8
ACF_LAGS = 24
ORDER_D = 3


def rect(x, y, w, h, cls, extra=""):
    return f'<rect class="{cls}" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"{extra}/>'


def circle(x, y, r, cls):
    return f'<circle class="{cls}" cx="{f(x)}" cy="{f(y)}" r="{f(r)}"/>'


def group_cls(k):
    return "fill-ink" if k == 0 else "fill-accent" if k == 1 else "fill-muted"


def scaled(values, top, h, lo, hi):
    return [top + h - h * (float(v) - lo) / (hi - lo) for v in values]


# --- preprocessing --------------------------------------------------------------------------

def fig_preprocess(day, name):
    d = np.diff(day)
    panels = [("raw values, kW", np.arange(48), day, False),
              ("z-normalised", np.arange(48), znorm(day), True),
              ("first difference", np.arange(1, 48), d, True),
              ("moving average, k = 2", np.arange(2, 46), fm.moving_average(day, 2)[2:46], False),
              ("2-hour means", None, fm.block_mean(day, 4), False)]
    x0, w, h, pitch = 4, WIDTH - 8, 38, 62
    body = []
    for r, (label, idx, y, zero) in enumerate(panels):
        top = r * pitch + 20
        body.append(text(x0, top - 6, label))
        lo, hi = float(np.min(y)), float(np.max(y))
        pad = (hi - lo) * 0.05
        lo, hi = lo - pad, hi + pad
        if idx is None:  # a held value per block: a step line
            pts = []
            for u, v in enumerate(y):
                yy = scaled([v], top, h, lo, hi)[0]
                pts += [(x0 + w * u * 4 / 48, yy), (x0 + w * (u + 1) * 4 / 48, yy)]
        else:
            pts = list(zip(x0 + w * idx / 48, scaled(y, top, h, lo, hi)))
        base = scaled([0], top, h, lo, hi)[0] if zero else top + h
        body.append(line(x0, base, x0 + w, base))
        body.append(polyline(pts, "ln", ' stroke-width="1.5"'))
    bottom = len(panels) * pitch + 12
    body.extend(hour_hints(x0, w, bottom))
    return document(bottom + 6, f"One day, {name}, through four preprocessing steps",
                    f"Five stacked panels of {name}, each on its own vertical scale: raw values, z-normalised values, "
                    "first differences, a moving average over five points, and means over two-hour blocks.", body)


# --- lock-step ------------------------------------------------------------------------------

def heatmap(D, x0, y0, title, pitch=13, gap=1, block=2):
    dmax = float(D.max())
    body = [text(x0, y0 - 8, title)]
    pos = lambda r: r * pitch + block * (r // 3)
    for r in range(12):
        for c in range(12):
            op = 0.06 + 0.94 * (1 - D[r, c] / dmax)
            body.append(f'<rect class="fill-ink" x="{f(x0 + pos(c))}" y="{f(y0 + pos(r))}" width="{pitch - gap}" '
                        f'height="{pitch - gap}" opacity="{op:.2f}"/>')
    return body


def fig_lockstep_matrices(De, Dc):
    body = heatmap(De, 4, 22, "Euclidean") + heatmap(Dc, 196, 22, "Correlation")
    return document(192, "Euclidean and correlation distance matrices of the twelve days",
                    "Two 12 by 12 matrices, rows and columns ordered early two-peak, early flat, late two-peak, late "
                    "flat. Higher opacity means a smaller distance, each panel on its own scale.", body)


# --- sliding --------------------------------------------------------------------------------

def fig_cross_correlation(m, s, w):
    x0, plot_w, top, h, limit = 4, WIDTH - 8, 24, 170, 24
    shifts, a = fm.ncc_curve(m, s)
    _, b = fm.ncc_curve(m, w)
    keep = np.abs(shifts) <= limit
    lo, hi = float(min(a[keep].min(), b[keep].min())), 1.0
    tx = lambda v: x0 + plot_w * (v + limit) / (2 * limit)
    ty = lambda v: scaled([v], top, h, lo, hi)[0]
    body = [line(tx(0), top, tx(0), top + h), line(x0, ty(0), x0 + plot_w, ty(0))]
    body.append(polyline([(tx(v), ty(c)) for v, c in zip(shifts[keep], a[keep])], "ln"))
    body.append(polyline([(tx(v), ty(c)) for v, c in zip(shifts[keep], b[keep])], "ln-accent"))
    sa, sb = int(shifts[np.argmax(a)]), int(shifts[np.argmax(b)])
    body.append(circle(tx(sa), ty(a.max()), 4, "fill-ink"))
    body.append(circle(tx(sb), ty(b.max()), 4, "fill-accent"))
    body += [circle(206, top + 7, 4, "fill-ink"), text(216, top + 12, f"mon, sat: s = {sa}"),
             circle(206, top + 27, 4, "fill-accent"), text(216, top + 32, f"mon, wed: s = {sb}")]
    body += [text(x0, top + h + 18, f"-{limit}"), text(tx(0), top + h + 18, "0", "t-sm t-mono mid"),
             text(x0 + plot_w, top + h + 18, f"+{limit}", "t-sm t-mono end")]
    return document(top + h + 24, "Normalised cross-correlation against the shift",
                    f"NCC_c of the z-normalised pairs mon, sat (ink) and mon, wed (accent) for shifts from -{limit} to "
                    f"+{limit} samples. The maxima sit at s = {sa} and s = {sb}.", body), sa, sb


# --- edit-based -----------------------------------------------------------------------------

def fig_lcss(x, y, nx, ny, pairs):
    x0, w, band, gap = 4, WIDTH - 8, 78, 52
    top_a, top_b = 20, 20 + band + gap
    lo, hi = float(min(x.min(), y.min())), float(max(x.max(), y.max()))
    px = lambda i: x0 + w * i / 47
    ya, yb = scaled(x, top_a, band, lo, hi), scaled(y, top_b, band, lo, hi)
    body = [text(x0, 14, nx), text(x0, top_b - 6, ny)]
    done_a, done_b = {i for i, _ in pairs}, {j for _, j in pairs}
    body += [line(px(i), ya[i], px(j), yb[j]) for i, j in pairs]
    body.append(polyline(list(zip(px(np.arange(48)), ya)), "ln"))
    body.append(polyline(list(zip(px(np.arange(48)), yb)), "ln-accent"))
    body += [circle(px(i), ya[i], 3.2, "fill-ink") for i in range(48) if i not in done_a]
    body += [circle(px(j), yb[j], 3.2, "fill-accent") for j in range(48) if j not in done_b]
    return document(top_b + band + 8, f"LCSS alignment of {nx} and {ny}",
                    f"Two z-normalised days with a line for each of the {len(pairs)} matched pairs, epsilon {LCSS_EPS}, "
                    f"delta {LCSS_DELTA} samples. Dots mark the points left unmatched.", body)


# --- features -------------------------------------------------------------------------------

def fig_acf(a, b, na, nb):
    x0, w, h, pitch = 4, WIDTH - 8, 76, 110
    body = []
    for r, (vals, name, cls) in enumerate(((a, na, "fill-ink"), (b, nb, "fill-accent"))):
        top = r * pitch + 20
        body.append(text(x0, top - 6, name))
        mid = top + h / 2
        body.append(line(x0, mid, x0 + w, mid))
        bw = w / len(vals)
        for k, v in enumerate(vals):
            yy = mid - v * h / 2
            body.append(rect(x0 + k * bw + 1, min(mid, yy), bw - 2, abs(mid - yy), cls))
    bottom = 2 * pitch
    body += [text(x0, bottom + 4, "lag 1"), text(x0 + w, bottom + 4, f"lag {len(a)}", "t-sm t-mono end")]
    return document(bottom + 10, f"Autocorrelation of {na} and {nb}",
                    f"Bars of the sample autocorrelation from lag 1 to lag {len(a)}, half-hour steps, for a two-peak "
                    "day and a flat-block day, on a scale from -1 to 1.", body)


# --- models ---------------------------------------------------------------------------------

def fig_ordinal(patterns, a, b, na, nb):
    x0, w, top, h = 4, WIDTH - 8, 26, 150
    hi = float(max(a.max(), b.max()))
    n = len(patterns)
    slot = w / n
    body = [text(x0, 14, f"{na} in ink, {nb} in accent"), line(x0, top + h, x0 + w, top + h)]
    for k, p in enumerate(patterns):
        for off, vals, cls in ((0, a, "fill-ink"), (1, b, "fill-accent")):
            bh = h * vals[k] / hi
            body.append(rect(x0 + k * slot + 8 + off * (slot - 16) / 2, top + h - bh, (slot - 16) / 2, bh, cls))
        body.append(text(x0 + (k + 0.5) * slot, top + h + 18, "".join(str(v) for v in p), "t-sm t-mono mid"))
    return document(top + h + 24, f"Ordinal patterns of length {ORDER_D}, {na} and {nb}",
                    f"Relative frequency of the {n} ordinal patterns of length {ORDER_D} in the two days.", body)


# --- learned --------------------------------------------------------------------------------

def fig_shapelet_map(ids, points, shapes):
    x0, y0, side_w, side_h = 34, 8, WIDTH - 44, 230
    xs, ys = points[:, 0], points[:, 1]
    lox, hix, loy, hiy = 0.0, float(xs.max()) * 1.1, 0.0, float(ys.max()) * 1.1
    tx = lambda v: x0 + side_w * v / hix
    ty = lambda v: y0 + side_h - side_h * v / hiy
    body = [rect(x0, y0, side_w, side_h, "box")]
    for k in range(len(ids)):
        body.append(circle(tx(xs[k]), ty(ys[k]), 5, "fill-ink" if shapes[k] == "twopeak" else "fill-accent"))
    body += [text(x0, y0 + side_h + 18, "0"), text(x0 + side_w, y0 + side_h + 18, "distance to shapelet A", "t-sm t-mono end"),
             text(x0 - 6, y0 + side_h, "0", "t-sm t-mono end"),
             text(x0 + side_w - 8, y0 + 18, "distance to shapelet B", "t-sm t-mono end")]
    return document(y0 + side_h + 24, "The twelve days in the plane of two shapelets",
                    "Each day is a point: its distance to a shapelet cut from a peak of mon and to a shapelet cut from a "
                    "flat block. Two-peak days in ink, flat-block days in accent.", body)


# --- subsequences ---------------------------------------------------------------------------

def fig_profile(a, b, na, nb):
    x0, w, top, h = 4, WIDTH - 8, 24, 150
    hi = float(max(a.max(), b.max())) * 1.05
    n = len(a)
    tx = lambda i: x0 + w * i / 48  # a window sits at its start, half-hour samples on the 24-hour axis
    body = [text(x0, 14, f"{na} in ink, {nb} in accent"), line(x0, top + h, x0 + w, top + h)]
    body.append(polyline(list(zip(tx(np.arange(n)), scaled(a, top, h, 0, hi))), "ln"))
    body.append(polyline(list(zip(tx(np.arange(n)), scaled(b, top, h, 0, hi))), "ln-accent"))
    body.extend(hour_hints(x0, w, top + h + 18))
    return document(top + h + 24, "Distance of each window of mon to its nearest neighbour in another day",
                    f"For every window of {PROFILE_LEN} samples of mon, the z-normalised Euclidean distance to the "
                    "closest window of a two-peak day (ink) and of a flat-block day (accent).", body)


# --- group ----------------------------------------------------------------------------------

def strip_chart(ids, rows, title, desc, note=None, lab_w=104):
    """One row per partition, one column per day. A cell's colour is the group, an empty box is noise."""
    right = 42 if note else 0
    pitch = (WIDTH - lab_w - right - 4) / len(ids)
    cell, row_h, top = pitch - 2, 24, 40
    body = []
    for c, name in enumerate(ids):
        body.append(text(lab_w + c * pitch + cell / 2, top - (8 if c % 2 == 0 else 24), name, "t-sm t-mono mid"))
    for r, (label, labels) in enumerate(rows):
        y = top + r * row_h
        body.append(text(4, y + 16, label))
        for c, g in enumerate(labels):
            cls = "box" if g < 0 else group_cls(int(g))
            body.append(rect(lab_w + c * pitch, y, cell, row_h - 4, cls, ' rx="2"'))
        if note:
            body.append(text(WIDTH - 4, y + 16, note[r], "t-sm t-mono end"))
    return document(top + len(rows) * row_h + 2, title, desc, body)


def fig_dendrogram(ids, D, labels):
    tree = dendrogram(fm.average_merges(D), no_plot=True, labels=ids)
    x0, w, top, h = 34, WIDTH - 38, 18, 170
    hi = float(max(max(d) for d in tree["dcoord"])) * 1.05
    n = len(ids)
    tx = lambda v: x0 + w * v / (10 * n)
    ty = lambda v: top + h - h * v / hi
    merges = sorted(float(d[1]) for d in tree["dcoord"])
    cut = (merges[-1] + merges[-2]) / 2
    body = [line(x0, top + h, x0 + w, top + h)]
    for ic, dc in zip(tree["icoord"], tree["dcoord"]):
        body.append(polyline([(tx(a), ty(b)) for a, b in zip(ic, dc)], "ln-muted"))
    body.append(line(x0, ty(cut), x0 + w, ty(cut), "ln-accent", ' stroke-dasharray="5 4"'))
    body.append(text(x0 + w, ty(cut) - 6, "k = 2", "t-sm t-mono end"))
    body.append(text(x0 - 6, top + 10, f"{merges[-1]:.1f}", "t-sm t-mono end"))
    body.append(text(x0 - 6, top + h, "0", "t-sm t-mono end"))
    for k, name in enumerate(tree["ivl"]):
        body.append(text(tx(10 * k + 5), top + h + (16 if k % 2 == 0 else 32), name, "t-sm t-mono mid"))
    return document(top + h + 38, f"Average-linkage tree of the DTW distances (w = {W_DTW})",
                    f"Dendrogram of the twelve days. The last merge is at height {merges[-1]:.2f}, the one before at "
                    f"{merges[-2]:.2f}, and the dashed line cuts the tree into two groups.", body)


# --- validate -------------------------------------------------------------------------------

def fig_silhouette(ids, scores, labels):
    order = sorted(range(len(ids)), key=lambda k: (labels[k], -scores[k]))
    x0, w, row, top = 44, WIDTH - 96, 19, 4
    hi = 1.0
    body = [line(x0, top, x0, top + row * len(ids) + 4)]
    y, prev = top + 2, labels[order[0]]
    for k in order:
        if labels[k] != prev:
            y += 8
            prev = labels[k]
        body.append(text(x0 - 6, y + 13, ids[k], "t-sm t-mono end"))
        body.append(rect(x0, y + 2, w * max(scores[k], 0) / hi, row - 5, group_cls(int(labels[k]))))
        body.append(text(x0 + w * max(scores[k], 0) / hi + 6, y + 13, f"{scores[k]:.2f}"))
        y += row
    return document(y + 8, "Silhouette of each day in the two-group cut",
                    "Horizontal bars of s(i) for the twelve days, group 1 in ink and group 2 in accent, sorted within "
                    "each group.", body)


def table(tab, rows, cols, x0, y0, title):
    cell_w, cell_h, lab_w = 76, 34, 64
    body = [text(x0, y0, title)]
    top = y0 + 26
    for c, name in enumerate(cols):
        body.append(text(x0 + lab_w + (c + 0.5) * cell_w, top - 6, name, "t-sm t-mono mid"))
    vmax = float(tab.max())
    for r, name in enumerate(rows):
        y = top + r * cell_h
        body.append(text(x0, y + 22, name))
        for c in range(tab.shape[1]):
            v = int(tab[r, c])
            body.append(rect(x0 + lab_w + c * cell_w, y, cell_w - 2, cell_h - 2, "box-accent" if v else "box", ' rx="2"'))
            body.append(text(x0 + lab_w + (c + 0.5) * cell_w, y + 22, str(v), "t-sm t-mono mid"))
    return body


def fig_contingency(tab_h, tab_s, cols_h, cols_s, stats_h, stats_s):
    rows = ["group 1", "group 2"]
    body = table(tab_h, rows, cols_h, 4, 16, "cut against the hour group")
    body += table(tab_s, rows, cols_s, 4, 148, "cut against the shape group")
    for y0, st in ((58, stats_h), (190, stats_s)):
        for i, line_text in enumerate(st):
            body.append(text(WIDTH - 4, y0 + i * 18, line_text, "t-sm t-mono end"))
    return document(250, "The two-group cut against the two stored labelings",
                    "Two 2 by 2 contingency tables of the DTW cut against the hour group and the shape group, each with "
                    "its adjusted Rand index and Jaccard index.", body)


# --- recipe ---------------------------------------------------------------------------------

def fig_recipe_flow(steps):
    body = []
    box_h, gap, y = 56, 16, 2
    for k, (name, output) in enumerate(steps):
        body.append(rect(4, y, WIDTH - 8, box_h, "box", ' rx="6"'))
        body.append(text(16, y + 23, name, "t"))
        body.append(text(16, y + 44, output))
        if k + 1 < len(steps):
            mid = WIDTH / 2
            body.append(line(mid, y + box_h, mid, y + box_h + gap, "ln-muted"))
        y += box_h + gap
    return document(y - gap + 4, "The four steps of the stock recipe and what each one hands over",
                    "A vertical flow: " + ", then ".join(f"{a} gives {b}" for a, b in steps) + ".", body)


# --- all ------------------------------------------------------------------------------------

def lesson_figures(ids, X):
    with open(ROOT / "fixtures" / "demand-12.csv") as fh:
        rows = list(csv.DictReader(fh))
    hour, shape = np.array([r["hour_group"] for r in rows]), np.array([r["shape_group"] for r in rows])
    day = {k: X[ids.index(k)] for k in ids}
    z = {k: znorm(v) for k, v in day.items()}
    Z = np.array([z[k] for k in ids])
    numbers = {}

    # preprocessing and lock-step
    order = [ids.index(k) for k in SEMANTIC_ORDER]
    De = distance_matrix(X, euclidean)[np.ix_(order, order)]
    Dc = distance_matrix(X, fm.correlation_distance)[np.ix_(order, order)]
    numbers["corr_mon_sat"] = f"{fm.correlation_distance(day['mon'], day['sat']):.2f}"
    numbers["corr_mon_wed"] = f"{fm.correlation_distance(day['mon'], day['wed']):.2f}"
    numbers["manhattan_mon_sat"] = f"{np.abs(day['mon'] - day['sat']).sum():.2f}"
    numbers["manhattan_mon_wed"] = f"{np.abs(day['mon'] - day['wed']).sum():.2f}"
    numbers["chebyshev_mon_sat"] = f"{np.abs(day['mon'] - day['sat']).max():.2f}"
    numbers["chebyshev_mon_wed"] = f"{np.abs(day['mon'] - day['wed']).max():.2f}"

    # sliding
    fig_cc, s_sat, s_wed = fig_cross_correlation(z["mon"], z["sat"], z["wed"])
    numbers["sbd_mon_sat"] = f"{sbd(z['mon'], z['sat']):.3f}"
    numbers["sbd_mon_wed"] = f"{sbd(z['mon'], z['wed']):.3f}"
    numbers["shift_mon_sat"] = str(abs(s_sat))
    numbers["shift_mon_wed"] = str(abs(s_wed))

    # edit-based
    l_sat, _ = fm.lcss_pairs(z["mon"], z["sat"], LCSS_EPS, LCSS_DELTA)
    l_wed, pairs = fm.lcss_pairs(z["mon"], z["wed"], LCSS_EPS, LCSS_DELTA)
    numbers.update(lcss_mon_sat=str(l_sat), lcss_mon_wed=str(l_wed), lcss_d_mon_sat=f"{1 - l_sat / 48:.2f}",
                   lcss_d_mon_wed=f"{1 - l_wed / 48:.2f}", lcss_eps=str(LCSS_EPS), lcss_delta=str(LCSS_DELTA))

    # features and models
    acf_mon, acf_sun = fm.acf(day["mon"], ACF_LAGS), fm.acf(day["sun"], ACF_LAGS)
    numbers["acf_d_mon_sun"] = f"{np.linalg.norm(acf_mon - acf_sun):.2f}"
    numbers["acf_d_mon_wed"] = f"{np.linalg.norm(acf_mon - fm.acf(day['wed'], ACF_LAGS)):.2f}"
    patterns, h_mon = fm.ordinal_histogram(day["mon"], ORDER_D)
    _, h_sun = fm.ordinal_histogram(day["sun"], ORDER_D)
    numbers["pe_mon"] = f"{fm.permutation_entropy(h_mon):.2f}"
    numbers["pe_sun"] = f"{fm.permutation_entropy(h_sun):.2f}"

    # learned: a shapelet cut from a peak of mon, one from the flat block of sun
    A = day["mon"][8:8 + SHAPELET_LEN]
    B = day["sun"][int(np.argmax(np.diff(day["sun"]))):][:SHAPELET_LEN]
    points = np.array([[fm.subsequence_distance(A, day[k]), fm.subsequence_distance(B, day[k])] for k in ids])

    # subsequences
    prof_sat, prof_sun = fm.nn_profile(day["mon"], day["sat"], PROFILE_LEN), fm.nn_profile(day["mon"], day["sun"], PROFILE_LEN)

    # group
    D = distance_matrix(X, lambda a, b: dtw(a, b, W_DTW))
    labels = fm.first_seen(average_linkage(D, 2))
    kmed, medoids = fm.k_medoids(D, 2)
    numbers["medoid_a"], numbers["medoid_b"] = ids[medoids[0]], ids[medoids[1]]
    partitions = [("k-medoids", kmed), ("average", labels)]
    for eps in DBSCAN_EPS:
        part = fm.first_seen(fm.dbscan(D, eps, DBSCAN_MIN_PTS))
        partitions.append((f"DBSCAN {eps:.2f}", part))
        if eps == DBSCAN_EPS[0]:
            numbers["dbscan_noise_small"] = str(int((part < 0).sum()))
    merges = fm.average_merges(D)[:, 2]
    numbers["merge_last"], numbers["merge_prev"] = f"{merges[-1]:.2f}", f"{merges[-2]:.2f}"

    # validate
    scores = fm.silhouette_samples(D, labels)
    numbers["silhouette_min"] = f"{scores.min():.2f}"
    numbers["silhouette_max"] = f"{scores.max():.2f}"
    tab_h, _, cols_h = fm.contingency(labels, hour)
    tab_s, _, cols_s = fm.contingency(labels, shape)

    def stats(ref):
        ss, sd, ds, _ = fm.pair_counts(labels, ref)
        return fm.adjusted_rand(labels, ref), ss / (ss + sd + ds)
    ari_h, jac_h = stats(hour)
    ari_s, jac_s = stats(shape)
    numbers.update(ari_hour=f"{ari_h:.2f}", ari_shape=f"{ari_s:.2f}", jaccard_hour=f"{jac_h:.2f}", jaccard_shape=f"{jac_s:.2f}")

    sens, notes = [], []
    for w in WINDOWS:
        Dw = distance_matrix(X, lambda a, b: dtw(a, b, w))
        part = fm.first_seen(average_linkage(Dw, 2))
        sens.append((f"w = {w}" if w is not None else "no window", part))
        notes.append(f"{silhouette_from_matrix(Dw, part):.2f}")
        if w in (10, None):
            numbers[f"sensitivity_sil_{'none' if w is None else w}"] = notes[-1]

    figures = {
        "preprocess-views": fig_preprocess(day["mon"], "mon"),
        "lockstep-matrices": fig_lockstep_matrices(De, Dc),
        "cross-correlation": fig_cc,
        "lcss-alignment": fig_lcss(z["mon"], z["wed"], "mon", "wed", pairs),
        "acf-bars": fig_acf(acf_mon, acf_sun, "mon", "sun"),
        "ordinal-patterns": fig_ordinal(patterns, h_mon, h_sun, "mon", "sun"),
        "shapelet-map": fig_shapelet_map(ids, points, shape),
        "nearest-window": fig_profile(prof_sat, prof_sun, "sat", "sun"),
        "dendrogram": fig_dendrogram(ids, D, labels),
        "partitions": strip_chart(ids, partitions, "One DTW matrix, five partitions",
                                  "Each row is a partition of the twelve days from the same DTW matrix, k-medoids and "
                                  "average linkage at two groups, DBSCAN at three radii. Colour is the group, an empty "
                                  "box is noise."),
        "silhouette-bars": fig_silhouette(ids, scores, labels),
        "contingency": fig_contingency(tab_h, tab_s, cols_h, ["two-peak" if c == "twopeak" else "flat" for c in cols_s],
                                       [f"ARI {ari_h:.2f}", f"Jaccard {jac_h:.2f}"], [f"ARI {ari_s:.2f}", f"Jaccard {jac_s:.2f}"]),
        "window-sensitivity": strip_chart(ids, sens, "The two-group cut at six windows",
                                          "Each row is average linkage with k = 2 on DTW at one window. Colour is the "
                                          "group, the number at the right is the mean silhouette of that partition on "
                                          "its own matrix.", note=notes),
        "recipe-flow": fig_recipe_flow([("Define", "question, object, N and T"), ("Measure", "N by N dissimilarity matrix"),
                                        ("Group", "tree or partition"), ("Validate", "checks, each on its own question")]),
    }
    return figures, numbers
