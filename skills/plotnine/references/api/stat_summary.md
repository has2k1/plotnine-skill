# stat_summary

Calculate summary statistics depending on x

## Signature

`stat_summary( mapping=None, data=None, *, geom="pointrange", position="identity", na_rm=False, fun_data="mean_cl_boot", fun_y=None, fun_ymin=None, fun_ymax=None, fun_args=None, random_state=None, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping.  Options for computed aesthetics Calculated aesthetics are accessed using the after_stat function. e.g. after_stat('ymin'). |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `geom` | str \| geom | `"pointrange"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"identity"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `fun_data` | str \| callable | `"mean_cl_boot"` | If string, it should be one of: or any function that takes a array and returns a dataframe with three columns named y, ymin and ymax. |
| `fun_y` | callable | `None` | Any function that takes a array_like and returns a value |
| `fun_ymin` | callable | `None` | Any function that takes an array_like and returns a value |
| `fun_ymax` | callable | `None` | Any function that takes an array_like and returns a value |
| `fun_args` | dict | `None` | Arguments to any of the functions. Provided the names of the arguments of the different functions are in not conflict, the arguments will be assigned to the right functions. If there is a conflict, create a wrapper function that resolves the ambiguity in the argument names. |
| `random_state` | int \| RandomState | `None` | Seed or Random number generator to use. If None, then numpy global generator numpy.random is used. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the geom. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y |  |

## See Also

*(List related symbols here.)*
