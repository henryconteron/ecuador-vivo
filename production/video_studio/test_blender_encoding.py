from pathlib import Path
import tempfile
import unittest
from studio_ffmpeg import read_frames


class BlenderEncodingTests(unittest.TestCase):
    def test_even_dimensions_do_not_get_silently_rounded_to_macroblocks(self):
        from studio_blender_worker import movie_writer
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'render.mp4'
            writer=movie_writer(path,(34,30));writer.send(None)
            writer.send(bytes(34*30*3));writer.send(bytes(34*30*3));writer.close()
            reader=read_frames(str(path))
            try:
                self.assertEqual(next(reader)['size'],(34,30))
                self.assertEqual(sum(1 for _ in reader),2)
            finally:reader.close()


if __name__=='__main__':unittest.main()
