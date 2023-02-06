Name:       fakeroot
Summary:    Gives a fake root environment
Version:    1.29
Release:    1
# setenv.c: LGPLv2+
# contrib/Fakeroot-Stat-1.8.8: Perl (GPL+ or Artistic)
# the rest: GPLv3+
License:    GPLv3+ and LGPLv2+ and (GPL+ or Artistic)
URL:        https://tracker.debian.org/pkg/fakeroot
Source0:    %{name}_%{version}.tar.gz
Patch0:     disable-cp-a-test.patch
Patch1:     disable-tar-test.patch
# Debian package patches, from debian.tar.xz
Patch2:     debian_fix-shell-in-fakeroot.patch
# Address some POSIX-types related problems.
Patch3:     fakeroot-inttypes.patch
# Fix LD_LIBRARY_PATH for multilib: https://bugzilla.redhat.com/show_bug.cgi?id=1241527
Patch4:     fakeroot-multilib.patch
Patch5:     debian_also-wrap-stat-library-call.patch
Requires:   util-linux
Requires(post):  /sbin/ldconfig
Requires(postun):  /sbin/ldconfig
BuildRequires:  gcc-c++
BuildRequires:  util-linux
BuildRequires:  sharutils
BuildRequires:  pkgconfig(libcap)

%description
fakeroot runs a command in an environment wherein it appears to have
root privileges for file manipulation. fakeroot works by replacing the
file manipulation library functions (chmod(2), stat(2) etc.) by ones
that simulate the effect the real library functions would have had,
had the user really been root.

%prep
%autosetup -p1 -n %{name}-%{version}

%build
./bootstrap
for file in ./doc/{*.1,*/*.1}; do
  iconv -f latin1 -t utf8 < $file > $file.new && \
  mv -f $file.new $file
done

# all build scripts in origin specfile as the following:
for type in sysv tcp; do
mkdir -p obj-$type
cd obj-$type
cat >> configure << 'EOF'
#! /bin/sh
exec ../configure "$@"
EOF
chmod +x configure
%configure \
  --disable-dependency-tracking \
  --disable-static \
  --libdir=%{_libdir}/libfakeroot \
  --with-ipc=$type \
  --program-suffix=-$type
%make_build
cd ..
done

%install

# all install scripts in origin specfile as the following:
rm -rf %{buildroot}
for type in sysv tcp; do
  make -C obj-$type install libdir=%{_libdir}/libfakeroot DESTDIR=%{buildroot}
  chmod 644 %{buildroot}%{_libdir}/libfakeroot/libfakeroot-0.so 
  mv %{buildroot}%{_libdir}/libfakeroot/libfakeroot-0.so \
     %{buildroot}%{_libdir}/libfakeroot/libfakeroot-$type.so
  rm -f %{buildroot}%{_libdir}/libfakeroot/libfakeroot.so
  rm -f %{buildroot}%{_libdir}/libfakeroot/libfakeroot.*a*
done

ln -s faked-sysv %{buildroot}%{_bindir}/faked
ln -s fakeroot-sysv %{buildroot}%{_bindir}/fakeroot
ln -s libfakeroot-sysv.so %{buildroot}%{_libdir}/libfakeroot/libfakeroot-0.so

# remove man pages
rm -Rf %{buildroot}/%{_mandir}

%check
%if ! 0%{?qemu_user_space_build}
for type in sysv tcp; do
  make -C obj-$type check
done
%endif

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%license COPYING
%doc AUTHORS BUGS DEBUG doc/README.saving
%{_bindir}/faked-*
%{_bindir}/faked
%{_bindir}/fakeroot-*
%{_bindir}/fakeroot
%dir %{_libdir}/libfakeroot
%{_libdir}/libfakeroot/libfakeroot-*.so
%{_libdir}/libfakeroot/libfakeroot-0.so
