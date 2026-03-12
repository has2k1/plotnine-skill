# plotnine Skill

An [AI Code skill](https://docs.anthropic.com/en/docs/claude-code/skills) for generating, refining, and exporting data visualizations using [plotnine](https://plotnine.org). When installed, Claude gains deep knowledge of plotnine's grammar of graphics — geoms, themes, scales, facets, accessibility best practices, and more.

## Installation

### Claude Code (Plugin)

```
/plugin marketplace add has2k1/plotnine-skill
/plugin install plotnine@plotnine-skill
```

### Manual Installation

1. Clone this repository:

```
git clone https://github.com/has2k1/plotnine-skill.git
cd plotnine-skill
```

2. Copy skill to your Claude Code skills directory:

```
cp -r skills/plotnine/ ~/.config/.claude/skills/
```

## Using the skill

Once installed, ask Claude things like:

```
> Use plotnine to create a scatter plot of price vs carat from the diamonds dataset
```

Claude will produce complete, runnable plotnine code — no pseudocode or undefined variables.

## License

This repository is licensed under the MIT License. See [LICENSE](./LICENSE) for details.
