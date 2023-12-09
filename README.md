# Precision, Recall, Accuracy (and Cost/Benefit)
Plaything name: pra

Keys in __asset_map__:
- about - a markdown file
- rocs - a JSON file containing a set of ROC curves as produced by the "ROC Curve Sim" notebook.

The rocs JSON entries look like (x is the FP rate and y is the TP rate), noting that the x value associated with the first y entry is x = x_step and the last y entry should correspond with x = 1.0:
```
"A": {"x_step": 0.01, "y": [0.018, 0.037, 0.055, 0.073, 0.091, 0.109, 0.126, 0.144, 0.162, 0.179, 0.196, 0.214, 0.231, 0.247, 0.264, 0.28, 0.297, 0.313, 0.329, 0.344, 0.36, 0.375, 0.39, 0.405, 0.419, 0.433, 0.447, 0.461, 0.474, 0.487, 0.5, 0.513, 0.525, 0.537, 0.548, 0.559, 0.57, 0.58, 0.59, 0.6, 0.609, 0.619, 0.628, 0.638, 0.647, 0.656, 0.666, 0.675, 0.684, 0.693, 0.702, 0.711, 0.72, 0.729, 0.738, 0.746, 0.755, 0.764, 0.772, 0.781, 0.789, 0.797, 0.805, 0.813, 0.821, 0.829, 0.836, 0.844, 0.851, 0.859, 0.866, 0.873, 0.88, 0.886, 0.893, 0.899, 0.906, 0.912, 0.918, 0.924, 0.929, 0.935, 0.94, 0.945, 0.95, 0.955, 0.959, 0.964, 0.968, 0.972, 0.976, 0.979, 0.983, 0.986, 0.989, 0.991, 0.994, 0.996, 0.998, 1.0]}
```