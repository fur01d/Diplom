import json
import customtkinter as ctk
from tkinter import StringVar
import xml.etree.ElementTree as ET

# Загрузка конфигурации и меток
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

with open("labels.json", "r", encoding="utf-8") as f:
    labels = json.load(f)

with open("value_translation.json", "r", encoding="utf-8") as f:
    value_translation = json.load(f)

# Загрузка регионов и городов
regions = {}
cities_by_region = {}

try:
    tree = ET.parse("Locations.xml")
    root = tree.getroot()
    for region in root.findall("Region"):
        region_name = region.attrib["Name"]
        region_id = region.attrib["Id"]
        regions[region_name] = region_id
        cities = []
        for city in region.findall("City"):
            cities.append((city.attrib["Name"], city.attrib["Id"]))
        cities_by_region[region_name] = cities
except Exception as e:
    print("Ошибка при загрузке Locations.xml:", e)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.geometry("1000x700")
app.title("Фильтры")

# Кэш для всех переменных и виджетов
dropdown_vars = {}     # key: StringVar для OptionMenu
dropdown_widgets = {}  # key: CTkOptionMenu
entry_widgets = {}     # key: CTkEntry

# Сохранение конфигурации
def update_config(key, value):
    config[key] = value
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# Обнуление конфигурации и UI
def reset_config():
    for key in config:
        if isinstance(config[key], list):
            config[key] = []
        else:
            config[key] = None if key not in ("per_page", "page", "fields") else config[key]
    # Сброс всех dropdown
    for key, var in dropdown_vars.items():
        var.set("Не выбрано")
        # Если есть callback у OptionMenu, вызываем его вручную
        widget = dropdown_widgets.get(key)
        if widget and widget.cget("command"):
            widget.cget("command")("Не выбрано")
    # Сброс всех текстовых полей
    for key, entry in entry_widgets.items():
        entry.delete(0, "end")
    # Сброс региона и города
    region_var.set("Не выбрано")
    update_city_dropdown("Не выбрано")
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# Боковая панель для всех параметров
sidebar_full = ctk.CTkScrollableFrame(app, width=350, fg_color="gray15")
sidebar_full.pack(side="left", fill="y", padx=10, pady=10)

header_frame = ctk.CTkFrame(sidebar_full, fg_color="transparent")
header_frame.pack(fill="x", pady=(10, 10))

ctk.CTkLabel(header_frame, text="Фильтры", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=5)
ctk.CTkButton(header_frame, text="Обнулить фильтры", fg_color="red", hover_color="#990000", width=120, command=reset_config).pack(side="left", padx=5)
ctk.CTkButton(header_frame, text="Начать поиск", fg_color="green", hover_color="#007700", width=120).pack(side="left", padx=5)

# Регион и город
region_frame = ctk.CTkFrame(sidebar_full, fg_color="transparent")
region_frame.pack(fill="x", pady=2)
ctk.CTkLabel(region_frame, text="Регион", width=130, anchor="w").pack(side="left", padx=5)

region_names = ["Не выбрано"] + list(regions.keys())
region_var = StringVar(value="Не выбрано")
region_menu = ctk.CTkOptionMenu(region_frame, values=region_names, variable=region_var)
region_menu.pack(fill="x", expand=True)

city_frame = ctk.CTkFrame(sidebar_full, fg_color="transparent")
city_var = StringVar(value="Не выбрано")
city_menu = None

def update_city_dropdown(region_name):
    global city_menu
    for widget in city_frame.winfo_children():
        widget.destroy()
    city_frame.pack_forget()
    city_var.set("Не выбрано")
    if region_name != "Не выбрано" and cities_by_region.get(region_name):
        ctk.CTkLabel(city_frame, text="Город", width=130, anchor="w").pack(side="left", padx=5)
        city_names = ["Не выбрано"] + [city[0] for city in cities_by_region[region_name]]
        def on_city_change(city_name):
            if city_name == "Не выбрано":
                update_config("location", int(regions[region_name]))
            else:
                city_id = next((c[1] for c in cities_by_region[region_name] if c[0] == city_name), None)
                update_config("location", int(city_id) if city_id else None)
        city_menu = ctk.CTkOptionMenu(city_frame, values=city_names, variable=city_var, command=on_city_change)
        city_menu.pack(fill="x", expand=True)
        city_frame.pack(after=region_frame, fill="x", pady=2)
    else:
        update_config("location", int(regions[region_name]) if region_name != "Не выбрано" else None)

region_menu.configure(command=update_city_dropdown)
sidebar_full.after(100, lambda: city_frame.pack_forget())

# Словарь для dropdown полей
dropdown_fields = {
    "fields": ["title", "location", "specialization", "education_level", "total_experience", "gender", "age", "salary"],
    "schedule": ["partial-day", "full-day", "fly-in-fly-out", "flexible", "shift", "remote"],
    "specialization": ["10166", "10167", "10168", "10169", "10170", "10171", "10172", "10173", "10174", "10175", "10180", "10181", "10182", "10183", "10184", "10185", "10186", "10187", "10188", "10189", "10190", "10191", "10192", "10193", "16844", "2804251", "2804250"],
    "business_trip_readiness": ["ready", "never", "sometimes"],
    "relocation_readiness": ["possible", "never"],
    "gender": ["female", "male"],
    "education_level": ["higher", "unfinished-higher", "secondary", "special-secondary"],
    "nationality": ["15973", "15974", "15975", "16020"],
    "driver_licence": ["true", "false"],
    "driver_licence_category": ["a", "b", "be", "c", "ce", "d", "de", "m", "tm", "tb"],
    "driving_experience": ["less-than-three-years", "more-than-three-years"],
    "own_transport": ["false", "car", "cargo-car", "bike", "scooter"],
    "medical_book": ["true", "false"]
}

all_keys = list(labels.keys())

for key in all_keys:
    frame = ctk.CTkFrame(sidebar_full, fg_color="transparent")
    frame.pack(fill="x", pady=2)
    label = labels.get(key, key)
    ctk.CTkLabel(frame, text=label, width=130, anchor="w").pack(side="left", padx=5)
    if key in dropdown_fields:
        readable_values = ["Не выбрано"] + [value_translation.get(key, {}).get(v, v) for v in dropdown_fields[key]]
        reverse_lookup = {"Не выбрано": None}
        for v in dropdown_fields[key]:
            translated = value_translation.get(key, {}).get(v, v)
            reverse_lookup[translated] = v
        current_value = config.get(key)
        if isinstance(current_value, list):
            current_value = current_value[0] if current_value else None
        val_display = value_translation.get(key, {}).get(str(current_value), "Не выбрано")
        var = StringVar(value=val_display)
        def make_callback(k, r_map):
            return lambda val: update_config(k, [r_map[val]] if r_map[val] is not None else None)
        menu = ctk.CTkOptionMenu(frame, values=readable_values, variable=var, command=make_callback(key, reverse_lookup))
        menu.pack(fill="x", expand=True)
        dropdown_vars[key] = var
        dropdown_widgets[key] = menu
    else:
        entry = ctk.CTkEntry(frame)
        entry.insert(0, str(config.get(key) or ""))
        entry.pack(fill="x", expand=True)
        entry.bind("<Return>", lambda e, k=key, ent=entry: update_config(k, ent.get() or None))
        entry_widgets[key] = entry

app.mainloop()