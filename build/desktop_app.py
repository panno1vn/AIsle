from __future__ import annotations

import copy
import csv
import io
import json
import math
import queue
import random
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from core import (DEFAULT_LAYOUT, generate_population, population_from_input,
                  position_at, run_simulation, validate)
from storage import (clear_history, delete_history, list_history, load_last_result, load_project,
                     save_history, save_last_result, save_project)


BG, SIDE, PANEL, PANEL_2 = "#080C11", "#0B1017", "#0F1620", "#131C28"
LINE, LINE_2, TEXT, DIM = "#233043", "#304158", "#EDF2F7", "#8A98AA"
BLUE, PINK, AMBER, GREEN, RED = "#4CC9F0", "#FF4D8D", "#FFC24B", "#22C55E", "#EF5D67"
FONT, DISPLAY, MONO = "Segoe UI", "Segoe UI Semibold", "Consolas"
ROOT = Path(__file__).resolve().parent


def money(value: float) -> str:
    return f"{value:,.0f} ₫".replace(",", ".")


def percent(value: float) -> str:
    return f"{value * 100:.1f}%"


class AIsleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AIsle — Store Simulator")
        self.geometry("1360x850")
        self.minsize(1120, 720)
        self.configure(bg=BG)
        self.layout_data, self.catalog = load_project()
        # Replay survives app restarts; a missing file still means no completed run yet.
        self.last_result = load_last_result()
        self.current_page = None
        self.nav_buttons = {}
        self.pages = {}
        self._configure_styles()
        self._build_shell()
        self.show_page("overview")

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT,
                        borderwidth=0, rowheight=34, font=(FONT, 10))
        style.configure("Treeview.Heading", background=SIDE, foreground=DIM, borderwidth=0,
                        font=(MONO, 9, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#17374A")], foreground=[("selected", TEXT)])
        style.configure("TCombobox", fieldbackground=PANEL_2, background=PANEL_2, foreground=TEXT,
                        arrowcolor=TEXT, bordercolor=LINE_2)
        style.map("TCombobox", fieldbackground=[("readonly", PANEL_2)], foreground=[("readonly", TEXT)])
        style.configure("Horizontal.TProgressbar", troughcolor=LINE, background=BLUE, borderwidth=0)

    def _build_shell(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        side = tk.Frame(self, bg=SIDE, width=230, highlightthickness=1, highlightbackground=LINE)
        side.grid(row=0, column=0, sticky="ns")
        side.grid_propagate(False)
        brand = tk.Frame(side, bg=SIDE)
        brand.pack(fill="x", padx=24, pady=(26, 28))
        mark = tk.Canvas(brand, width=29, height=29, bg=SIDE, highlightthickness=0)
        mark.pack(side="left", padx=(0, 10))
        mark.create_rectangle(1, 13, 7, 27, fill=BLUE, outline="")
        mark.create_rectangle(10, 2, 16, 27, fill=BLUE, outline="")
        mark.create_rectangle(19, 9, 25, 27, fill=BLUE, outline="")
        name = tk.Frame(brand, bg=SIDE)
        name.pack(side="left")
        tk.Label(name, text="AISLE", bg=SIDE, fg=TEXT, font=(DISPLAY, 16, "bold")).pack(anchor="w")
        tk.Label(name, text="STORE SIMULATOR", bg=SIDE, fg=DIM, font=(MONO, 7)).pack(anchor="w")
        items = [("00", "overview", "Tổng quan"), ("01", "layout", "Thiết kế layout"),
                 ("02", "catalog", "Catalog"), ("03", "run", "Cấu hình & chạy"),
                 ("04", "results", "Kết quả & replay"), ("05", "history", "Lịch sử")]
        for number, key, label in items:
            button = tk.Button(side, text=f"{number}    {label}", anchor="w", bg=SIDE, fg=DIM,
                               activebackground=PANEL_2, activeforeground=TEXT, relief="flat", bd=0,
                               font=(FONT, 10), padx=13, pady=12, cursor="hand2",
                               command=lambda page=key: self.show_page(page))
            button.pack(fill="x", padx=13, pady=2)
            self.nav_buttons[key] = button
        status = tk.Frame(side, bg=SIDE, highlightthickness=1, highlightbackground=LINE)
        status.pack(side="bottom", fill="x", padx=18, pady=20)
        tk.Label(status, text="●", fg=GREEN, bg=SIDE, font=(FONT, 12)).pack(side="left", padx=(12, 8), pady=12)
        status_text = tk.Frame(status, bg=SIDE)
        status_text.pack(side="left")
        tk.Label(status_text, text="SIM CORE", fg=TEXT, bg=SIDE, font=(MONO, 8, "bold")).pack(anchor="w")
        self.core_status = tk.Label(status_text, text="Sẵn sàng", fg=DIM, bg=SIDE, font=(MONO, 7))
        self.core_status.pack(anchor="w")

        content = tk.Frame(self, bg=BG)
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_rowconfigure(1, weight=1)
        content.grid_columnconfigure(0, weight=1)
        top = tk.Frame(content, bg=BG, height=65, highlightthickness=1, highlightbackground=LINE)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_propagate(False)
        self.crumb = tk.Label(top, text="AISLE / TỔNG QUAN", bg=BG, fg=DIM, font=(MONO, 9, "bold"))
        self.crumb.pack(side="left", padx=32)
        tk.Button(top, text="Xuất cấu hình", command=self.export_project, bg=PANEL_2, fg=TEXT,
                  activebackground=LINE_2, activeforeground=TEXT, relief="flat", padx=15, pady=8,
                  font=(FONT, 9), cursor="hand2").pack(side="right", padx=30)
        tk.Label(top, text="●  Đã tự lưu", bg=BG, fg=DIM, font=(MONO, 8)).pack(side="right")
        self.page_host = tk.Frame(content, bg=BG)
        self.page_host.grid(row=1, column=0, sticky="nsew")
        self.page_host.grid_rowconfigure(0, weight=1)
        self.page_host.grid_columnconfigure(0, weight=1)

    def show_page(self, key: str):
        if self.current_page:
            self.pages[self.current_page].grid_remove()
        if key not in self.pages:
            cls = {"overview": OverviewPage, "layout": LayoutPage, "catalog": CatalogPage,
                   "run": RunPage, "results": ResultsPage, "history": HistoryPage}[key]
            self.pages[key] = cls(self.page_host, self)
            self.pages[key].grid(row=0, column=0, sticky="nsew")
        else:
            self.pages[key].grid()
            if hasattr(self.pages[key], "refresh"):
                self.pages[key].refresh()
        self.current_page = key
        titles = {"overview": "TỔNG QUAN", "layout": "THIẾT KẾ LAYOUT", "catalog": "CATALOG",
                  "run": "CẤU HÌNH & CHẠY", "results": "KẾT QUẢ & REPLAY", "history": "LỊCH SỬ"}
        self.crumb.configure(text=f"AISLE  /  {titles[key]}")
        for page, button in self.nav_buttons.items():
            button.configure(bg=PANEL_2 if page == key else SIDE, fg=TEXT if page == key else DIM)

    def persist(self):
        save_project(self.layout_data, self.catalog)

    def export_project(self):
        path = filedialog.asksaveasfilename(title="Xuất cấu hình AIsle", defaultextension=".json",
                                            filetypes=[("JSON", "*.json")], initialfile="aisle-project.json")
        if path:
            Path(path).write_text(json.dumps({"layout": self.layout_data, "catalog": self.catalog},
                                             ensure_ascii=False, indent=2), encoding="utf-8")


class Page(tk.Frame):
    def __init__(self, parent, app: AIsleApp):
        super().__init__(parent, bg=BG)
        self.app = app

    def heading(self, eyebrow: str, title: str, subtitle: str):
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=42, pady=(32, 24))
        tk.Label(head, text=eyebrow, bg=BG, fg=BLUE, font=(MONO, 8, "bold")).pack(anchor="w")
        tk.Label(head, text=title, bg=BG, fg=TEXT, font=(DISPLAY, 29, "bold")).pack(anchor="w", pady=(8, 4))
        tk.Label(head, text=subtitle, bg=BG, fg=DIM, font=(FONT, 10)).pack(anchor="w")
        return head

    @staticmethod
    def button(parent, text, command, primary=False, danger=False):
        color = BLUE if primary else PANEL_2
        fg = BG if primary else (RED if danger else TEXT)
        return tk.Button(parent, text=text, command=command, bg=color, fg=fg, activebackground=LINE_2,
                         activeforeground=TEXT, relief="flat", padx=16, pady=9, font=(FONT, 9, "bold"), cursor="hand2")


class OverviewPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=54, pady=55)
        tk.Label(body, text="SIMULATION WORKSPACE", bg=BG, fg=BLUE, font=(MONO, 9, "bold")).pack(anchor="w")
        tk.Label(body, text="Đọc luồng khách.\nKhông đoán.", justify="left", bg=BG, fg=TEXT,
                 font=(DISPLAY, 48, "bold")).pack(anchor="w", pady=(14, 18))
        tk.Label(body, text="Mô phỏng cách khách di chuyển, dừng lại và mua sắm trên layout hiện tại.\n"
                                 "AIsle chỉ trả dữ liệu để Manager tự quyết định.", justify="left",
                 bg=BG, fg=DIM, font=(FONT, 12)).pack(anchor="w")
        self.button(body, "Bắt đầu từ layout  →", lambda: app.show_page("layout"), True).pack(anchor="w", pady=28)
        stats = tk.Frame(body, bg=LINE)
        stats.pack(fill="x", pady=(25, 30))
        for title, value, note in [("QUẦN THỂ MỤC TIÊU", "150–200", "NPC / lần chạy"),
                                   ("THỜI GIAN XỬ LÝ", "< 30s", "mục tiêu PoC"),
                                   ("CƠ CHẾ", "GA + A*", "genome & pathfinding")]:
            card = tk.Frame(stats, bg=PANEL, padx=22, pady=18)
            card.pack(side="left", fill="both", expand=True, padx=(0, 1))
            tk.Label(card, text=title, bg=PANEL, fg=DIM, font=(MONO, 8, "bold")).pack(anchor="w")
            tk.Label(card, text=value, bg=PANEL, fg=AMBER, font=(MONO, 20, "bold")).pack(anchor="w", pady=6)
            tk.Label(card, text=note, bg=PANEL, fg=DIM, font=(FONT, 8)).pack(anchor="w")
        flow = tk.Frame(body, bg=BG)
        flow.pack(fill="x")
        for index, (name, note) in enumerate([("VẼ", "Tường, kệ, lối vào, checkout"), ("NHẬP", "Catalog tạo vũ trụ nhu cầu"),
                                               ("CHẠY", "Sinh quần thể, mô phỏng"), ("ĐỌC", "Replay, heatmap, doanh thu")], 1):
            card = tk.Frame(flow, bg=BG)
            card.pack(side="left", fill="x", expand=True)
            tk.Label(card, text=f"0{index}", bg=BG, fg=BLUE, font=(MONO, 8, "bold")).pack(anchor="w")
            tk.Label(card, text=name, bg=BG, fg=TEXT, font=(DISPLAY, 11, "bold")).pack(anchor="w", pady=(8, 4))
            tk.Label(card, text=note, bg=BG, fg=DIM, font=(FONT, 8)).pack(anchor="w")


class LayoutPage(Page):
    SCALE = 80

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.tool, self.start, self.preview, self.selected = "select", None, None, None
        head = self.heading("01 / STORE GEOMETRY", "Thiết kế layout", "Chọn công cụ rồi thao tác trực tiếp trên mặt bằng. Mỗi ô lưới là 0,5 m.")
        actions = tk.Frame(head, bg=BG)
        actions.pack(side="right", anchor="e")
        self.button(actions, "Mẫu mặc định", self.reset).pack(side="left", padx=5)
        self.button(actions, "Xóa đối tượng", self.delete_selected, danger=True).pack(side="left")
        main = tk.Frame(self, bg=PANEL, highlightthickness=1, highlightbackground=LINE)
        main.pack(fill="both", expand=True, padx=42, pady=(0, 28))
        tools = tk.Frame(main, bg=PANEL, width=210)
        tools.pack(side="left", fill="y", padx=14, pady=14)
        tools.pack_propagate(False)
        tk.Label(tools, text="CÔNG CỤ", bg=PANEL, fg=DIM, font=(MONO, 8, "bold")).pack(anchor="w", pady=(2, 9))
        self.tool_buttons = {}
        for key, label, note in [("select", "↖  Chọn", "Chọn và kéo kệ"), ("wall", "╱  Đặt tường", "Kéo một đoạn thẳng"),
                                 ("shelf", "▰  Đặt kệ hàng", "Kéo hình chữ nhật"), ("entrance", "▽  Đặt lối vào", "Nhấp một vị trí"),
                                 ("checkout", "◇  Quầy thu ngân", "Nhấp một vị trí")]:
            btn = tk.Button(tools, text=f"{label}\n    {note}", justify="left", anchor="w", command=lambda k=key: self.set_tool(k),
                            bg=PANEL_2 if key == "select" else PANEL, fg=TEXT if key == "select" else DIM,
                            activebackground=PANEL_2, activeforeground=TEXT, relief="flat", padx=10, pady=8,
                            font=(FONT, 9), cursor="hand2")
            btn.pack(fill="x", pady=2)
            self.tool_buttons[key] = btn
        tk.Frame(tools, height=1, bg=LINE).pack(fill="x", pady=16)
        tk.Label(tools, text="THUỘC TÍNH KỆ", bg=PANEL, fg=DIM, font=(MONO, 8, "bold")).pack(anchor="w")
        self.shelf_label = self.entry(tools, "Nhãn")
        self.shelf_category = self.entry(tools, "Category")
        tk.Label(tools, text="Base valence", bg=PANEL, fg=DIM, font=(FONT, 8)).pack(anchor="w", pady=(10, 3))
        self.valence = tk.DoubleVar(value=.2)
        tk.Scale(tools, from_=-1, to=1, resolution=.05, orient="horizontal", variable=self.valence,
                 command=self.update_properties, bg=PANEL, fg=DIM, troughcolor=LINE, activebackground=BLUE,
                 highlightthickness=0, showvalue=True).pack(fill="x")
        canvas_host = tk.Frame(main, bg=BG)
        canvas_host.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(canvas_host, width=960, height=640, bg="#090F16", highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.pointer_down)
        self.canvas.bind("<B1-Motion>", self.pointer_move)
        self.canvas.bind("<ButtonRelease-1>", self.pointer_up)
        self.canvas.bind("<Configure>", lambda _e: self.draw())
        self.draw()

    def entry(self, parent, label):
        tk.Label(parent, text=label, bg=PANEL, fg=DIM, font=(FONT, 8)).pack(anchor="w", pady=(10, 3))
        entry = tk.Entry(parent, bg=SIDE, fg=TEXT, insertbackground=TEXT, relief="flat", font=(FONT, 9))
        entry.pack(fill="x", ipady=6)
        entry.bind("<FocusOut>", self.update_properties)
        entry.bind("<Return>", self.update_properties)
        return entry

    def set_tool(self, tool):
        self.tool = tool
        for key, button in self.tool_buttons.items():
            button.configure(bg=PANEL_2 if key == tool else PANEL, fg=TEXT if key == tool else DIM)

    def point(self, event):
        sx = max(.001, self.canvas.winfo_width() / self.app.layout_data["width"])
        sy = max(.001, self.canvas.winfo_height() / self.app.layout_data["height"])
        return {"x": round(event.x / sx * 4) / 4, "y": round(event.y / sy * 4) / 4}

    def pointer_down(self, event):
        point = self.point(event)
        if self.tool in ("entrance", "checkout"):
            self.app.layout_data[self.tool] = point
            self.selected = self.tool
            self.app.persist(); self.draw(); return
        if self.tool == "select":
            self.selected = self.pick(point)
            if self.selected and self.selected[0] == "shelf":
                shelf = next(s for s in self.app.layout_data["shelves"] if s["id"] == self.selected[1])
                self.start = {"dx": point["x"] - shelf["x"], "dy": point["y"] - shelf["y"]}
                self.load_properties(shelf)
            self.draw(); return
        self.start = point
        self.preview = point

    def pointer_move(self, event):
        point = self.point(event)
        if self.tool == "select" and self.start and self.selected and self.selected[0] == "shelf":
            shelf = next(s for s in self.app.layout_data["shelves"] if s["id"] == self.selected[1])
            shelf["x"] = clamp(point["x"] - self.start["dx"], .25, self.app.layout_data["width"] - shelf["w"] - .25)
            shelf["y"] = clamp(point["y"] - self.start["dy"], .25, self.app.layout_data["height"] - shelf["h"] - .25)
            self.draw()
        elif self.start:
            self.preview = point
            self.draw()

    def pointer_up(self, event):
        point = self.point(event)
        if self.tool == "wall" and self.start and math.hypot(point["x"] - self.start["x"], point["y"] - self.start["y"]) > .4:
            self.app.layout_data["walls"].append({"id": f"w{time.time_ns()}", "x1": self.start["x"], "y1": self.start["y"], "x2": point["x"], "y2": point["y"]})
        elif self.tool == "shelf" and self.start:
            x, y = min(self.start["x"], point["x"]), min(self.start["y"], point["y"])
            width, height = abs(point["x"] - self.start["x"]), abs(point["y"] - self.start["y"])
            if width >= .5 and height >= .4:
                shelf = {"id": f"s{time.time_ns()}", "label": f"Kệ {len(self.app.layout_data['shelves']) + 1}",
                         "category": "other", "x": x, "y": y, "w": width, "h": height, "valence": .2}
                self.app.layout_data["shelves"].append(shelf)
                self.selected = ("shelf", shelf["id"])
                self.load_properties(shelf)
        self.start = self.preview = None
        self.app.persist(); self.draw()

    def pick(self, point):
        for shelf in reversed(self.app.layout_data["shelves"]):
            if shelf["x"] <= point["x"] <= shelf["x"] + shelf["w"] and shelf["y"] <= point["y"] <= shelf["y"] + shelf["h"]:
                return "shelf", shelf["id"]
        for wall in self.app.layout_data["walls"]:
            ax, ay, bx, by = wall["x1"], wall["y1"], wall["x2"], wall["y2"]
            length2 = (bx - ax) ** 2 + (by - ay) ** 2
            ratio = clamp(((point["x"] - ax) * (bx - ax) + (point["y"] - ay) * (by - ay)) / max(length2, .001), 0, 1)
            if math.hypot(point["x"] - ax - ratio * (bx - ax), point["y"] - ay - ratio * (by - ay)) < .18:
                return "wall", wall["id"]
        return None

    def load_properties(self, shelf):
        self.shelf_label.delete(0, "end"); self.shelf_label.insert(0, shelf["label"])
        self.shelf_category.delete(0, "end"); self.shelf_category.insert(0, shelf["category"])
        self.valence.set(shelf["valence"])

    def update_properties(self, _event=None):
        if not self.selected or self.selected[0] != "shelf": return
        shelf = next(s for s in self.app.layout_data["shelves"] if s["id"] == self.selected[1])
        shelf["label"], shelf["category"], shelf["valence"] = self.shelf_label.get() or shelf["label"], self.shelf_category.get() or shelf["category"], self.valence.get()
        self.app.persist(); self.draw()

    def delete_selected(self):
        if not self.selected: return
        kind, ident = self.selected if isinstance(self.selected, tuple) else (self.selected, None)
        if kind == "shelf": self.app.layout_data["shelves"] = [s for s in self.app.layout_data["shelves"] if s["id"] != ident]
        elif kind == "wall": self.app.layout_data["walls"] = [w for w in self.app.layout_data["walls"] if w["id"] != ident]
        else: self.app.layout_data[kind] = None
        self.selected = None; self.app.persist(); self.draw()

    def reset(self):
        if messagebox.askyesno("Khôi phục layout", "Thay layout hiện tại bằng mẫu mặc định?"):
            self.app.layout_data = copy.deepcopy(DEFAULT_LAYOUT); self.selected = None; self.app.persist(); self.draw()

    def draw(self):
        c, layout = self.canvas, self.app.layout_data
        c.delete("all")
        width, height = max(1, c.winfo_width()), max(1, c.winfo_height())
        sx, sy = width / layout["width"], height / layout["height"]
        for x in range(round(layout["width"] * 2) + 1):
            px = x / 2 * sx; c.create_line(px, 0, px, height, fill=LINE if x % 4 == 0 else "#16202C")
        for y in range(round(layout["height"] * 2) + 1):
            py = y / 2 * sy; c.create_line(0, py, width, py, fill=LINE if y % 4 == 0 else "#16202C")
        for wall in layout["walls"]:
            selected = self.selected == ("wall", wall["id"])
            c.create_line(wall["x1"]*sx, wall["y1"]*sy, wall["x2"]*sx, wall["y2"]*sy, fill=BLUE if selected else "#9BA9B8", width=8, capstyle="round")
            c.create_line(wall["x1"]*sx, wall["y1"]*sy, wall["x2"]*sx, wall["y2"]*sy, fill="#D5DCE4", width=2)
        for shelf in layout["shelves"]:
            selected = self.selected == ("shelf", shelf["id"])
            x, y, x2, y2 = shelf["x"]*sx, shelf["y"]*sy, (shelf["x"]+shelf["w"])*sx, (shelf["y"]+shelf["h"])*sy
            c.create_rectangle(x, y, x2, y2, fill="#16293A", outline=BLUE if selected else "#3A6683", width=3 if selected else 2)
            c.create_text((x+x2)/2, (y+y2)/2, text=shelf["label"], fill=TEXT, font=(FONT, 8, "bold"))
            c.create_text((x+x2)/2, y2+10, text=f"{shelf['w']:.1f} × {shelf['h']:.1f} m", fill=DIM, font=(MONO, 7))
        self.marker(layout.get("entrance"), "▽", "ENTRANCE", BLUE, sx, sy)
        self.marker(layout.get("checkout"), "◇", "CHECKOUT", PINK, sx, sy)
        if self.start and self.preview and self.tool in ("wall", "shelf"):
            x1, y1, x2, y2 = self.start["x"]*sx, self.start["y"]*sy, self.preview["x"]*sx, self.preview["y"]*sy
            if self.tool == "wall": c.create_line(x1, y1, x2, y2, fill=BLUE, width=3, dash=(6, 4))
            else: c.create_rectangle(x1, y1, x2, y2, fill="#153245", outline=BLUE, dash=(6, 4))

    def marker(self, point, icon, label, color, sx, sy):
        if not point: return
        x, y = point["x"]*sx, point["y"]*sy
        self.canvas.create_oval(x-14, y-14, x+14, y+14, fill=BG, outline=color, width=2)
        self.canvas.create_text(x, y, text=icon, fill=color, font=(MONO, 13, "bold"))
        self.canvas.create_text(x, y-23, text=label, fill=color, font=(MONO, 7, "bold"))


class CatalogPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        head = self.heading("02 / PRODUCT UNIVERSE", "Catalog sản phẩm", "Category quyết định nhu cầu mục tiêu và kệ NPC sẽ tìm đến.")
        self.button(head, "Nhập CSV", self.import_csv).pack(side="right")
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=42, pady=(0, 28))
        columns = ("id", "name", "category", "shelf", "price")
        self.tree = ttk.Treeview(body, columns=columns, show="headings", selectmode="browse")
        for col, label, width in [("id", "MÃ", 90), ("name", "TÊN SẢN PHẨM", 250), ("category", "CATEGORY", 180), ("shelf", "KỆ", 100), ("price", "GIÁ (₫)", 120)]:
            self.tree.heading(col, text=label); self.tree.column(col, width=width, anchor="e" if col == "price" else "w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.load_selected)
        form = tk.Frame(body, bg=PANEL, padx=14, pady=12)
        form.pack(fill="x", pady=(12, 0))
        self.vars = {key: tk.StringVar() for key in columns}
        for index, (key, label, width) in enumerate([("id", "Mã", 10), ("name", "Tên", 22), ("category", "Category", 18), ("shelf", "Kệ ID", 10), ("price", "Giá", 12)]):
            box = tk.Frame(form, bg=PANEL); box.pack(side="left", padx=(0, 8))
            tk.Label(box, text=label, bg=PANEL, fg=DIM, font=(FONT, 8)).pack(anchor="w")
            tk.Entry(box, textvariable=self.vars[key], width=width, bg=SIDE, fg=TEXT, insertbackground=TEXT, relief="flat", font=(FONT, 9)).pack(ipady=6)
        self.button(form, "Thêm / cập nhật", self.upsert, True).pack(side="left", padx=5, pady=(15, 0))
        self.button(form, "Xóa", self.delete, danger=True).pack(side="left", pady=(15, 0))
        self.refresh()

    def refresh(self):
        if not hasattr(self, "tree"): return
        self.tree.delete(*self.tree.get_children())
        shelves = {s["id"]: s["label"] for s in self.app.layout_data["shelves"]}
        for item in self.app.catalog:
            self.tree.insert("", "end", iid=item["id"], values=(item["id"], item["name"], item["category"], shelves.get(item["shelf"], item["shelf"]), money(item["price"])))

    def load_selected(self, _event=None):
        if not self.tree.selection(): return
        item = next(p for p in self.app.catalog if p["id"] == self.tree.selection()[0])
        for key in self.vars: self.vars[key].set(item[key])

    def upsert(self):
        try: price = float(self.vars["price"].get())
        except ValueError: messagebox.showerror("Dữ liệu không hợp lệ", "Giá phải là số."); return
        item = {"id": self.vars["id"].get().strip() or f"p{len(self.app.catalog)+1:03d}", "name": self.vars["name"].get().strip(),
                "category": self.vars["category"].get().strip(), "shelf": self.vars["shelf"].get().strip(), "price": price}
        if not item["name"] or not item["category"]: messagebox.showerror("Thiếu dữ liệu", "Tên và category là bắt buộc."); return
        existing = next((p for p in self.app.catalog if p["id"] == item["id"]), None)
        if existing: existing.update(item)
        else: self.app.catalog.append(item)
        self.app.persist(); self.refresh()

    def delete(self):
        if self.tree.selection():
            ident = self.tree.selection()[0]; self.app.catalog = [p for p in self.app.catalog if p["id"] != ident]; self.app.persist(); self.refresh()

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path: return
        try:
            with open(path, newline="", encoding="utf-8-sig") as handle:
                rows = list(csv.DictReader(handle))
            self.app.catalog = [{"id": r.get("product_id") or r.get("id") or f"p{i+1:03d}", "name": r.get("name") or f"Sản phẩm {i+1}",
                                 "category": r.get("category") or "other", "shelf": r.get("shelf") or r.get("zone") or "",
                                 "price": float(r.get("price") or 0)} for i, r in enumerate(rows)]
            self.app.persist(); self.refresh()
        except Exception as exc: messagebox.showerror("Không thể nhập CSV", str(exc))


class RunPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.heading("03 / SIMULATION CONTROL", "Cấu hình & chạy", "Mỗi lần chạy sinh một lứa NPC độc lập; không tự học qua các lần chạy.")
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=42, pady=(0, 28))
        config = tk.Frame(main, bg=PANEL, padx=24, pady=20, highlightthickness=1, highlightbackground=LINE)
        config.pack(side="left", fill="y", ipadx=20)
        self.npc = tk.IntVar(value=180); self.duration = tk.IntVar(value=30); self.seed = tk.IntVar(value=42); self.name = tk.StringVar(value="Layout A — baseline"); self.crowd = tk.BooleanVar(value=True)
        self.population_mode = tk.StringVar(value="ga")
        self.manual_rows = []
        tk.Label(config, text="NGUỒN NPC", bg=PANEL, fg=DIM, font=(MONO, 8, "bold")).pack(anchor="w", pady=(0, 5))
        modes = tk.Frame(config, bg=PANEL); modes.pack(fill="x", pady=(0, 8))
        for value, label in (("ga", "Sinh tự động GA"), ("manual", "Nhập thủ công")):
            tk.Radiobutton(modes, text=label, value=value, variable=self.population_mode,
                           command=self.refresh, bg=PANEL, fg=TEXT, selectcolor=SIDE,
                           activebackground=PANEL, activeforeground=TEXT, font=(FONT, 8)).pack(side="left", padx=(0, 8))
        self.manual_button = self.button(config, "Mở bảng input NPC...", self.edit_manual_population)
        self.manual_button.pack(fill="x", pady=(0, 12))
        self.manual_count = tk.Label(config, text="Chưa có NPC thủ công", bg=PANEL, fg=DIM, font=(MONO, 7))
        self.manual_count.pack(anchor="w", pady=(0, 8))
        self.slider(config, "Quần thể NPC", self.npc, 150, 200, 5)
        self.slider(config, "Thời lượng (phút)", self.duration, 5, 60, 5)
        tk.Label(config, text="Tên lần chạy", bg=PANEL, fg=DIM, font=(FONT, 9)).pack(anchor="w", pady=(18, 5))
        tk.Entry(config, textvariable=self.name, width=34, bg=SIDE, fg=TEXT, insertbackground=TEXT, relief="flat", font=(FONT, 10)).pack(fill="x", ipady=7)
        tk.Label(config, text="Random seed", bg=PANEL, fg=DIM, font=(FONT, 9)).pack(anchor="w", pady=(18, 5))
        tk.Entry(config, textvariable=self.seed, bg=SIDE, fg=TEXT, insertbackground=TEXT, relief="flat", font=(MONO, 10)).pack(fill="x", ipady=7)
        tk.Checkbutton(config, text="Tránh va chạm giữa NPC", variable=self.crowd, bg=PANEL, fg=TEXT, selectcolor=SIDE,
                       activebackground=PANEL, activeforeground=TEXT, font=(FONT, 9)).pack(anchor="w", pady=18)
        visual = tk.Frame(main, bg=PANEL, highlightthickness=1, highlightbackground=LINE)
        visual.pack(side="left", fill="both", expand=True, padx=(16, 0))
        tk.Label(visual, text="SPAWN RATE λ(t)  ·  POISSON", bg=PANEL, fg=TEXT, font=(MONO, 9, "bold")).pack(anchor="w", padx=22, pady=(18, 0))
        self.chart = tk.Canvas(visual, height=280, bg=PANEL, highlightthickness=0)
        self.chart.pack(fill="x", padx=16, pady=10)
        self.chart.bind("<Configure>", lambda _e: self.draw_curve())
        origins = tk.Frame(visual, bg=PANEL)
        origins.pack(fill="x", padx=20, pady=16)
        for title, value in [("CATALOG", "80%"), ("THỪA HƯỞNG", "10%"), ("NHU CẦU MA", "6%"), ("DẠO CHƠI", "4%")]:
            box = tk.Frame(origins, bg=PANEL); box.pack(side="left", expand=True, fill="x")
            tk.Label(box, text=title, bg=PANEL, fg=DIM, font=(MONO, 7, "bold")).pack()
            tk.Label(box, text=value, bg=PANEL, fg=TEXT, font=(MONO, 15, "bold")).pack(pady=5)
        self.validation = tk.Label(visual, text="", bg=PANEL, fg=GREEN, font=(MONO, 9))
        self.validation.pack(anchor="w", padx=22, pady=12)
        self.run_button = self.button(visual, "▶  Chạy mô phỏng", self.start_run, True)
        self.run_button.pack(fill="x", padx=22, pady=(4, 10))
        self.progress = ttk.Progressbar(visual, style="Horizontal.TProgressbar", maximum=100)
        self.progress.pack(fill="x", padx=22, pady=(0, 5))
        self.progress_label = tk.Label(visual, text="Sẵn sàng", bg=PANEL, fg=DIM, font=(MONO, 8))
        self.progress_label.pack(anchor="w", padx=22)
        self.events = queue.Queue()
        self.refresh()

    def slider(self, parent, label, variable, start, end, step):
        row = tk.Frame(parent, bg=PANEL); row.pack(fill="x", pady=(4, 0))
        tk.Label(row, text=label, bg=PANEL, fg=DIM, font=(FONT, 9)).pack(side="left")
        tk.Label(row, textvariable=variable, bg=PANEL, fg=BLUE, font=(MONO, 10, "bold")).pack(side="right")
        tk.Scale(parent, from_=start, to=end, resolution=step, orient="horizontal", variable=variable, command=lambda _v: self.draw_curve(),
                 bg=PANEL, fg=DIM, troughcolor=LINE, activebackground=BLUE, highlightthickness=0, showvalue=False).pack(fill="x")

    def refresh(self):
        if not hasattr(self, "validation"): return
        issues = validate(self.app.layout_data, self.app.catalog)
        errors = [text for level, text in issues if level == "error"]
        if self.population_mode.get() == "manual" and not self.manual_rows:
            errors.append("Chưa nhập NPC thủ công")
        self.manual_count.configure(text=f"{len(self.manual_rows)} NPC thủ công" if self.manual_rows else "Chưa có NPC thủ công",
                                    fg=BLUE if self.manual_rows else DIM)
        self.validation.configure(text="✓ Sẵn sàng chạy" if not errors else "! " + " · ".join(errors), fg=GREEN if not errors else AMBER)
        self.run_button.configure(state="normal" if not errors else "disabled")
        self.draw_curve()

    def draw_curve(self):
        if not hasattr(self, "chart"): return
        c = self.chart; c.delete("all"); width, height = max(200, c.winfo_width()), max(180, c.winfo_height())
        pad = 30
        for i in range(5):
            y = pad + i * (height - 2*pad) / 4; c.create_line(pad, y, width-pad, y, fill=LINE)
        points = []
        for i in range(61):
            phase = i/60; rate = max(.3, .55 + 3.4*math.sin(phase*math.pi) + .65*math.sin(phase*math.pi*4+.7))
            points.extend((pad + phase*(width-2*pad), height-pad-rate/4.8*(height-2*pad)))
        if points: c.create_line(*points, fill=BLUE, width=3, smooth=True)
        for i in range(5): c.create_text(pad+i*(width-2*pad)/4, height-12, text=f"{round(self.duration.get()*i/4)}m", fill=DIM, font=(MONO, 7))

    def start_run(self):
        self.run_button.configure(state="disabled"); self.progress["value"] = 2; self.app.core_status.configure(text="Đang chạy"); self.progress_label.configure(text="Đang chuẩn bị quần thể...")
        args = (copy.deepcopy(self.app.layout_data), copy.deepcopy(self.app.catalog), self.npc.get(), self.duration.get(), self.seed.get(), self.crowd.get(), self.name.get(), self.population_mode.get(), copy.deepcopy(self.manual_rows))
        threading.Thread(target=self.worker, args=args, daemon=True).start(); self.after(50, self.poll)

    def worker(self, layout, catalog, n, duration, seed, crowd, name, mode, manual_rows):
        try:
            population = population_from_input(manual_rows) if mode == "manual" else generate_population(catalog, n, seed)
            result = run_simulation(layout, catalog, population, duration, seed, crowd, lambda p, text: self.events.put(("progress", p, text)))
            result["name"] = name.strip() or "Lần chạy mới"
            save_last_result(result)
            self.events.put(("done", result))
        except Exception as exc: self.events.put(("error", str(exc)))

    def edit_manual_population(self):
        dialog = tk.Toplevel(self)
        dialog.title("Manual NPC Input")
        dialog.geometry("1060x560")
        dialog.configure(bg=BG)
        dialog.transient(self.winfo_toplevel())
        tk.Label(dialog, text="NPC INPUT TABLE", bg=BG, fg=BLUE, font=(MONO, 9, "bold")).pack(anchor="w", padx=22, pady=(18, 5))
        tk.Label(dialog, text="Một dòng cho mỗi NPC. Có thể dán trực tiếp dữ liệu CSV từ Excel.",
                 bg=BG, fg=DIM, font=(FONT, 9)).pack(anchor="w", padx=22)
        columns = ["npc_id", "target_category", "need_product", "need_growth", "need_explore", "explore_growth",
                   "attractor", "stability", "dispersion", "recovery", "speed", "dwell", "steadiness"]
        editor = tk.Text(dialog, bg=SIDE, fg=TEXT, insertbackground=TEXT, relief="flat", wrap="none", font=(MONO, 9))
        editor.pack(fill="both", expand=True, padx=22, pady=14)
        output = io.StringIO(); writer = csv.DictWriter(output, fieldnames=columns, lineterminator="\n"); writer.writeheader()
        rows = self.manual_rows or [{"npc_id": "test_001", "target_category": "beverage", "need_product": .8,
                                     "need_growth": .02, "need_explore": .25, "explore_growth": .01,
                                     "attractor": .3, "stability": .65, "dispersion": .4, "recovery": .15,
                                     "speed": 1.3, "dwell": 9, "steadiness": .75}]
        writer.writerows(rows); editor.insert("1.0", output.getvalue())
        status = tk.Label(dialog, text="Các giá trị ngoài phạm vi sẽ được giới hạn tự động.", bg=BG, fg=DIM, font=(MONO, 8))
        status.pack(anchor="w", padx=22)
        actions = tk.Frame(dialog, bg=BG); actions.pack(fill="x", padx=22, pady=16)
        def apply_rows():
            try:
                parsed = list(csv.DictReader(io.StringIO(editor.get("1.0", "end").strip())))
                population_from_input(parsed)
                if not parsed: raise ValueError("Cần ít nhất một dòng NPC.")
                self.manual_rows = parsed
                self.population_mode.set("manual")
                self.refresh(); dialog.destroy()
            except Exception as exc:
                status.configure(text=str(exc), fg=RED)
        self.button(actions, "Áp dụng input", apply_rows, True).pack(side="right")
        self.button(actions, "Hủy", dialog.destroy).pack(side="right", padx=8)

    def poll(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "progress": self.progress["value"] = event[1]*100; self.progress_label.configure(text=event[2])
                elif event[0] == "done":
                    self.app.last_result = event[1]; self.progress["value"] = 100; self.progress_label.configure(text=f"Hoàn tất trong {event[1]['elapsed_ms']} ms"); self.app.core_status.configure(text="Sẵn sàng"); self.run_button.configure(state="normal"); self.app.show_page("results"); return
                elif event[0] == "error": raise RuntimeError(event[1])
        except queue.Empty: self.after(50, self.poll)
        except Exception as exc:
            self.run_button.configure(state="normal"); self.app.core_status.configure(text="Lỗi"); messagebox.showerror("Mô phỏng thất bại", str(exc))


class ResultsPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.replay_time, self.playing, self.speed = 0.0, False, tk.IntVar(value=15)
        head = self.heading("04 / OBSERVATION", "Kết quả & replay", "Dữ liệu quan sát; không xếp hạng hoặc đề xuất layout.")
        self.save_btn = self.button(head, "Lưu vào lịch sử", self.save, True); self.save_btn.pack(side="right")
        self.body = tk.Frame(self, bg=BG); self.body.pack(fill="both", expand=True, padx=42, pady=(0, 25))
        self.refresh()

    def refresh(self):
        if not hasattr(self, "body"): return
        for child in self.body.winfo_children(): child.destroy()
        result = self.app.last_result
        if not result:
            empty = tk.Frame(self.body, bg=BG)
            empty.pack(expand=True)
            tk.Label(empty, text="◎", bg=BG, fg=DIM, font=(DISPLAY, 28)).pack(pady=(0, 12))
            tk.Label(empty, text="Chưa có dữ liệu mô phỏng", bg=BG, fg=TEXT, font=(DISPLAY, 18)).pack()
            tk.Label(empty, text="Hãy hoàn thiện layout và catalog, rồi chạy mô phỏng ở màn 03.",
                     bg=BG, fg=DIM, font=(FONT, 10)).pack(pady=(8, 18))
            self.button(empty, "Đi tới Cấu hình & chạy  →", lambda: self.app.show_page("run"), True).pack()
            self.save_btn.configure(state="disabled"); return
        self.save_btn.configure(state="normal")
        metrics = tk.Frame(self.body, bg=LINE); metrics.pack(fill="x", pady=(0, 14))
        values = [("DOANH THU", money(result["revenue"]), f"{len(result['purchases'])} giao dịch"),
                  ("TỶ LỆ MUA", percent(result["conversion_rate"]), f"Main {percent(result['main_rate'])}"),
                  ("TỔNG KHÁCH", str(result["n"]), f"{result['duration_minutes']} phút"),
                  ("TÌM KHÔNG THẤY", percent(result["missing_rate"]), "Nhu cầu ngoài catalog")]
        for title, value, note in values:
            card = tk.Frame(metrics, bg=PANEL, padx=16, pady=12); card.pack(side="left", fill="both", expand=True, padx=(0, 1))
            tk.Label(card, text=title, bg=PANEL, fg=DIM, font=(MONO, 7, "bold")).pack(anchor="w")
            tk.Label(card, text=value, bg=PANEL, fg=TEXT, font=(MONO, 17, "bold")).pack(anchor="w", pady=4)
            tk.Label(card, text=note, bg=PANEL, fg=DIM, font=(FONT, 7)).pack(anchor="w")
        tabs = ttk.Notebook(self.body); tabs.pack(fill="both", expand=True)
        replay = tk.Frame(tabs, bg=PANEL); heat = tk.Frame(tabs, bg=PANEL); analytics = tk.Frame(tabs, bg=PANEL)
        tabs.add(replay, text="  Replay  "); tabs.add(heat, text="  Heatmap  "); tabs.add(analytics, text="  Phân tích  ")
        self.replay_canvas = tk.Canvas(replay, bg="#090F16", highlightthickness=0)
        self.replay_canvas.pack(fill="both", expand=True)
        self.replay_canvas.bind("<Configure>", lambda _e: self.draw_replay())
        controls = tk.Frame(replay, bg=PANEL, padx=10, pady=8); controls.pack(fill="x")
        self.play_btn = self.button(controls, "▶", self.toggle_play, True); self.play_btn.pack(side="left")
        self.slider = tk.Scale(controls, from_=0, to=result["duration_minutes"]*60, resolution=1, orient="horizontal", command=self.seek,
                               bg=PANEL, fg=DIM, troughcolor=LINE, activebackground=BLUE, highlightthickness=0, showvalue=False)
        self.slider.pack(side="left", fill="x", expand=True, padx=10)
        ttk.Combobox(controls, textvariable=self.speed, values=(5, 15, 30, 60), state="readonly", width=5).pack(side="right")
        self.time_label = tk.Label(controls, text="00:00", bg=PANEL, fg=TEXT, font=(MONO, 10, "bold")); self.time_label.pack(side="right", padx=12)
        heat_canvas = tk.Canvas(heat, bg="#090F16", highlightthickness=0); heat_canvas.pack(fill="both", expand=True)
        heat_canvas.bind("<Configure>", lambda _e, c=heat_canvas: self.draw_heatmap(c))
        analytics_canvas = tk.Canvas(analytics, bg=PANEL, highlightthickness=0); analytics_canvas.pack(fill="both", expand=True)
        analytics_canvas.bind("<Configure>", lambda _e, c=analytics_canvas: self.draw_analytics(c))

    def draw_store(self, canvas, layout):
        canvas.delete("all"); width, height = max(1, canvas.winfo_width()), max(1, canvas.winfo_height()); sx, sy = width/layout["width"], height/layout["height"]
        for x in range(round(layout["width"]*2)+1): canvas.create_line(x/2*sx, 0, x/2*sx, height, fill=LINE if x%4==0 else "#16202C")
        for y in range(round(layout["height"]*2)+1): canvas.create_line(0, y/2*sy, width, y/2*sy, fill=LINE if y%4==0 else "#16202C")
        for wall in layout["walls"]: canvas.create_line(wall["x1"]*sx, wall["y1"]*sy, wall["x2"]*sx, wall["y2"]*sy, fill="#A4B0BE", width=7)
        for shelf in layout["shelves"]:
            x,y,x2,y2=shelf["x"]*sx,shelf["y"]*sy,(shelf["x"]+shelf["w"])*sx,(shelf["y"]+shelf["h"])*sy
            canvas.create_rectangle(x,y,x2,y2,fill="#16293A",outline="#3A6683",width=2);canvas.create_text((x+x2)/2,(y+y2)/2,text=shelf["label"],fill=TEXT,font=(FONT,7,"bold"))
        return sx, sy

    def draw_replay(self):
        if not self.app.last_result or not hasattr(self, "replay_canvas"): return
        result=self.app.last_result;sx,sy=self.draw_store(self.replay_canvas,result["layout"]);colors={"TRANSIT":BLUE,"DWELL":AMBER,"PURCHASED":GREEN,"LEAVING":PINK};active=0
        for agent in result["agents"]:
            point=position_at(agent,self.replay_time)
            if point: active+=1;self.replay_canvas.create_oval(point["x"]*sx-4,point["y"]*sy-4,point["x"]*sx+4,point["y"]*sy+4,fill=colors[point["status"]],outline="")
        minutes,seconds=divmod(int(self.replay_time),60);self.time_label.configure(text=f"{minutes:02d}:{seconds:02d}  ·  {active} NPC")

    def toggle_play(self):
        self.playing=not self.playing;self.play_btn.configure(text="❚❚" if self.playing else "▶")
        if self.playing:self.last_tick=time.perf_counter();self.animate()

    def animate(self):
        if not self.playing:return
        now=time.perf_counter();self.replay_time+=min(.1,now-self.last_tick)*self.speed.get();self.last_tick=now;maximum=self.app.last_result["duration_minutes"]*60
        if self.replay_time>=maximum:self.replay_time=maximum;self.playing=False;self.play_btn.configure(text="▶")
        self.slider.set(self.replay_time);self.draw_replay()
        if self.playing:self.after(33,self.animate)

    def seek(self,value):
        self.replay_time=float(value);self.draw_replay()

    def draw_heatmap(self,canvas):
        result=self.app.last_result
        if not result:return
        sx,sy=self.draw_store(canvas,result["layout"]);maximum=max(result["dwell_by_shelf"].values(),default=1)
        for shelf in result["layout"]["shelves"]:
            q=result["dwell_by_shelf"].get(shelf["id"],0)/maximum;color=f"#{255:02x}{int(185*(1-q)):02x}{int(70*(1-q)):02x}"
            x,y,x2,y2=(shelf["x"]-.12)*sx,(shelf["y"]-.12)*sy,(shelf["x"]+shelf["w"]+.12)*sx,(shelf["y"]+shelf["h"]+.12)*sy
            canvas.create_rectangle(x,y,x2,y2,fill=color,outline="");canvas.create_text((x+x2)/2,(y+y2)/2,text=f"{shelf['label']}\n{result['dwell_by_shelf'][shelf['id']]:.0f}s",fill=BG,font=(MONO,8,"bold"))

    def draw_analytics(self,canvas):
        result=self.app.last_result;canvas.delete("all")
        if not result:return
        width,height=max(200,canvas.winfo_width()),max(200,canvas.winfo_height());left=60;right=width-30;top=50;bottom=height-45
        canvas.create_text(left,22,text="DOANH THU TÍCH LŨY",fill=TEXT,font=(MONO,9,"bold"),anchor="w")
        for i in range(5):y=top+i*(bottom-top)/4;canvas.create_line(left,y,right,y,fill=LINE)
        purchases=sorted(result["purchases"],key=lambda p:p["tick"]);total=0;points=[left,bottom]
        for p in purchases:
            total+=p["price"];x=left+p["tick"]/(result["duration_minutes"]*60)*(right-left);y=bottom-total/max(1,result["revenue"])*(bottom-top);points.extend((x,y))
        if len(points)>2:canvas.create_line(*points,fill=GREEN,width=3)
        canvas.create_text(right,top-12,text=money(result["revenue"]),fill=TEXT,font=(MONO,10,"bold"),anchor="e")
        labels={"catalog_sampled":"Catalog","crossover_inherited":"Thừa hưởng","phantom_mutation":"Nhu cầu ma","no_intent_mutation":"Dạo chơi","manual_input":"Nhập tay"};x0=left
        origins=[(key,value) for key,value in result["origin_counts"].items() if value]
        for i,(key,value) in enumerate(origins):
            x=x0+i*(right-left)/max(1,len(origins));canvas.create_text(x,bottom+25,text=f"{labels.get(key,key)} {value/result['n']*100:.0f}%",fill=DIM,font=(MONO,8),anchor="w")

    def save(self):
        result=self.app.last_result
        if result:run_id=save_history(result.get("name","Lần chạy"),result);messagebox.showinfo("Đã lưu",f"Đã lưu lần chạy #{run_id} vào lịch sử.")


class HistoryPage(Page):
    def __init__(self,parent,app):
        super().__init__(parent,app)
        head=self.heading("05 / RUN ARCHIVE","Lịch sử mô phỏng","Chọn đúng 2 lần chạy để đặt cạnh nhau. Hệ thống không xếp hạng.")
        self.button(head,"Xóa toàn bộ",self.clear,danger=True).pack(side="right")
        body=tk.Frame(self,bg=BG);body.pack(fill="both",expand=True,padx=42,pady=(0,28))
        self.tree=ttk.Treeview(body,columns=("name","date","revenue","conversion","npc","missing"),show="headings",selectmode="extended")
        for col,label,width in [("name","TÊN LẦN CHẠY",240),("date","THỜI GIAN",160),("revenue","DOANH THU",130),("conversion","CHUYỂN ĐỔI",100),("npc","NPC",70),("missing","KHÔNG THẤY",100)]:self.tree.heading(col,text=label);self.tree.column(col,width=width)
        self.tree.pack(fill="both",expand=True);self.tree.bind("<<TreeviewSelect>>",self.compare)
        actions=tk.Frame(body,bg=BG);actions.pack(fill="x",pady=10);self.button(actions,"Xóa dòng đã chọn",self.delete,danger=True).pack(side="right")
        self.compare_label=tk.Label(body,text="",justify="left",bg=PANEL,fg=TEXT,font=(MONO,10),anchor="nw",padx=20,pady=15);self.compare_label.pack(fill="x")
        self.rows=[];self.refresh()

    def refresh(self):
        if not hasattr(self,"tree"):return
        self.rows=list_history();self.tree.delete(*self.tree.get_children())
        for row in self.rows:self.tree.insert("","end",iid=str(row["id"]),values=(row["name"],row["created_at"],money(row["revenue"]),percent(row["conversion_rate"]),row["npc_count"],percent(row["missing_rate"])))
        self.compare_label.configure(text="Chọn 2 lần chạy để so sánh cạnh nhau.")

    def compare(self,_event=None):
        selected=self.tree.selection()
        if len(selected)!=2:self.compare_label.configure(text="Chọn đúng 2 lần chạy để so sánh cạnh nhau.");return
        a,b=[next(r for r in self.rows if r["id"]==int(i)) for i in selected]
        self.compare_label.configure(text=f"CHỈ SỐ                 {a['name']:<24} {b['name']}\n"
                                          f"Doanh thu              {money(a['revenue']):<24} {money(b['revenue'])}\n"
                                          f"Tỷ lệ mua              {percent(a['conversion_rate']):<24} {percent(b['conversion_rate'])}\n"
                                          f"Mua chính              {percent(a['main_rate']):<24} {percent(b['main_rate'])}\n"
                                          f"Mua thêm               {percent(a['impulse_rate']):<24} {percent(b['impulse_rate'])}\n"
                                          f"Tìm không thấy         {percent(a['missing_rate']):<24} {percent(b['missing_rate'])}")

    def delete(self):
        for ident in self.tree.selection():delete_history(int(ident))
        self.refresh()

    def clear(self):
        if messagebox.askyesno("Xóa lịch sử","Xóa toàn bộ các lần chạy đã lưu?"):clear_history();self.refresh()


def clamp(value, low, high):
    return max(low, min(high, value))


if __name__ == "__main__":
    AIsleApp().mainloop()
