# nix/tui.nix — NIA TUI (Ink/React) compiled with tsc and bundled
{ pkgs, niaNpmLib, ... }:
let
  src = ../ui-tui;
  npmDeps = pkgs.fetchNpmDeps {
    inherit src;
    hash = "sha256-a/HGI9OgVcTnZrMXA7xFMGnFoVxyHe95fulVz+WNYB0=";
  };

  npm = niaNpmLib.mkNpmPassthru { folder = "ui-tui"; attr = "tui"; pname = "nia-tui"; };

  packageJson = builtins.fromJSON (builtins.readFile (src + "/package.json"));
  version = packageJson.version;
in
pkgs.buildNpmPackage (npm // {
  pname = "nia-tui";
  inherit src npmDeps version;

  doCheck = false;
  npmFlags = [ "--legacy-peer-deps" ];

  installPhase = ''
    runHook preInstall

    mkdir -p $out/lib/nia-tui

    cp -r dist $out/lib/nia-tui/dist

    # runtime node_modules
    cp -r node_modules $out/lib/nia-tui/node_modules

    # @nia/ink is a file: dependency, we need to copy it in fr
    rm -f $out/lib/nia-tui/node_modules/@nia/ink
    cp -r packages/nia-ink $out/lib/nia-tui/node_modules/@nia/ink

    # package.json needed for "type": "module" resolution
    cp package.json $out/lib/nia-tui/

    runHook postInstall
  '';
})
