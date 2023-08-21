import matplotlib.pyplot as plt
import numpy as np


if __name__ == "__main__":

  pys = []
  rusts = []
    
  with open("../../yearly_parser.log", "r") as f:
    f = f.read()

    lines = [e.split(":") for e in f.split("\n")]
    lines = [e for e in lines if len(e)==3]
    lines = [float(e[2]) for e in lines]
    rusts.extend(lines)

  with open("../just_py.log", "r") as f:
    f = f.read()

    lines = [e.split(":") for e in f.split("\n")]
    lines = [e for e in lines if len(e)==3]
    lines = [float(e[2]) for e in lines]
    pys.extend(lines)

  print(len(rusts), len(pys))
  rusts = np.array(rusts)
  pys = np.array(pys)
  iters = list(range(1, 1+len(rusts)))
  decrease_ratios = (pys-rusts)/pys * 100;
  print(decrease_ratios)

  fig, ax2 = plt.subplots(1,1, figsize=(4, 3))
  ax2.bar(iters, decrease_ratios, fc="lightgrey", zorder=10, alpha=0.5)
  ax2.set_ylabel("Bar: Time decreased(%)")

  ax = ax2.twinx()

  ax.plot(iters, pys, c="lightblue", label="py", marker="o", zorder=10)
  ax.plot(iters, rusts, c="lightcoral", label="py+rust", marker="s", zorder=10)
  ax.set_ylabel("Accumulated time(sec)")
  ax2.set_xlabel("iter(10_000_000)")
  ax.legend()
  ax.grid(True)

  plt.savefig("./py_rust_bench.png", dpi=240, bbox_inches='tight')
  plt.show()