# Maintainer: ArchLatam <corelinux@gmail.com>

pkgname=archlatam-welcome
pkgver=0.1.0
pkgrel=1
pkgdesc="Welcome application and Calamares launcher for ArchLatam"
arch=('any')
url="https://archlatam.github.io"
license=('GPL-3.0-or-later')
depends=('python' 'pyside6')

source=('main.py' 'archlatam-welcome.desktop' 'LICENSE' 'archlatam-welcome-autostart.desktop')
sha256sums=(
  '14c03d2d90a430ac89d87ce1636d387688080284f99a7c92b5fbee9c733fdb71'
  'dfb58a07d5c2f911285f6490dc906e1dcf9bd72c4b7ee61ad2c6e19ddbe2967e'
  'fb981668c18a279e285fc4d83fba1e836cc84dd4daa73c9697d3cfd2d8aca6e0'
  '4f547896d17da69618488f8ec867911cb0d0122607443c26edb478bb1ef6e5d4'
)

package() {
  install -Dm755 "$srcdir/main.py" \
    "$pkgdir/usr/bin/archlatam-welcome"

  install -Dm644 "$srcdir/archlatam-welcome.desktop" \
    "$pkgdir/usr/share/applications/archlatam-welcome.desktop"

  install -Dm644 "$srcdir/archlatam-welcome-autostart.desktop" \
    "$pkgdir/etc/xdg/autostart/archlatam-welcome.desktop"

  install -Dm644 "$srcdir/LICENSE" \
    "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
