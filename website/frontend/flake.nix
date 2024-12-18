{
  description = "A Node.js app";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = {nixpkgs, ...}: let
    system = "x86_64-linux";
    pkgs = import nixpkgs {inherit system;};
  in {
    formatter.${system} = pkgs.alejandra;

    devShell.${system} = pkgs.mkShell {
      packages = with pkgs; [
        nodejs_22
        corepack_22
      ];
    };
  };
}
