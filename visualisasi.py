import tkinter as tk
from tkinter import ttk
import random, math

BG = "#1a1f2e"
BLUE   = "#3b6fd4"; BORDER_B = "#5a8aee"
ORANGE = "#e8922a"; BORDER_O = "#f0a843"
GREEN  = "#27ae60"; BORDER_G = "#2ecc71"
YELLOW = "#f0c040"; BORDER_Y = "#f5d060"
RED    = "#c0392b"; BORDER_R = "#e74c3c"
TEAL   = "#1abc9c"; BORDER_T = "#30d0e0"
ARROW_CLR = "#8899bb"; LABEL_CLR = "#cce0ff"
PANEL_BG = "#0f1420"; ACCENT = "#a371f7"
DIM = "#6677aa"; WHITE = "#ffffff"; DARK = "#111111"

BW, BH, BR, HG = 46, 38, 7, 10
VG = 175
FRAME_MS = 16


def rrect(cv, x0, y0, x1, y1, r, **kw):
    pts = [x0+r,y0, x1-r,y0, x1,y0, x1,y0+r, x1,y1-r, x1,y1,
           x1-r,y1, x0+r,y1, x0,y1, x0,y1-r, x0,y0+r, x0,y0, x0+r,y0]
    return cv.create_polygon(pts, smooth=True, **kw)


def ease(t): return t * t * (3 - 2 * t)
def arr_pw(n): return max(1, n) * (BW + HG) - HG


class Box:
    def __init__(self, cv, val, cx, cy, fill=BLUE, border=BORDER_B, tfg=WHITE):
        self.cv = cv; self.val = val; self.cx = float(cx); self.cy = float(cy)
        x0, y0 = cx - BW//2, cy - BH//2; x1, y1 = cx + BW//2, cy + BH//2
        self.rid = rrect(cv, x0, y0, x1, y1, BR, fill=fill, outline=border, width=2)
        self.tid = cv.create_text(cx, cy, text=str(val), fill=tfg,
                                  font=("Consolas", 12, "bold"))

    def set_color(self, fill, border, tfg=WHITE):
        self.cv.itemconfig(self.rid, fill=fill, outline=border)
        self.cv.itemconfig(self.tid, fill=tfg)

    def clone(self, fill=None, border=None, tfg=WHITE):
        cf = self.cv.itemcget(self.rid, "fill")
        cb = self.cv.itemcget(self.rid, "outline")
        return Box(self.cv, self.val, int(self.cx), int(self.cy),
                   fill=fill or cf, border=border or cb, tfg=tfg)

    def snap_to(self, tx, ty):
        dx, dy = tx - self.cx, ty - self.cy
        self.cv.move(self.rid, dx, dy); self.cv.move(self.tid, dx, dy)
        self.cx, self.cy = float(tx), float(ty)


def fn_step(fn):
    def step(): fn(); return True
    return step

def delay_step(ms):
    rem = [int(ms)]
    def step(): rem[0] -= FRAME_MS; return rem[0] <= 0
    return step

def make_fly(cv, b, tx, ty, steps=20, arc=-35):
    fh = [0]
    def step():
        if fh[0] == 0: b._ox, b._oy = b.cx, b.cy
        t = (fh[0] + 1) / steps; et = ease(min(t, 1.0))
        nx = b._ox + (tx - b._ox) * et
        ny = b._oy + (ty - b._oy) * et + arc * math.sin(math.pi * t)
        dx, dy = nx - b.cx, ny - b.cy
        cv.move(b.rid, dx, dy); cv.move(b.tid, dx, dy)
        b.cx, b.cy = nx, ny; fh[0] += 1
        if fh[0] >= steps:
            b.cx, b.cy = float(tx), float(ty); return True
        return False
    return step


class Animator:
    def __init__(self, root):
        self.root = root; self.queue = []; self.stopped = False
        self._running = False

    def add(self, s): self.queue.append(s)

    def start(self):
        self.stopped = False
        if not self._running:
            self._running = True
            self._tick()

    def stop(self):
        self.stopped = True; self.queue.clear()

    def resume(self):
        pass

    def _tick(self):
        if self.stopped:
            self._running = False; return
        if self.queue:
            done = self.queue[0]()
            if done: self.queue.pop(0)
        self.root.after(FRAME_MS, self._tick)


class App:
    def __init__(self, root):
        self.root = root; self.root.title("Quick Sort Visualizer")
        self.root.configure(bg=PANEL_BG); self.root.resizable(True, True)
        self.running = False; self.array = []; self.anim = None
        self._build_ui(); self._new_array()

    # ------------------------------------------------------------------ UI ---
    def _build_ui(self):
        hdr = tk.Frame(self.root, bg=PANEL_BG)
        hdr.pack(fill="x", padx=20, pady=(14, 4))
        tk.Label(hdr, text="QUICK SORT", font=("Consolas", 15, "bold"),
                 fg=ACCENT, bg=PANEL_BG).pack(side="left")
        self.cmp_lbl = tk.Label(hdr, text="", font=("Consolas", 12, "bold"),
                                fg=YELLOW, bg=PANEL_BG)
        self.cmp_lbl.pack(side="right")

        cf = tk.Frame(self.root, bg=PANEL_BG)
        cf.pack(fill="both", expand=True, padx=20, pady=4)
        self.cv = tk.Canvas(cf, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(cf, orient="vertical",   command=self.cv.yview)
        hsb = ttk.Scrollbar(cf, orient="horizontal", command=self.cv.xview)
        self.cv.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y"); hsb.pack(side="bottom", fill="x")
        self.cv.pack(fill="both", expand=True)
        self.cv.bind("<MouseWheel>",
                     lambda e: self.cv.yview_scroll(int(-e.delta/60), "units"))
        self.cv.bind("<Shift-MouseWheel>",
                     lambda e: self.cv.xview_scroll(int(-e.delta/60), "units"))

        pnl = tk.Frame(self.root, bg=PANEL_BG, pady=10)
        pnl.pack(fill="x", padx=20)

        def lbl(t, col):
            tk.Label(pnl, text=t, font=("Consolas", 10),
                     fg=WHITE, bg=PANEL_BG).grid(row=0, column=col, padx=(12,3))

        lbl("Size", 0); self.sv = tk.IntVar(value=8)
        ttk.Scale(pnl, from_=4, to=14, variable=self.sv,
                  orient="horizontal", length=100).grid(row=0, column=1)
        sd = tk.Label(pnl, text="8", font=("Consolas",10),
                      fg=ACCENT, bg=PANEL_BG, width=3)
        sd.grid(row=0, column=2, padx=(2,12))
        self.sv.trace_add("write", lambda *_: sd.config(text=str(self.sv.get())))

        lbl("Speed", 3); self.spd = tk.DoubleVar(value=1.0)
        ttk.Scale(pnl, from_=0.3, to=3.0, variable=self.spd,
                  orient="horizontal", length=100).grid(row=0, column=4, padx=(0,12))
        tk.Label(pnl, text="(kiri=cepat)", font=("Consolas",8),
                 fg=DIM, bg=PANEL_BG).grid(row=0, column=5, padx=(0,14))

        lbl("Pivot", 6); self.pv = tk.StringVar(value="last")
        ttk.Combobox(pnl, textvariable=self.pv,
                     values=["last","first","random","tengah","median","mean","modus"],
                     state="readonly", width=12,
                     font=("Consolas",10)).grid(row=0, column=7, padx=(0,18))

        btn = dict(font=("Consolas",10,"bold"), fg=WHITE, bg="#21262d",
                   activebackground="#30363d", activeforeground=WHITE,
                   relief="flat", cursor="hand2", padx=12, pady=5)
        tk.Button(pnl, text="🔀 Generate",
                  command=self._new_array, **btn).grid(row=0, column=8, padx=3)
        self.sb = tk.Button(pnl, text="▶ Sort", command=self._start, **btn)
        self.sb.grid(row=0, column=9, padx=3)
        tk.Button(pnl, text="⏹ Stop",
                  command=self._stop, **btn).grid(row=0, column=10, padx=(3,12))

        leg = tk.Frame(self.root, bg=PANEL_BG); leg.pack(pady=(2,2))
        for fill, border, tfg, ltxt in [
            #(BLUE,   BORDER_B, WHITE, "Asli (tetap)"),
            (ORANGE, BORDER_O, DARK,  "Pivot"),
            (YELLOW, BORDER_Y, DARK,  "Checking"),
            (RED,    BORDER_R, WHITE, "angka ≤ pivot"),
            (TEAL,   BORDER_T, WHITE, "angka > pivot"),
            (GREEN,  BORDER_G, WHITE, "sorted"),
        ]:
            c = tk.Canvas(leg, width=30, height=22, bg=PANEL_BG, highlightthickness=0)
            c.pack(side="left", padx=(8,2))
            rrect(c, 2,2,28,20,4, fill=fill, outline=border, width=2)
            c.create_text(15,11, text=" ", fill=tfg, font=("Consolas",8,"bold"))
            tk.Label(leg, text=ltxt, font=("Consolas",9),
                     fg=DIM, bg=PANEL_BG).pack(side="left", padx=(0,6))

        self.stat = tk.StringVar(value="Tekan Generate lalu Sort")
        tk.Label(self.root, textvariable=self.stat, font=("Consolas",10),
                 fg=DIM, bg=PANEL_BG, anchor="w").pack(fill="x", padx=22, pady=(2,10))

    # --------------------------------------------------------- array / start ---
    def _new_array(self):
        if self.running: return
        n = self.sv.get(); pool = list(range(1,100)); random.shuffle(pool)
        self.array = pool[:n]; self.cv.delete("all")
        self.stat.set(f"Array: {self.array}"); self.cmp_lbl.config(text="")
        cw = max(self.cv.winfo_width(), 900)
        cx0 = cw//2 - arr_pw(n)//2; cy = 80
        pi = self._choose_pivot(self.array)
        for i, v in enumerate(self.array):
            cx = cx0 + i*(BW+HG) + BW//2
            Box(self.cv, v, cx, cy,
                fill=ORANGE if i==pi else BLUE,
                border=BORDER_O if i==pi else BORDER_B,
                tfg=DARK if i==pi else WHITE)
        self._set_scroll()

    def _start(self):
        if self.running: return
        self.running = True; self.sb.config(state="disabled")
        self.stat.set("Sorting…"); self.cv.delete("all")

        arr = self.array[:]
        cw = max(self.cv.winfo_width(), 900); cx = cw//2; cy = 80
        boxes = self._make_boxes(arr, cx, cy)

        self.anim = Animator(self.root)

        def on_all_done(result):
            self._start_merge(result)

        self._build_steps(arr, boxes, cx, cy, on_all_done)
        self.anim.start()

    def _stop(self):
        if self.anim: self.anim.stop()
        self.running = False; self.sb.config(state="normal")
        self.stat.set("Dihentikan"); self.cmp_lbl.config(text="")

    def _make_boxes(self, arr, cx, cy):
        n = len(arr); pw = arr_pw(n); x0 = cx - pw//2; boxes = []
        pi = self._choose_pivot(arr)
        for i, v in enumerate(arr):
            bx = x0 + i*(BW+HG) + BW//2; ip = (i == pi)
            boxes.append(Box(self.cv, v, bx, cy,
                             fill=ORANGE if ip else BLUE,
                             border=BORDER_O if ip else BORDER_B,
                             tfg=DARK if ip else WHITE))
        self._set_scroll(); return boxes

    def _build_steps(self, arr, boxes, cx, cy, on_done):

        cv = self.cv; n = len(arr); FLY = 20

        if n == 0:
            self.anim.add(fn_step(lambda: on_done([])))
            return

        if n == 1:
            b = boxes[0]
            def _base(b=b, on_done=on_done):
                b.set_color(GREEN, BORDER_G, WHITE)
                on_done([b])
            self.anim.add(fn_step(_base))
            return

        pi = self._choose_pivot(arr); pv = arr[pi]
        pivot_box = boxes[pi]
        self.anim.add(fn_step(
            lambda pb=pivot_box: pb.set_color(ORANGE, BORDER_O, DARK)))
        self.anim.add(delay_step(int(250 * self.spd.get())))

        next_cy = cy + VG
        lv = [v for j, v in enumerate(arr) if j != pi and v <= pv]
        rv = [v for j, v in enumerate(arr) if j != pi and v >  pv]
        nl, nr = len(lv), len(rv)

        lw      = self._subtree_width(lv) if nl else 0
        rw      = self._subtree_width(rv) if nr else 0
        lw_flat = arr_pw(nl) if nl else 0
        rw_flat = arr_pw(nr) if nr else 0
        GAP   = 80
        total = (lw+GAP if nl else 0) + BW + (GAP+rw if nr else 0)
        cx_P  = cx - total//2 + (lw+GAP if nl else 0) + BW//2
        cx_L  = (cx_P - GAP - lw//2)  if nl else None
        cx_R  = (cx_P + GAP + rw//2)  if nr else None

        def draw_arrows(cx=cx, cy=cy, cx_P=cx_P, cx_L=cx_L, cx_R=cx_R,
                        next_cy=next_cy, pv=pv):
            self._draw_arrow(cx, cy, cx_P, next_cy, f"={pv}")
            if cx_L: self._draw_arrow(cx, cy, cx_L, next_cy, f"≤{pv}")
            if cx_R: self._draw_arrow(cx, cy, cx_R, next_cy, f">{pv}")
            self._set_scroll()
        self.anim.add(fn_step(draw_arrows))
        self.anim.add(delay_step(int(200 * self.spd.get())))

        left_clones = []; right_clones = []
        lcount = [0];     rcount = [0]

        for i in range(n):
            if i == pi: continue  # pivot dilewati
            b = boxes[i]; v = arr[i]

            def do_hl(b=b, v=v, pv=pv):
                b.set_color(YELLOW, BORDER_Y, DARK)
                op = '≤' if v <= pv else '>'
                self.cmp_lbl.config(
                    text=f"{v}  {op}  {pv}  →  {'◀ kiri' if v<=pv else 'kanan ▶'}")
            self.anim.add(fn_step(do_hl))
            self.anim.add(delay_step(int(280 * self.spd.get())))

            if v <= pv:
                k = lcount[0]; lcount[0] += 1
                dx = (cx_L - lw_flat//2 + k*(BW+HG) + BW//2) if cx_L else cx_P
                def mk_left(b=b, dx=dx, dy=next_cy, lc=left_clones):
                    cl = b.clone(fill=RED, border=BORDER_R, tfg=WHITE)
                    lc.append(cl)
                    self.anim.queue.insert(1, make_fly(cv, cl, dx, dy, FLY, arc=-40))
                    b.set_color(BLUE, BORDER_B, WHITE)
                    return True
                self.anim.add(fn_step(mk_left))
            else:
                k = rcount[0]; rcount[0] += 1
                dx = (cx_R - rw_flat//2 + k*(BW+HG) + BW//2) if cx_R else cx_P
                def mk_right(b=b, dx=dx, dy=next_cy, rc=right_clones):
                    cl = b.clone(fill=TEAL, border=BORDER_T, tfg=WHITE)
                    rc.append(cl)
                    self.anim.queue.insert(1, make_fly(cv, cl, dx, dy, FLY, arc=-40))
                    b.set_color(BLUE, BORDER_B, WHITE)
                    return True
                self.anim.add(fn_step(mk_right))

        self.anim.add(fn_step(lambda: self.cmp_lbl.config(text="")))

        pivot_clone = [None]
        def clone_piv(pb=pivot_box, tx=cx_P, ty=next_cy):
            pcl = pb.clone(fill=GREEN, border=BORDER_G, tfg=WHITE)
            pivot_clone[0] = pcl
            self.anim.queue.insert(1, make_fly(cv, pcl, tx, ty, FLY, arc=-25))
            return True
        self.anim.add(fn_step(clone_piv))
        self.anim.add(delay_step(int(150 * self.spd.get())))

        def launch(lv=lv, rv=rv, lc=left_clones, rc=right_clones,
                   cx_L=cx_L, cx_R=cx_R, next_cy=next_cy,
                   pc=pivot_clone, on_done=on_done):

            def on_right_done(rr, pc=pc, on_done=on_done):
                merged = left_res[0] + [pc[0]] + rr
                self.anim.add(fn_step(lambda merged=merged: on_done(merged)))
                self.anim.resume()

            def on_left_done(lr, rv=rv, rc=rc, cx_R=cx_R,
                             next_cy=next_cy, on_right_done=on_right_done):
                left_res[0] = lr
                if rv and rc:
                    self.anim.add(delay_step(int(120 * self.spd.get())))
                    self._build_steps(rv, rc, cx_R, next_cy, on_right_done)
                    self.anim.resume()
                else:
                    on_right_done([])

            left_res = [[]]

            if lv and lc:
                self.anim.add(delay_step(int(120 * self.spd.get())))
                self._build_steps(lv, lc, cx_L, next_cy, on_left_done)
                self.anim.resume()
            else:
                on_left_done([])

        self.anim.add(fn_step(launch))

    def _start_merge(self, sorted_boxes):

        self.stat.set("Menggabungkan hasil…")
        if not sorted_boxes:
            self._finish(); return

        n   = len(sorted_boxes)
        cw  = max(self.cv.winfo_width(), 900)

        self.cv.update_idletasks()
        bb = self.cv.bbox("all")
        canvas_bottom = bb[3] if bb else 200
        final_cy = canvas_bottom + VG

        final_cx = cw // 2
        pw = arr_pw(n); x0 = final_cx - pw // 2

        #self.cv.create_line(
         #   final_cx - pw//2 - 60, final_cy - VG//2,
          #  final_cx + pw//2 + 60, final_cy - VG//2,
           # fill=GREEN, dash=(8, 5), width=2)
        self.cv.create_text(
            x0 - 32, final_cy, text="Array terurut ▶", fill=GREEN,
            font=("Consolas", 11, "bold"), anchor="e")
        self._set_scroll()

        MFLY = 22
        for i, b in enumerate(sorted_boxes):
            tx = x0 + i*(BW+HG) + BW//2; ty = final_cy
            def add_clone(b=b, tx=tx, ty=ty):
                cl = b.clone(fill=GREEN, border=BORDER_G, tfg=WHITE)
                self.anim.queue.insert(1, make_fly(self.cv, cl, tx, ty, MFLY, arc=-28))
                return True
            self.anim.add(fn_step(add_clone))
            self.anim.add(delay_step(60))

        self.anim.add(fn_step(self._set_scroll))
        self.anim.add(fn_step(self._finish))
        self.anim.resume()

    def _finish(self):
        self.running = False; self.sb.config(state="normal")
        self.stat.set("✅  Selesai! Array terurut.")
        self.cmp_lbl.config(text="")

    def _subtree_width(self, arr):
        n = len(arr)
        if n <= 1: return arr_pw(max(n, 1))
        pi  = self._choose_pivot(arr); pv = arr[pi]
        lv  = [v for j, v in enumerate(arr) if j != pi and v <= pv]
        rv  = [v for j, v in enumerate(arr) if j != pi and v >  pv]
        lw  = self._subtree_width(lv) if lv else 0
        rw  = self._subtree_width(rv) if rv else 0
        GAP = 80
        return max((lw+GAP if lv else 0) + BW + (GAP+rw if rv else 0), arr_pw(n))

    def _choose_pivot(self, arr):
        import statistics
        n = len(arr); s = self.pv.get()
        if s == "first":  return 0
        if s == "tengah":
            return n // 2
        if s == "median":
            med_val = statistics.median(arr)
            return min(range(n), key=lambda i: abs(arr[i] - med_val))
        if s == "mean":
            mean_val = sum(arr) / n
            return min(range(n), key=lambda i: abs(arr[i] - mean_val))
        if s == "modus":
            from collections import Counter
            freq = Counter(arr)
            max_freq = max(freq.values())
            mode_vals = {v for v, c in freq.items() if c == max_freq}
            for i, v in enumerate(arr):
                if v in mode_vals:
                    return i
        return n-1

    def _draw_arrow(self, x0, y0, x1, y1, label=""):
        yf = y0 + BH//2 + 3; yt = y1 - BH//2 - 4
        self.cv.create_line(x0, yf, x1, yt, fill=ARROW_CLR, width=2,
                            arrow=tk.LAST, arrowshape=(9,11,4))
        if label:
            mx = (x0+x1)/2; my = (yf+yt)/2; ox = 18 if x1>=x0 else -18
            self.cv.create_text(mx+ox, my, text=label, fill=LABEL_CLR,
                                font=("Consolas",9,"bold"))

    def _set_scroll(self):
        self.cv.update_idletasks()
        bb = self.cv.bbox("all")
        if bb: self.cv.config(
            scrollregion=(bb[0]-60, bb[1]-40, bb[2]+60, bb[3]+60))


def main():
    root = tk.Tk(); root.geometry("1150x740"); root.minsize(750, 540)
    sty = ttk.Style(); sty.theme_use("clam")
    sty.configure("TScale",     background=PANEL_BG, troughcolor="#21262d", sliderlength=16)
    sty.configure("TCombobox",  fieldbackground="#21262d", background="#21262d",
                  foreground=WHITE, selectbackground=ACCENT)
    sty.configure("TScrollbar", background="#21262d", troughcolor=PANEL_BG, arrowcolor=DIM)
    App(root); root.mainloop()


if __name__ == "__main__":
    main()