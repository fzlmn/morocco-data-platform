"""Inline SVG icons as CSS data URIs. Real icons, not emoji."""

# Nav icons, in two tints: resting (pale) and active (deep).
NAV = {
    "overview": {
        "rest": "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2523b9d4ce%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Crect%20x%3D%223%22%20y%3D%223%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221.5%22%2F%3E%3Crect%20x%3D%2214%22%20y%3D%223%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221.5%22%2F%3E%3Crect%20x%3D%2214%22%20y%3D%2214%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221.5%22%2F%3E%3Crect%20x%3D%223%22%20y%3D%2214%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221.5%22%2F%3E%3C%2Fsvg%3E",
        "active": "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%25230d3b35%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Crect%20x%3D%223%22%20y%3D%223%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221.5%22%2F%3E%3Crect%20x%3D%2214%22%20y%3D%223%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221.5%22%2F%3E%3Crect%20x%3D%2214%22%20y%3D%2214%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221.5%22%2F%3E%3Crect%20x%3D%223%22%20y%3D%2214%22%20width%3D%227%22%20height%3D%227%22%20rx%3D%221.5%22%2F%3E%3C%2Fsvg%3E",
    },
    "prices": {
        "rest": "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2523b9d4ce%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M3%2016.5l5.5-5.5%204%204L21%206%22%2F%3E%3Cpath%20d%3D%22M15.5%206H21v5.5%22%2F%3E%3C%2Fsvg%3E",
        "active": "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%25230d3b35%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M3%2016.5l5.5-5.5%204%204L21%206%22%2F%3E%3Cpath%20d%3D%22M15.5%206H21v5.5%22%2F%3E%3C%2Fsvg%3E",
    },
    "output": {
        "rest": "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2523b9d4ce%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M3%2021h18%22%2F%3E%3Cpath%20d%3D%22M6%2021V12%22%2F%3E%3Cpath%20d%3D%22M12%2021V5%22%2F%3E%3Cpath%20d%3D%22M18%2021v-6%22%2F%3E%3C%2Fsvg%3E",
        "active": "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%25230d3b35%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M3%2021h18%22%2F%3E%3Cpath%20d%3D%22M6%2021V12%22%2F%3E%3Cpath%20d%3D%22M12%2021V5%22%2F%3E%3Cpath%20d%3D%22M18%2021v-6%22%2F%3E%3C%2Fsvg%3E",
    },
    "quality": {
        "rest": "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2523b9d4ce%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M12%203l7.5%203v5.5c0%204.4-3.1%208.2-7.5%209.5C7.6%2019.7%204.5%2015.9%204.5%2011.5V6z%22%2F%3E%3Cpath%20d%3D%22M9%2012.2l2.2%202.2L15.2%2010%22%2F%3E%3C%2Fsvg%3E",
        "active": "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%25230d3b35%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M12%203l7.5%203v5.5c0%204.4-3.1%208.2-7.5%209.5C7.6%2019.7%204.5%2015.9%204.5%2011.5V6z%22%2F%3E%3Cpath%20d%3D%22M9%2012.2l2.2%202.2L15.2%2010%22%2F%3E%3C%2Fsvg%3E",
    },
    "about": {
        "rest": "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2523b9d4ce%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M12%202.8l8.4%204.7L12%2012.2%203.6%207.5z%22%2F%3E%3Cpath%20d%3D%22M3.6%2012.4L12%2017.1l8.4-4.7%22%2F%3E%3Cpath%20d%3D%22M3.6%2016.9L12%2021.6l8.4-4.7%22%2F%3E%3C%2Fsvg%3E",
        "active": "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%25230d3b35%22%20stroke-width%3D%221.75%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M12%202.8l8.4%204.7L12%2012.2%203.6%207.5z%22%2F%3E%3Cpath%20d%3D%22M3.6%2012.4L12%2017.1l8.4-4.7%22%2F%3E%3Cpath%20d%3D%22M3.6%2016.9L12%2021.6l8.4-4.7%22%2F%3E%3C%2Fsvg%3E",
    },
}

# Stat-card icons, coloured per metric at render time.
def stat_svg(name: str, colour: str, size: int = 19) -> str:
    """Return an inline <svg> string in the given hex colour."""
    raw = _RAW[name].replace('COLOUR', colour)
    return raw.replace('<svg ', f'<svg width="{size}" height="{size}" ')

_RAW = {
    "overview": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"COLOUR\" stroke-width=\"1.75\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"3\" y=\"3\" width=\"7\" height=\"7\" rx=\"1.5\"/><rect x=\"14\" y=\"3\" width=\"7\" height=\"7\" rx=\"1.5\"/><rect x=\"14\" y=\"14\" width=\"7\" height=\"7\" rx=\"1.5\"/><rect x=\"3\" y=\"14\" width=\"7\" height=\"7\" rx=\"1.5\"/></svg>",
    "prices": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"COLOUR\" stroke-width=\"1.75\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M3 16.5l5.5-5.5 4 4L21 6\"/><path d=\"M15.5 6H21v5.5\"/></svg>",
    "output": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"COLOUR\" stroke-width=\"1.75\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M3 21h18\"/><path d=\"M6 21V12\"/><path d=\"M12 21V5\"/><path d=\"M18 21v-6\"/></svg>",
    "quality": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"COLOUR\" stroke-width=\"1.75\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M12 3l7.5 3v5.5c0 4.4-3.1 8.2-7.5 9.5C7.6 19.7 4.5 15.9 4.5 11.5V6z\"/><path d=\"M9 12.2l2.2 2.2L15.2 10\"/></svg>",
    "about": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"COLOUR\" stroke-width=\"1.75\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M12 2.8l8.4 4.7L12 12.2 3.6 7.5z\"/><path d=\"M3.6 12.4L12 17.1l8.4-4.7\"/><path d=\"M3.6 16.9L12 21.6l8.4-4.7\"/></svg>",
}
