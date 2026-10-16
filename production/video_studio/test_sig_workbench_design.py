"""HTML structure contract, not a substitute for screenshot/browser acceptance."""
import ast,unittest
from html.parser import HTMLParser
from pathlib import Path

class Structure(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.tasks=[];self.separators=[];self.panels=[];self.nodes={}
 def handle_starttag(self,tag,attributes):
  row=dict(attributes)
  if 'id' in row:self.ids.append(row['id']);self.nodes[row['id']]=row
  if 'data-floating-panel' in row:self.panels.append(row)
  if 'data-workbench-task' in row:self.tasks.append(row['data-workbench-task'])
  if row.get('role')=='separator':self.separators.append(row)

class WorkbenchDesignTests(unittest.TestCase):
 def markup(self):
  source=Path(__file__).with_name('ecuador-vivo-sig-map')/'ecuador_vivo_sig_map/__init__.py'
  tree=ast.parse(source.read_text(encoding='utf-8'))
  value=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='HTML' for t in n.targets))
  parser=Structure();parser.feed(ast.literal_eval(value));return parser
 def test_one_map_clock_and_each_task_control_are_retained(self):
  parser=self.markup();self.assertEqual(len(parser.ids),len(set(parser.ids)))
  for name in ('sig-geographic-map','sig-raster-date','sig-raster-send','sig-import','sig-analysis','sig-raster-tools','sig-prepare','sig-results-view','sig-processes','sig-inspector-content','sig-layer-tree','sig-dock-content'):
   self.assertEqual(parser.ids.count(name),1,name)
  self.assertEqual(parser.tasks,['map','data','analysis','time','output'])
 def test_series_has_one_configuration_entry_and_palette_access(self):
  parser=self.markup();self.assertIn('sig-series-palette',parser.ids)
  self.assertNotIn('sig-raster-configure',parser.ids)
 def test_resizable_panels_have_keyboard_and_orientation_metadata(self):
  parser=self.markup();self.assertEqual(len(parser.panels),5)
  for row in parser.panels:
   self.assertEqual(row.get('role'),'dialog');self.assertEqual(row.get('aria-modal'),'false');self.assertIn('hidden',row)
  for name in ('sig-layers-view','sig-reference-view','sig-properties-view','sig-attributes-view'):
   self.assertIn('aria-controls',parser.nodes[name]);self.assertEqual(parser.nodes[name]['aria-expanded'],'false')
 def test_temporal_controls_are_conditional_and_keep_one_clock(self):
  parser=self.markup();self.assertIn('hidden',parser.nodes['sig-raster-controls'])
  for name in ('sig-time-view','sig-time-prev','sig-time-next','sig-time-zoom-in','sig-time-zoom-out','sig-time-close','sig-time-start','sig-time-end','sig-raster-pick'):
   self.assertEqual(parser.ids.count(name),1)

if __name__=='__main__':unittest.main()
