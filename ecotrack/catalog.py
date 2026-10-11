"""Factores de emisión aproximados (kg CO₂e) para comida, transporte y energía."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CatalogItem:
    id: str
    category: str  # food | transport | energy
    label: str
    keywords: tuple[str, ...]
    # food: per serving; transport: per km; energy: per hour (or per cycle if cycle=True)
    factor: float
    unit: str
    default_qty: float
    is_cycle: bool = False
    icon: str = "•"


# Valores típicos de ACV / DEFRA / Our World in Data, redondeados para un estimado diario.
FOOD: tuple[CatalogItem, ...] = (
    CatalogItem("beef", "food", "Carne de res", ("carne de res", "bistec", "filete", "asado de tira", "carne asada"), 6.5, "porción", 1, icon="🥩"),
    CatalogItem("burger", "food", "Hamburguesa", ("hamburguesas", "hamburguesa", "burger"), 3.4, "unidad", 1, icon="🍔"),
    CatalogItem("lamb", "food", "Cordero", ("cordero",), 5.8, "porción", 1, icon="🍖"),
    CatalogItem("pork", "food", "Cerdo", ("cerdo", "chuleta", "bacon", "tocino", "jamon", "jamón"), 1.9, "porción", 1, icon="🥓"),
    CatalogItem("chicken", "food", "Pollo", ("pollo", "pechuga", "alitas"), 1.1, "porción", 1, icon="🍗"),
    CatalogItem("cheese", "food", "Queso", ("queso",), 1.4, "porción", 1, icon="🧀"),
    CatalogItem("pizza", "food", "Pizza", ("pizzas", "pizza"), 1.8, "porción", 1, icon="🍕"),
    CatalogItem("fish", "food", "Pescado", ("pescado", "salmon", "salmón", "atun", "atún", "sushi"), 1.0, "porción", 1, icon="🐟"),
    CatalogItem("eggs", "food", "Huevos", ("huevos", "huevo"), 0.4, "porción", 1, icon="🥚"),
    CatalogItem("rice", "food", "Arroz", ("arroz",), 0.35, "plato", 1, icon="🍚"),
    CatalogItem("pasta", "food", "Pasta", ("pasta", "espagueti", "spaghetti", "fideos"), 0.4, "plato", 1, icon="🍝"),
    CatalogItem("bread", "food", "Pan", ("pan tostado", "tostadas", "tostada", "pan"), 0.15, "porción", 1, icon="🍞"),
    CatalogItem("milk", "food", "Leche", ("leche",), 0.32, "vaso", 1, icon="🥛"),
    CatalogItem("yogurt", "food", "Yogur", ("yogur", "yogurt"), 0.25, "unidad", 1, icon="🥣"),
    CatalogItem("coffee", "food", "Café", ("cafes", "cafés", "cafe", "café"), 0.28, "taza", 1, icon="☕"),
    CatalogItem("chocolate", "food", "Chocolate", ("chocolate",), 0.7, "porción", 1, icon="🍫"),
    CatalogItem("soda", "food", "Refresco", ("refresco", "gaseosa", "coca cola", "coca-cola", "soda"), 0.22, "lata", 1, icon="🥤"),
    CatalogItem("beer", "food", "Cerveza", ("cervezas", "cerveza"), 0.35, "unidad", 1, icon="🍺"),
    CatalogItem("wine", "food", "Vino", ("vino",), 0.28, "copa", 1, icon="🍷"),
    CatalogItem("salad", "food", "Ensalada / vegetales", ("ensalada", "verduras", "vegetales", "brocoli", "brócoli"), 0.18, "plato", 1, icon="🥗"),
    CatalogItem("lentils", "food", "Lentejas / legumbres", ("lentejas", "frijoles", "alubias", "garbanzos", "legumbres"), 0.2, "plato", 1, icon="🫘"),
    CatalogItem("tofu", "food", "Tofu", ("tofu",), 0.35, "porción", 1, icon="🧈"),
    CatalogItem("fruit", "food", "Fruta", ("frutas", "fruta", "manzana", "platano", "plátano", "banana", "naranja"), 0.12, "pieza", 1, icon="🍎"),
)

TRANSPORT: tuple[CatalogItem, ...] = (
    CatalogItem("plane", "transport", "Avión", ("avion", "avión", "vuelo", "volar", "vole"), 0.255, "km", 900, icon="✈️"),
    CatalogItem("car", "transport", "Auto / coche", ("automovil", "automóvil", "coche", "carro", "auto", "gasolina"), 0.192, "km", 15, icon="🚗"),
    CatalogItem("taxi", "transport", "Taxi / Uber", ("uber", "taxi", "cabify", "diddi"), 0.21, "km", 8, icon="🚕"),
    CatalogItem("moto", "transport", "Moto", ("motocicleta", "moto"), 0.113, "km", 12, icon="🏍️"),
    CatalogItem("bus", "transport", "Autobús", ("autobus", "autobús", "bus", "camion", "camión"), 0.089, "km", 10, icon="🚌"),
    CatalogItem("metro", "transport", "Metro", ("metro", "subway", "subte"), 0.041, "km", 8, icon="🚇"),
    CatalogItem("train", "transport", "Tren", ("tren", "cercanias", "cercanías", "ave"), 0.041, "km", 40, icon="🚆"),
    CatalogItem("bike", "transport", "Bicicleta", ("bicicleta", "bici", "cicla"), 0.0, "km", 8, icon="🚲"),
    CatalogItem("walk", "transport", "Caminar", ("caminando", "caminar", "camine", "caminé", "a pie"), 0.0, "km", 3, icon="🚶"),
)

ENERGY: tuple[CatalogItem, ...] = (
    CatalogItem("ac", "energy", "Aire acondicionado", ("aire acondicionado", "aire acond", "ac ", " a/c"), 0.36, "h", 4, icon="❄️"),
    CatalogItem("heat", "energy", "Calefacción", ("calefaccion", "calefacción", "estufa electrica", "estufa eléctrica"), 0.60, "h", 4, icon="🔥"),
    CatalogItem("oven", "energy", "Horno", ("horno electrico", "horno eléctrico", "horno"), 0.45, "h", 1, icon="🍳"),
    CatalogItem("shower", "energy", "Ducha (agua caliente)", ("ducharme", "duchar", "duche", "duché", "ducha", "banarme", "bañarme", "bano", "baño"), 7.2, "h", 0.15, icon="🚿"),
    CatalogItem("washer", "energy", "Lavadora", ("lavadora", "lavar ropa", "lavado de ropa"), 0.21, "ciclo", 1, True, icon="🧺"),
    CatalogItem("dryer", "energy", "Secadora", ("secadora",), 0.75, "ciclo", 1, True, icon="🌬️"),
    CatalogItem("dishwasher", "energy", "Lavavajillas", ("lavavajillas", "lava vajillas"), 0.36, "ciclo", 1, True, icon="🍽️"),
    CatalogItem("tv", "energy", "Televisión", ("television", "televisión", "televisor", "tele ", "tv"), 0.03, "h", 2, icon="📺"),
    CatalogItem("laptop", "energy", "Portátil", ("portatil", "portátil", "laptop", "notebook"), 0.015, "h", 4, icon="💻"),
    CatalogItem("desktop", "energy", "Computadora de escritorio", ("computadora", "ordenador", "pc"), 0.045, "h", 4, icon="🖥️"),
    CatalogItem("lights", "energy", "Luces", ("luces encendidas", "luces", "bombillas", "lamparas", "lámparas"), 0.018, "h", 5, icon="💡"),
    CatalogItem("microwave", "energy", "Microondas", ("microondas", "micro ondas"), 0.24, "h", 0.15, icon="📡"),
)

ALL_ITEMS: tuple[CatalogItem, ...] = FOOD + TRANSPORT + ENERGY

CATEGORY_LABELS = {
    "food": "Comida",
    "transport": "Transporte",
    "energy": "Energía",
}

CATEGORY_COLORS = {
    "food": "#2e7d4f",
    "transport": "#3d6b8c",
    "energy": "#c9a227",
}

# Meta diaria de ~2 t CO₂e/año ≈ 5.5 kg/día.
DAILY_TARGET_KG = 5.5
DAILY_AVG_KG = 16.0
