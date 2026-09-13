"""Create local folders and optionally import the three user-supplied CSVs.

python setup_project.py
python setup_project.py --data-zip /path/to/original-data.zip

Uses only the Python standard library. Never fabricates raw inputs or
overwrites an existing file with different contents.
"""
import argparse
from pathlib import Path
from zipfile import ZipFile
from settings import ROOT, FILES


def setup(raw_dir=ROOT / 'data/raw', output_dir=ROOT / 'outputs', data_zip=None):
    raw_dir, output_dir = Path(raw_dir), Path(output_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    if data_zip is not None:
        payloads = {}
        with ZipFile(data_zip) as archive:
            for filename in FILES.values():
                matches = [entry for entry in archive.infolist()
                           if not entry.is_dir() and Path(entry.filename).name == filename]
                if len(matches) != 1:
                    raise ValueError(f'Expected exactly one {filename} in ZIP; found {len(matches)}.')
                payloads[filename] = archive.read(matches[0])
        # Validate every destination before writing anything. No extractall:
        # archive paths can never write outside the selected raw directory.
        for filename, contents in payloads.items():
            destination = raw_dir / filename
            if destination.exists() and destination.read_bytes() != contents:
                raise FileExistsError(f'{destination} already has different contents. Use another --raw-dir.')
        for filename, contents in payloads.items():
            destination = raw_dir / filename
            if not destination.exists():
                destination.write_bytes(contents)
        print(f'Imported or verified {len(payloads)} raw CSVs in {raw_dir}')
    missing = [filename for filename in FILES.values() if not (raw_dir / filename).is_file()]
    if missing:
        print(f'Place these original input files in {raw_dir}:')
        for filename in missing:
            print(f'  {filename}')
    else:
        print('All three input CSVs are present. Run python run_pipeline.py next.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', type=Path, default=ROOT / 'data/raw')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs')
    parser.add_argument('--data-zip', type=Path)
    args = parser.parse_args()
    setup(args.raw_dir, args.output_dir, args.data_zip)
