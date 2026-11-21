"""Design tokens, chart styling and page CSS.

Brand colour is used for chrome (sidebar, nav, buttons) and never as a data
series. The categorical slots are assigned in fixed order and validated: worst
adjacent pair dE 9.2 under deutan simulation, above the 8 threshold.
"""

# --- brand (chrome only) ---
BRAND = "#13524a"
BRAND_DEEP = "#0d3b35"
BRAND_MID = "#1d6b60"
BRAND_ACCENT = "#5fe3b0"
BRAND_SOFT = "#e7f4f1"

# --- surfaces ---
PAGE = "#eef1f0"
SURFACE = "#ffffff"
BORDER = "#e4e9e8"
GRID = "#eef1f0"
AXIS = "#d6dcdb"

# --- ink ---
INK_PRIMARY = "#0f1c1a"
INK_SECONDARY = "#4b5a58"
INK_MUTED = "#8a9794"
INK_ON_BRAND = "#eaf5f2"

# --- categorical slots, in order (green-led, validated) ---
SERIES = ["#1baf7a", "#eb6834", "#2a78d6", "#eda100"]

# --- status ---
GOOD = "#0ca30c"
CRITICAL = "#d03b3b"

FONT = '"IBM Plex Sans", system-ui, -apple-system, sans-serif'


def rgba(hex_colour: str, alpha: float) -> str:
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def base_layout(title: str | None = None, height: int = 340,
                show_legend: bool = False, margin_top: int = 30) -> dict:
    return dict(
        height=height,
        margin=dict(l=4, r=8, t=margin_top, b=4),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family=FONT, size=12, color=INK_SECONDARY),
        title=dict(text=title, font=dict(size=14, color=INK_PRIMARY),
                   x=0, xanchor="left"),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=SURFACE, bordercolor=AXIS,
                        font=dict(family=FONT, size=12, color=INK_PRIMARY)),
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1,
                    font=dict(size=11, color=INK_SECONDARY)),
    )


def style_axes(fig, y_title: str | None = None, zeroline: bool = False):
    fig.update_xaxes(showgrid=False, showline=False, ticks="",
                     tickfont=dict(color=INK_MUTED, size=11))
    fig.update_yaxes(showgrid=True, gridcolor=GRID, gridwidth=1,
                     zeroline=zeroline, zerolinecolor=AXIS, zerolinewidth=1,
                     showline=False, ticks="",
                     tickfont=dict(color=INK_MUTED, size=11),
                     title=dict(text=y_title,
                                font=dict(size=11, color=INK_MUTED))
                          if y_title else None)
    return fig


def sparkline(x, y, colour: str = SERIES[0]):
    import plotly.graph_objects as go
    fig = go.Figure(go.Scatter(
        x=list(x), y=list(y), mode="lines",
        line=dict(color=colour, width=2, shape="spline", smoothing=0.6),
        fill="tozeroy", fillcolor=rgba(colour, 0.14),
        hoverinfo="skip",
    ))
    fig.update_layout(
        height=52, margin=dict(l=0, r=0, t=6, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
    )
    return fig


CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

/* 4-point spacing grid: every value below is a multiple of 4px. */

html, body, .stApp, [class*="css"] {{ font-family: {FONT}; }}

/* ===== canvas ===== */
.stApp {{ background: {PAGE}; }}
.block-container {{ padding: 24px 32px 48px 24px; max-width: 1560px; }}
#MainMenu, footer {{ visibility: hidden; }}

/* Leave Streamlit's header alone apart from its background. It renders the
   control that re-opens a collapsed sidebar, and anything that changes its
   height or visibility takes that control with it. */
header[data-testid="stHeader"] {{ background: transparent; }}

/* The re-open button, made obvious rather than a faint grey chevron. */
div[data-testid="stSidebarCollapsedControl"] button,
div[data-testid="collapsedControl"] button {{
    background: {BRAND_DEEP};
    border: none;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(15,28,26,0.20);
}}
div[data-testid="stSidebarCollapsedControl"] button svg,
div[data-testid="collapsedControl"] button svg,
div[data-testid="stSidebarCollapsedControl"] button path,
div[data-testid="collapsedControl"] button path {{
    fill: #ffffff;
    color: #ffffff;
    stroke: #ffffff;
}}

/* ===== sidebar ===== */
section[data-testid="stSidebar"] {{
    background: {BRAND_DEEP}; border-right: none;
}}
section[data-testid="stSidebar"] > div {{ padding-top: 0; }}
section[data-testid="stSidebar"] * {{ color: {INK_ON_BRAND}; }}

.brand {{
    display: flex; align-items: center; gap: 12px;
    padding: 4px 4px 20px 4px;
    border-bottom: 1px solid rgba(255,255,255,0.09);
    margin-bottom: 16px;
}}
.brand .mark {{
    width: 36px; height: 36px; border-radius: 8px;
    background: {BRAND_ACCENT}; color: {BRAND_DEEP};
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 16px; flex-shrink: 0;
}}
.brand .name {{ font-weight: 600; font-size: 15px; line-height: 1.2; }}
.brand .sub {{ font-size: 12px; color: rgba(234,245,242,0.55); margin-top: 2px; }}

/* nav rows: compact radio list with the circle removed */
section[data-testid="stSidebar"] div[role="radiogroup"] {{ gap: 4px; }}
section[data-testid="stSidebar"] div[role="radiogroup"] > label {{
    width: 100%; padding: 8px 12px; border-radius: 8px; margin: 0;
    cursor: pointer; transition: background 0.12s ease; background: transparent;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {{
    background: rgba(255,255,255,0.07);
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {{
    background: {BRAND_ACCENT};
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) * {{
    color: {BRAND_DEEP} !important; font-weight: 600;
}}

/* Kill the radio circle, whichever way the markup nests it. Streamlit has
   moved this element between releases, so every plausible position is
   covered rather than relying on one. */
section[data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] {{
    display: none !important;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:has(input[type="radio"]) {{
    display: none !important;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child:not([data-testid="stMarkdownContainer"]) {{
    display: none !important;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label > div[data-baseweb="radio"] > div:first-child {{
    display: none !important;
}}

section[data-testid="stSidebar"] div[role="radiogroup"] p {{
    font-size: 14px; font-weight: 500; margin: 0;
    display: flex; align-items: center; gap: 12px;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] p::before {{
    content: ""; width: 18px; height: 18px; flex-shrink: 0;
    background-repeat: no-repeat; background-position: center;
    background-size: 18px 18px;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(1) p::before {{
    background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2523b9d4ce%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Crect%20x%3D%223%22%20y%3D%223%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221.5%22%2F%3E%3Crect%20x%3D%2214%22%20y%3D%223%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221.5%22%2F%3E%3Crect%20x%3D%2214%22%20y%3D%2214%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221.5%22%2F%3E%3Crect%20x%3D%223%22%20y%3D%2214%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221.5%22%2F%3E%3C%2Fsvg%3E");
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(1):has(input:checked) p::before {{
    background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%25230d3b35%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Crect%20x%3D%223%22%20y%3D%223%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221.5%22%2F%3E%3Crect%20x%3D%2214%22%20y%3D%223%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221.5%22%2F%3E%3Crect%20x%3D%2214%22%20y%3D%2214%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221.5%22%2F%3E%3Crect%20x%3D%223%22%20y%3D%2214%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221.5%22%2F%3E%3C%2Fsvg%3E");
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(2) p::before {{
    background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2523b9d4ce%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M3%2016.5l5.5-5.5%204%204L21%206%22%2F%3E%3Cpath%20d%3D%22M15.5%206H21v5.5%22%2F%3E%3C%2Fsvg%3E");
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(2):has(input:checked) p::before {{
    background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%25230d3b35%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M3%2016.5l5.5-5.5%204%204L21%206%22%2F%3E%3Cpath%20d%3D%22M15.5%206H21v5.5%22%2F%3E%3C%2Fsvg%3E");
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(3) p::before {{
    background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2523b9d4ce%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M3%2021h18%22%2F%3E%3Cpath%20d%3D%22M6%2021V12%22%2F%3E%3Cpath%20d%3D%22M12%2021V5%22%2F%3E%3Cpath%20d%3D%22M18%2021v-6%22%2F%3E%3C%2Fsvg%3E");
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(3):has(input:checked) p::before {{
    background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%25230d3b35%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M3%2021h18%22%2F%3E%3Cpath%20d%3D%22M6%2021V12%22%2F%3E%3Cpath%20d%3D%22M12%2021V5%22%2F%3E%3Cpath%20d%3D%22M18%2021v-6%22%2F%3E%3C%2Fsvg%3E");
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(4) p::before {{
    background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2523b9d4ce%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M12%202.8l8.4%204.7L12%2012.2%203.6%207.5z%22%2F%3E%3Cpath%20d%3D%22M3.6%2012.4L12%2017.1l8.4-4.7%22%2F%3E%3Cpath%20d%3D%22M3.6%2016.9L12%2021.6l8.4-4.7%22%2F%3E%3C%2Fsvg%3E");
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(4):has(input:checked) p::before {{
    background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%25230d3b35%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M12%202.8l8.4%204.7L12%2012.2%203.6%207.5z%22%2F%3E%3Cpath%20d%3D%22M3.6%2012.4L12%2017.1l8.4-4.7%22%2F%3E%3Cpath%20d%3D%22M3.6%2016.9L12%2021.6l8.4-4.7%22%2F%3E%3C%2Fsvg%3E");
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(5) p::before {{
    background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2523b9d4ce%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M12%203l7.5%203v5.5c0%204.4-3.1%208.2-7.5%209.5C7.6%2019.7%204.5%2015.9%204.5%2011.5V6z%22%2F%3E%3Cpath%20d%3D%22M9%2012.2l2.2%202.2L15.2%2010%22%2F%3E%3C%2Fsvg%3E");
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(5):has(input:checked) p::before {{
    background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%25230d3b35%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M12%203l7.5%203v5.5c0%204.4-3.1%208.2-7.5%209.5C7.6%2019.7%204.5%2015.9%204.5%2011.5V6z%22%2F%3E%3Cpath%20d%3D%22M9%2012.2l2.2%202.2L15.2%2010%22%2F%3E%3C%2Fsvg%3E");
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(6) p::before {{
    background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2523b9d4ce%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M12%202.8l8.4%204.7L12%2012.2%203.6%207.5z%22%2F%3E%3Cpath%20d%3D%22M3.6%2012.4L12%2017.1l8.4-4.7%22%2F%3E%3Cpath%20d%3D%22M3.6%2016.9L12%2021.6l8.4-4.7%22%2F%3E%3C%2Fsvg%3E");
}}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(6):has(input:checked) p::before {{
    background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%25230d3b35%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M12%202.8l8.4%204.7L12%2012.2%203.6%207.5z%22%2F%3E%3Cpath%20d%3D%22M3.6%2012.4L12%2017.1l8.4-4.7%22%2F%3E%3Cpath%20d%3D%22M3.6%2016.9L12%2021.6l8.4-4.7%22%2F%3E%3C%2Fsvg%3E");
}}

.nav-label {{
    font-size: 12px; color: rgba(234,245,242,0.5); font-weight: 600;
    margin: 20px 0 8px 4px;
}}
section[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,0.09); margin: 16px 0;
}}
.side-card {{
    background: rgba(255,255,255,0.06); border-radius: 8px;
    padding: 12px; margin-top: 8px;
    border: 1px solid rgba(255,255,255,0.08);
}}
.side-card .k {{ font-size: 12px; color: rgba(234,245,242,0.5); }}
.side-card .v {{ font-size: 13px; font-weight: 600; margin-bottom: 8px; }}
.side-card .v:last-child {{ margin-bottom: 0; }}

/* ===== top bar & header ===== */
.topbar {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 16px;
}}
.topbar .crumb {{ font-size: 13px; color: {INK_MUTED}; font-weight: 500; }}
.topbar .stamp {{
    font-size: 12px; color: {INK_MUTED};
    background: {SURFACE}; border: 1px solid {BORDER};
    padding: 4px 12px; border-radius: 8px;
}}
.page-head {{ margin-bottom: 24px; }}
.page-head h1 {{
    font-size: 28px; font-weight: 600; letter-spacing: -0.02em;
    color: {INK_PRIMARY}; margin: 0 0 4px 0;
}}
.page-head p {{
    color: {INK_SECONDARY}; font-size: 14px; margin: 0 0 12px 0;
    max-width: 72ch; line-height: 1.6;
}}
.pill {{
    display: inline-block; background: {SURFACE}; color: {INK_SECONDARY};
    border: 1px solid {BORDER}; font-weight: 500; padding: 4px 12px;
    border-radius: 8px; font-size: 12px; margin-right: 8px;
}}

/* ===== stat cards ===== */
.stat-top {{
    display: flex; align-items: flex-start; justify-content: space-between;
    margin-bottom: 12px;
}}
.tile {{
    width: 36px; height: 36px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
}}
.delta {{
    font-size: 12px; font-weight: 600; padding: 4px 8px;
    border-radius: 999px; white-space: nowrap;
}}
.delta.up {{ background: #e8f6ee; color: #16794a; }}
.delta.down {{ background: #fdecec; color: #b42626; }}
.delta.flat {{ background: {GRID}; color: {INK_MUTED}; }}
.stat-label {{ font-size: 13px; color: {INK_MUTED}; font-weight: 500; }}
.stat-value {{
    font-size: 32px; font-weight: 600; color: {INK_PRIMARY};
    letter-spacing: -0.03em; line-height: 1.25;
    margin: 4px 0 10px 0; padding-bottom: 2px;
}}
.stat-sub {{
    font-size: 12px; color: {INK_MUTED}; margin-top: 0; padding-bottom: 4px;
}}

/* ===== cards ===== */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px;
    padding: 20px;
}}
/* Streamlit nests its own wrappers inside; keep them transparent so the
   white above shows through rather than being overpainted. */
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlock"],
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stElementContainer"] {{
    background: transparent;
}}

/* ===== sections ===== */
.section-title {{
    font-size: 16px; font-weight: 600; color: {INK_PRIMARY};
    margin: 24px 0 4px 0; letter-spacing: -0.01em;
}}
.section-note {{
    color: {INK_SECONDARY}; font-size: 13px; margin: 0 0 16px 0;
    max-width: 86ch; line-height: 1.6;
}}

/* ===== misc ===== */
div[data-testid="stDataFrame"] {{ border-radius: 8px; overflow: hidden; }}
.stDownloadButton button {{
    background: {BRAND}; color: #fff; border: none; border-radius: 8px;
    font-weight: 500; font-size: 13px; padding: 8px 16px;
}}
.foot {{
    color: {INK_MUTED}; font-size: 12px; margin-top: 40px;
    padding-top: 16px; border-top: 1px solid {BORDER};
}}

/* ===== hover definitions ===== */
.tip {{
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    cursor: help;
}}
.tip-mark {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 14px; height: 14px; border-radius: 50%;
    background: {GRID}; color: {INK_MUTED};
    font-size: 9px; font-weight: 700; line-height: 1;
    flex-shrink: 0;
}}
.tip:hover .tip-mark {{ background: {BRAND_SOFT}; color: {BRAND}; }}

.tip-body {{
    visibility: hidden; opacity: 0;
    position: absolute; bottom: calc(100% + 8px); left: 0;
    z-index: 1000; width: 290px;
    background: {INK_PRIMARY}; color: #f2f5f4;
    padding: 12px 14px; border-radius: 10px;
    font-size: 12.5px; font-weight: 400; line-height: 1.5;
    letter-spacing: 0;
    box-shadow: 0 6px 20px rgba(15,28,26,0.26);
    transition: opacity 0.14s ease;
    pointer-events: none;
    white-space: normal; text-align: left;
}}
.tip-body strong {{
    display: block; font-size: 13px; font-weight: 600;
    color: #ffffff; margin-bottom: 2px;
}}
.tip-body em {{
    display: block; font-style: normal; font-size: 11px;
    color: {BRAND_ACCENT}; margin-bottom: 7px; font-weight: 500;
}}
.tip:hover .tip-body {{ visibility: visible; opacity: 1; }}

/* ===== definitions page ===== */
.def-head {{
    display: flex; align-items: baseline; justify-content: space-between;
    gap: 12px; margin-bottom: 10px;
}}
.def-name {{ font-size: 16px; font-weight: 600; color: {INK_PRIMARY}; }}
.def-code {{
    font-size: 11px; color: {BRAND}; background: {BRAND_SOFT};
    padding: 3px 9px; border-radius: 6px; font-weight: 600;
    white-space: nowrap;
}}
.def-row {{ display: flex; gap: 14px; margin-bottom: 10px; }}
.def-key {{
    font-size: 11px; color: {INK_MUTED}; font-weight: 600;
    width: 74px; flex-shrink: 0; padding-top: 1px;
}}
.def-val {{ font-size: 13.5px; color: {INK_SECONDARY}; line-height: 1.6; }}
.def-row.caveat .def-val {{ color: {INK_PRIMARY}; }}
.def-row.caveat .def-key {{ color: #b45309; }}
</style>
"""
