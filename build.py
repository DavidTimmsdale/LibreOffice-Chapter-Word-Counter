"""Build deterministic public archives from an explicit source allowlist."""
from pathlib import Path
import ast, hashlib, zipfile, xml.etree.ElementTree as ET
root = Path(__file__).resolve().parent
package = ['chaptercounter.py', 'Jobs.xcu', 'Controller.xcu', 'description.xml', 'description.txt', 'META-INF/manifest.xml', 'LICENSE', 'README.md', 'CHANGELOG.md']
for p in root.glob('src/*.py'): ast.parse(p.read_text())
for p in root.glob('tests/*.py'): ast.parse(p.read_text())
for p in root.rglob('*'):
 if p.suffix in ('.xml', '.xcu'): ET.parse(p)
for entry in ET.parse(root/'src/META-INF/manifest.xml').getroot():
 assert entry.attrib['{http://openoffice.org/2001/manifest}full-path'] in package

def archive(path, entries):
 with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
  for source, target in sorted(entries, key=lambda pair: pair[1]):
   info = zipfile.ZipInfo(target, (2026, 11, 6, 0, 0, 0))
   info.compress_type = zipfile.ZIP_DEFLATED
   info.external_attr = 0o100644 << 16
   z.writestr(info, source.read_bytes())
archive(root/'Chapter_Counter_1.0.0.oxt', [(root/'src'/n,n) for n in package])
names = ['README.md','LICENSE','CHANGELOG.md','build.py']
entries = [(root/n,n) for n in names]
entries += [(root/'src'/n,'src/'+n) for n in package]
entries += [(p,'tests/'+p.name) for p in sorted((root/'tests').glob('*.py'))]
archive(root/'Chapter_Counter_1.0.0_source.zip', entries)
artifacts = ['Chapter_Counter_1.0.0.oxt','Chapter_Counter_1.0.0_source.zip']
(root/'SHA256SUMS').write_text(''.join(hashlib.sha256((root/n).read_bytes()).hexdigest()+'  '+n+'\n' for n in artifacts))
print('Validated Python, XML, manifest; built two deterministic archives')
