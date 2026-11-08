#!/usr/bin/env python3
"""Run reference end-to-end OMR systems (Python, CPU) on the spike scans and score them.

systems: homr (AGPL, 0.7.0 PyPI), oemer (MIT, 0.1.8 PyPI), cop2m / cop28m (copisteria, Apache-2.0)
Each job is pinned to its own block of cores (taskset) so timings are comparable.
Usage: .venv/bin/python src/run_e2e.py [system ...] [--images glob] [--cores-per-job 8]
Writes out/e2e/<system>/<image>/... and out/e2e/results.jsonl (one line per run, appended).
"""
import argparse, glob, json, os, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from eval_xml import evaluate  # noqa: E402

CMDS = {
    "homr": lambda img, wd: ([os.path.join(ROOT, ".venv-homr/bin/homr"), os.path.basename(img)], wd,
                             os.path.join(wd, os.path.splitext(os.path.basename(img))[0] + ".musicxml")),
    "oemer": lambda img, wd: ([os.path.join(ROOT, ".venv-oemer/bin/python"), os.path.join(ROOT, "src/oemer_wrap.py"), "8", os.path.basename(img), "-o", "."], wd,
                              os.path.join(wd, os.path.splitext(os.path.basename(img))[0] + ".musicxml")),
    "cop2m": lambda img, wd: ([os.path.join(ROOT, ".venv-cop/bin/python"), "-m", "copisteria.pipeline",
                               os.path.join(wd, os.path.basename(img)), "--out", wd, "--detector", "2m"],
                              os.path.join(ROOT, "dl/copisteria"),
                              os.path.join(wd, os.path.splitext(os.path.basename(img))[0] + ".musicxml")),
    "cop28m": lambda img, wd: ([os.path.join(ROOT, ".venv-cop/bin/python"), "-m", "copisteria.pipeline",
                                os.path.join(wd, os.path.basename(img)), "--out", wd, "--detector", "28m"],
                               os.path.join(ROOT, "dl/copisteria"),
                               os.path.join(wd, os.path.splitext(os.path.basename(img))[0] + ".musicxml")),
}

lock = threading.Lock()


def run(job):
    system, img, cores = job
    name = os.path.splitext(os.path.basename(img))[0]
    piece = name.rsplit("_", 2)[0]
    wd = os.path.join(ROOT, "out", "e2e", system, name)
    os.makedirs(wd, exist_ok=True)
    shutil.copy(img, wd)
    cmd, cwd, outxml = CMDS[system](img, wd)
    env = dict(os.environ, OMP_NUM_THREADS=str(len(cores)), MKL_NUM_THREADS=str(len(cores)),
               CUDA_VISIBLE_DEVICES="", OPENBLAS_NUM_THREADS=str(len(cores)))
    t0 = time.time()
    with open(os.path.join(wd, "run.log"), "w") as log:
        rc = subprocess.run(["taskset", "-c", ",".join(map(str, cores))] + cmd, cwd=cwd, env=env,
                            stdout=log, stderr=subprocess.STDOUT, timeout=7200).returncode
    dt = time.time() - t0
    if not os.path.exists(outxml):
        cands = glob.glob(os.path.join(wd, "*.musicxml")) + glob.glob(os.path.join(wd, "*.xml"))
        outxml = cands[0] if cands else None
    res = evaluate(outxml, piece) if outxml else {"error": "no output", "mp_f1": 0, "mpd_f1": 0, "voice_acc": 0}
    rec = {"system": system, "image": name, "piece": piece, "rc": rc, "wall_s": round(dt, 1),
           "cores": len(cores), **res}
    with lock:
        with open(os.path.join(ROOT, "out", "e2e", "results.jsonl"), "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec), flush=True)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("systems", nargs="*", default=["homr", "cop2m", "cop28m"])
    ap.add_argument("--images", default="scans/*_*_*.png")
    ap.add_argument("--cores-per-job", type=int, default=8)
    ap.add_argument("--first-core", type=int, default=0)
    ap.add_argument("--max-cores", type=int, default=176)
    a = ap.parse_args()
    imgs = sorted(glob.glob(os.path.join(ROOT, a.images)))
    jobs = [(s, i) for s in a.systems for i in imgs]
    nslots = max(1, a.max_cores // a.cores_per_job)
    slots = [list(range(a.first_core + k * a.cores_per_job, a.first_core + (k + 1) * a.cores_per_job))
             for k in range(nslots)]
    free = list(range(nslots))
    cv = threading.Condition()

    def worker(j):
        with cv:
            while not free:
                cv.wait()
            k = free.pop()
        try:
            return run((j[0], j[1], slots[k]))
        finally:
            with cv:
                free.append(k)
                cv.notify()

    with ThreadPoolExecutor(max_workers=nslots) as ex:
        list(ex.map(worker, jobs))


if __name__ == "__main__":
    main()
