# Example only. Adapt paths/module placement to the repository that owns your Home Manager config.
{ pkgs, ... }:

let
  desktopctl = pkgs.writeShellApplication {
    name = "desktopctl";
    runtimeInputs = [ pkgs.nodejs ];
    text = ''
      exec ${pkgs.nodejs}/bin/node --experimental-strip-types \
        ${../scripts/desktopctl.ts} "$@"
    '';
  };
in
{
  home.packages = [
    desktopctl
  ];

  # Optional: expose these Skills declaratively at the user-level Agent Skills path.
  # Adjust the paths if this repository is consumed through another Nix source.
  #
  # home.file.".agents/skills/desktop-control".source = ../.;
  # home.file.".agents/skills/desktop-system".source = ../../desktop-system;

  # Optional Niri runtime-preview hook.
  # Add this at top level to the declaratively generated Niri KDL only if
  # you actually want a temporary preview layer:
  #
  # include optional=true "~/.local/state/desktop-agent/niri-preview.kdl"
}
