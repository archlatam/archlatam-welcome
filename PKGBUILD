# Maintainer: ArchLatam <corelinux@gmail.com>

pkgname=archlatam-welcome
pkgver=0.1.0
pkgrel=2
pkgdesc="Welcome application and Calamares launcher for ArchLatam"
arch=('any')
url="https://archlatam.github.io"
license=('GPL-3.0-or-later')
depends=('python' 'pyside6')
install="$pkgname.install"

source=('main.py' 'archlatam-welcome.desktop' 'LICENSE' 'archlatam-welcome-autostart.desktop')
sha256sums=(
  'd7d20f783e37c7730fb9cca59b31ee154788ccecb4f2b9053362ac407cf18738'
  '15820138c9e650906ab1d57e93ff6a6e42cdb285131fd3ec8720db50d77b8735'
  'fb981668c18a279e285fc4d83fba1e836cc84dd4daa73c9697d3cfd2d8aca6e0'
  '79d22db36d9a5dd4ec8833595a6cb62954155c5671a88ab7eede9eb272a6097e'
)

prepare() {
  # makepkg no acepta fuentes locales en subcarpetas, así que los iconos
  # que viven en assets/ se copian a $srcdir antes de empaquetar.
  cp -f "$startdir/assets/archlatam-welcome.svg" "$srcdir/"
  cp -f "$startdir/assets/"archlatam-welcome-*.png "$srcdir/"
}

package() {
  install -Dm755 "$srcdir/main.py" \
    "$pkgdir/usr/bin/archlatam-welcome"

  install -Dm644 "$srcdir/archlatam-welcome.desktop" \
    "$pkgdir/usr/share/applications/archlatam-welcome.desktop"

  install -Dm644 "$srcdir/archlatam-welcome-autostart.desktop" \
    "$pkgdir/etc/xdg/autostart/archlatam-welcome.desktop"

  install -Dm644 "$srcdir/LICENSE" \
    "$pkgdir/usr/share/licenses/$pkgname/LICENSE"

  # Icono en el tema hicolor (ventana + barra de tareas de KDE Plasma)
  install -Dm644 "$srcdir/archlatam-welcome.svg" \
    "$pkgdir/usr/share/icons/hicolor/scalable/apps/archlatam-welcome.svg"

  for size in 16 22 24 32 48 64 128 256 512; do
    install -Dm644 "$srcdir/archlatam-welcome-$size.png" \
      "$pkgdir/usr/share/icons/hicolor/${size}x${size}/apps/archlatam-welcome.png"
  done
}
