# coord_trans

Transformed cartesian coordinate system

## Signature

`coord_trans(x="identity", y="identity", xlim=None, ylim=None, expand=True)`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `x` | str \| trans | `"identity"` | Name of transform or trans class to transform the x axis |
| `y` | str \| trans | `"identity"` | Name of transform or trans class to transform the y axis |
| `xlim` | tuple[float, float] | `None` | Limits for x axis. If None, then they are automatically computed. |
| `ylim` | tuple[float, float] | `None` | Limits for y axis. If None, then they are automatically computed. |
| `expand` | bool | `True` | If True, expand the coordinate axes by some factor. If False, use the limits from the data. |

## See Also

*(List related symbols here.)*
