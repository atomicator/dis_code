import matplotlib.pyplot as plt
from toolkit import toolkit
import numpy as np
import healpy as hp
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--catalogue", default="./test.fits")
parser.add_argument("--save_path")
parser.add_argument("--weight_version", type=int, choices=[1, 2, 3, 4], default=3)
parser.add_argument("--raise_path", type=int, default=2)

args = parser.parse_args()

v = args.weight_version
toolkit.plt_use_tex()
#mask_names = ["planck_modified_point", "planck_modified_galactic"]
mask_names = ["planck_modified_point"]
labels = ["point", "galactic"]
title = [f"Estimating the masked fraction using the ratio ({args.catalogue})", f"Estimating the masked ratio ({args.catalogue})", f"Estimating the masked fraction directly ({args.catalogue})", f"Regression analysis ({({args.catalogue})})"][v - 1]
y_axis_label = [r"Absolute masked fraction difference $(\%)$", "Ratio", r"Absolute masked fraction difference $(\%)$", "Gradient"][v - 1]
line_colors = ["xkcd:aqua blue", "orange"]
error_bar_colors = ["xkcd:electric blue", "red"]
raise_dir = args.raise_path
y_multiplicative_factor = [100, 1, 100, 1][v - 1]

#mask = toolkit.load_mask("planck_galactic")
if args.catalogue in ["sdss"]:
    cat = toolkit.load_catalogue(args.catalogue, raise_dir=args.raise_path)
else:
    cat = toolkit.StarCatalogue(path=args.catalogue, table=True)
cat.load_lon_lat()

fig = plt.figure()
ax = fig.add_subplot(111)

f = []
#sample_error = 0.017
#sample_error = 0.025
#sky_frac = 0.99223
#sky_frac = 2.3232
#sky_frac = 2.3232 - 0.99223

#NSIDES = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
NSIDES = [1, 4, 16, 64]
#NSIDES = [2]
#NSIDES = []

results = []
for mask_name in mask_names:
    mask = toolkit.load_mask(mask_name, raise_dir=args.raise_path)
    results.append([])
    f.append((1 - np.sum(mask.lookup_point(*cat.lon_lat.transpose())) / len(cat.lon_lat)) * 100)
    binmap = toolkit.ConstantMap()
    binmap.bin_catalogue(cat)
    binmap.load_catalogue(cat)
    data = np.array((
        np.mean(toolkit.HealpyMask("./" + "../" * raise_dir + f"data/cached_results/sdss_mask_{mask_name}_512_1.fits").map),
        np.mean(toolkit.HealpyMask("./" + "../" * raise_dir + f"data/cached_results/sdss_mask_{mask_name}_512_2.fits").map),
        np.mean(toolkit.HealpyMask("./" + "../" * raise_dir + f"data/cached_results/sdss_mask_{mask_name}_512_3.fits").map),
        np.mean(toolkit.HealpyMask("./" + "../" * raise_dir + f"data/cached_results/sdss_mask_{mask_name}_512_4.fits").map)
    ))
    results[-1].append(binmap.calc_masked_fraction_new(mask, data, v, const=True))
    for n in NSIDES:
        binmap = toolkit.HealpixBinMap(n)
        binmap.bin_catalogue(cat)
        binmap.load_catalogue(cat)
        data = np.array((
            hp.pixelfunc.ud_grade(toolkit.HealpyMask("./" + "../" * raise_dir + f"data/cached_results/sdss_mask_{mask_name}_512_1.fits").map, n),
            hp.pixelfunc.ud_grade(toolkit.HealpyMask("./" + "../" * raise_dir + f"data/cached_results/sdss_mask_{mask_name}_512_2.fits").map, n),
            hp.pixelfunc.ud_grade(toolkit.HealpyMask("./" + "../" * raise_dir + f"data/cached_results/sdss_mask_{mask_name}_512_3.fits").map, n),
            hp.pixelfunc.ud_grade(toolkit.HealpyMask("./" + "../" * raise_dir + f"data/cached_results/sdss_mask_{mask_name}_512_4.fits").map, n)
        ))
        results[-1].append(binmap.calc_masked_fraction_new(mask, data, v))

results = np.array(results) * y_multiplicative_factor

if v in [2, 4]:
    f = np.zeros(len(f))

print(np.shape(results))
for i in range(len(mask_names)):
    # ax.plot([0.5] + NSIDES, np.abs(f[i] - results[i, :, 0]), label=labels[i], color=line_colors[i])
    # ax.errorbar([0.5] + NSIDES, np.abs(f[i] - results[i, :, 0]), results[i, :, 1], fmt="none", capsize=3, capthick=1, ecolor=error_bar_colors[i])
    ax.plot([0.5] + NSIDES, (-f[i] + results[i, :, 0]), label=labels[i], color=line_colors[i])
    ax.errorbar([0.5] + NSIDES, (-f[i] + results[i, :, 0]), results[i, :, 1], fmt="none", capsize=3, capthick=1, ecolor=error_bar_colors[i])

#ax.plot([0] + NSIDES, results[2], label="Galactic")
#ax.errorbar([0] + NSIDES, results[2], results[3], fmt="none", capsize=5, capthick=1, ecolor="k")

#ax.plot([0] + NSIDES, np.ones(len(NSIDES)) * sample_error, label="Total sky fraction", linestyle="dashdot", color="black")
#ax.plot([0] + NSIDES, np.ones(len(NSIDES)) * np.abs(f - sky_frac), label="Sample error", linestyle="dashed", color="black")
if v not in [2, 4]:
    ax.plot([0.5] + NSIDES, np.zeros(len(NSIDES) + 1), linestyle="solid", color="black")
else:
    ax.plot([0.5] + NSIDES, np.ones(len(NSIDES) + 1), linestyle="solid", color="black")
#ax.plot(NSIDES, np.ones(len(NSIDES)) * 100, label="Sample error", linestyle="dashed", color="black")

#ax.set_yscale("log")
ax.set_xscale("log", base=2)
ax.legend()
#ax.set_ylim(0.01, 10)
ax.set_xlim(0.5, NSIDES[-1])
ax.set_xticks([0.5] + NSIDES, ["C"] + NSIDES)

ax.set_xlabel("NSIDE")
ax.set_ylabel(y_axis_label)
ax.set_title(title)

if args.save_path:
    plt.savefig(args.save_path)

plt.show()

print(f, results)
