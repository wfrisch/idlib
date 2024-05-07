#!/usr/bin/env python3
from pathlib import Path
import re


re_source = re.compile(r'.*\.(c|cc|cpp|cxx|h|hh|hpp|hxx|asm|S)$', re.I)


class Library:
    def __init__(self, name, sparse_files=[]):
        self.name = name
        self.sparse_files = sparse_files

    @property
    def path(self):
        return Path("libraries") / self.name

    @property
    def sparse_paths(self):
        for f in self.sparse_files:
            for p in self.path.glob(f):
                if re_source.match(p.name) and p.is_file():
                    yield p.relative_to(self.path)


libraries = [
    Library('boringssl', [
            "ssl/internal.h",
            "ssl/ssl_lib.cc",
            "ssl/handshake_client.cc",
            "ssl/extensions.cc",
            "ssl/handshake_server.cc",
            "ssl/test/bssl_shim.cc",
            "ssl/ssl_test.cc",
            "ssl/ssl_x509.cc",
            "ssl/s3_lib.cc",
            "ssl/handshake.cc",
            "ssl/ssl_session.cc",
            "ssl/s3_both.cc",
            "ssl/ssl_cipher.cc",
            "ssl/ssl_cert.cc",
            "ssl/tls13_server.cc"]),
    Library('botan',
            [
             "src/lib/tls/tls12/tls_server_impl_12.cpp",
             "src/lib/tls/tls_server.cpp",
             "src/lib/tls/tls12/tls_client_impl_12.cpp",
             "src/lib/tls/tls_client.cpp",
             "src/tests/unit_x509.cpp",
             "src/tests/test_pubkey.cpp",
             "src/lib/tls/tls_messages.h",
             "src/lib/x509/x509path.cpp",
             "src/lib/math/bigint/bigint.h",
             "src/lib/pubkey/rsa/rsa.cpp",
             "src/lib/x509/x509cert.cpp",
             "src/lib/pubkey/ec_group/ec_point.cpp",
             "src/lib/tls/msg_client_hello.cpp",
             "src/lib/x509/x509_ext.cpp",
             "src/lib/tls/tls12/tls_channel_impl_12.cpp",
             "src/lib/tls/tls_policy.cpp",
             "src/lib/block/aes/aes.cpp",
             "src/lib/pubkey/pubkey.cpp",
             "src/lib/math/bigint/bigint.cpp",
             "src/cli/tls_client.cpp",
            ]),
    Library('brotli',
            ['c/common/platform.h',
             'c/enc/encode.c',
             'c/enc/brotli_bit_stream.c',
             'c/dec/decode.c']),
    Library('curl',
            ['lib/http.c',
             'lib/ftp.c',
             'lib/smtp.c']),
    Library('fatfs',
            ['source/ff.c']),
    Library('flac',
            ['src/libFLAC/stream_encoder.c',
             'src/libFLAC/stream_decoder.c',
             'src/flac/encode.c',
             'src/flac/decode.c']),
    Library('fmt',
            ['src/os.cc',
             'src/fmt.cc']),
    Library('freetype',
            [
             "src/base/ftobjs.c",
             "include/freetype/freetype.h",
             "src/truetype/ttgload.c",
             "src/truetype/ttinterp.c",
             "src/smooth/ftgrays.c",
             "src/type1/t1load.c",
             "src/sfnt/sfobjs.c",
             "src/raster/ftraster.c",
             "src/cff/cffobjs.c",
             "include/freetype/config/ftoption.h",
             "src/truetype/ttobjs.c",
             "src/cff/cffload.c",
             "src/truetype/ttgxvar.c",
             "src/psaux/cffdecode.c",
             "src/cff/cffdrivr.c",
             "src/autofit/aflatin.c",
             "src/cff/cffgload.c",
             "devel/ftoption.h",
             "src/psaux/psobjs.c",
             "include/freetype/internal/ftobjs.h",
            ]),
    Library('googletest',
            ["googletest/src/gtest.cc",
             "googletest/include/gtest/internal/gtest-port.h",
             "googletest/test/gtest_unittest.cc",
             "googlemock/include/gmock/gmock-matchers.h",
             "googletest/include/gtest/gtest.h",
             "googletest/include/gtest/internal/gtest-internal.h",
             "googletest/src/gtest-internal-inl.h",
             "googletest/src/gtest-death-test.cc",
             "googlemock/include/gmock/gmock-actions.h",
             "googletest/src/gtest-port.cc",
             "googlemock/test/gmock-actions_test.cc",
             "googlemock/include/gmock/gmock-spec-builders.h",
             "googlemock/include/gmock/internal/gmock-internal-utils.h",
             "googletest/test/googletest-port-test.cc",
             "googlemock/src/gmock-spec-builders.cc",
             "googletest/test/googletest-printers-test.cc",
             "googletest/include/gtest/gtest-printers.h",
             "googletest/test/googletest-death-test-test.cc",
             "googlemock/include/gmock/gmock-more-actions.h",
             "googlemock/test/gmock-spec-builders_test.cc"]),
    Library('harfbuzz',
            [
             "src/hb-open-type.hh",
             "src/hb-ot-layout-gsubgpos.hh",
             "src/hb-ot-layout.cc",
             "src/hb.hh",
             "src/hb-ot-layout-common.hh",
             "src/hb-ot-layout-gsub-table.hh",
             "src/hb-ot-shape.cc",
             "src/hb-ot-layout-gpos-table.hh",
             "src/hb-buffer.cc",
             "src/hb-bit-set.hh",
             "src/hb-subset-plan.cc",
             "src/hb-set.hh",
             "src/hb-ot-shaper-indic.cc",
             "src/hb-ot-shaper-khmer.cc",
             "src/hb-font.cc",
             "src/hb-buffer.hh",
             "src/hb-ot-layout.hh",
             "src/OT/Layout/GDEF/GDEF.hh",
             "src/hb-subset.cc",
             "src/hb-ft.cc",
            ]),
    Library('hunspell',
            ["src/hunspell/affixmgr.cxx",
             "src/hunspell/hunspell.cxx",
             "src/hunspell/suggestmgr.cxx",
             "src/tools/hunspell.cxx",
             "src/hunspell/csutil.cxx",
             "src/hunspell/hashmgr.cxx",
             "src/hunspell/affixmgr.hxx",
             "src/hunspell/csutil.hxx",
             "src/hunspell/hunspell.hxx",
             "src/hunspell/suggestmgr.hxx",
             "src/hunspell/affentry.cxx",
             "src/hunspell/hashmgr.hxx",
             "src/hunspell/affentry.hxx",
             "src/hunspell/replist.cxx",
             "src/parsers/textparser.cxx",
             "src/hunspell/atypes.hxx",
             "src/tools/munch.cxx",
             "src/tools/unmunch.cxx",
             "src/parsers/textparser.hxx",
             "src/hunspell/replist.hxx"]),
    Library('json-c',
            [
             "json_object.c",
             "json_object.h",
             "json_tokener.c",
             "json_util.c",
             "linkhash.c",
             "tests/test1.c",
             "json_tokener.h",
             "json_object_private.h",
             "linkhash.h",
             "printbuf.c",
             "tests/test_parse.c",
             "arraylist.c",
             "json_util.h",
             "printbuf.h",
             "arraylist.h",
             "random_seed.c",
             "tests/test_util_file.c",
             "debug.h",
             "json_pointer.c",
             "json_inttypes.h",
            ]),
    Library('leveldb',
            ["db/db_test.cc",
             "db/db_impl.cc",
             "db/version_set.cc",
             "benchmarks/db_bench.cc",
             "util/env_posix.cc",
             "port/port_stdcxx.h",
             "include/leveldb/db.h",
             "util/env_test.cc",
             "table/table_test.cc",
             "include/leveldb/options.h",
             "db/db_impl.h",
             "db/version_set.h",
             "db/corruption_test.cc",
             "include/leveldb/env.h",
             "db/log_test.cc",
             "util/cache.cc",
             "port/port_example.h",
             "db/repair.cc",
             "db/skiplist_test.cc",
             "table/format.cc"]),
    Library('libb2',
            ["src/blake2b.c",
             "src/blake2-dispatch.c",
             "src/blake2s.c",
             "src/blake2-impl.h",
             "src/blake2b-round.h",
             "src/blake2s-load-xop.h",
             "src/blake2s-round.h",
             "src/blake2-config.h",
             "src/blake2bp.c",
             "src/blake2b-ref.c",
             "src/blake2s-ref.c",
             "src/blake2sp.c",
             "src/blake2.h",
             "src/blake2-kat.h",
             "src/blake2b-load-sse2.h",
             "src/blake2b-load-sse41.h",
             "src/blake2b-test.c",
             "src/blake2bp-test.c",
             "src/blake2s-load-sse2.h",
             "src/blake2s-load-sse41.h"]),
    Library('libbpf',
            ["src/libbpf.c",
             "src/libbpf.h",
             "src/btf.c",
             "src/bpf.c",
             "src/libbpf_internal.h",
             "src/bpf.h",
             "src/bpf_helper_defs.h",
             "src/btf.h",
             "src/btf_dump.c",
             "src/bpf_tracing.h",
             "src/bpf_helpers.h",
             "src/libbpf_probes.c",
             "src/netlink.c",
             "src/bpf_core_read.h",
             "src/linker.c",
             "src/ringbuf.c"]),
    Library('libevent',
            [
             "event.c",
             "http.c",
             "test/regress.c",
             "buffer.c",
             "test/regress_http.c",
             "evdns.c",
             "evutil.c",
             "test/regress_dns.c",
             "include/event2/http.h",
             "bufferevent.c",
             "kqueue.c",
             "include/event2/event.h",
             "include/event2/util.h",
             "test/regress_bufferevent.c",
             "epoll.c",
             "include/event.h",
             "bufferevent-internal.h",
             "test/regress_buffer.c",
             "signal.c",
             "event-internal.h",
            ]),
    Library('libjpeg-turbo',
            ['jcarith.c',
             'jchuff.c',
             'jdhuff.c',
             'turbojpeg.c']),
    Library('libnsgif',
            ['src/gif.c',
             'src/lzw.c']),
    Library('libpng',
            ['png.c',
             'png.h']),
    Library('libsodium',
            [
             "src/libsodium/sodium/utils.c",
             "src/libsodium/randombytes/internal/randombytes_internal_random.c",
             "src/libsodium/crypto_aead/aes256gcm/aesni/aead_aes256gcm_aesni.c",
             "src/libsodium/crypto_aead/aes256gcm/armcrypto/aead_aes256gcm_armcrypto.c",
             "src/libsodium/randombytes/sysrandom/randombytes_sysrandom.c",
             "src/libsodium/sodium/core.c",
             "src/libsodium/crypto_core/ed25519/ref10/ed25519_ref10.c",
             "src/libsodium/include/sodium.h",
             "src/libsodium/sodium/runtime.c",
             "builds/msvc/version.h",
             "src/libsodium/crypto_sign/ed25519/ref10/open.c",
             "src/libsodium/randombytes/randombytes.c",
             "test/default/cmptest.h",
             "src/libsodium/include/sodium/utils.h",
             "src/libsodium/crypto_pwhash/scryptsalsa208sha256/sse/pwhash_scryptsalsa208sha256_sse.c",
             "src/libsodium/crypto_sign/ed25519/ref10/sign.c",
             "src/libsodium/crypto_sign/ed25519/ref10/keypair.c",
             "src/libsodium/crypto_generichash/blake2b/ref/blake2b-ref.c",
             "src/libsodium/include/sodium/crypto_onetimeauth_poly1305.h",
            ]),
    Library('libsndfile',
            [
             "src/sndfile.c",
             "src/common.h",
             "src/wav.c",
             "src/aiff.c",
             "src/ogg_vorbis.c",
             "include/sndfile.h",
             "src/ogg.c",
             "src/common.c",
             "src/file_io.c",
             "src/wavlike.c",
             "src/flac.c",
             "programs/sndfile-play.c",
             "programs/sndfile-convert.c",
             "src/caf.c",
             "tests/command_test.c",
             "src/rf64.c",
             "src/ima_adpcm.c",
             "src/double64.c",
             "tests/lossy_comp_test.c",
             "src/sd2.c",
            ]),
    Library('libtiff',
            ["libtiff/tif_dirread.c",
             "libtiff/tif_dir.c",
             "libtiff/tif_jpeg.c",
             "libtiff/tif_dirinfo.c",
             "libtiff/tiffiop.h",
             "libtiff/tif_getimage.c",
             "libtiff/tif_dirwrite.c",
             "tools/unsupported/tiff2pdf.c",
             "libtiff/tiffio.h",
             "tools/tiffcp.c",
             "libtiff/tif_fax3.c",
             "libtiff/tif_read.c",
             "libtiff/tiff.h",
             "libtiff/tif_ojpeg.c",
             "libtiff/tif_lzw.c",
             "tools/unsupported/tiff2ps.c",
             "libtiff/tif_print.c",
             "libtiff/tif_open.c",
             "archive/tools/tiffcrop.c",
             "libtiff/tif_dir.h"]),
    Library('libusb',
            [
             "libusb/version_nano.h",
             "libusb/core.c",
             "libusb/io.c",
             "libusb/os/linux_usbfs.c",
             "libusb/libusbi.h",
             "libusb/os/windows_winusb.c",
             "libusb/os/darwin_usb.c",
             "libusb/libusb.h",
             "libusb/descriptor.c",
             "libusb/version.h",
             "libusb/os/windows_winusb.h",
             "libusb/sync.c",
             "libusb/os/openbsd_usb.c",
             "libusb/os/netbsd_usb.c",
             "libusb/os/windows_common.c",
             "libusb/hotplug.c",
             "libusb/os/darwin_usb.h",
            ]),
    Library('libuv',
            ['src/uv-common.c',
             'src/uv-common.h',
             'src/unix/linux.c',
             'src/unix/core.c']),
    Library('libwebp',
            [
             "src/enc/vp8l_enc.c",
             "examples/cwebp.c",
             "src/enc/vp8i_enc.h",
             "src/dsp/dsp.h",
             "src/enc/picture_csp_enc.c",
             "src/dec/vp8l_dec.c",
             "src/enc/backward_references_enc.c",
             "src/dsp/lossless_enc.c",
             "src/dec/vp8i_dec.h",
             "src/dsp/lossless.c",
             "src/dec/vp8_dec.c",
             "src/dec/webp_dec.c",
             "src/webp/encode.h",
             "src/enc/histogram_enc.c",
             "src/dsp/dec_neon.c",
             "src/webp/mux.h",
             "src/enc/picture_enc.c",
            ]),
    Library('libyaml',
            [
             "src/scanner.c",
             "include/yaml.h",
             "src/emitter.c",
             "src/api.c",
             "src/parser.c",
             "src/yaml_private.h",
             "src/reader.c",
             "src/loader.c",
             "tests/run-emitter.c",
             "tests/test-version.c",
             "tests/example-deconstructor.c",
             "tests/run-dumper.c",
             "tests/run-parser.c",
             "src/writer.c",
             "tests/run-emitter-test-suite.c",
             "tests/example-deconstructor-alt.c",
             "tests/example-reformatter.c",
             "tests/run-parser-test-suite.c",
             "src/dumper.c",
            ]),
    Library('libxml2',
            [
             "parser.c",
             "tree.c",
             "xpath.c",
             "HTMLparser.c",
             "valid.c",
             "xmllint.c",
             "xmlIO.c",
             "SAX2.c",
             "xmlschemas.c",
             "parserInternals.c",
             "xmlreader.c",
             "include/libxml/tree.h",
             "include/libxml/parser.h",
             "xinclude.c",
             "encoding.c",
             "relaxng.c",
             "debugXML.c",
             "xmlschemastypes.c",
             "nanohttp.c",
             "error.c",
            ]),
    Library('libzmq',
            [
             "include/zmq.h",
             "src/socket_base.cpp",
             "src/zmq.cpp",
             "src/session_base.cpp",
             "src/options.cpp",
             "src/router.cpp",
             "src/ctx.cpp",
             "src/socket_base.hpp",
             "src/stream.cpp",
             "src/dgram.cpp",
             "src/ws_connecter.cpp",
             "src/options.hpp",
             "src/tcp_connecter.cpp",
             "src/ws_listener.cpp",
             "src/pipe.cpp",
             "src/tcp_listener.cpp",
             "src/signaler.cpp",
             "src/xpub.cpp",
             "src/ip.cpp",
             "src/tcp_address.cpp",
            ]),
    Library('Little-CMS',
            ["include/lcms2.h",
             "src/cmstypes.c",
             "testbed/testcms2.c",
             "src/cmscgats.c",
             "src/cmsopt.c",
             "src/cmsio0.c",
             "src/cmsxform.c",
             "src/lcms2_internal.h",
             "src/cmslut.c",
             "src/cmspack.c",
             "src/cmsplugin.c",
             "src/cmscnvrt.c",
             "src/cmsps2.c",
             "src/cmsnamed.c",
             "src/cmsvirt.c",
             "utils/tificc/tificc.c",
             "src/cmsio1.c",
             "src/cmsgamma.c",
             "src/cmsintrp.c",
             "include/lcms2_plugin.h"]),
    Library('lua',
            ['lvm.c',    # Lua Virtual Machine
             'lapi.c',   # Lua API
             'lgc.c']),  # Lua Garbage Collector
    Library('mbedtls',
            [
             "library/ssl_tls.c",
             "library/ssl_msg.c",
             "include/mbedtls/ssl.h",
             "include/mbedtls/mbedtls_config.h",
             "library/ssl_tls12_server.c",
             "programs/ssl/ssl_server2.c",
             "library/ssl_tls12_client.c",
             "library/x509_crt.c",
             "programs/ssl/ssl_client2.c",
             "library/psa_crypto.c",
             "library/ecp.c",
             "library/rsa.c",
             "library/bignum.c",
             "library/ssl_misc.h",
             "include/mbedtls/pk.h",
             "include/mbedtls/config_adjust_legacy_from_psa.h",
             "include/mbedtls/check_config.h",
             "library/aes.c",
             "programs/test/benchmark.c",
             "include/mbedtls/x509_crt.h",
            ]),
    Library('minizip-ng',
            ['minizip.c',
             'mz_zip.c']),
    Library('nghttp2', [
            "lib/nghttp2_session.c",
            "src/shrpx.cc",
            "lib/includes/nghttp2/nghttp2.h",
            "src/shrpx_http2_upstream.cc",
            "src/shrpx_config.cc",
            "src/nghttp.cc",
            "src/shrpx_config.h",
            "src/shrpx_http2_session.cc",
            "src/shrpx_tls.cc",
            "src/shrpx_https_upstream.cc",
            "src/HttpServer.cc",
            "src/shrpx_client_handler.cc",
            "src/shrpx_http_downstream_connection.cc",
            "src/h2load.cc",
            "src/shrpx_downstream.cc",
            "src/util.cc",
            "lib/nghttp2_session.h",
            "src/util.h"]),
    Library('openjpeg',
            ['src/lib/openjp2/j2k.c',
             'src/lib/openjpip/jp2k_decoder.c',
             'src/lib/openjpip/jp2k_encoder.c']),
    Library('pcre2',
            ['src/pcre2_compile.c',
             'src/pcre2_match.c']),
    Library('protobuf', []),
    Library('sqlite',
            ["src/sqliteInt.h",
             "src/vdbe.c",
             "src/where.c",
             "src/btree.c",
             "src/select.c",
             "src/expr.c",
             "src/build.c",
             "src/main.c",
             "src/delete.c"]),
    Library('tinyxml2',
            ['tinyxml2.h',
             'tinyxml2.cpp']),
    Library('uthash',
            ["src/uthash.h",
             "src/utlist.h",
             "src/utarray.h",
             "src/utstring.h",
             "src/utringbuffer.h"]),
    Library('uvwasi',
            ["src/uvwasi.c",
             "include/uvwasi.h",
             "src/fd_table.c",
             "src/fd_table.h",
             "include/wasi_types.h",
             "src/uv_mapping.c",
             "src/clocks.c",
             "src/path_resolver.c"]),
    Library('xxHash',
            ['xxhash.h',
             'xxh3.h',
             'xxhash.c']),
    Library('xz',
            ['src/liblzma/api/lzma/block.h',
             'src/liblzma/common/stream_decoder.c',
             'src/liblzma/common/stream_encoder.c',
             'src/liblzma/common/block_decoder.c',
             'src/liblzma/common/block_encoder.c',
             'src/liblzma/lz/lz_decoder.c',
             'src/liblzma/lz/lz_encoder.c',
             'src/liblzma/lzma/lzma_decoder.c',
             'src/liblzma/lzma/lzma_encoder.c',
             'src/liblzma/rangecoder/range_decoder.h',
             'src/xz/coder.c']),
    Library('xz-embedded',
            ["linux/lib/decompress_unxz.c",
             "linux/lib/xz/xz_dec_stream.c",
             "linux/lib/xz/xz_dec_lzma2.c",
             "linux/lib/xz/xz_private.h",
             "linux/lib/xz/xz_dec_bcj.c",
             "linux/include/linux/xz.h",
             "userspace/xzminidec.c",
             "linux/lib/xz/xz_stream.h",
             "linux/lib/xz/xz_dec_syms.c",
             "linux/lib/xz/xz_crc32.c",
             "linux/lib/xz/xz_dec_test.c",
             "linux/lib/xz/xz_crc64.c"]),
    Library('zlib',
            ['deflate.c',
             'deflate.h',
             'inflate.c',
             'gzlib.c']),
    Library('zstd',
            ['lib/zstd.h',
             'lib/common/fse.h',
             'lib/common/zstd_internal.h',
             'lib/compress/zstd_compress.c',
             'lib/decompress/zstd_decompress.c']),
]

# Some libraries embed code themselves:
embedded = {
    "boringssl":  ["googletest"],
    # botan embeds numerous test files from these:
    "botan":      ["boringssl", "mbedtls"],
    "fmt":        ["googletest"],
    "freetype":   ["zlib"],
    "libpng":     ["zlib"],
    "libsndfile": ["flac"],
    "minizip-ng": ["xz"],
    "openjpeg":   ["libpng", "libtiff", "Little-CMS", "zlib"],
    "protobuf":   ["googletest"],
    "zlib":       ["minizip-ng"],
    "zstd":       ["xxHash", "zlib"],
}

# vim:set expandtab tabstop=4 shiftwidth=4 softtabstop=4 nowrap:
