# Statistical Layers

Statistical layers compute and display summaries, models, and transformations
of the data. They combine a `stat_*` computation with a default geom.

## geom_smooth / stat_smooth

Adds a smoothed conditional mean with an optional confidence interval.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `method` | `"auto"` | Smoothing method: `"auto"`, `"lm"`, `"loess"`, `"lowess"`, `"glm"`, `"gls"`, `"rlm"` |
| `formula` | `None` | Model formula (e.g., `"y ~ x + I(x**2)"`) |
| `se` | `True` | Show confidence interval |
| `level` | `0.95` | Confidence level |
| `fullrange` | `False` | Extend fit to full range of x |
| `span` | `0.75` | Span for loess/lowess (controls smoothness) |
| `n` | `80` | Number of evaluation points |

When `method="auto"`, plotnine uses loess for <1000 observations and
GLM for >=1000.

Loess smoothing requires the `scikit-misc` package.

### Linear fit

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="lm")
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Linear Fit")
)
```

### Loess smoother with custom span

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="loess", span=0.5, color="darkred")
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Loess Smoother (span=0.5)")
)
```

### Grouped smoothers

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy", color="factor(drv)"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="lm", se=False)
    + labs(x="Engine Displacement (L)", y="Highway MPG", color="Drive", title="Linear Fit by Drive Type")
)
```

### Full-range prediction

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="lm", fullrange=True)
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Full-Range Linear Fit")
)
```

## stat_summary

Summarizes y values at each x with a central tendency and range.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `fun_data` | `"mean_cl_boot"` | Function returning y, ymin, ymax |
| `fun_y` | `None` | Function for central y value |
| `fun_ymin` | `None` | Function for lower bound |
| `fun_ymax` | `None` | Function for upper bound |
| `geom` | `"pointrange"` | Default geom |

Built-in `fun_data` options: `"mean_cl_boot"` (bootstrap CI), `"mean_se"`
(mean +/- SE), `"median_hilow"` (median with quantile range).

### Mean with bootstrap confidence interval

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class", y="hwy"))
    + stat_summary(fun_data="mean_se")
    + labs(x="Vehicle Class", y="Highway MPG", title="Mean +/- SE by Vehicle Class")
)
```

### Custom summary functions

Use `fun_y`, `fun_ymin`, and `fun_ymax` for custom aggregation.

```python
from plotnine import *
from plotnine.data import mpg
import numpy as np

(
    ggplot(mpg, aes(x="class", y="hwy"))
    + stat_summary(fun_y=np.median, fun_ymin=np.min, fun_ymax=np.max, color="red")
    + labs(x="Vehicle Class", y="Highway MPG", title="Median with Min/Max Range")
)
```

### stat_summary with bar geom

```python
from plotnine import *
from plotnine.data import mpg
import numpy as np

(
    ggplot(mpg, aes(x="class", y="hwy"))
    + stat_summary(fun_y=np.mean, geom="bar", fill="steelblue", alpha=0.7)
    + stat_summary(fun_data="mean_se", geom="errorbar", width=0.2)
    + labs(x="Vehicle Class", y="Mean Highway MPG", title="Bar Chart with Error Bars")
)
```

## stat_ecdf

Computes and plots the empirical cumulative distribution function.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n` | `None` | Number of evaluation points (None = all data) |
| `pad` | `True` | Pad ECDF with 0 at start and 1 at end |

Default geom is `step`.

### Basic ECDF

```python
from plotnine import *
from plotnine.data import faithful

(
    ggplot(faithful, aes(x="eruptions"))
    + stat_ecdf()
    + labs(x="Eruption Duration (min)", y="Cumulative Proportion", title="ECDF of Old Faithful Eruptions")
)
```

### Grouped ECDF

```python
from plotnine import *
from plotnine.data import penguins

(
    ggplot(penguins.dropna(), aes(x="body_mass_g", color="species"))
    + stat_ecdf()
    + labs(x="Body Mass (g)", y="Cumulative Proportion", color="Species", title="Body Mass ECDF by Species")
)
```

## Position Adjustments

Position adjustments control how overlapping geoms are arranged.

| Position | Description | Common with |
|----------|-------------|-------------|
| `position_dodge(width)` | Side-by-side within groups | `geom_bar`, `geom_col`, `geom_boxplot` |
| `position_dodge2(width)` | Side-by-side, works with variable widths | `geom_boxplot` |
| `position_stack()` | Stack on top of each other | `geom_bar`, `geom_area` |
| `position_fill()` | Stack normalized to 100% | `geom_bar`, `geom_area` |
| `position_jitter(width, height)` | Random offset | `geom_point` |
| `position_jitterdodge()` | Jitter within dodged groups | `geom_point` with grouped bars |

### Dodged bars with explicit width

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class", fill="factor(drv)"))
    + geom_bar(position=position_dodge(width=0.8), width=0.7)
    + labs(x="Vehicle Class", y="Count", fill="Drive", title="Dodged Bar Chart")
)
```

### Stacked bars

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds, aes(x="cut", fill="clarity"))
    + geom_bar(position="stack")
    + labs(x="Cut", y="Count", fill="Clarity", title="Stacked Bar Chart")
)
```

### Proportional (fill) bars

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds, aes(x="cut", fill="clarity"))
    + geom_bar(position="fill")
    + labs(x="Cut", y="Proportion", fill="Clarity", title="Proportional Bar Chart")
)
```

### Jittered points with dodge

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class", y="hwy", color="factor(drv)"))
    + geom_jitter(position=position_jitterdodge(jitter_width=0.15, dodge_width=0.8), alpha=0.6)
    + labs(x="Vehicle Class", y="Highway MPG", color="Drive", title="Jittered Points by Class and Drive")
)
```

## Common Pitfalls

- **`method="lm"` requires statsmodels**: `geom_smooth(method="lm")` uses
  statsmodels internally. If statsmodels is not installed, plotnine raises an
  error. Install it with `uv add statsmodels`.

- **`position_fill` normalizes to 1, not stacking**: `position_fill` rescales
  bar heights so each x position sums to 1.0. The y-axis shows proportions,
  not counts. Use `position_stack` for raw counts.

- **`fun_data` vs `fun_y`**: `fun_data` returns a DataFrame with y, ymin,
  ymax columns (used for range geoms like pointrange, errorbar). `fun_y` only
  returns the central value. Using `fun_y` with a pointrange geom produces no
  range bars.

- **Default `fun_data="mean_cl_boot"` is slow**: Bootstrap CI computes many
  resamples. For large datasets, use `fun_data="mean_se"` for faster results,
  or provide `fun_y`/`fun_ymin`/`fun_ymax` with numpy functions.

- **Forgetting `width` in `position_dodge`**: Without an explicit width, dodged
  elements may not align properly with bar widths. Match `position_dodge(width=)`
  to `geom_bar(width=)`.

## Resources

- [plotnine geom_smooth reference](https://plotnine.org/reference/geom_smooth)
- [plotnine stat_summary reference](https://plotnine.org/reference/stat_summary)
- [plotnine stat_ecdf reference](https://plotnine.org/reference/stat_ecdf)
