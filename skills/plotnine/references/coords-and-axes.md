# Coordinates and Axes

Coordinate systems control how data coordinates map to the 2D plane of the plot.
They affect axis limits, aspect ratio, and coordinate transformations.

## coord_cartesian

Zooms into a region without removing data points. This is the default coordinate
system — use it explicitly when you need to set axis limits while preserving all
data for statistical computations.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `xlim` | `None` | Tuple of (min, max) for x-axis |
| `ylim` | `None` | Tuple of (min, max) for y-axis |
| `expand` | `True` | Add default expansion around limits |

### Zooming without data removal

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="lm")
    + coord_cartesian(xlim=(2, 5), ylim=(15, 40))
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Zoomed View (Data Preserved)")
)
```

## coord_flip

Swaps the x and y axes. Useful for horizontal bar charts and horizontal box
plots.

### Horizontal bar chart

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class"))
    + geom_bar()
    + coord_flip()
    + labs(x="Vehicle Class", y="Count", title="Horizontal Bar Chart")
)
```

### Horizontal box plot

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds.sample(2000, random_state=42), aes(x="cut", y="price"))
    + geom_boxplot()
    + coord_flip()
    + labs(x="Cut", y="Price (USD)", title="Diamond Price by Cut (Horizontal)")
)
```

## coord_fixed / coord_equal

Forces a fixed aspect ratio between x and y axes. `coord_equal` is an alias
for `coord_fixed`.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ratio` | `1` | Ratio of y-units to x-units |
| `xlim` | `None` | X-axis limits |
| `ylim` | `None` | Y-axis limits |
| `expand` | `True` | Add default expansion |

### Equal aspect ratio with 1:1 line

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="cty", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_abline(slope=1, intercept=0, linetype="dashed", color="grey")
    + coord_fixed(ratio=1)
    + labs(x="City MPG", y="Highway MPG", title="City vs Highway (Equal Scale)")
)
```

## coord_trans

Applies a coordinate transformation without changing the underlying scale. The
data remains on the original scale, but the coordinate space is transformed.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `x` | `"identity"` | Transform name for x-axis |
| `y` | `"identity"` | Transform name for y-axis |
| `xlim` | `None` | X-axis limits (in transformed space) |
| `ylim` | `None` | Y-axis limits (in transformed space) |

### Log-transformed coordinates

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds.sample(2000, random_state=42), aes(x="carat", y="price"))
    + geom_point(alpha=0.3, size=0.5)
    + coord_trans(x="log10", y="log10")
    + labs(x="Carat", y="Price (USD)", title="Log-Log Coordinate Transform")
)
```

## lims() vs coord_cartesian()

These two approaches to setting axis limits behave differently:

| Approach | Behavior | Affects stats? |
|----------|----------|----------------|
| `lims(x=(a, b))` | **Removes** data outside range | Yes |
| `scale_x_continuous(limits=(a, b))` | **Removes** data outside range | Yes |
| `coord_cartesian(xlim=(a, b))` | **Zooms** without removing data | No |

### Data removal vs zooming

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="lm")
    + lims(x=(3, 6))
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="lims() Removes Data Outside Range")
)
```

Compare with `coord_cartesian`, which preserves all data for the smooth fit:

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="lm")
    + coord_cartesian(xlim=(3, 6))
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="coord_cartesian() Zooms (Data Preserved)")
)
```

## No coord_polar

plotnine does not support polar coordinates. There is no `coord_polar()`
function. For pie charts or radar charts, consider alternative representations:

- Pie chart → stacked or dodged bar chart
- Radar chart → parallel coordinates or faceted bar chart

## Common Pitfalls

- **`lims()` removes data, affecting stats**: Using `lims(y=(0, 40))` drops
  rows where y > 40 before computing `geom_smooth` or `stat_summary`. This
  changes the fitted line or summary statistics. Use `coord_cartesian(ylim=...)`
  to zoom without altering computations.

- **`coord_cartesian()` only zooms**: It does not filter data or change the
  underlying data range. Points outside the view still participate in all
  statistical computations.

- **`coord_flip` with discrete x**: When flipping a bar chart, the variable
  mapped to `x` appears on the y-axis visually, but you still define it as
  `aes(x=...)`. Do not swap x and y in the aesthetic mapping.

- **`coord_fixed` distorts when data ranges differ**: If x ranges from 0-100
  and y from 0-10, `coord_fixed(ratio=1)` creates an extremely wide plot. Use
  a different ratio or let plotnine choose automatically.

## Resources

- [plotnine coord_cartesian reference](https://plotnine.org/reference/coord_cartesian)
- [plotnine coord_flip reference](https://plotnine.org/reference/coord_flip)
- [plotnine coord_fixed reference](https://plotnine.org/reference/coord_fixed)
