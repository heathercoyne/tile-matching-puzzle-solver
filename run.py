import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# Create figure
fig, ax = plt.subplots(figsize=(10, 3))
ax.set_xlim(0, 10)
ax.set_ylim(0, 4)
ax.axis('off')

def add_box(x, y, text, width=1.6, height=0.8):
    box = FancyBboxPatch(
        (x - width/2, y - height/2),
        width, height,
        boxstyle="round,pad=0.02",
        linewidth=1
    )
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=9)

def add_arrow(x1, y1, x2, y2):
    ax.annotate(
        '',
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle='->', linewidth=1)
    )

# Upper row: software flow
x_positions = [1, 2.7, 4.4, 6.1, 7.8, 9.5]
y_top = 2.8

texts_top = [
    "查询矩阵 Q\n键矩阵 K",
    "4bit 量化",
    "低比特\n注意力预测",
    "二值阈值裁剪\n二值注意力掩码",
    "掩码打包/切分\n结构化稀疏块",
    "score-stationary\n可重构 systolic 阵列\nSDDMM / SpMM"
]

for x, t in zip(x_positions, texts_top):
    add_box(x, y_top, t, width=1.8 if "\n" in t else 1.6)

# Output box
add_box(9.5 + 1.7, y_top, "稀疏注意力\n结果输出", width=1.8)
x_positions.append(9.5 + 1.7)

# Arrows along the top flow
for i in range(len(x_positions) - 1):
    add_arrow(x_positions[i] + 0.9, y_top, x_positions[i+1] - 0.9, y_top)

# Lower box: dense Q/K/V feeding the array
y_bottom = 1.0
add_box(4.4, y_bottom, "查询 Q / 键 K / 值 V\n稠密存储", width=2.3)

# Bent arrow from dense Q/K/V up into the systolic array
add_arrow(4.4 + 1.15, y_bottom, 7.8, 2.1)

plt.tight_layout()
# Optional: save to file
# plt.savefig("sanger_flow.png", dpi=300, bbox_inches="tight")
plt.show()
