import hashlib,importlib.util,json,pathlib,tempfile,unittest
p=pathlib.Path(__file__).resolve().parents[1]/'tools'/'unesco_framework_drift.py'
s=importlib.util.spec_from_file_location('drift',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class TestDrift(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
  root=pathlib.Path(t.name);self.f=root/'fw';self.d=root/'dik';self.i=root/'ip'
  (self.f/'schemas/v11').mkdir(parents=True);self.d.mkdir();(self.i/'contracts').mkdir(parents=True)
  (self.f/'VERSION').write_text('11.0.0-draft.4')
  (self.f/'schemas/v11/test.json').write_text('{"x":1}')
  h=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
  (self.i/'contracts/v11-framework-pin.json').write_text(json.dumps({'version':'11.0.0-draft.4','files':{'VERSION':h(self.f/'VERSION'),'schemas/v11/test.json':h(self.f/'schemas/v11/test.json')}}))
  (self.d/'FRAMEWORK-SOURCE-SHA256.json').write_text(json.dumps({'contract':'11.0.0-draft.3','files':[{'upstream':'schemas/v11/test.json','vendored_sha256':h(self.f/'schemas/v11/test.json'),'identical':True}]}))
 def test_subset_matches_without_claiming_runtime_approval(self):
  x=m.inspect(framework=self.f,diK=self.d,integration_pack=self.i)
  self.assertTrue(x['pinned_framework_verified']);self.assertTrue(x['upstream_source_unchanged_for_dik_subset'])
  self.assertFalse(x['runtime_compatibility_qualified']);self.assertFalse(x['public_release_authorized'])
 def test_tampered_framework_is_blocked(self):
  (self.f/'schemas/v11/test.json').write_text('{"x":99}')
  x=m.inspect(framework=self.f,diK=self.d,integration_pack=self.i)
  self.assertFalse(x['pinned_framework_verified']);self.assertFalse(x['upstream_source_unchanged_for_dik_subset'])
 def test_unsafe_pin_path_rejected(self):
  (self.i/'contracts/v11-framework-pin.json').write_text(json.dumps({'version':'11.0.0-draft.4','files':{'../evil':'x'}}))
  with self.assertRaises(m.DriftError):m.inspect(framework=self.f,diK=self.d,integration_pack=self.i)
if __name__=='__main__':unittest.main()
