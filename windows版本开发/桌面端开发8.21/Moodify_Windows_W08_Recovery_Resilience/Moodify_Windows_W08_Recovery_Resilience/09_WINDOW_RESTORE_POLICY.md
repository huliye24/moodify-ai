# Window Restore Policy

## Persist

```text
x
y
width
height
maximized
```

## Restore Validation

- minimum width/height
- finite numeric values
- visible display intersection
- current monitor topology
- work area bounds

## Off-screen

如果上次 monitor 不存在：

```text
move/clamp window to primary/current visible display
```

## Maximized

如果 previously maximized：

```text
restore maximized
```

但仍需安全 bounds fallback。

## Do Not Persist

- transient tooltip/menu
- drag overlay
- temporary modal coordinates
