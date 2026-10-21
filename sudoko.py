# sudoku_short.py
# 9:16 YouTube Short - Python Sudoku Solver with backtracking animation.
# Install:  pip install matplotlib numpy imageio-ffmpeg
# Run:      python sudoku_short.py
# Output:   sudoku_shorts.mp4  (1080x1920, 30fps)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import FancyBboxPatch
from copy import deepcopy

# -------------------------------------------------------------
# FFmpeg setup (bundled binary via imageio-ffmpeg)
# -------------------------------------------------------------
try:
    import imageio_ffmpeg
    plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"[INFO] FFmpeg: {plt.rcParams['animation.ffmpeg_path']}")
except Exception:
    print("[WARN] imageio-ffmpeg not found. Falling back to system ffmpeg.")
    plt.rcParams["animation.ffmpeg_path"] = "ffmpeg"

# =============================================================
# 1. SUDOKU ENGINE
# =============================================================
def find_empty(bo):
    for i in range(9):
        for j in range(9):
            if bo[i][j] == 0:
                return (i, j)
    return None

def valid(bo, num, pos):
    r, c = pos
    if any(bo[r][i] == num for i in range(9) if i != c):
        return False
    if any(bo[i][c] == num for i in range(9) if i != r):
        return False
    br, bc = 3 * (r // 3), 3 * (c // 3)
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if bo[i][j] == num and (i, j) != pos:
                return False
    return True

PUZZLE = [
    [0, 0, 0, 2, 6, 0, 7, 0, 1],
    [6, 8, 0, 0, 7, 0, 0, 9, 0],
    [1, 9, 0, 0, 0, 4, 5, 0, 0],
    [8, 2, 0, 1, 0, 0, 0, 4, 0],
    [0, 0, 4, 6, 0, 2, 9, 0, 0],
    [0, 5, 0, 0, 0, 3, 0, 2, 8],
    [0, 0, 9, 3, 0, 0, 0, 7, 4],
    [0, 4, 0, 0, 5, 0, 0, 3, 6],
    [7, 0, 3, 0, 1, 8, 0, 0, 0]
]

STEPS = []

def solve(bo, record=True):
    empty = find_empty(bo)
    if not empty:
        return True
    r, c = empty
    for num in range(1, 10):
        if valid(bo, num, (r, c)):
            bo[r][c] = num
            if record:
                STEPS.append((deepcopy(bo), r, c, num, "place"))
            if solve(bo, record):
                return True
            bo[r][c] = 0
            if record:
                STEPS.append((deepcopy(bo), r, c, 0, "remove"))
    return False

# Final solved board
solved_board = deepcopy(PUZZLE)
solve(solved_board, record=False)

# Recorded steps
solve(deepcopy(PUZZLE), record=True)
print(f"[INFO] Raw steps recorded: {len(STEPS)}")

# Subsample to keep the video short
MAX_SOLVE_FRAMES = 3000
if len(STEPS) > MAX_SOLVE_FRAMES:
    idx = np.linspace(0, len(STEPS) - 1, MAX_SOLVE_FRAMES, dtype=int)
    STEPS = [STEPS[i] for i in idx]
TOTAL_STEPS = len(STEPS)
print(f"[INFO] Animation steps used: {TOTAL_STEPS}")

# =============================================================
# 2. THEME
# =============================================================
BG            = "#0D1117"
GRID_BOLD     = "#00FFFF"
GRID_THIN     = "#30363D"
NUM_GIVEN     = "#FFFFFF"
NUM_NEW       = "#00FFFF"
NUM_TEST      = "#FF00FF"
NUM_BACK      = "#FF3B3B"
NUM_SOLVED    = "#FFD700"
TXT_WHITE     = "#FFFFFF"
TXT_ACCENT    = "#00FFFF"
TXT_GOLD      = "#FFD700"
TXT_MUTED     = "#8B949E"

# =============================================================
# 3. FIGURE (1080x1920, 9:16)
# =============================================================
FIG_W, FIG_H = 5.625, 10.0
DPI = 192
FPS = 30

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=DPI)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

def setup_axes():
    ax.clear()
    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(-2.0, 11.5)
    ax.set_aspect("equal")
    ax.axis("off")

def draw_grid(highlight=None, hl_color=None):
    # Glow frame
    ax.add_patch(FancyBboxPatch(
        (-0.55, -0.05), 10.1, 9.1,
        boxstyle="round,pad=0.02,rounding_size=0.15",
        linewidth=3, edgecolor=GRID_BOLD, facecolor="none", alpha=0.35
    ))
    # Lines
    for i in range(10):
        lw = 3.5 if i % 3 == 0 else 1.2
        col = GRID_BOLD if i % 3 == 0 else GRID_THIN
        ax.plot([i, i], [0, 9], color=col, lw=lw, zorder=2)
        ax.plot([0, 9], [i, i], color=col, lw=lw, zorder=2)
    # Highlight cell
    if highlight is not None:
        r, c = highlight
        ax.add_patch(FancyBboxPatch(
            (c + 0.05, 8.95 - r + 0.05), 0.9, 0.9,
            boxstyle="round,pad=0.02,rounding_size=0.1",
            linewidth=2, edgecolor=hl_color,
            facecolor=hl_color, alpha=0.25, zorder=3
        ))

def draw_board(board, original, active=None, active_color=None):
    for r in range(9):
        for c in range(9):
            n = board[r][c]
            if n == 0:
                continue
            if original[r][c] != 0:
                color, size = NUM_GIVEN, 22
            elif active == (r, c):
                color, size = active_color, 28
            else:
                color, size = NUM_NEW, 22
            ax.text(c + 0.5, 8.5 - r, str(n),
                    ha="center", va="center", fontsize=size, color=color,
                    fontfamily="monospace", fontweight="bold", zorder=4)

# =============================================================
# 4. FRAME SCHEDULE
# =============================================================
INTRO_FRAMES = 450
CODE_FRAMES  = 600
OUTRO_FRAMES = 900
TOTAL_FRAMES = INTRO_FRAMES + CODE_FRAMES + TOTAL_STEPS + OUTRO_FRAMES
print(f"[INFO] Total frames: {TOTAL_FRAMES}  (~{TOTAL_FRAMES / FPS:.1f}s)")

CODE_LINES = [
    "def solve(bo):",
    "    find = findyhggfd  gfsdfsfsfsjf    gfsgfsggfsfsfs  fgsfd_empt  y(bo)",
    "    if not find:",
    "        return True",
    "    row, col = find",
    "",
    "    for i in range(1, 10):",
    "        if valid(bo, i, (row, col)):",
    "            bo[row][col] = i",
    "            if solve(bo):",
    "                return True",
    "            bo[row][col] = 0",
    "    return False",
]

def line_color(line):
    if "def solve" in line:
        return "#FF7B72"
    if "for i in range" in line or "if valid" in line:
        return "#FFA657"
    if "bo[row][col]" in line:
        return "#79C0FF"
    if "return" in line:
        return "#D2A8FF"
    return TXT_WHITE

# =============================================================
# 5. ANIMATION
# =============================================================
def animate(frame):
    setup_axes()

    # ---------- INTRO ----------
    if frame < INTRO_FRAMES:
        draw_grid()
        draw_board(PUZZLE, PUZZLE)
        ax.text(4.5, 10.7, "Can Python",
                ha="center", va="center", fontsize=34,
                color=TXT_WHITE, fontweight="bold", fontfamily="monospace")
        ax.text(4.5, 10.0, "Solve This?!",
                ha="center", va="center", fontsize=30,
                color=TXT_ACCENT, fontweight="bold", fontfamily="monospace")
        return []

    # ---------- CODE REVEAL ----------
    if frame < INTRO_FRAMES + CODE_FRAMES:
        local = frame - INTRO_FRAMES
        visible = int((local / CODE_FRAMES) * len(CODE_LINES)) + 1

        ax.add_patch(FancyBboxPatch(
            (-0.2, -0.5), 9.4, 11.0,
            boxstyle="round,pad=0.05,rounding_size=0.2",
            linewidth=2, edgecolor=GRID_BOLD,
            facecolor="#161B22", alpha=0.95
        ))
        ax.plot([-0.2, 9.2], [10.0, 10.0], color=GRID_THIN, lw=1)
        for i, c in enumerate(["#FF5F56", "#FFBD2E", "#27C93F"]):
            ax.scatter(i * 0.4, 10.3, s=120, color=c, zorder=5)
        ax.text(1.6, 10.3, "solver.py", color="#C9D1D9",
                fontsize=11, fontfamily="monospace", va="center")

        y = 9.4
        for line in CODE_LINES[:visible]:
            ax.text(0.1, y, line, color=line_color(line),
                    fontsize=11, fontfamily="monospace",
                    va="center", ha="left")
            y -= 0.62

        ax.text(4.5, 10.9, ">> Backtracking Algorithm",
                ha="center", va="center", fontsize=15,
                color=TXT_ACCENT, fontweight="bold", fontfamily="monospace")
        return []

    # ---------- SOLVING ----------
    if frame < INTRO_FRAMES + CODE_FRAMES + TOTAL_STEPS:
        idx = frame - INTRO_FRAMES - CODE_FRAMES
        board_state, r, c, num, action = STEPS[idx]
        hl = NUM_TEST if action == "place" else NUM_BACK

        draw_grid(highlight=(r, c), hl_color=hl)
        draw_board(board_state, PUZZLE, active=(r, c), active_color=hl)

        ax.text(4.5, 10.6, ">> Python Solving...",
                ha="center", va="center", fontsize=16,
                color=TXT_ACCENT, fontweight="bold", fontfamily="monospace")

        label = f"Testing: {num}" if action == "place" else "Backtracking..."
        ax.text(4.5, 9.85, label,
                ha="center", va="center", fontsize=14,
                color=hl, fontweight="bold", fontfamily="monospace")

        p = (idx + 1) / TOTAL_STEPS
        ax.add_patch(FancyBboxPatch(
            (0.0, -0.6), 9.0, 0.25,
            boxstyle="round,pad=0.0,rounding_size=0.1",
            linewidth=0, facecolor="#21262D"))
        ax.add_patch(FancyBboxPatch(
            (0.0, -0.6), 9.0 * p, 0.25,
            boxstyle="round,pad=0.0,rounding_size=0.1",
            linewidth=0, facecolor=GRID_BOLD))
        ax.text(4.5, -1.2, f"{int(p * 100)}%",
                ha="center", va="center", fontsize=11,
                color=TXT_WHITE, fontfamily="monospace")
        return []

    # ---------- OUTRO ----------
    local = frame - INTRO_FRAMES - CODE_FRAMES - TOTAL_STEPS
    pulse = 1.0 + 0.03 * np.sin(local * 0.4)

    draw_grid()
    draw_board(solved_board, PUZZLE)
    for r in range(9):
        for c in range(9):
            if PUZZLE[r][c] == 0:
                ax.text(c + 0.5, 8.5 - r, str(solved_board[r][c]),
                        ha="center", va="center", fontsize=22,
                        color=NUM_SOLVED, fontweight="bold",
                        fontfamily="monospace", zorder=5)

    ax.text(4.5, 10.7, "Solved by Python!",
            ha="center", va="center", fontsize=26 * pulse,
            color=TXT_GOLD, fontweight="bold", fontfamily="monospace")
    ax.text(4.5, -1.3, "Coding Sikho",
            ha="center", va="center", fontsize=22,
            color=TXT_ACCENT, fontweight="bold", fontfamily="monospace")
    ax.text(4.5, -0.7, "Subscribe for more!",
            ha="center", va="center", fontsize=12,
            color=TXT_MUTED, fontfamily="monospace")
    return []

# =============================================================
# 6. RENDER
# =============================================================
if __name__ == "__main__":
    print("[INFO] Building animation...")
    anim = animation.FuncAnimation(
        fig, animate, frames=TOTAL_FRAMES, interval=1000 / FPS, blit=False
    )

    writer = animation.FFMpegWriter(
        fps=FPS,
        codec="libx264",
        bitrate=8000,
        extra_args=[
            "-pix_fmt", "yuv420p",
            "-crf", "20",
            "-preset", "medium",
            "-profile:v", "high",
            "-level", "4.0",
            "-movflags", "+faststart",
        ],
    )

    out = "sudoku_shorts.mp4"
    print(f"[INFO] Rendering -> {out}")
    anim.save(out, writer=writer, dpi=DPI)
    print(f"[DONE] Saved {out}")
