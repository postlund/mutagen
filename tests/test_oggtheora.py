import os
import shutil
import sys

from tempfile import mkstemp
from cStringIO import StringIO

from mutagen.oggtheora import OggTheora, OggTheoraInfo, delete
from mutagen.ogg import OggPage
from tests import add
from tests.test_ogg import TOggFileType

class TOggTheora(TOggFileType):
    Kind = OggTheora

    def setUp(self):
        original = os.path.join("tests", "data", "sample.oggtheora")
        fd, self.filename = mkstemp(suffix='.ogg')
        os.close(fd)
        shutil.copy(original, self.filename)
        self.audio = OggTheora(self.filename)

    def test_theora_bad_version(self):
        page = OggPage(file(self.filename, "rb"))
        packet = page.packets[0]
        packet = packet[:7] + "\x03\x00" + packet[9:]
        page.packets = [packet]
        fileobj = StringIO(page.write())
        self.failUnlessRaises(IOError, OggTheoraInfo, fileobj)

    def test_vendor(self):
        self.failUnless(
            self.audio.tags.vendor.startswith("Xiph.Org libTheora"))
        self.failUnlessRaises(KeyError, self.audio.tags.__getitem__, "vendor")

    def test_not_my_ogg(self):
        fn = os.path.join('tests', 'data', 'empty.ogg')
        self.failUnlessRaises(IOError, type(self.audio), fn)
        self.failUnlessRaises(IOError, self.audio.save, fn)
        self.failUnlessRaises(IOError, self.audio.delete, fn)

    def test_length(self):
        self.failUnlessAlmostEqual(5.5, self.audio.info.length, 1)

    def test_theora_reference_simple_save(self):
        self.audio.save()
        self.scan_file()
        value = os.system("ogginfo %s > /dev/null 2> /dev/null" % self.filename)
        self.failIf(value and value != NOTFOUND)

    def test_theora_reference_really_big(self):
        self.test_really_big()
        self.audio.save()
        self.scan_file()
        value = os.system("ogginfo %s > /dev/null 2> /dev/null" % self.filename)
        self.failIf(value and value != NOTFOUND)

    def test_module_delete(self):
        delete(self.filename)
        self.scan_file()
        self.failIf(OggTheora(self.filename).tags)

    def test_theora_reference_delete(self):
        self.audio.delete()
        self.scan_file()
        value = os.system("ogginfo %s > /dev/null 2> /dev/null" % self.filename)
        self.failIf(value and value != NOTFOUND)
 
    def test_theora_reference_medium_sized(self):
        self.audio["foobar"] = "foobar" * 1000
        self.audio.save()
        self.scan_file()
        value = os.system("ogginfo %s > /dev/null 2> /dev/null" % self.filename)
        self.failIf(value and value != NOTFOUND)

    def test_theora_reference_delete_readd(self):
        self.audio.delete()
        self.audio.tags.clear()
        self.audio["foobar"] = "foobar" * 1000
        self.audio.save()
        self.scan_file()
        value = os.system("ogginfo %s > /dev/null 2> /dev/null" % self.filename)
        self.failIf(value and value != NOTFOUND)
 
add(TOggTheora)

NOTFOUND = os.system("tools/notarealprogram 2> /dev/null")

if os.system("ogginfo > /dev/null 2> /dev/null") == NOTFOUND:
    print "WARNING: Skipping Ogg Theora reference tests."