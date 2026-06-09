#!/usr/bin/env python3
"""
Generate an animated GIF showing evolution of the PMF of Y_n as n grows.

Usage:
  python generate_pmf_gif.py --max_n 200 --a 0.5 --b 0.3 --step 1 --fps 8 --out pmf_evolution.gif

The script implements the optimized PMF construction from the notebook and
saves a GIF. Keep `--max_n` modest for a quick demo (e.g. 100--300).
"""

import argparse
import os
import shutil
import tempfile

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    import imageio
except Exception:
    imageio = None


def compute_exact_distributions_optimized(max_N, a, b, verbose=True):
    pmfs = [np.array([1.0]), np.array([1.0]), np.array([1.0])]
    cdfs = [np.array([1.0]), np.array([1.0]), np.array([1.0])]
    termination_prob = 1.0 - a - b

    for N_target in range(3, max_N + 1):
        if verbose and (N_target % 10 == 0):
            print(f"Computing pmf up to N={N_target}...")

        n = N_target - 2
        current_pmf = np.zeros(N_target, dtype=float)

        # Use symmetry in the split U_n
        for u in range(1, ((n + 1) // 2) + 1):
            v = n + 1 - u
            weight = 2.0 if u != v else 1.0

            # Concatenation (sum + shift by 1)
            conv_pmf = np.convolve(pmfs[u], pmfs[v])
            concat_pmf = np.zeros(len(conv_pmf) + 1)
            concat_pmf[1:] = conv_pmf
            length_c = min(len(concat_pmf), N_target)
            current_pmf[:length_c] += weight * a * concat_pmf[:length_c]

            # Alternation (max) via CDF product
            len_u = len(cdfs[u])
            len_v = len(cdfs[v])
            max_len = max(len_u, len_v)

            cdf_u_ext = np.ones(max_len)
            cdf_u_ext[:len_u] = cdfs[u]
            cdf_v_ext = np.ones(max_len)
            cdf_v_ext[:len_v] = cdfs[v]

            cdf_max = cdf_u_ext * cdf_v_ext
            pmf_max = np.zeros(max_len)
            pmf_max[0] = cdf_max[0]
            pmf_max[1:] = cdf_max[1:] - cdf_max[:-1]
            length_m = min(len(pmf_max), N_target)
            current_pmf[:length_m] += weight * b * pmf_max[:length_m]

        # Average over uniform split and add termination mass
        current_pmf /= n
        current_pmf[0] += termination_prob

        # Numerical safety and normalization
        current_pmf = np.maximum(current_pmf, 0.0)
        s = np.sum(current_pmf)
        if s == 0:
            current_pmf[0] = 1.0
        else:
            current_pmf /= s

        pmfs.append(current_pmf)
        cdfs.append(np.cumsum(current_pmf))

    return pmfs


def make_gif(pmfs, out_file, step=1, fps=8, dpi=120):
    frames_dir = tempfile.mkdtemp(prefix="pmf_frames_")
    try:
        max_support = max(len(pmf) for pmf in pmfs)
        max_pmf_value = max((np.max(pmf) if len(pmf) else 0.0) for pmf in pmfs)

        filenames = []
        indices = list(range(1, len(pmfs), step))
        for n in indices:
            pmf = pmfs[n]
            fig, ax = plt.subplots(figsize=(6, 3))
            xs = np.arange(len(pmf))
            ax.bar(xs, pmf, color="C0")
            ax.set_xlim(0, max_support - 1)
            ax.set_ylim(0, max_pmf_value * 1.05)
            ax.set_title(f"PMF of $Y_{{{n}}}$ (support $0\ldots {len(pmf)-1}$)")
            ax.set_xlabel("k")
            ax.set_ylabel("P(Y_n=k)")
            plt.tight_layout()

            fname = os.path.join(frames_dir, f"frame_{n:05d}.png")
            fig.savefig(fname, dpi=dpi)
            plt.close(fig)
            filenames.append(fname)

        if imageio is None:
            try:
                from PIL import Image
            except Exception as ex:
                raise RuntimeError("Install imageio or pillow to create GIFs (pip install imageio pillow)") from ex

            images = [Image.open(fn).convert("RGBA") for fn in filenames]
            images[0].save(out_file, save_all=True, append_images=images[1:], duration=int(1000 / fps), loop=0)
        else:
            images = [imageio.imread(fn) for fn in filenames]
            imageio.mimsave(out_file, images, fps=fps)

    finally:
        shutil.rmtree(frames_dir)


def main():
    parser = argparse.ArgumentParser(description="Generate GIF of PMF evolution for Y_n")
    parser.add_argument("--max_n", type=int, default=150, help="Maximum n to compute (>=3)")
    parser.add_argument("--a", type=float, default=0.5, help="Parameter a")
    parser.add_argument("--b", type=float, default=0.3, help="Parameter b")
    parser.add_argument("--step", type=int, default=1, help="Frame step (use >1 to skip frames)")
    parser.add_argument("--fps", type=int, default=8, help="Frames per second for GIF")
    parser.add_argument("--out", type=str, default="pmf_evolution.gif", help="Output GIF path")
    parser.add_argument("--verbose", action="store_true", help="Verbose progress prints")
    args = parser.parse_args()

    if args.max_n < 3:
        parser.error("--max_n must be >= 3")

    print(f"Computing pmfs up to n={args.max_n} with a={args.a}, b={args.b} ...")
    pmfs = compute_exact_distributions_optimized(args.max_n, args.a, args.b, verbose=args.verbose)
    print("Creating GIF (this may take a moment)...")
    make_gif(pmfs, args.out, step=args.step, fps=args.fps)
    print("GIF saved to", args.out)


if __name__ == "__main__":
    main()
