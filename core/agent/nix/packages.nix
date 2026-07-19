# nix/packages.nix — NIA package built with uv2nix
{ inputs, ... }:
{
  perSystem =
    { pkgs, inputs', ... }:
    let
      niaAgent = pkgs.callPackage ./nia-agent.nix {
        inherit (inputs) uv2nix pyproject-nix pyproject-build-systems;
        npm-lockfile-fix = inputs'.npm-lockfile-fix.packages.default;
        # Only embed clean revs — dirtyRev doesn't represent any upstream
        # commit, so comparing it would always claim "update available".
        rev = inputs.self.rev or null;
      };
    in
    {
      packages = {
        default = niaAgent;
        tui = niaAgent.niaTui;
        web = niaAgent.niaWeb;

        fix-lockfiles = niaAgent.niaNpmLib.mkFixLockfiles {
          packages = [ niaAgent.niaTui niaAgent.niaWeb ];
        };
      };
    };
}
