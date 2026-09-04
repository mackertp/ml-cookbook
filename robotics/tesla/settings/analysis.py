import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter


def _prepare_charging_history(charging_history):
    if isinstance(charging_history, dict):
        if "data" in charging_history:
            frame = pd.DataFrame(charging_history["data"])
        else:
            frame = pd.DataFrame(charging_history)
    elif isinstance(charging_history, list):
        frame = pd.DataFrame(charging_history)
    else:
        frame = charging_history.copy()

    if frame.empty:
        raise ValueError("Charging history is empty.")

    timestamp_column = "chargeStartDateTime"
    if timestamp_column not in frame.columns:
        if "chargeStopDateTime" in frame.columns:
            timestamp_column = "chargeStopDateTime"
        else:
            raise ValueError("Charging history does not include a usable charge timestamp column.")

    frame = frame.copy()
    frame[timestamp_column] = pd.to_datetime(frame[timestamp_column], errors="coerce", utc=True)
    frame = frame.dropna(subset=[timestamp_column]).sort_values(timestamp_column).reset_index(drop=True)

    if frame.empty:
        raise ValueError("No valid charging timestamps were found.")

    return frame, timestamp_column


def _extract_charging_fee(row):
    fees = row.get("fees") or []
    for fee in fees:
        if isinstance(fee, dict) and fee.get("feeType") == "CHARGING":
            total_due = fee.get("totalDue")
            return float(total_due) if total_due is not None else 0.0
    return 0.0


def _extract_miles_added(row):
    for column in ("chargeMilesAdded", "milesAdded", "milesAddedThisSession", "chargeMilesAddedThisSession"):
        if column in row:
            value = row.get(column)
            if value is None:
                continue
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
    return 0.0


def _resolve_overall_miles(frame, total_miles=None):
    if total_miles is not None:
        try:
            miles = float(total_miles)
            if miles > 0:
                return miles
        except (TypeError, ValueError):
            pass

    odometer_columns = (
        "odometer",
        "vehicleOdometer",
        "odometerMiles",
        "startOdometer",
        "endOdometer",
    )

    for column in odometer_columns:
        if column in frame.columns:
            numeric_values = pd.to_numeric(frame[column], errors="coerce").dropna()
            if len(numeric_values) > 1:
                miles = float(numeric_values.max() - numeric_values.min())
                if miles > 0:
                    return miles

    # Fallback if odometer values are unavailable in charging history.
    miles_added = frame.apply(_extract_miles_added, axis=1).sum()
    return float(max(miles_added, 0.0))


def _format_thousands(value, _):
    if abs(value) < 500:
        return "0" if value == 0 else f"{value:.0f}"
    thousands = value / 1000
    if abs(thousands - round(thousands)) < 1e-6:
        return f"{int(round(thousands))}K"
    return f"{thousands:.1f}K"


def _style_cost_axis(ax):
    ax.grid(True, which="major", axis="both", linestyle="--", linewidth=0.7, alpha=0.35)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value:,.2f}"))


def plot_charging_history_rolling_sum(charging_history, ax=None, title='All Time Supercharger Spend'):
    """
    Build a styled line plot of cumulative charging spend across charging sessions.
    """
    frame, timestamp_column = _prepare_charging_history(charging_history)
    frame['session_fee'] = frame.apply(_extract_charging_fee, axis=1)
    frame['rolling_total'] = frame['session_fee'].cumsum()
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 5))
    else:
        fig = ax.figure
    ax.plot(
        frame[timestamp_column],
        frame['rolling_total'],
        color='#508766',
        linewidth=2.5,
        marker="o",
        markersize=4,
        label="Charging spend",
    )

    ax.set_title(title, fontsize=14, pad=10)
    ax.set_xlabel('Charge Session Date')
    _style_cost_axis(ax)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax.get_xticklabels(), rotation=35, ha='right')

    fig.tight_layout()
    return fig, ax, frame


def plot_charging_vs_gas_cost(
    charging_history,
    ax=None,
    title="Cost per Mile: Tesla vs Gas",
    mpg=28.0,
    gas_price_per_gallon=3.50,
    total_miles=None,
):
    """
    Compare Tesla and gas as constant cost-per-mile lines across miles driven.

    Tesla rate is total supercharger spend / odometer miles. Gas rate is
    gas price / mpg. Both lines start at (0, $0) and grow at that rate.
    """
    frame, _timestamp_column = _prepare_charging_history(charging_history)
    frame["session_fee"] = frame.apply(_extract_charging_fee, axis=1)
    frame["cumulative_charging_spend"] = frame["session_fee"].cumsum()
    overall_miles = _resolve_overall_miles(frame, total_miles=total_miles)
    if overall_miles <= 0:
        raise ValueError("Need a positive mile total to plot cost against miles driven.")

    tesla_total = float(frame["cumulative_charging_spend"].iloc[-1])
    tesla_cost_per_mile = tesla_total / overall_miles
    gas_cost_per_mile = float(gas_price_per_gallon) / float(mpg)
    estimated_gas_total = overall_miles * gas_cost_per_mile
    frame["estimated_total_miles"] = overall_miles
    frame["estimated_gas_total"] = estimated_gas_total
    frame["tesla_cost_per_mile"] = tesla_cost_per_mile
    frame["gas_cost_per_mile"] = gas_cost_per_mile

    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 5))
    else:
        fig = ax.figure

    ax.plot(
        [0.0, overall_miles],
        [0.0, tesla_total],
        color="#1f77b4",
        linewidth=2.5,
        label=f'Tesla supercharger',
    )
    ax.plot(
        [0.0, overall_miles],
        [0.0, estimated_gas_total],
        color="red",
        linewidth=2.5,
        label=f'Gas @ {mpg:g} mpg',
    )
    ax.set_title(title, fontsize=14, pad=10)
    ax.set_xlabel("Miles driven")
    ax.set_ylabel("Cumulative cost")
    ax.legend(loc="best")
    _style_cost_axis(ax)
    ax.xaxis.set_major_formatter(FuncFormatter(_format_thousands))
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    fig.tight_layout()
    return fig, ax, frame
