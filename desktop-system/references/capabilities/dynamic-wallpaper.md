# Capability: Dynamic Wallpaper

## Goal

Provide video wallpaper on Wayland/Niri while keeping the long-term configuration declarative.

## Typical resources

Required or commonly required:

- `mpvpaper`
- `mpv`

Optional:

- `ffmpeg` — frame extraction/theme synchronization
- Noctalia mpvpaper integration/plugin — picker, assignment management, pause/resource policy
- wallpaper/video directory
- theme synchronization hook

## Design choices

Ask from existing context or infer conservatively:

### Engine

Prefer `mpvpaper` when the current shell/compositor integration already targets it.

### Shell integration

If Noctalia is present, prefer its supported mpvpaper integration instead of writing a competing supervisor.

If another shell owns wallpaper management, integrate with that shell rather than running two wallpaper managers.

### Theme synchronization

Treat as optional.

If enabled:

```text
video
→ extract representative frame
→ shell/theme engine derives palette
```

Do not continuously extract frames merely to update colors unless the user explicitly wants continuously changing palette.

### Pause policy

Prefer hardware decode.

Expose pause/resource behavior as policy rather than hard-coding it.

Possible policy:

```text
never
fullscreen
manual
```

Do not assume workspace count multiplies video instances; reason in terms of outputs and actual supervisor behavior.

## Nix implementation shape

A capability may contain:

```nix
{
  home.packages = with pkgs; [
    mpvpaper
    mpv
    # ffmpeg only if needed
  ];

  # Noctalia config/plugin integration
  # optional user service only if the shell is not supervising mpvpaper
}
```

Avoid starting both a custom systemd user `mpvpaper` service and a Noctalia plugin that also supervises mpvpaper.

## Validation

Check:

- only one component owns/supervises the wallpaper process
- video directory exists or is created declaratively
- hardware decoding is enabled where supported
- shell config validates
- Niri config validates
- process count matches the intended number of outputs
- no stale static wallpaper process is fighting the video wallpaper

## Runtime test

After activation:

- switch multiple workspaces
- open/close overview
- fullscreen an application
- observe CPU/GPU/video decode usage if performance is a concern
- ensure wallpaper survives shell reload as intended

## Removal

Removal must be straightforward:

- disable/remove integration
- remove packages no longer used
- remove hooks/services
- retain user-owned video files unless explicitly asked to delete them
