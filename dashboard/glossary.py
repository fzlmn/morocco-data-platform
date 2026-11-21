"""Indicator definitions.

What each series measures, how to read it, and what it does not say. Wording
follows the World Bank's own metadata rather than paraphrasing it loosely -
these are the definitions the numbers were produced under.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Indicator:
    code: str
    name: str
    short: str          # one line, for a hover tooltip
    measures: str       # what the number is
    reading: str        # how to interpret a movement
    caveat: str         # the thing that misleads people
    unit: str


INDICATORS: dict[str, Indicator] = {
    "inflation_pct": Indicator(
        code="FP.CPI.TOTL.ZG",
        name="Inflation, consumer prices",
        short="How much the cost of a typical basket of goods rose over "
              "the year, as a percentage.",
        measures=(
            "The annual percentage change in the cost of acquiring a fixed "
            "basket of goods and services bought by the average household. "
            "The basket is held constant, so the figure isolates price "
            "movement rather than changes in what people buy."
        ),
        reading=(
            "2% means the same basket cost 2% more than a year earlier. A "
            "falling rate still means prices rose — just more slowly. Prices "
            "only fall when the figure is negative."
        ),
        caveat=(
            "It is an average across a national basket. Individual households "
            "experience something different depending on what they actually "
            "spend money on; food and energy move far more than the average."
        ),
        unit="annual %",
    ),
    "gdp_growth_pct": Indicator(
        code="NY.GDP.MKTP.KD.ZG",
        name="GDP growth",
        short="How much more the economy produced than the year before, "
              "with inflation already removed.",
        measures=(
            "The annual growth rate of gross domestic product at market "
            "prices, in constant local currency. Constant prices means the "
            "effect of inflation has already been taken out, so this is real "
            "growth in output, not growth in prices."
        ),
        reading=(
            "4% means the economy produced 4% more goods and services than "
            "the previous year. Negative years are contractions."
        ),
        caveat=(
            "Total output, not output per person. An economy can grow while "
            "the average person gets poorer if the population grows faster. "
            "GDP per capita is the series that answers that."
        ),
        unit="annual %",
    ),
    "gdp_per_capita_usd": Indicator(
        code="NY.GDP.PCAP.CD",
        name="GDP per capita",
        short="Total economic output divided by population, in current "
              "US dollars.",
        measures=(
            "Gross domestic product divided by midyear population, converted "
            "to US dollars at official exchange rates. Current dollars means "
            "no adjustment for inflation has been made."
        ),
        reading=(
            "A rough measure of average economic output per person. Useful "
            "for comparing a country against itself over time, and against "
            "other countries at the same moment."
        ),
        caveat=(
            "Because it is converted at the official exchange rate and not "
            "adjusted for inflation, it moves when the dirham moves even if "
            "nothing changed in the real economy. It is also an average, so "
            "it says nothing about distribution."
        ),
        unit="current US$",
    ),
    "unemployment_pct": Indicator(
        code="SL.UEM.TOTL.ZS",
        name="Unemployment",
        short="The share of people who want work and are looking for it, "
              "but do not have it.",
        measures=(
            "The share of the labour force that is without work, available "
            "for work, and actively seeking it. The labour force is people "
            "working plus people looking — not the whole population."
        ),
        reading=(
            "9% means nine of every hundred people in the labour force are "
            "looking for work and have not found it."
        ),
        caveat=(
            "This is a modelled ILO estimate, harmonised across countries "
            "rather than taken straight from national statistics, and it is "
            "the thinnest series here at 53% coverage. It also excludes "
            "people who have stopped looking, so it understates the problem "
            "where discouragement is widespread."
        ),
        unit="% of labour force",
    ),
    "mad_per_usd": Indicator(
        code="PA.NUS.FCRF",
        name="Official exchange rate",
        short="How many Moroccan dirhams one US dollar bought, averaged "
              "over the year.",
        measures=(
            "The official exchange rate determined by national authorities "
            "or in the legally sanctioned exchange market, as an annual "
            "average of daily rates."
        ),
        reading=(
            "A rising number means the dirham weakened — more dirhams are "
            "needed per dollar. A falling number means it strengthened."
        ),
        caveat=(
            "An annual average hides movement within the year, and the "
            "official rate can differ from what is available in practice."
        ),
        unit="MAD per US$",
    ),
}

DERIVED: dict[str, Indicator] = {
    "inflation_3y_avg": Indicator(
        code="derived",
        name="Three-year average inflation",
        short="Inflation averaged over the current year and the two before "
              "it, to separate a shock from a trend.",
        measures=(
            "A trailing three-year mean of the annual inflation rate, "
            "computed with a window function in the dbt mart."
        ),
        reading=(
            "When the annual line spikes above the average, that year was "
            "unusual. When both move together, the change is sustained."
        ),
        caveat=(
            "Trailing, so it lags turning points by design. The first two "
            "years of any range are averaged over fewer observations."
        ),
        unit="annual %",
    ),
    "mad_depreciation_pct": Indicator(
        code="derived",
        name="Dirham movement",
        short="The year-on-year percentage change in the exchange rate; "
              "positive means the dirham weakened.",
        measures=(
            "The percentage change in dirhams per dollar against the "
            "previous year, computed with a lag window function."
        ),
        reading=(
            "Positive bars mean the dirham lost ground against the dollar "
            "that year. Negative bars mean it gained."
        ),
        caveat=(
            "A movement against the dollar specifically. The dirham is "
            "pegged to a basket, so it can weaken against the dollar while "
            "holding steady against the euro."
        ),
        unit="% change",
    ),
}

ALL = {**INDICATORS, **DERIVED}


def tooltip(key: str, label: str | None = None) -> str:
    """An inline label with a hover definition. Returns raw HTML."""
    ind = ALL.get(key)
    if ind is None:
        return label or key
    text = label or ind.name
    return (
        f'<span class="tip">{text}'
        f'<span class="tip-mark">?</span>'
        f'<span class="tip-body">'
        f'<strong>{ind.name}</strong>'
        f'<em>{ind.unit}'
        + (f' · {ind.code}' if ind.code != "derived" else ' · derived in dbt')
        + f'</em>{ind.short}</span></span>'
    )
