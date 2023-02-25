{
  description = "Application packaged using poetry2nix";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    # url = "github:jhh/poetry2nix/build-systems";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        inherit (poetry2nix.legacyPackages.${system}) mkPoetryEnv mkPoetryApplication;
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        packages = {
          myapp = mkPoetryApplication { projectDir = self; };

          devEnv = mkPoetryEnv {
            projectDir = self;
            preferWheels = true;
          };

          default = self.packages.${system}.devEnv;
        };

        devShells.default = pkgs.mkShell {
          packages = [
            self.packages.${system}.devEnv
            poetry2nix.packages.${system}.poetry
            pkgs.pre-commit
          ];
        };

      });
}
