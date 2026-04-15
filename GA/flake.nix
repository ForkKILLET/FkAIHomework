{
  description = "Develop Python on Nix with uv";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs =
    { nixpkgs, ... }:
    let
      inherit (nixpkgs) lib;
      forAllSystems = lib.genAttrs lib.systems.flakeExposed;
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};

        in
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              uv
              vim
            ];

            buildInputs = with pkgs; [
              glib
              zlib
              libGL
              stdenv.cc.cc.lib
            ];

            env = {
              LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (with pkgs;
                pythonManylinuxPackages.manylinux1 ++
                [
                  libX11
                  libxkbcommon
                  fontconfig
                  freetype
                  zstd
                  dbus.lib
                  libxcb
                  libxcb-cursor
                  libxcb-wm
                  libxcb-util
                  libxcb-image
                  libxcb-keysyms
                  libxcb-render-util
                ]
              );

              PROJECT = "ga";
            };

            shellHook = ''
              unset PYTHONPATH
              uv sync
              . .venv/bin/activate
            '';
          };
        }
      );
    };
}
