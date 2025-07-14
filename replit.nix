{pkgs}: {
  deps = [
    pkgs.zlib
    pkgs.xcodebuild
    pkgs.postgresql
    pkgs.sqlite
    pkgs.glibcLocales
  ];
}
