# Geoms

Geometric objects (geoms) are the visual marks placed on a plot. Each geom
represents data using different shapes: points, lines, bars, etc.

## Reading Order

| Task                                        | Read in order                                                    |
|---------------------------------------------|------------------------------------------------------------------|
| Pick a geom for a one-variable distribution | Geom Quick-Reference → Distributions                             |
| Pick a geom for a two-variable relationship | Geom Quick-Reference → Point and Scatter Plots → Lines and Paths |
| Show counts or aggregates by category       | Geom Quick-Reference → Bars and Columns                          |
| Compose a geom with a stat layer            | Geom Quick-Reference → See Also → `statistical-layers.md`        |

## Geom Quick-Reference

| Geom | Typical aes | Default stat | Common params |
|------|------------|--------------|---------------|
| `geom_point` | x, y, color, size, shape, alpha | `identity` | `size`, `alpha` |
| `geom_jitter` | x, y, color, size, shape | `identity` | `width`, `height` |
| `geom_line` | x, y, color, linetype, group | `identity` | `size` |
| `geom_step` | x, y, color, linetype | `identity` | `direction` |
| `geom_bar` | x, fill, color | `count` | `width`, `position` |
| `geom_col` | x, y, fill, color | `identity` | `width`, `position` |
| `geom_histogram` | x, fill, color | `bin` | `bins`, `binwidth` |
| `geom_density` | x, fill, color, linetype | `density` | `alpha` |
| `geom_boxplot` | x, y, fill, color | `boxplot` | `width`, `outlier_shape` |
| `geom_violin` | x, y, fill, color | `ydensity` | `scale`, `draw_quantiles` |
| `geom_area` | x, y, fill, alpha | `identity` | — |
| `geom_ribbon` | x, ymin, ymax, fill, alpha | `identity` | — |
| `geom_tile` | x, y, fill | `identity` | `width`, `height` |
| `geom_segment` | x, y, xend, yend, color | `identity` | `arrow` |
| `geom_rug` | x, y, color | `identity` | `sides`, `length` |
| `geom_smooth` | x, y, color | `smooth` | `method`, `se` |
| `geom_text` | x, y, label, color, size | `identity` | `nudge_x`, `nudge_y` |

### How geoms and stats share parameters

The "Common params" column above lists parameters that belong to the
geom's **default stat**, not the geom itself. Every geom forwards its
`**kwargs` to its paired stat, so `geom_histogram(binwidth=0.5)` is
passing `binwidth` through to `stat_bin`, and
`geom_smooth(method="lm", se=False)` is passing both kwargs through
to `stat_smooth`.

Consequences:

- A geom's own parameters are `mapping`, `data`, `stat`, `position`,
  `na_rm`, plus a small number of geom-specific options.
- Parameters like `binwidth`, `bins`, `method`, `span`, `width`,
  `scale`, `direction` live on the stat.
- Pairing a geom with a non-default stat
  (e.g. `geom_bar(stat="identity")`) changes which kwargs are
  accepted — the stat's, not the geom's.

See [statistical-layers.md](statistical-layers.md) for stat-specific
details.

## Quick one-liners

Each geom below is a complete layer. Combine with the minimal
`ggplot() + aes() + labs()` structure shown in SKILL.md Essentials.

```python
# Scatter
geom_point()

# Bar chart (counts)
geom_bar()                              # x only, counts rows

# Bar chart (pre-computed values)
geom_col()                              # x and y required

# Line chart
geom_line()                             # sort data by x first

# Histogram
geom_histogram(binwidth=0.5)

# Box plot
geom_boxplot()                          # x (categorical) and y (continuous)
```

## Point and Scatter Plots

### Basic scatter plot

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy", color="factor(cyl)"))
    + geom_point()
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Fuel Efficiency by Engine Size", color="Cylinders")
)
```

### Scatter with alpha for dense data

Larger datasets benefit from `alpha` transparency and a smaller `size`
to reduce overplotting.

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds.sample(2000, random_state=42), aes(x="carat", y="price", color="cut"))
    + geom_point(alpha=0.5, size=1)
    + labs(x="Carat", y="Price (USD)", title="Diamond Price by Carat and Cut", color="Cut Quality")
)
```

### Jittered points

`geom_jitter` adds random noise to avoid over-plotting on discrete axes.

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class", y="hwy"))
    + geom_jitter(width=0.2, height=0, alpha=0.6, random_state=42)
    + labs(x="Vehicle Class", y="Highway MPG", title="Highway MPG by Vehicle Class")
)
```

## Lines and Paths

### Time series with geom_line

Data must be sorted by x for `geom_line` to draw correctly.

```python
from plotnine import *
from plotnine.data import economics

(
    ggplot(economics, aes(x="date", y="unemploy"))
    + geom_line()
    + labs(x="Date", y="Unemployed (thousands)", title="US Unemployment Over Time")
)
```

### Step function

`geom_step` connects points with horizontal-then-vertical steps.

```python
from plotnine import *
from plotnine.data import economics

(
    ggplot(economics.head(30), aes(x="date", y="psavert"))
    + geom_step()
    + labs(x="Date", y="Personal Savings Rate (%)", title="Savings Rate (Step)")
)
```

## Bars and Columns

### geom_bar (stat="count")

Counts occurrences of each x value. No y aesthetic needed.

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class"))
    + geom_bar()
    + labs(x="Vehicle Class", y="Count", title="Number of Cars by Class")
)
```

### geom_col (stat="identity")

Plots pre-computed y values. Requires both x and y aesthetics.

```python
from plotnine import *
from plotnine.data import mpg
import pandas as pd

avg_hwy = mpg.groupby("class", as_index=False).agg(mean_hwy=("hwy", "mean"))

(
    ggplot(avg_hwy, aes(x="class", y="mean_hwy"))
    + geom_col()
    + labs(x="Vehicle Class", y="Mean Highway MPG", title="Average Highway MPG by Class")
)
```

### Stacked and dodged bars

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class", fill="factor(cyl)"))
    + geom_bar(position="dodge")
    + labs(x="Vehicle Class", y="Count", title="Cylinder Distribution by Class", fill="Cylinders")
)
```

## Distributions

### Histogram

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds, aes(x="carat"))
    + geom_histogram(binwidth=0.1)
    + labs(x="Carat", y="Count", title="Distribution of Diamond Carat Weight")
)
```

### Density curve

```python
from plotnine import *
from plotnine.data import faithful

(
    ggplot(faithful, aes(x="eruptions"))
    + geom_density()
    + labs(x="Eruption Duration (min)", y="Density", title="Old Faithful Eruption Durations")
)
```

### Box plot

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class", y="hwy"))
    + geom_boxplot()
    + labs(x="Vehicle Class", y="Highway MPG", title="Highway MPG Distribution by Class")
)
```

### Violin plot with jittered points

Layering `geom_violin` with `geom_jitter` shows both distribution shape and
individual observations.

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class", y="hwy"))
    + geom_violin()
    + geom_jitter(width=0.15, alpha=0.4, size=1)
    + labs(x="Vehicle Class", y="Highway MPG", title="Highway MPG: Violin + Points")
)
```

## Area and Ribbon

### Filled area

```python
from plotnine import *
from plotnine.data import economics

(
    ggplot(economics, aes(x="date", y="unemploy"))
    + geom_area(alpha=0.4)
    + labs(x="Date", y="Unemployed (thousands)", title="US Unemployment (Filled Area)")
)
```

### Confidence ribbon

`geom_ribbon` requires `ymin` and `ymax` aesthetics. Useful for confidence
bands or forecast intervals.

```python
from plotnine import *
import pandas as pd
import numpy as np

x = np.arange(0, 10, 0.5)
y = np.sin(x)
df = pd.DataFrame({"x": x, "y": y, "ymin": y - 0.3, "ymax": y + 0.3})

(
    ggplot(df, aes(x="x", y="y"))
    + geom_ribbon(aes(ymin="ymin", ymax="ymax"), alpha=0.3)
    + geom_line()
    + labs(x="X", y="Y", title="Line with Confidence Band")
)
```

## Tile and Raster

### Heatmap with geom_tile

```python
from plotnine import *
from plotnine.data import faithfuld

(
    ggplot(faithfuld, aes(x="eruptions", y="waiting", fill="density"))
    + geom_tile()
    + labs(x="Eruption Duration (min)", y="Waiting Time (min)", title="Old Faithful Density Heatmap", fill="Density")
)
```

## Segments and Arrows

### Basic segment

```python
from plotnine import *
from plotnine.data import economics
import pandas as pd

subset = economics.iloc[::60].copy()

(
    ggplot(subset, aes(x="date", y="unemploy"))
    + geom_point()
    + geom_segment(aes(xend="date", yend=0), alpha=0.4)
    + labs(x="Date", y="Unemployed (thousands)", title="Lollipop Chart of Unemployment")
)
```

### Segments with arrowheads

The `arrow()` function creates arrowheads with parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `angle` | 30 | Angle in degrees between tail and edge |
| `length` | 0.2 | Length of the arrowhead edge in inches |
| `ends` | `"last"` | Draw arrowhead at `"first"`, `"last"`, or `"both"` ends |
| `type` | `"open"` | `"open"` or `"closed"` (closed is also filled) |

```python
from plotnine import *
import pandas as pd

df = pd.DataFrame({
    "x": [1, 3, 5],
    "y": [1, 3, 2],
    "xend": [2, 4, 6],
    "yend": [3, 1, 4],
})

(
    ggplot(df, aes(x="x", y="y", xend="xend", yend="yend"))
    + geom_segment(arrow=arrow(angle=25, length=0.15, type="closed"))
    + labs(x="X", y="Y", title="Directed Arrows")
)
```

## Marginal Distributions

### Rug plot

`geom_rug` draws tick marks along axes to show individual data values.

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + geom_rug(sides="bl", length=0.03, alpha=0.3)
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Scatter with Marginal Rugs")
)
```

The `sides` parameter controls which axes get rugs: `"b"` (bottom), `"l"`
(left), `"t"` (top), `"r"` (right), or any combination like `"bl"`.

## Common Pitfalls

- **`geom_bar` vs `geom_col`**: `geom_bar` counts rows (no `y` aes);
  `geom_col` uses pre-computed `y` values. Using `geom_bar` with a `y`
  aesthetic requires `stat="identity"`, but prefer `geom_col` instead.

- **`color` inside vs outside `aes()`**: `aes(color="species")` maps a
  variable; `color="blue"` sets a fixed value. Putting a fixed color inside
  `aes()` creates a legend entry for a literal string. See
  [aesthetics-and-scales.md](aesthetics-and-scales.md) for details.

- **`bins` vs `binwidth`**: Use one or the other with `geom_histogram`, not
  both. `bins=30` (default) sets the number of bins; `binwidth=0.1` sets the
  width of each bin.

- **Unsorted data with `geom_line`**: `geom_line` connects points in x-order.
  If your data is not sorted by x, the line will zigzag. Sort before plotting:
  `df.sort_values("x")`.

- **Overplotting**: With many data points, use `alpha` transparency,
  `geom_jitter`, `geom_bin2d`, or `geom_density_2d` instead of `geom_point`.

## See Also

- [aesthetics-and-scales.md](aesthetics-and-scales.md) — mapping
  variables to geom aesthetics
- [statistical-layers.md](statistical-layers.md) — smoothers,
  stat summaries, and position adjustments
- [facets.md](facets.md) — splitting a geom across small multiples
- [labels-and-annotations.md](labels-and-annotations.md) — adding
  text labels to geoms

## Resources

- [plotnine geom reference](https://plotnine.org/reference/#geoms)
