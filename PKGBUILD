# See http://wiki.archlinux.org/index.php/Python_Package_Guidelines for more
# information on Python packaging.

# Maintainer: Yann Balland <y.balland@laposte.net>
_name=katal
_branch=master

pkgname=$_name-git
pkgrel=1
pkgver=0.3.2.r6.ge5b4210
pkgdesc="Create a catalogue from various source directories, without any duplicate. Add some tags to the files."
arch=('any')
url="https://github.com/suizokukan/katal"
license=('GPL3')
depends=('python')
makedepends=('git')
provides=("$_name")
source=("$pkgname::git+https://github.com/suizokukan/katal")
md5sums=(SKIP)

pkgver() { 
  cd "$srcdir/$pkgname"
  git describe --long --tags | sed 's/^v//;s/\([^-]*-g\)/r\1/;s/-/./g'
}

package() {
  cd "$srcdir/$pkgname"
  python setup.py install --root="$pkgdir/" --optimize=1
}

# vim:set ts=2 sw=2 et:
