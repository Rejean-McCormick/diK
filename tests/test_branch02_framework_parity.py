"""Source parity tests complement, not replace, diK alpha.7 application tests."""
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from dik.framework_compatibility import inspect_schema_parity, FrameworkCompatibilityError

FRAMEWORK = Path(os.environ.get('DIK_TEST_FRAMEWORK_SOURCE', '/missing-framework'))
VENDORED = Path(__file__).resolve().parents[1] / 'src/dik/_framework/schemas/v11'

class FrameworkSourceParityTests(unittest.TestCase):
    def fixture(self, target, version='11.0.0-draft.4'):
        path = Path(target)
        (path/'schemas/v11').mkdir(parents=True)
        (path/'VERSION').write_text(version)
        for f in VENDORED.glob('*.schema.json'):
            shutil.copyfile(f, path/'schemas/v11'/f.name)
        return path

    def test_identical_schema_bytes_report_parity_not_certification(self):
        with tempfile.TemporaryDirectory() as td:
            root=self.fixture(td)
            report=inspect_schema_parity(root)
            self.assertEqual(report['schema_count'],11)
            self.assertTrue(report['schemas_identical'])
            self.assertFalse(report['canonical_state_modified'])
            self.assertIn('not end-to-end',report['qualification'])

    def test_modified_framework_schema_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=self.fixture(td)
            target=root/'schemas/v11/kristal-semantic-graph.schema.json'
            target.write_bytes(target.read_bytes()+b'\n')
            with self.assertRaisesRegex(FrameworkCompatibilityError,'schema drift'):
                inspect_schema_parity(root)

    def test_unsupported_version_and_missing_schema_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root=self.fixture(td,version='12.0.0')
            with self.assertRaisesRegex(FrameworkCompatibilityError,'Unsupported Framework'):
                inspect_schema_parity(root)
            (root/'VERSION').write_text('11.0.0-draft.4')
            (root/'schemas/v11/kristal-semantic-graph.schema.json').unlink()
            with self.assertRaisesRegex(FrameworkCompatibilityError,'inventory differs'):
                inspect_schema_parity(root)

    @unittest.skipUnless(FRAMEWORK.is_dir(), 'Provide actual Framework snapshot for source parity')
    def test_actual_draft4_source_matches_dik_draft3_v11_schema_bytes(self):
        self.assertEqual(inspect_schema_parity(FRAMEWORK)['framework_source_version'], '11.0.0-draft.4')

if __name__ == '__main__': unittest.main()
