"""Read-only source benchmark; snapshots/commits go ONLY to a temporary store."""
import argparse,cProfile,io,json,pstats,statistics,sys,tempfile,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'production/video_studio'))
from studio_recovery import recover_snapshot
from studio_sig_layers import layer_command,map_payload,workspace_for

def main():
 parser=argparse.ArgumentParser();parser.add_argument('snapshot');parser.add_argument('--profile',action='store_true');parser.add_argument('--transaction',action='store_true');args=parser.parse_args()
 project,_=recover_snapshot(Path(args.snapshot).resolve())
 box=workspace_for(project)['view']['bbox'];box=[box[0]+(box[2]-box[0])*.001,box[1],box[2],box[3]]
 def operation():
  candidate=layer_command(project,{'action':'view','bbox':box});map_payload(candidate)
 # Compare hot against hot; samples include native proofs, not network tiles.
 operation();samples=[]
 for _ in range(5):
  start=time.perf_counter();operation();samples.append(round((time.perf_counter()-start)*1000,1))
 print(json.dumps({'stage':'view_command_and_payload','observations':len(workspace_for(project).get('raster_time',{}).get('layers',[])),'ms':samples,'median_ms':statistics.median(samples)}))
 if args.profile:
  profile=cProfile.Profile();profile.runcall(operation);stream=io.StringIO();pstats.Stats(profile,stream=stream).sort_stats('cumulative').print_stats(15);print(stream.getvalue())
 if args.transaction:
  from studio_workspace import WorkspaceSession
  from studio_project import source_projection
  from studio_sig_protocol import apply_map_intents
  from studio_sig_shell import shell_payload
  import copy
  with tempfile.TemporaryDirectory(prefix='ev-sig-benchmark-') as folder:
   state={'project_document':copy.deepcopy(project),'project':source_projection(project)}
   session=WorkspaceSession(state,'bench',state['project'],store=folder,canonical=True)
   def transaction(i):
    view=workspace_for(session.project)['view']['bbox'];view[0]+=(view[2]-view[0])*.001
    apply_map_intents(session,{'client':'1'*32,'version':session.version,'sequence':i,'commands':[{'sequence':i,'action':'view','bbox':view}]})
    map_payload(session.project);shell_payload(session)
   transaction(1);samples=[]
   for i in range(2,7):
    start=time.perf_counter();transaction(i);samples.append(round((time.perf_counter()-start)*1000,1))
   print(json.dumps({'stage':'durable_transaction_and_payloads_temporary_store','ms':samples,'median_ms':statistics.median(samples)}))
if __name__=='__main__':main()
