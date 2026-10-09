"""Own the pipes omitted at EOF by the pinned imageio-ffmpeg 0.6.0 reader.

The adapter isolates a version-specific generator detail; it never patches a
global factory or changes decoding. See the installed _io.read_frames finally:
stdin/stdout close only while the process is running. Tests pin ownership on
EOF, early close and metadata failure so an upgrade must verify this bridge.
"""
import imageio_ffmpeg


def read_frames(*args,**kwargs):
    reader=imageio_ffmpeg.read_frames(*args,**kwargs)
    process=catcher=None

    def capture(frame):
        nonlocal process,catcher
        if frame is not None and frame.f_globals.get('__name__')=='imageio_ffmpeg._io':
            process=frame.f_locals.get('process',process)
            catcher=frame.f_locals.get('log_catcher',catcher)

    try:
        while True:
            try: value=next(reader)
            except StopIteration: return
            except BaseException as error:
                # A failed first next clears gi_frame; traceback still owns
                # the library's frame and its process/pipe references.
                traceback=error.__traceback__
                while traceback is not None:
                    capture(traceback.tb_frame);traceback=traceback.tb_next
                raise
            capture(getattr(reader,'gi_frame',None))
            yield value
    finally:
        try:
            close=getattr(reader,'close',None)
            if close is not None: close()
        finally:
            if process is not None:
                try:
                    if process.poll() is None: process.kill()
                    process.wait(timeout=5)
                    if catcher is not None: catcher.join(timeout=2)
                finally:
                    for stream in (process.stdin,process.stdout,process.stderr):
                        if stream is not None and not stream.closed: stream.close()
