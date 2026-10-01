"""Data loading and the estimators every analysis here shares."""
import json, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "decisions.jsonl")
PRIMARY = "opus5"
FACTORS = ("severity", "prior", "remorse", "cooperation")
WEBB = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5),
                 np.sqrt(0.5), 1.0, np.sqrt(1.5)])


def load(model=None):
    """Valid decisions, one per design cell. `model` restricts to one model."""
    out, seen = [], set()
    for line in open(DATA):
        if not line.strip():
            continue
        r = json.loads(line)
        k = (r["model"], r["arm"], r["judge"], r["step"])
        if k in seen or not r["ok"]:
            continue
        if model is not None and r["model"] != model:
            continue
        seen.add(k)
        out.append(r)
    return out


def factor_matrix(d):
    return np.column_stack([[r[f] for r in d] for f in FACTORS]).astype(float)


def ols(X, y):
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return b


def cluster_vcov(X, y, b, g):
    """Cluster-robust covariance with the usual small-sample correction."""
    n, k = X.shape
    u = y - X @ b
    XtX_inv = np.linalg.pinv(X.T @ X)
    meat = np.zeros((k, k))
    for c in np.unique(g):
        m = g == c
        s = X[m].T @ u[m]
        meat += np.outer(s, s)
    G = len(np.unique(g))
    return (G / (G - 1.0)) * ((n - 1.0) / (n - k)) * XtX_inv @ meat @ XtX_inv


def wild_bootstrap(X, y, g, j, B=9999, seed=7):
    """p-value for beta_j = 0. Webb weights, null imposed."""
    rng = np.random.default_rng(seed)
    b = ols(X, y)
    t_obs = b[j] / np.sqrt(cluster_vcov(X, y, b, g)[j, j])
    keep = [i for i in range(X.shape[1]) if i != j]
    Xr = X[:, keep]
    br = ols(Xr, y)
    fitted, ur = Xr @ br, y - Xr @ br
    clusters = np.unique(g)
    cnt = 0
    for _ in range(B):
        w = rng.choice(WEBB, size=len(clusters))
        wv = np.empty(len(y))
        for ci, c in enumerate(clusters):
            wv[g == c] = w[ci]
        yb = fitted + ur * wv
        bb = ols(X, yb)
        tb = bb[j] / np.sqrt(cluster_vcov(X, yb, bb, g)[j, j])
        if abs(tb) >= abs(t_obs) - 1e-12:
            cnt += 1
    return t_obs, (cnt + 1) / (B + 1)


def pull(d):
    """Slope of deviation on displacement, controlling for the case factors."""
    y = np.array([r["dev"] for r in d])
    x = np.array([r["delta"] for r in d])
    X = np.column_stack([np.ones(len(y)), x, factor_matrix(d)])
    b = ols(X, y)
    se = np.sqrt(cluster_vcov(X, y, b, np.array([r["cid"] for r in d]))[1, 1])
    return float(b[1]), float(se)
