"""CLI usage of the API."""

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime

from meteofrance_api import MeteoFranceClient


def _local(iso_utc: str | None, fmt: str = "%Y-%m-%d %H:%M %Z") -> str:
    """Convert a UTC ISO 8601 string to the system's local timezone."""
    if iso_utc is None:
        return "N/A"
    return (
        datetime.fromisoformat(iso_utc.replace("Z", "+00:00"))
        .astimezone()
        .strftime(fmt)
    )


def _resolve_coords(
    client: MeteoFranceClient,
    lat: float | None,
    lon: float | None,
    place: str | None,
) -> tuple[float, float, str]:
    """Return (lat, lon, location_name) from explicit coords or a place search."""
    if lat is not None and lon is not None:
        return lat, lon, f"{lat},{lon}"
    if place:
        results = client.search_places(place)
        if not results:
            print(f"No place found for '{place}'.", file=sys.stderr)
            sys.exit(1)
        p = results[0]
        print(f"Using: {p.name} ({p.latitude}, {p.longitude})", file=sys.stderr)
        return p.latitude, p.longitude, p.name
    print("Provide --lat/--lon or --place.", file=sys.stderr)
    sys.exit(1)


def _out(data: object) -> None:
    """Print data as JSON."""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_places(args: argparse.Namespace) -> None:
    """Search places by name."""
    client = MeteoFranceClient()
    results = client.search_places(args.query)

    if args.json:
        _out([asdict(p) for p in results])
        return

    if not results:
        print("No results.")
        return
    for p in results:
        parts = [p.name, p.country]
        if p.admin:
            parts.append(p.admin)
        if p.postal_code:
            parts.append(p.postal_code)
        print(f"  {', '.join(parts)}  ({p.latitude}, {p.longitude})")


def cmd_forecast(args: argparse.Namespace) -> None:
    """Show current + daily weather forecast."""
    client = MeteoFranceClient()
    lat, lon, _ = _resolve_coords(client, args.lat, args.lon, args.place)
    fc = client.get_forecast(lat, lon, language=args.lang)

    if args.json:
        _out(asdict(fc))
        return

    pos = fc.position
    print(f"Location : {pos.name}, {pos.country}  (alt. {pos.altitude} m, tz {pos.timezone})")

    now = fc.current_forecast
    print(f"\nNow       : {fc.iso_to_locale_time(now.time).strftime('%H:%M')}  "
          f"{now.T}°C  {now.weather_description or ''}  "
          f"wind {now.wind_speed} km/h")

    print("\nDaily forecast:")
    for day in fc.daily_forecast[:5]:
        dt = fc.iso_to_locale_time(day.time).strftime("%a %d %b")
        print(f"  {dt}  {day.T_min}–{day.T_max}°C  {day.daily_weather_description or ''}")


def cmd_rain(args: argparse.Namespace) -> None:
    """Show next-hour rain forecast."""
    client = MeteoFranceClient()
    lat, lon, _ = _resolve_coords(client, args.lat, args.lon, args.place)
    try:
        rain = client.get_rain(lat, lon, language=args.lang)
    except ValueError as e:
        print(f"Rain forecast unavailable: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        data = asdict(rain)
        next_rain = rain.next_rain_date_locale()
        data["next_rain"] = next_rain.isoformat() if next_rain else None
        _out(data)
        return

    pos = rain.position
    print(f"Location  : {pos.name}  (tz {pos.timezone})")
    print(f"Confidence: {rain.confidence}")

    next_rain = rain.next_rain_date_locale()
    if next_rain:
        print(f"Next rain : {next_rain.strftime('%H:%M %Z')}")
    else:
        print("Next rain : none expected in the next hour")

    print("\nForecast:")
    for entry in rain.forecast:
        t = rain.iso_to_locale_time(entry.time).strftime("%H:%M")
        intensity = entry.rain_intensity or 0
        fill = "█" * intensity
        print(f"  {t}  [{fill:<4}]  {entry.rain_intensity_description or ''}")


def cmd_observation(args: argparse.Namespace) -> None:
    """Show current weather observation."""
    client = MeteoFranceClient()
    lat, lon, _ = _resolve_coords(client, args.lat, args.lon, args.place)
    obs = client.get_observation(lat, lon, language=args.lang)

    if args.json:
        _out(asdict(obs))
        return

    dt = obs.time_as_datetime
    local_time = dt.astimezone().strftime("%Y-%m-%d %H:%M %Z") if dt else "N/A"
    print(f"Time         : {local_time}")
    print(f"Temperature  : {obs.temperature}°C")
    print(f"Wind         : {obs.wind_speed} km/h  dir {obs.wind_direction}°")
    print(f"Condition    : {obs.weather_description or 'N/A'}")


def cmd_warning(args: argparse.Namespace) -> None:
    """Show weather alerts for a department or domain."""
    client = MeteoFranceClient()
    dictionary = client.get_warning_dictionary(language=args.lang)
    phenomenons = client.get_warning_current_phenomenons(domain=args.domain)

    if args.json:
        _out({
            "domain_id": phenomenons.domain_id,
            "update_time": phenomenons.update_time,
            "end_validity_time": phenomenons.end_validity_time,
            "color_max": phenomenons.get_domain_max_color(),
            "phenomenons": [
                {
                    "id": p.phenomenon_id,
                    "name": dictionary.get_phenomenon_name_by_id(int(p.phenomenon_id)),
                    "color_id": p.phenomenon_max_color_id,
                    "color_name": dictionary.get_color_name_by_id(p.phenomenon_max_color_id),
                }
                for p in phenomenons.phenomenons_max_colors
            ],
        })
        return

    print(f"Domain: {phenomenons.domain_id}  (max level: {phenomenons.get_domain_max_color()})")
    print()
    for p in phenomenons.phenomenons_max_colors:
        name = dictionary.get_phenomenon_name_by_id(int(p.phenomenon_id)) or p.phenomenon_id
        color = (
            dictionary.get_color_name_by_id(p.phenomenon_max_color_id)
            or str(p.phenomenon_max_color_id)
        )
        print(f"  {name:<25} {color}")


def cmd_ephemeris(args: argparse.Namespace) -> None:
    """Show sunrise, sunset, moon phase and saint of the day."""
    client = MeteoFranceClient()
    lat, lon, _ = _resolve_coords(client, args.lat, args.lon, args.place)
    eph = client.get_ephemeris(lat, lon, language=args.lang)

    if args.json:
        _out(asdict(eph))
        return

    print(f"Sunrise  : {_local(eph.sunrise_time, '%H:%M %Z')}")
    print(f"Sunset   : {_local(eph.sunset_time, '%H:%M %Z')}")
    print(f"Moonrise : {_local(eph.moonrise_time, '%H:%M %Z')}")
    print(f"Moonset  : {_local(eph.moonset_time, '%H:%M %Z')}")
    print(f"Moon     : {eph.moon_phase_description or 'N/A'}  ({eph.moon_phase})")
    print(f"Saint    : {eph.saint or 'N/A'}")


def cmd_picture(args: argparse.Namespace) -> None:  # pylint: disable=unused-argument
    """Show picture of the day URL and description."""
    client = MeteoFranceClient()
    pic = client.get_picture_of_the_day()

    if args.json:
        _out(asdict(pic))
        return

    print(f"URL  : {pic.image_url}")
    print(f"\n{pic.description}")


def main() -> None:
    """Entry point for the meteofrance-api CLI."""
    parser = argparse.ArgumentParser(
        prog="meteofrance-api",
        description="Météo-France weather data CLI",
    )
    parser.add_argument("--lang", default="fr", metavar="LANG", help="Language (fr/en, default fr)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # places
    p_places = sub.add_parser("places", help="Search places by name")
    p_places.add_argument("query", help="Place name or postal code")
    p_places.set_defaults(func=cmd_places)

    # forecast
    p_fc = sub.add_parser("forecast", help="Weather forecast for a location")
    p_fc.add_argument("--lat", type=float)
    p_fc.add_argument("--lon", type=float)
    p_fc.add_argument("--place", help="Place name (searched automatically)")
    p_fc.set_defaults(func=cmd_forecast)

    # rain
    p_rain = sub.add_parser("rain", help="Next-hour rain forecast")
    p_rain.add_argument("--lat", type=float)
    p_rain.add_argument("--lon", type=float)
    p_rain.add_argument("--place", help="Place name (searched automatically)")
    p_rain.set_defaults(func=cmd_rain)

    # observation
    p_obs = sub.add_parser("observation", help="Current weather observation")
    p_obs.add_argument("--lat", type=float)
    p_obs.add_argument("--lon", type=float)
    p_obs.add_argument("--place", help="Place name (searched automatically)")
    p_obs.set_defaults(func=cmd_observation)

    # warning
    p_warn = sub.add_parser("warning", help="Weather alerts for a department")
    p_warn.add_argument("domain", help="Department number (e.g. 75) or 'france'")
    p_warn.set_defaults(func=cmd_warning)

    # ephemeris
    p_eph = sub.add_parser("ephemeris", help="Sunrise, sunset and moon phase")
    p_eph.add_argument("--lat", type=float)
    p_eph.add_argument("--lon", type=float)
    p_eph.add_argument("--place", help="Place name (searched automatically)")
    p_eph.set_defaults(func=cmd_ephemeris)

    # picture
    p_pic = sub.add_parser("picture", help="Picture of the day")
    p_pic.set_defaults(func=cmd_picture)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
