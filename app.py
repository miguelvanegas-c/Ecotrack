from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from ecotrack.catalog import CATEGORY_COLORS, CATEGORY_LABELS, DAILY_AVG_KG, DAILY_TARGET_KG
from ecotrack.parser import ParseResult, parse_diary

st.set_page_config(
    page_title="EcoTrack",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(180deg, #f3f8f4 0%, #eef4f0 100%); }
      h1 { letter-spacing: -0.03em; }
      .hint { color: #4a5c52; font-size: 0.95rem; }
      div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #d7e5dc;
        border-radius: 14px;
        padding: 12px 16px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

EXAMPLES = {
    "Día urbano": (
        "Hoy desayuné huevos y café, fui 15 km en auto al trabajo, "
        "almorcé una hamburguesa, usé el aire acondicionado 3 horas "
        "y volví 8 km en metro. Por la noche vi 2 horas de tele."
    ),
    "Día bajo impacto": (
        "Caminé 4 km, desayuné fruta y yogur, almorcé ensalada con lentejas, "
        "trabajé 5 horas en el portátil y me duché 8 minutos."
    ),
    "Viaje": (
        "Tomé un vuelo de 1200 km, comí pollo y arroz en el aeropuerto, "
        "luego 20 km en taxi y usé calefacción 2 horas en el hotel."
    ),
}


def _qty_label(activity) -> str:
    item = activity.item
    qty = activity.quantity
    if item.unit == "h":
        minutes = qty * 60
        if minutes < 90:
            return f"{minutes:.0f} min"
        return f"{qty:.1f} h"
    if qty == int(qty):
        return f"{int(qty)} {item.unit}"
    return f"{qty:.1f} {item.unit}"


def _gauge_message(total: float) -> tuple[str, str]:
    if total <= DAILY_TARGET_KG:
        return "Dentro de la meta diaria (~2 t CO₂e/año).", "normal"
    if total <= DAILY_AVG_KG:
        return "Por encima de la meta, por debajo del promedio típico.", "off"
    return "Por encima del promedio diario habitual en países de alto consumo.", "off"


def render_charts(result: ParseResult) -> None:
    rows = [
        {
            "Actividad": f"{a.item.icon} {a.item.label}",
            "Categoría": CATEGORY_LABELS[a.item.category],
            "category_id": a.item.category,
            "kg": a.kg_co2,
        }
        for a in result.activities
    ]
    df = pd.DataFrame(rows)
    cat = (
        df.groupby(["Categoría", "category_id"], as_index=False)["kg"]
        .sum()
        .sort_values("kg", ascending=False)
    )

    left, right = st.columns(2)
    with left:
        fig_bar = px.bar(
            df.sort_values("kg", ascending=True),
            x="kg",
            y="Actividad",
            color="Categoría",
            color_discrete_map={
                CATEGORY_LABELS[k]: v for k, v in CATEGORY_COLORS.items()
            },
            orientation="h",
            labels={"kg": "kg CO₂e"},
        )
        fig_bar.update_layout(
            title="Emisiones por actividad",
            height=max(320, 48 * len(df) + 80),
            margin=dict(l=10, r=10, t=50, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with right:
        fig_pie = px.pie(
            cat,
            names="Categoría",
            values="kg",
            color="Categoría",
            color_discrete_map={
                CATEGORY_LABELS[k]: v for k, v in CATEGORY_COLORS.items()
            },
            hole=0.55,
        )
        fig_pie.update_layout(
            title="Participación por categoría",
            height=360,
            margin=dict(l=10, r=10, t=50, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[
                dict(
                    text=f"<b>{result.total_kg:.1f}</b><br>kg CO₂e",
                    x=0.5,
                    y=0.5,
                    font_size=16,
                    showarrow=False,
                )
            ],
        )
        st.plotly_chart(fig_pie, use_container_width=True)


def main() -> None:
    st.title("🌿 EcoTrack")
    st.markdown(
        "Escribe en lenguaje natural lo que hiciste hoy: **comida**, **transporte** y **energía**. "
        "EcoTrack detecta las actividades y estima el CO₂ equivalente."
    )

    example_name = st.selectbox("Ejemplos para probar", ["(escribir el mío)"] + list(EXAMPLES))
    default_text = EXAMPLES.get(example_name, "")

    diary = st.text_area(
        "Diario del día",
        value=default_text,
        height=140,
        key=f"diary_{example_name}",
        placeholder="Ej.: Desayuné huevos y café, fui 12 km en auto, almorcé pizza y usé el aire 2 horas...",
    )

    st.caption(
        "El cálculo se actualiza al cambiar el texto. Estimados orientativos (ACV / factores típicos); no sustituyen un inventario formal."
    )

    if not diary.strip():
        st.info("Escribe tu día o elige un ejemplo para ver el estimado de CO₂.")
        return

    result = parse_diary(diary)
    if not result.activities:
        st.warning(
            "No detecté actividades claras. Prueba con palabras como *auto, metro, hamburguesa, pollo, ducha, aire acondicionado* y cantidades (*15 km*, *2 horas*)."
        )
        return

    cats = result.by_category()
    msg, _ = _gauge_message(result.total_kg)
    trees_days = result.total_kg / (21.8 / 365)  # ~21.8 kg CO₂/año por árbol urbano típico

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total estimado", f"{result.total_kg:.1f} kg CO₂e")
    m2.metric("Comida", f"{cats['food']:.1f} kg")
    m3.metric("Transporte", f"{cats['transport']:.1f} kg")
    m4.metric("Energía", f"{cats['energy']:.1f} kg")
    st.caption(f"{msg} Equivale a unos {trees_days:.0f} días de absorción de un árbol adulto.")

    st.progress(min(result.total_kg / DAILY_AVG_KG, 1.0), text=f"Respecto al promedio diario de referencia ({DAILY_AVG_KG:.0f} kg)")

    render_charts(result)

    st.subheader("Detalle detectado")
    table = pd.DataFrame(
        [
            {
                "Categoría": CATEGORY_LABELS[a.item.category],
                "Actividad": f"{a.item.icon} {a.item.label}",
                "Cantidad": _qty_label(a),
                "kg CO₂e": round(a.kg_co2, 2),
                "Nota": "cantidad por defecto" if a.assumed_default else "cantidad leída del texto",
            }
            for a in result.activities
        ]
    )
    st.dataframe(table, use_container_width=True, hide_index=True)

    with st.expander("Cómo se calcula"):
        st.markdown(
            """
- **Comida:** kg CO₂e por porción típica (carne de res es la más intensiva; vegetales y legumbres, las más bajas).
- **Transporte:** factor por km × distancia. Si no hay km, se asume un trayecto cotidiano.
- **Energía:** consumo típico × mix eléctrico de ~0.30 kg CO₂e/kWh (o agua caliente en duchas).
- Las cantidades en el texto (*2 hamburguesas*, *15 km*, *8 minutos*) tienen prioridad sobre los valores por defecto.
            """
        )


if __name__ == "__main__":
    main()
