import tkinter as tk
from tkinter import ttk, simpledialog
import math


class Draw:
    def __init__(self, root):
        self.root = root
        self.root.title("Геометрические преобразования")
        self.root.geometry("1280x1024")

        self.scale = 30
        self.offset_x = 500
        self.offset_y = 350

        self.points = []
        self.edges = []
        self.original_points = []

        self.create_variant_11()
        self.save_original_points()
        self.create_interface()

    def multipl(self, matrix_1, matrix_2):
        row1 = len(matrix_1)
        col1 = len(matrix_1[0])
        row2 = len(matrix_2)
        col2 = len(matrix_2[0])

        result = [[0 for c in range(col2)] for c in range(row1)]

        for i in range(row1):
            for j in range(col2):
                for k in range(col1):
                    result[i][j] += matrix_1[i][k] * matrix_2[k][j]
        return result

    def create_variant_11(self):


        variant_points = [
            (-1.0, -4.75),
            (1.0, -4.75),
            (1.0, -2.75),
            (-1.0, -2.75),
            (1.0, -0.75),
            (-1.0, -0.75),
            (0.0, 0.75)
        ]

        for x, y in variant_points:
            point_matrix = [[x, y, 1]]
            self.points.append(point_matrix)

        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (3, 2), (2, 4), (4, 5), (5, 3),
            (3, 1),
            (3, 4),
            (5, 6), (6, 4)
        ]

    def save_original_points(self):
        self.original_points = []
        for point_matrix in self.points:
            point_copy = [row[:] for row in point_matrix]
            self.original_points.append(point_copy)

    def reset(self):
        self.points = []
        for original_matrix in self.original_points:
            point_copy = [row[:] for row in original_matrix]
            self.points.append(point_copy)
        self.draw_figure()

    def transformation(self, matrix):
        for i, point_matrix in enumerate(self.points):
            new_point = self.multipl(point_matrix, matrix)
            self.points[i] = new_point
        self.draw_figure()

    def create_interface(self):
        main_place = ttk.Frame(self.root)
        main_place.pack(fill=tk.BOTH, expand=True)

        button_place = ttk.LabelFrame(main_place, padding=10)
        button_place.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        buttons = [
            ("Перенос по X", lambda: self.translate(ask=True, axis='x')),
            ("Перенос по Y", lambda: self.translate(ask=True, axis='y')),
            ("Отражение по X", lambda: self.transformation(self.reflection('x'))),
            ("Отражение по Y", lambda: self.transformation(self.reflection('y'))),
            ("Отражение по Y=X", lambda: self.transformation(self.reflection('yx'))),
            ("Поворот относительно центра", self.rotate_center),
            ("Поворот относительно точки", self.rotate_point),
            ("Масштабирование", self.scale_xy),
            ("Восстановить", self.reset),
            ("Шагающий человечек", self.open_walking_man_window)
        ]

        for text, cmd in buttons:
            btn = ttk.Button(button_place, text=text, command=cmd)
            btn.pack(fill=tk.X, pady=3)

        main_field = ttk.LabelFrame(main_place, padding=5)
        main_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(main_field, width=600, height=500, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.draw_figure()

        self.root.after(100, self.draw_axes)

    def draw_axes(self):
        self.canvas.update_idletasks()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        self.canvas.delete("axes")

        self.canvas.create_line(0, self.offset_y, w, self.offset_y, fill='gray', dash=(2, 2), tags="axes")
        self.canvas.create_line(self.offset_x, 0, self.offset_x, h, fill='gray', dash=(2, 2), tags="axes")
        self.canvas.create_text(self.offset_x - 5, self.offset_y + 10, text="0", fill='gray', tags="axes")

        for x in range(-100, 100):
            if x != 0:
                cx = self.offset_x + x * self.scale
                if 0 <= cx <= w:
                    self.canvas.create_line(cx, self.offset_y - 2, cx, self.offset_y + 2, fill='gray', tags="axes")
                    self.canvas.create_text(cx, self.offset_y + 10, text=str(x), fill='gray', tags="axes")

        for y in range(-100, 100):
            if y != 0:
                cy = self.offset_y - y * self.scale
                if 0 <= cy <= h:
                    self.canvas.create_line(self.offset_x - 3, cy, self.offset_x + 3, cy, fill='gray', tags="axes")
                    self.canvas.create_text(self.offset_x - 10, cy, text=str(y), fill='gray', tags="axes")

    def transform_coords(self, x, y):
        return self.offset_x + x * self.scale, self.offset_y - y * self.scale

    def draw_figure(self):
        self.canvas.delete("figure")

        for i1, i2 in self.edges:
            x1 = self.points[i1][0][0]
            y1 = self.points[i1][0][1]

            x2 = self.points[i2][0][0]
            y2 = self.points[i2][0][1]

            cx1, cy1 = self.transform_coords(x1, y1)
            cx2, cy2 = self.transform_coords(x2, y2)
            self.canvas.create_line(cx1, cy1, cx2, cy2, fill='blue', width=2, tags="figure")

        for point_matrix in self.points:
            x = point_matrix[0][0]
            y = point_matrix[0][1]
            cx, cy = self.transform_coords(x, y)
            self.canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill='red', tags="figure")

    def move_matrix(self, e, f):
        return [
            [1, 0, 0],
            [0, 1, 0],
            [e, f, 1]
        ]

    def reflection(self, axis):
        if axis == 'x':
            return [
                [1, 0, 0],
                [0, -1, 0],
                [0, 0, 1]
            ]
        elif axis == 'y':
            return [
                [-1, 0, 0],
                [0, 1, 0],
                [0, 0, 1]
            ]
        elif axis == 'yx':
            return [
                [0, 1, 0],
                [1, 0, 0],
                [0, 0, 1]
            ]

    def scaling_matrix(self, sx, sy):
        return [
            [sx, 0, 0],
            [0, sy, 0],
            [0, 0, 1]
        ]

    def rotation_matrix(self, angle, direction='counter'):
        radians = math.radians(angle)
        if direction == 'clockwise':
            radians = -radians

        cos_a = math.cos(radians)
        sin_a = math.sin(radians)

        return [
            [cos_a, -sin_a, 0],
            [sin_a, cos_a, 0],
            [0, 0, 1]
        ]

    def rotation_about_point_matrix(self, angle, center_x, center_y, direction='counter'):
        rad = math.radians(angle)
        if direction == 'clockwise':
            rad = -rad
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        T1 = [
            [1, 0, 0],
            [0, 1, 0],
            [-center_x, -center_y, 1]
        ]
        R = [
            [cos_a, -sin_a, 0],
            [sin_a, cos_a, 0],
            [0, 0, 1]
        ]
        T2 = [
            [1, 0, 0],
            [0, 1, 0],
            [center_x, center_y, 1]
        ]

        temp = self.multipl(T1, R)
        final = self.multipl(temp, T2)
        return final

    def rotate_center(self):
        angle = simpledialog.askfloat("Поворот", "Введите угол поворота (в градусах):", minvalue=-360, maxvalue=360)
        direction = simpledialog.askstring("Направление поворота",
                                           "Выберите направление:\n'против' - против часовой\n'по' - по часовой",
                                           initialvalue='против')
        if direction.lower() == 'по':
            type = 'counter'
        else:
            type = 'clockwise'

        matrix = self.rotation_matrix(angle, type)
        self.transformation(matrix)

    def rotate_point(self):
        center_x = simpledialog.askfloat("Центр поворота", "Введите X координату точки:", minvalue=-17, maxvalue=17)
        center_y = simpledialog.askfloat("Центр поворота", "Введите Y координату точки:", minvalue=-17, maxvalue=17)
        angle = simpledialog.askfloat("Поворот", "Введите угол поворота (в градусах):", minvalue=-360, maxvalue=360)
        direction = simpledialog.askstring("Направление поворота",
                                           "Выберите направление:\n'против' - против часовой\n'по' - по часовой",
                                           initialvalue='против')

        if direction.lower() == 'против':
            dir_type = 'clockwise'
        else:
            dir_type = 'counter'
        matrix = self.rotation_about_point_matrix(angle, center_x, center_y, dir_type)
        self.transformation(matrix)

    def translate(self, ask=True, axis=None, dx=0, dy=0):
        if ask:
            if axis == 'x':
                dx = simpledialog.askfloat("Перенос", "Смещение по X:", minvalue=-17, maxvalue=17)
                dy = 0
            elif axis == 'y':
                dy = simpledialog.askfloat("Перенос", "Смещение по Y:", minvalue=-17, maxvalue=17)
                dx = 0
        self.transformation(self.move_matrix(dx, dy))

    def scale_xy(self):
        sx = simpledialog.askfloat("Масштабирование", "Коэффициент по X (0.1-10):", minvalue=0.1, maxvalue=10)
        if sx:
            sy = simpledialog.askfloat("Масштабирование", "Коэффициент по Y (0.1-10):", minvalue=0.1, maxvalue=10)
            if sy:
                self.transformation(self.scaling_matrix(sx, sy))

    def open_walking_man_window(self):
        man_window = tk.Toplevel(self.root)
        man_window.title("Шагающий человечек (Упрощенный)")
        man_window.geometry("1000x650")
        WalkingMan(man_window, self)


class WalkingMan:
    def __init__(self, window, parent):
        self.window = window
        self.parent = parent
        self.scale = 15
        self.offset_x = 100
        self.offset_y = 400

        self.x_position = 0
        self.step_counter = 0

        self.create_interface()
        self.animate()

    def create_interface(self):
        main_field = ttk.Frame(self.window)
        main_field.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(main_field, width=950, height=600, bg='lightblue', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Земля
        self.canvas.create_line(0, self.offset_y, 1000, self.offset_y, fill='green', width=3)

    def to_screen(self, x, y):
        cx = self.offset_x + x * self.scale
        cy = self.offset_y - y * self.scale
        return cx, cy

    def draw_segment_matrix(self, p1, p2, matrix, color, width):
        # p1, p2 - локальные координаты [x, y, 1]
        res1 = self.parent.multipl([p1], matrix)[0]
        res2 = self.parent.multipl([p2], matrix)[0]

        x1, y1 = res1[0], res1[1]
        x2, y2 = res2[0], res2[1]

        cx1, cy1 = self.to_screen(x1, y1)
        cx2, cy2 = self.to_screen(x2, y2)

        self.canvas.create_line(cx1, cy1, cx2, cy2, fill=color, width=width, tags="man")

    def draw_man(self):
        self.canvas.delete("man")

        # 1. Матрица переноса всего человечка (ходьба вправо)
        walk_matrix = self.parent.move_matrix(self.x_position, 0)

        # 2. Матрица покачивания тела (вверх-вниз)
        # Синусоида для плавного покачивания
        step_val = math.sin(self.step_counter * 0.2)
        bob_val = abs(step_val) * 0.5

        bob_matrix = self.parent.move_matrix(0, bob_val)

        # Общая матрица тела: Сначала идем, потом подпрыгиваем
        body_matrix = self.parent.multipl(walk_matrix, bob_matrix)

        # --- ТУЛОВИЩЕ ---
        # Таз (0,0) -> Шея (0, 2.5)
        self.draw_segment_matrix([0, 0, 1], [0, 2.5, 1], body_matrix, 'black', 4)

        # --- ГОЛОВА ---
        head_center_local = [0, 3.0, 1]
        head_center_global = self.parent.multipl([head_center_local], body_matrix)[0]
        hx, hy = head_center_global[0], head_center_global[1]
        sc_x, sc_y = self.to_screen(hx, hy)
        self.canvas.create_oval(sc_x - 12, sc_y - 12, sc_x + 12, sc_y + 12, fill='yellow', outline='black', tags="man")

        # --- РУКИ (Одна линия) ---
        shoulder_y = 2.3  # Плечи чуть ниже шеи
        arm_len = 1.2

        # Руки двигаются в противофазе ногам
        # Когда левая нога идет вперед (вправо), левая рука идет назад (влево)
        l_arm_angle = -step_val * 30
        r_arm_angle = step_val * 30

        # Левая рука
        # Вращаем вокруг плеча (0, shoulder_y)
        rot_l_arm = self.parent.rotation_about_point_matrix(l_arm_angle, 0, shoulder_y, 'counter')
        m_l_arm = self.parent.multipl(rot_l_arm, body_matrix)
        # Рисуем от плеча вниз (локально)
        # Плечо (0, shoulder_y) -> Кисть (0, shoulder_y - arm_len)
        self.draw_segment_matrix([0, shoulder_y, 1], [0, shoulder_y - arm_len, 1], m_l_arm, 'blue', 3)

        # Правая рука
        rot_r_arm = self.parent.rotation_about_point_matrix(r_arm_angle, 0, shoulder_y, 'counter')
        m_r_arm = self.parent.multipl(rot_r_arm, body_matrix)
        self.draw_segment_matrix([0, shoulder_y, 1], [0, shoulder_y - arm_len, 1], m_r_arm, 'red', 3)

        # --- НОГИ (Одна линия) ---
        leg_len = 1.8

        # Углы ног
        # step_val > 0 : левая нога должна идти вперед (вправо).
        # В нашей системе положительный угол вращает влево.
        # Значит, для движения вправо (вперед) нужен отрицательный угол.
        l_leg_angle = -step_val * 35
        r_leg_angle = step_val * 35

        # Левая нога
        # Вращаем вокруг таза (0,0)
        rot_l_leg = self.parent.rotation_about_point_matrix(l_leg_angle, 0, 0, 'counter')
        m_l_leg = self.parent.multipl(rot_l_leg, body_matrix)

        # Рисуем: Таз (0,0) -> Стопа (0, -leg_len)
        self.draw_segment_matrix([0, 0, 1], [0, -leg_len, 1], m_l_leg, 'blue', 4)

        # Правая нога
        rot_r_leg = self.parent.rotation_about_point_matrix(r_leg_angle, 0, 0, 'counter')
        m_r_leg = self.parent.multipl(rot_r_leg, body_matrix)

        # Рисуем: Таз (0,0) -> Стопа (0, -leg_len)
        self.draw_segment_matrix([0, 0, 1], [0, -leg_len, 1], m_r_leg, 'red', 4)

    def animate(self):
        # Движение вправо
        self.x_position += 0.15

        # Если ушел за экран, возвращаем
        if self.x_position * self.scale > 950:
            self.x_position = -50

        self.step_counter += 1

        self.draw_man()

        self.window.after(30, self.animate)


if __name__ == "__main__":
    window = tk.Tk()
    app = Draw(window)
    window.mainloop()