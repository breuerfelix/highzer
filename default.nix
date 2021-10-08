{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  pname = "just-testing";
  buildInputs = with pkgs; [
    geckodriver
    poetry
    ffmpeg
    imagemagick
  ];
  shellHook = ''
    export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [pkgs.stdenv.cc.cc]}
  '';
}
