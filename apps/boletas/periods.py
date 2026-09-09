import calendar
from dataclasses import dataclass
from datetime import date, datetime, timedelta


@dataclass(frozen=True)
class DateRange:
    start: date
    end: date
    label: str

    @property
    def start_sql(self):
        return self.start.strftime("%Y%m%d")

    @property
    def end_sql(self):
        return self.end.strftime("%Y%m%d")


MONTH_NAMES = (
    "",
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
)

MIN_PAYSLIP_DATE = date(2026, 8, 1)


def visible_period(period):
    """Nunca consultar fechas anteriores al inicio del portal."""
    if period.end < MIN_PAYSLIP_DATE:
        return None
    if period.start < MIN_PAYSLIP_DATE:
        return DateRange(MIN_PAYSLIP_DATE, period.end, '{} al {}'.format(MIN_PAYSLIP_DATE.strftime('%d/%m/%Y'), period.end.strftime('%d/%m/%Y')))
    return period


def portal_month_range(value):
    period = month_range(value)
    if period.start < MIN_PAYSLIP_DATE:
        raise ValueError('Las boletas están disponibles desde agosto de 2026.')
    return period


def month_range(value):
    parsed = datetime.strptime(value, "%Y-%m").date()
    last_day = calendar.monthrange(parsed.year, parsed.month)[1]
    return DateRange(
        start=parsed.replace(day=1),
        end=parsed.replace(day=last_day),
        label="{} {}".format(MONTH_NAMES[parsed.month], parsed.year),
    )


def week_range(value):
    year_text, week_text = value.split("-W", 1)
    year = int(year_text)
    week = int(week_text)
    if week < 1:
        raise ValueError("La semana debe ser mayor que cero.")

    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    first_sunday = year_start + timedelta(days=(6 - year_start.weekday()) % 7)
    if week == 1:
        start = year_start
        end = first_sunday
    else:
        first_monday = first_sunday + timedelta(days=1)
        start = first_monday + timedelta(weeks=week - 2)
        end = min(start + timedelta(days=6), year_end)

    if start > year_end:
        raise ValueError("La semana no existe en el año seleccionado.")
    return DateRange(
        start=start,
        end=end,
        label="Semana {} · {} al {}".format(
            week,
            start.strftime("%d/%m/%Y"),
            end.strftime("%d/%m/%Y"),
        ),
    )


def week_value_for_date(value):
    """Return the calendar-week key used by the payslip filters."""
    year_start = date(value.year, 1, 1)
    first_sunday = year_start + timedelta(days=(6 - year_start.weekday()) % 7)
    if value <= first_sunday:
        week = 1
    else:
        week = 2 + (value - (first_sunday + timedelta(days=1))).days // 7
    return "{}-W{:02d}".format(value.year, week)


def custom_range(start_value, end_value):
    start = datetime.strptime(start_value, "%Y-%m-%d").date()
    end = datetime.strptime(end_value, "%Y-%m-%d").date()
    if start > end:
        raise ValueError("La fecha inicial no puede ser posterior a la fecha final.")
    if (end - start).days > 366:
        raise ValueError("El rango no puede superar 366 días.")
    return DateRange(
        start=start,
        end=end,
        label="{} al {}".format(start.strftime("%d/%m/%Y"), end.strftime("%d/%m/%Y")),
    )


def resolve_date_range(mode, month_value=None, week_value=None, start_value=None, end_value=None):
    today = date.today()
    if mode == "week":
        return week_range(week_value or week_value_for_date(today))
    if mode == "custom":
        return custom_range(start_value or today.isoformat(), end_value or today.isoformat())
    return month_range(month_value or today.strftime("%Y-%m"))
