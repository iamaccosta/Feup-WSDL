{
  description = "A very basic flake for WSDL project";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { nixpkgs, ... }:  
  let system = "x86_64-linux";
  pkgs = import nixpkgs { inherit system; };
  in {
    formatter.${system} = pkgs.alejandra;

    devShell.${system} = pkgs.mkShell {
      packages = with pkgs; [
        python3
        nodejs_22
      ];
    };
  };
}
