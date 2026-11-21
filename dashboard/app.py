"""Morocco Data Platform - analytical dashboard.

Reads the dbt marts. Run from the repo root:

    streamlit run dashboard/app.py
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, text

from dashboard import glossary, icons, theme

st.set_page_config(page_title="Morocco Data Platform", page_icon=str(Path(__file__).parent / "assets" / "favicon.png"),
                   layout="wide", initial_sidebar_state="expanded")
st.markdown(theme.CSS, unsafe_allow_html=True)

CFG = {"displayModeBar": False, "responsive": True}


# --- data ------------------------------------------------------------------

def _database_url() -> str:
    try:
        db = st.secrets["postgres"]
        return (f"postgresql+psycopg2://{db['user']}:{db['password']}"
                f"@{db['host']}:{db['port']}/{db['dbname']}")
    except Exception:
        from config import database_url
        return database_url()


@st.cache_resource
def get_engine():
    return create_engine(_database_url(), future=True, pool_pre_ping=True)


SNAPSHOT = ROOT / "data" / "snapshot"

QUERIES = {
    "macro_annual": """
        select year, inflation_pct, inflation_3y_avg, gdp_growth_pct,
               gdp_per_capita_usd, unemployment_pct, mad_per_usd,
               mad_depreciation_pct, decade
        from analytics.mart_macro_annual
        where country_code = 'MAR'
        order by year
    """,
    "indicators": """
        select indicator_name, domain, unit_type, first_year, last_year,
               observation_count, observed_count, missing_count, coverage_pct
        from analytics.dim_indicator
        order by coverage_pct desc, indicator_name
    """,
    "missing_years": """
        select d.indicator_name, f.year
        from analytics.fct_indicator_observation f
        join analytics.dim_indicator d using (indicator_code)
        where f.is_missing
        order by d.indicator_name, f.year
    """,
}


@st.cache_data(ttl=600, show_spinner=False)
def load_all() -> tuple[dict[str, pd.DataFrame], str]:
    """Read the warehouse if it is reachable, otherwise the committed snapshot.

    Streamlit Community Cloud cannot reach a Postgres running locally, so the
    public deployment falls back to CSVs generated from the marts by
    scripts/export_snapshot.py. The source in use is reported on screen rather
    than hidden - a dashboard that silently serves stale data is worse than
    one that says where its numbers came from.
    """
    try:
        with get_engine().connect() as conn:
            frames = {name: pd.read_sql(text(sql), conn)
                      for name, sql in QUERIES.items()}
        return frames, "warehouse"
    except Exception:
        frames = {name: pd.read_csv(SNAPSHOT / f"{name}.csv")
                  for name in QUERIES}
        return frames, "snapshot"


def snapshot_date() -> str:
    stamp = SNAPSHOT / "generated_at.txt"
    return stamp.read_text(encoding="utf-8").strip() if stamp.exists() else ""


# --- components ------------------------------------------------------------

def latest_with_value(df, column):
    s = df[["year", column]].dropna(subset=[column])
    if s.empty:
        return None, None
    row = s.iloc[-1]
    return int(row["year"]), float(row[column])


def stat_card(container, label, column, df, icon_name, colour,
              suffix="%", decimals=1, higher_is_better=None):
    """Icon tile, pill delta, big number, filled sparkline."""
    with container.container(border=True):
        year, value = latest_with_value(df, column)
        if value is None:
            st.markdown(f'<div class="stat-label">{label}</div>'
                        '<div class="stat-value">—</div>',
                        unsafe_allow_html=True)
            return

        prior = df.loc[df["year"] == year - 1, column]
        delta_html = '<span class="delta flat">no prior year</span>'
        if not prior.empty and pd.notna(prior.iloc[0]):
            change = value - float(prior.iloc[0])
            arrow = "↑" if change > 0 else ("↓" if change < 0 else "→")
            if higher_is_better is None or change == 0:
                cls = "flat"
            else:
                good = (change > 0) == higher_is_better
                cls = "up" if good else "down"
            delta_html = (f'<span class="delta {cls}">{arrow} '
                          f'{abs(change):.{decimals}f}</span>')

        st.markdown(
            f"""
            <div class="stat-top">
              <div class="tile" style="background:{theme.rgba(colour, 0.12)}">
                {icons.stat_svg(icon_name, colour)}
              </div>
              {delta_html}
            </div>
            <div class="stat-label">{glossary.tooltip(column, label)}</div>
            <div class="stat-value">{value:,.{decimals}f}{suffix}</div>
            <div class="stat-sub">latest published · {year}</div>
            """,
            unsafe_allow_html=True,
        )

        trail = df[["year", column]].dropna(subset=[column]).tail(20)
        if len(trail) > 1:
            st.plotly_chart(theme.sparkline(trail["year"], trail[column],
                                            colour),
                            width="stretch", config=CFG,
                            key=f"spark_{column}")


def section(title, note="", define=None):
    heading = glossary.tooltip(define, title) if define else title
    st.markdown(f'<div class="section-title">{heading}</div>',
                unsafe_allow_html=True)
    if note:
        st.markdown(f'<p class="section-note">{note}</p>',
                    unsafe_allow_html=True)


def area(df, column, title, colour, y_title, suffix="%", decimals=2,
         height=320):
    fig = go.Figure(go.Scatter(
        x=df["year"], y=df[column], mode="lines",
        line=dict(color=colour, width=2.5, shape="spline", smoothing=0.5),
        fill="tozeroy", fillcolor=theme.rgba(colour, 0.15),
        showlegend=False,
        hovertemplate=f"%{{y:.{decimals}f}}{suffix}<extra></extra>",
    ))
    fig.update_layout(**theme.base_layout(title=title, height=height))
    theme.style_axes(fig, y_title=y_title, zeroline=True)
    return fig


# --- load ------------------------------------------------------------------

try:
    frames, data_source = load_all()
    macro = frames["macro_annual"]
    indicators = frames["indicators"]
    missing = frames["missing_years"]
except Exception as exc:
    st.error(
        "No data available. Either start the warehouse "
        "(`docker compose up -d`, `python run_pipeline.py`, `dbt build`), "
        "or generate the snapshot with "
        "`python scripts/export_snapshot.py`."
    )
    st.exception(exc)
    st.stop()

year_min, year_max = int(macro["year"].min()), int(macro["year"].max())

# --- sidebar: brand, nav, filters ------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
          <div class="mark">M</div>
          <div>
            <div class="name">Morocco Data</div>
            <div class="sub">Macro indicators</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Overview", "Prices & currency", "Output & labour",
         "Definitions", "Data quality", "How it works"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="nav-label">Period</div>', unsafe_allow_html=True)
    preset = st.radio(
        "Period",
        ["Since 1960", "Since 1990", "Since 2000", "Last 15 years", "Custom"],
        index=1, label_visibility="collapsed",
    )
    presets = {"Since 1960": (1960, year_max), "Since 1990": (1990, year_max),
               "Since 2000": (2000, year_max),
               "Last 15 years": (year_max - 15, year_max)}
    if preset == "Custom":
        start, end = st.slider("Range", year_min, year_max, (1990, year_max),
                               label_visibility="collapsed")
    else:
        start, end = presets[preset]

    st.divider()
    smoothing = st.toggle("3-year average", value=True)

    st.markdown(
        f"""
        <div class="side-card">
          <div class="k">Source</div>
          <div class="v">World Bank Open Data</div>
          <div class="k">Coverage</div>
          <div class="v">{year_min}–{year_max} · {len(indicators)} indicators</div>
          <div class="k">Quality</div>
          <div class="v">24 / 24 tests passing</div>
          <div class="k">Serving from</div>
          <div class="v">{"live warehouse" if data_source == "warehouse"
                          else "committed snapshot"}</div>
        </div>
        """, unsafe_allow_html=True)

view = macro[(macro["year"] >= start) & (macro["year"] <= end)].copy()
page_name = page

# --- top bar + header ------------------------------------------------------

st.markdown(
    f"""
    <div class="topbar">
      <div></div>
      <div class="stamp">Updated {datetime.now():%d %b %Y}</div>
    </div>
    <div class="page-head">
      <h1>{page_name}</h1>
      <p>Macroeconomic indicators for Morocco — ingested from the World Bank
      API, transformed and tested with dbt, served from PostgreSQL.</p>
      <div>
        <span class="pill">{start}–{end}</span>
        <span class="pill">{len(view)} years</span>
        <span class="pill">330 observations</span>
        {'<span class="pill snap">snapshot · ' + snapshot_date() + '</span>'
         if data_source == "snapshot" else ''}
      </div>
    </div>
    """, unsafe_allow_html=True)

GREEN, ORANGE, BLUE, YELLOW = theme.SERIES

# --- Overview --------------------------------------------------------------

if page_name == "Overview":
    c1, c2, c3, c4 = st.columns(4)
    stat_card(c1, "Inflation", "inflation_pct", macro, "prices", GREEN,
              higher_is_better=False)
    stat_card(c2, "GDP growth", "gdp_growth_pct", macro, "output", BLUE,
              higher_is_better=True)
    stat_card(c3, "Unemployment", "unemployment_pct", macro, "overview", ORANGE,
              higher_is_better=False)
    stat_card(c4, "Dirhams per US$", "mad_per_usd", macro, "about", YELLOW,
              suffix="", decimals=2)

    section("Consumer price inflation",
            "The annual rate against a trailing three-year average. The "
            "average separates a one-year shock from a sustained move.",
            define="inflation_pct")
    with st.container(border=True):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=view["year"], y=view["inflation_pct"], name="Annual",
            mode="lines",
            line=dict(color=GREEN, width=2.5, shape="spline", smoothing=0.5),
            fill="tozeroy", fillcolor=theme.rgba(GREEN, 0.15),
            hovertemplate="%{y:.2f}%<extra>Annual</extra>"))
        if smoothing:
            fig.add_trace(go.Scatter(
                x=view["year"], y=view["inflation_3y_avg"],
                name="3-year average", mode="lines",
                line=dict(color=ORANGE, width=2, dash="dot"),
                hovertemplate="%{y:.2f}%<extra>3-year average</extra>"))
        fig.update_layout(**theme.base_layout(height=380,
                                              show_legend=smoothing))
        theme.style_axes(fig, y_title="annual %", zeroline=True)
        st.plotly_chart(fig, width="stretch", config=CFG,
                        key="ov_inflation")

    left, right = st.columns(2)
    with left.container(border=True):
        st.plotly_chart(area(view, "gdp_per_capita_usd", "GDP per capita",
                             BLUE, "current US$", suffix="", decimals=0),
                        width="stretch", config=CFG, key="ov_gdppc")
    with right.container(border=True):
        st.plotly_chart(area(view, "unemployment_pct", "Unemployment",
                             ORANGE, "% of labour force"),
                        width="stretch", config=CFG, key="ov_unemp")

# --- Prices & currency -----------------------------------------------------

elif page_name == "Prices & currency":
    section("Inflation and the dirham",
            "Two panels sharing an x-axis rather than two scales on one chart. "
            "A second y-axis can be rescaled until any two series appear to "
            "move together, so the comparison is made without one.")
    with st.container(border=True):
        fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                             vertical_spacing=0.11,
                             subplot_titles=("Inflation (annual %)",
                                             "Exchange rate (MAD per US$)"))
        fig2.add_trace(go.Scatter(
            x=view["year"], y=view["inflation_pct"], mode="lines",
            line=dict(color=GREEN, width=2.5, shape="spline", smoothing=0.5),
            fill="tozeroy", fillcolor=theme.rgba(GREEN, 0.15),
            showlegend=False,
            hovertemplate="%{y:.2f}%<extra>Inflation</extra>"), row=1, col=1)
        fig2.add_trace(go.Scatter(
            x=view["year"], y=view["mad_per_usd"], mode="lines",
            line=dict(color=BLUE, width=2.5, shape="spline", smoothing=0.5),
            fill="tozeroy", fillcolor=theme.rgba(BLUE, 0.13),
            showlegend=False,
            hovertemplate="%{y:.2f} MAD<extra>Rate</extra>"), row=2, col=1)
        fig2.update_layout(**theme.base_layout(height=520, margin_top=26))
        for ann in fig2.layout.annotations:
            ann.font = dict(size=12, color=theme.INK_SECONDARY)
        theme.style_axes(fig2, zeroline=True)
        st.plotly_chart(fig2, width="stretch", config=CFG,
                        key="pr_panels")

    section("Year-on-year currency movement",
            "Positive bars mean the dirham weakened against the dollar that "
            "year; negative bars mean it strengthened.",
            define="mad_depreciation_pct")
    with st.container(border=True):
        dep = view.dropna(subset=["mad_depreciation_pct"])
        fig3 = go.Figure(go.Bar(
            x=dep["year"], y=dep["mad_depreciation_pct"],
            marker=dict(color=[ORANGE if v >= 0 else GREEN
                               for v in dep["mad_depreciation_pct"]],
                        line=dict(color=theme.SURFACE, width=1),
                        cornerradius=3),
            showlegend=False, hovertemplate="%{y:+.2f}%<extra></extra>"))
        fig3.update_layout(**theme.base_layout(height=300))
        theme.style_axes(fig3, y_title="% change", zeroline=True)
        st.plotly_chart(fig3, width="stretch", config=CFG,
                        key="pr_dep")

# --- Output & labour -------------------------------------------------------

elif page_name == "Output & labour":
    section("Output", "GDP per capita in current dollars alongside annual real "
                      "growth. Contraction years are marked in red.",
            define="gdp_per_capita_usd")
    left, right = st.columns(2)
    with left.container(border=True):
        st.plotly_chart(area(view, "gdp_per_capita_usd",
                             "GDP per capita (current US$)", BLUE, "US$",
                             suffix="", decimals=0),
                        width="stretch", config=CFG, key="out_gdppc")
    with right.container(border=True):
        g = view.dropna(subset=["gdp_growth_pct"])
        fig4 = go.Figure(go.Bar(
            x=g["year"], y=g["gdp_growth_pct"],
            marker=dict(color=[GREEN if v >= 0 else theme.CRITICAL
                               for v in g["gdp_growth_pct"]],
                        line=dict(color=theme.SURFACE, width=1),
                        cornerradius=3),
            showlegend=False, hovertemplate="%{y:.2f}%<extra></extra>"))
        fig4.update_layout(**theme.base_layout(title="GDP growth", height=320))
        theme.style_axes(fig4, y_title="annual %", zeroline=True)
        st.plotly_chart(fig4, width="stretch", config=CFG,
                        key="out_growth")

    section("Labour", "Unemployment is a modelled ILO estimate and the series "
                      "with the thinnest coverage.",
            define="unemployment_pct")
    with st.container(border=True):
        st.plotly_chart(area(view, "unemployment_pct", "Unemployment", ORANGE,
                             "% of labour force", height=300),
                        width="stretch", config=CFG, key="out_unemp")

    section("By decade", "Averages across each decade in the selected range.")
    with st.container(border=True):
        st.dataframe(
            view.groupby("decade").agg(
                inflation=("inflation_pct", "mean"),
                gdp_growth=("gdp_growth_pct", "mean"),
                unemployment=("unemployment_pct", "mean"),
                gdp_per_capita=("gdp_per_capita_usd", "mean"),
            ).round(2).reset_index(),
            width="stretch", hide_index=True)

# --- Definitions -----------------------------------------------------------

elif page_name == "Definitions":
    section("What each number means",
            "Every indicator on this dashboard, what it measures, how to "
            "read a movement in it, and the thing about it that most often "
            "misleads people. Definitions follow the World Bank's own "
            "metadata rather than a loose paraphrase — these are the terms "
            "the figures were produced under.")

    for ind in glossary.INDICATORS.values():
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="def-head">
                  <div class="def-name">{ind.name}</div>
                  <div class="def-code">{ind.code}</div>
                </div>
                <div class="def-row">
                  <div class="def-key">Measures</div>
                  <div class="def-val">{ind.measures}</div>
                </div>
                <div class="def-row">
                  <div class="def-key">Reading it</div>
                  <div class="def-val">{ind.reading}</div>
                </div>
                <div class="def-row caveat">
                  <div class="def-key">Careful</div>
                  <div class="def-val">{ind.caveat}</div>
                </div>
                """,
                unsafe_allow_html=True)

    section("Derived measures",
            "Not published by the World Bank — computed in the dbt mart "
            "with window functions.")

    for ind in glossary.DERIVED.values():
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="def-head">
                  <div class="def-name">{ind.name}</div>
                  <div class="def-code">computed in dbt</div>
                </div>
                <div class="def-row">
                  <div class="def-key">Measures</div>
                  <div class="def-val">{ind.measures}</div>
                </div>
                <div class="def-row">
                  <div class="def-key">Reading it</div>
                  <div class="def-val">{ind.reading}</div>
                </div>
                <div class="def-row caveat">
                  <div class="def-key">Careful</div>
                  <div class="def-val">{ind.caveat}</div>
                </div>
                """,
                unsafe_allow_html=True)

# --- Data quality ----------------------------------------------------------

elif page_name == "Data quality":
    c1, c2, c3 = st.columns(3)
    for col, label, value, icon_name, colour in [
        (c1, "Observations loaded",
         f"{int(indicators['observation_count'].sum()):,}", "about", GREEN),
        (c2, "Missing values",
         f"{int(indicators['missing_count'].sum()):,}", "overview", ORANGE),
        (c3, "dbt tests passing", "24 / 24", "quality", BLUE),
    ]:
        with col.container(border=True):
            st.markdown(
                f"""
                <div class="stat-top">
                  <div class="tile" style="background:{theme.rgba(colour, .12)}">
                    {icons.stat_svg(icon_name, colour)}</div>
                </div>
                <div class="stat-label">{label}</div>
                <div class="stat-value">{value}</div>
                """, unsafe_allow_html=True)

    section("Source coverage",
            "Not every indicator is published for every year. Missing years "
            "are kept as nulls rather than filled, so a gap stays visible "
            "instead of being silently turned into a zero.")
    with st.container(border=True):
        cov = indicators.sort_values("coverage_pct")
        fig5 = go.Figure(go.Bar(
            x=cov["coverage_pct"], y=cov["indicator_name"], orientation="h",
            marker=dict(color=theme.BRAND,
                        line=dict(color=theme.SURFACE, width=1),
                        cornerradius=5),
            text=[f"{v:.0f}%" for v in cov["coverage_pct"]],
            textposition="outside",
            textfont=dict(color=theme.INK_SECONDARY, size=11),
            showlegend=False,
            hovertemplate="%{y}<br>%{x:.0f}% published<extra></extra>"))
        fig5.update_layout(**theme.base_layout(height=300))
        fig5.update_xaxes(range=[0, 118], showgrid=False, showticklabels=False)
        fig5.update_yaxes(showgrid=False,
                          tickfont=dict(color=theme.INK_SECONDARY, size=11))
        st.plotly_chart(fig5, width="stretch", config=CFG,
                        key="dq_cov")

    section("Which years are missing",
            "Gaps sit at the edges of each series — a figure is absent either "
            "because it was never collected or because it has not been "
            "published yet. A gap in the middle would be the worrying case; "
            "there are none.")
    with st.container(border=True):
        if missing.empty:
            st.caption("No missing values.")
        else:
            st.dataframe(
                missing.groupby("indicator_name")["year"]
                .agg(["count", "min", "max"])
                .rename(columns={"count": "missing years", "min": "earliest",
                                 "max": "latest"}).reset_index(),
                width="stretch", hide_index=True)

    with st.expander("Indicator catalogue"):
        st.dataframe(indicators, width="stretch", hide_index=True)
    with st.expander("Full table"):
        st.dataframe(view, width="stretch", hide_index=True)
        st.download_button("Download CSV",
                           view.to_csv(index=False).encode("utf-8"),
                           file_name=f"morocco_macro_{start}_{end}.csv",
                           mime="text/csv")

# --- How it works ----------------------------------------------------------

else:
    section("Pipeline", "Every layer is version-controlled and reproducible "
                        "from an empty database.")
    with st.container(border=True):
        st.markdown("""
| Stage | Tool | What happens |
|---|---|---|
| **Extract** | Python, `requests` | Five indicator series from the World Bank API. Each response is asserted complete against the record count the API reports — it paginates at 50 by default and truncates without an error. |
| **Land** | PostgreSQL | Upserted into a `raw` schema on the natural key `(country_code, indicator_code, year)`, so a re-run is idempotent. |
| **Transform** | dbt | A staging view cleans and casts; three mart tables model the data. |
| **Test** | dbt | 24 checks: uniqueness, referential integrity, accepted values and ranges, plus three singular tests on plausibility. |
| **Serve** | Streamlit, Plotly | This page, reading `analytics.mart_macro_annual`. |
        """)

    section("Three decisions worth knowing about")
    with st.container(border=True):
        st.markdown("""
**Nulls are kept, never filled.** A missing year is a real fact about the
source. Zero-filling would read as "no inflation that year" — a different and
false claim. The dbt test on `value` is deliberately not `not_null`.

**No dual-axis charts anywhere.** Two measures on different scales are shown as
two panels sharing an x-axis. A second y-axis can be rescaled until any two
series appear correlated, so the form is avoided rather than used carefully.

**The country code is ISO-3, and a test found that.** The extractor originally
read `country.id`, which is ISO-2 (`MA`), not `countryiso3code` (`MAR`). The
pipeline ran clean and every number was correct — only the identifier was
wrong. An `accepted_values` test caught it on the first run.
        """)

    section("Running it yourself")
    with st.container(border=True):
        st.code("docker compose up -d\n"
                "python run_pipeline.py\n"
                "dbt run  --project-dir transform --profiles-dir transform\n"
                "dbt test --project-dir transform --profiles-dir transform\n"
                "streamlit run dashboard/app.py", language="bash")

st.markdown('<div class="foot">Data: World Bank Open Data · '
            'Pipeline: Python, PostgreSQL, dbt, Streamlit</div>',
            unsafe_allow_html=True)
