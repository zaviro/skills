# Example only. Adapt paths/module placement to the repository that owns your Home Manager config.
{ pkgs, ... }:

let
  desktopctl = pkgs.writeShellApplication {
    name = "desktopctl";
    runtimeInputs = [ pkgs.nodejs ];
    text = ''
      exec ${pkgs.nodejs}/bin/node --experimental-strip-types \
        ${../bin/desktopctl.ts} "$@"
    '';
  };
in
{
  home.packages = [
    desktopctl
  ];

  # Optional: make the skills themselves declarative for Codex.
  # Adjust `../desktop-control` and `../desktop-system` to the real paths
  # after placing this bundle inside your nix-config repository.
  #
  # home.file.".codex/skills/desktop-control".source = ../desktop-control;
  # home.file.".codex/skills/desktop-system".source = ../desktop-system;

  # Optional Niri runtime-preview hook.
  # Add this at top level to the declaratively generated Niri KDL only if
  # you actually want a temporary preview layer:
  #
  # include optional=true "~/.local/state/desktop-agent/niri-preview.kdl"
}
