"""Run oemer's CLI with onnxruntime pinned to CPU and a fixed thread count (default ORT threads = all
192 cores, which thrashes on a shared box).  Usage: python oemer_wrap.py <threads> <oemer args...>"""
import sys
import onnxruntime as ort

THREADS = int(sys.argv.pop(1))
_Orig = ort.InferenceSession


class Pinned(_Orig):
    def __init__(self, path, sess_options=None, providers=None, **kw):
        so = sess_options or ort.SessionOptions()
        so.intra_op_num_threads = THREADS
        so.inter_op_num_threads = 1
        super().__init__(path, so, providers=["CPUExecutionProvider"], **kw)


ort.InferenceSession = Pinned
from oemer.ete import main  # noqa: E402

sys.exit(main())
