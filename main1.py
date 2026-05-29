import tkinter as tk
import random

# Глобальный список для хранения истории шагов
VISUAL_STEPS = []
ALL_POINTS = []


def cross_product(o, a, b):
    """Векторное произведение (o->a) x (o->b)"""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def find_upper_bridge(left_hull, right_hull):
    """Находит верхний мостик, записывая шаги в VISUAL_STEPS"""
    idx_l = 0
    max_x = -1
    for i, p in enumerate(left_hull):
        if p[0] > max_x:
            max_x = p[0]
            idx_l = i

    idx_r = 0
    min_x = float('inf')
    for i, p in enumerate(right_hull):
        if p[0] < min_x:
            min_x = p[0]
            idx_r = i

    Vl = left_hull[idx_l]
    Vr = right_hull[idx_r]

    VISUAL_STEPS.append({
        "action": "bridge_start",
        "mode": "upper",
        "Vl": Vl, "Vr": Vr,
        "left_hull": left_hull,
        "right_hull": right_hull
    })

    while True:
        moved = False

        next_r_idx = (idx_r + 1) % len(right_hull)
        Vr_next = right_hull[next_r_idx]

        if cross_product(Vl, Vr, Vr_next) < 0:
            idx_r = next_r_idx
            Vr = Vr_next
            moved = True
            VISUAL_STEPS.append({
                "action": "bridge_move",
                "mode": "upper",
                "Vl": Vl, "Vr": Vr,
                "left_hull": left_hull, "right_hull": right_hull
            })

        next_l_idx = (idx_l - 1) % len(left_hull)
        Vl_next = left_hull[next_l_idx]

        if cross_product(Vr, Vl, Vl_next) > 0:
            idx_l = next_l_idx
            Vl = Vl_next
            moved = True
            VISUAL_STEPS.append({
                "action": "bridge_move",
                "mode": "upper",
                "Vl": Vl, "Vr": Vr,
                "left_hull": left_hull, "right_hull": right_hull
            })

        if not moved:
            break

    return Vl, Vr


def find_lower_bridge(left_hull, right_hull):
    """Находит нижний мостик"""
    idx_l = 0
    max_x = -1
    for i, p in enumerate(left_hull):
        if p[0] > max_x:
            max_x = p[0]
            idx_l = i

    idx_r = 0
    min_x = float('inf')
    for i, p in enumerate(right_hull):
        if p[0] < min_x:
            min_x = p[0]
            idx_r = i

    Vl = left_hull[idx_l]
    Vr = right_hull[idx_r]

    VISUAL_STEPS.append({
        "action": "bridge_start",
        "mode": "lower",
        "Vl": Vl, "Vr": Vr,
        "left_hull": left_hull,
        "right_hull": right_hull
    })

    while True:
        moved = False

        next_r_idx = (idx_r - 1) % len(right_hull)
        Vr_next = right_hull[next_r_idx]

        if cross_product(Vl, Vr, Vr_next) > 0:
            idx_r = next_r_idx
            Vr = Vr_next
            moved = True
            VISUAL_STEPS.append({
                "action": "bridge_move",
                "mode": "lower",
                "Vl": Vl, "Vr": Vr,
                "left_hull": left_hull, "right_hull": right_hull
            })

        next_l_idx = (idx_l + 1) % len(left_hull)
        Vl_next = left_hull[next_l_idx]

        if cross_product(Vr, Vl, Vl_next) < 0:
            idx_l = next_l_idx
            Vl = Vl_next
            moved = True
            VISUAL_STEPS.append({
                "action": "bridge_move",
                "mode": "lower",
                "Vl": Vl, "Vr": Vr,
                "left_hull": left_hull, "right_hull": right_hull
            })

        if not moved:
            break

    return Vl, Vr


def divide_and_conquer(points):
    """Рекурсивная функция построения оболочки"""
    n = len(points)

    if n <= 3:
        if n == 3:
            p0, p1, p2 = points[0], points[1], points[2]
            cp = cross_product(p0, p1, p2)
            if cp < 0:
                points[1], points[2] = points[2], points[1]

        VISUAL_STEPS.append({
            "action": "base_hull",
            "hull": points
        })
        return points

    mid = n // 2
    left_pts = points[:mid]
    right_pts = points[mid:]

    VISUAL_STEPS.append({
        "action": "divide",
        "line_start": left_pts[-1],
        "line_end": right_pts[0]
    })

    left_hull = divide_and_conquer(left_pts)
    right_hull = divide_and_conquer(right_pts)

    VISUAL_STEPS.append({
        "action": "pre_merge",
        "left_hull": left_hull,
        "right_hull": right_hull
    })

    u_left, u_right = find_upper_bridge(left_hull, right_hull)
    l_left, l_right = find_lower_bridge(left_hull, right_hull)

    new_hull = []

    idx = left_hull.index(l_left)
    while True:
        new_hull.append(left_hull[idx])
        if left_hull[idx] == u_left: break
        idx = (idx + 1) % len(left_hull)

    idx = right_hull.index(u_right)
    while True:
        new_hull.append(right_hull[idx])
        if right_hull[idx] == l_right: break
        idx = (idx + 1) % len(right_hull)

    VISUAL_STEPS.append({
        "action": "merged",
        "hull": new_hull,
        "upper_bridge": (u_left, u_right),
        "lower_bridge": (l_left, l_right)
    })

    return new_hull


# --- GUI ---

def draw_current_step(canvas, step_idx):
    """Рисует только текущий шаг"""
    canvas.delete("all")

    # Всегда рисуем все исходные точки
    for p in ALL_POINTS:
        canvas.create_oval(p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3, fill="gray")

    if step_idx < 0 or step_idx >= len(VISUAL_STEPS):
        return

    step = VISUAL_STEPS[step_idx]
    action = step["action"]

    if action == "base_hull":
        # Рисуем маленькую оболочку из 2-3 точек
        draw_poly(canvas, step["hull"], "blue", 2)
        canvas.create_text(10, 10, anchor="w", text="Базовый случай: малая оболочка", fill="blue")

    elif action == "divide":
        # Рисуем линию разделения
        canvas.create_line(step["line_start"][0], step["line_start"][1],
                           step["line_end"][0], step["line_end"][1],
                           fill="red", width=2, dash=(5, 5))
        canvas.create_text(10, 10, anchor="w", text="Разделение множества", fill="red")

    elif action == "pre_merge":
        # Рисуем две оболочки перед объединением
        draw_poly(canvas, step["left_hull"], "blue", 2)
        draw_poly(canvas, step["right_hull"], "blue", 2)
        canvas.create_text(10, 10, anchor="w", text="Две оболочки перед объединением", fill="blue")

    elif action == "bridge_start" or action == "bridge_move":
        # Рисуем оболочки и текущий мостик
        draw_poly(canvas, step["left_hull"], "blue", 1)
        draw_poly(canvas, step["right_hull"], "blue", 1)
        Vl, Vr = step["Vl"], step["Vr"]
        canvas.create_line(Vl[0], Vl[1], Vr[0], Vr[1], fill="green", width=3)
        canvas.create_oval(Vl[0] - 5, Vl[1] - 5, Vl[0] + 5, Vl[1] + 5, fill="red")
        canvas.create_oval(Vr[0] - 5, Vr[1] - 5, Vr[0] + 5, Vr[1] + 5, fill="red")
        mode_text = "Верхний" if step["mode"] == "upper" else "Нижний"
        canvas.create_text(10, 10, anchor="w", text=f"Поиск {mode_text} мостика", fill="green")

    elif action == "merged":
        # Рисуем ТОЛЬКО новую объединенную оболочку (внутренние линии исчезают!)
        draw_poly(canvas, step["hull"], "darkgreen", 3)
        # Подсвечиваем мостики
        canvas.create_line(step["upper_bridge"][0][0], step["upper_bridge"][0][1],
                           step["upper_bridge"][1][0], step["upper_bridge"][1][1],
                           fill="red", width=2, dash=(3, 3))
        canvas.create_line(step["lower_bridge"][0][0], step["lower_bridge"][0][1],
                           step["lower_bridge"][1][0], step["lower_bridge"][1][1],
                           fill="red", width=2, dash=(3, 3))
        canvas.create_text(10, 10, anchor="w", text="Объединение: внутренние линии удалены", fill="darkgreen")


def draw_poly(canvas, points, color, width):
    if len(points) < 2:
        return
    poly = []
    for p in points:
        poly.extend(p)
    poly.extend(points[0])
    canvas.create_line(poly, fill=color, width=width)


def step_forward(canvas):
    root = canvas.master
    if root.step_idx < len(VISUAL_STEPS):
        draw_current_step(canvas, root.step_idx)
        root.lbl.config(text=f"Шаг {root.step_idx + 1} / {len(VISUAL_STEPS)}")
        root.step_idx += 1


def reset(canvas, width, height):
    global ALL_POINTS, VISUAL_STEPS

    VISUAL_STEPS = []
    ALL_POINTS = []

    for _ in range(20):
        x = random.randint(50, width - 50)
        y = random.randint(50, height - 50)
        ALL_POINTS.append((x, y))

    sorted_points = sorted(ALL_POINTS, key=lambda p: (p[0], p[1]))
    divide_and_conquer(list(sorted_points))

    root = canvas.master
    root.step_idx = 0
    root.lbl.config(text=f"Всего шагов: {len(VISUAL_STEPS)}. Нажмите 'Следующий шаг'")

    # Показываем только точки в начале
    canvas.delete("all")
    for p in ALL_POINTS:
        canvas.create_oval(p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3, fill="gray")


def init_app():
    root = tk.Tk()
    root.title("Разделяй и Властвуй")

    width = 800
    height = 600

    canvas = tk.Canvas(root, width=width, height=height, bg="white")
    canvas.pack()

    frame = tk.Frame(root)
    frame.pack(fill=tk.X, pady=5)

    btn_next = tk.Button(frame, text="Следующий шаг", command=lambda: step_forward(canvas))
    btn_next.pack(side=tk.LEFT, padx=5)

    btn_reset = tk.Button(frame, text="Сброс", command=lambda: reset(canvas, width, height))
    btn_reset.pack(side=tk.LEFT, padx=5)

    lbl = tk.Label(frame, text="Готово", width=50, anchor="w")
    lbl.pack(side=tk.RIGHT, padx=10)

    root.canvas = canvas
    root.lbl = lbl
    root.step_idx = 0

    reset(canvas, width, height)
    root.mainloop()


if __name__ == "__main__":
    init_app()