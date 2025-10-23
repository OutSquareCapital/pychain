from typing import Any

import pyochain as pc

SAMPLE_DATA = {
    "StrategyInfo": {
        "active": True,
        "config_gen_end_date": {
            "formatted": "2025-10-14T17:00:00Z",
            "nanos": 0,
            "seconds": 1760461200,
        },
        "config_gen_start_date": {
            "formatted": "2025-09-01T08:00:00Z",
            "nanos": 0,
            "seconds": 1756713600,
        },
        "execution_parameters": {"slippage_bps": 1.5},
        "ext_info": {"owner": "quant-team"},
        "fill_time_gaps": False,
        "filters": ["liq>1M", "country==US"],
        "hidden": False,
        "horizon": "intra",
        "id": 101,
        "individual_tags": "core;intraday",
        "inserted": {
            "formatted": "2025-10-10T12:00:00Z",
            "nanos": 0,
            "seconds": 1760097600,
        },
        "instruments": [
            {
                "id": 1,
                "inserted": {
                    "formatted": "2025-09-03T12:00:00Z",
                    "nanos": 0,
                    "seconds": 1756900800,
                },
                "instrument_execution_params": {
                    "chasing_frequency": 0.25,
                    "execution_mode": "TWAP",
                    "trade_size_limit_percent": 0.2,
                },
                "instrument_executor_class": "EquityExecutor",
                "nid": "AAPL.OQ",
                "reuters_parent_code": "AAPL.O",
                "roll_parameters": "std",
            },
            {
                "id": 2,
                "inserted": {
                    "formatted": "2025-09-03T12:00:00Z",
                    "nanos": 0,
                    "seconds": 1756900800,
                },
                "instrument_execution_params": {
                    "chasing_frequency": 0.15,
                    "execution_mode": "VWAP",
                    "trade_size_limit_percent": 0.3,
                },
                "instrument_executor_class": "EquityExecutor",
                "nid": "MSFT.OQ",
                "reuters_parent_code": "MSFT.O",
                "roll_parameters": "std",
            },
        ],
        "intended_risk_weight": 0.75,
        "json_data_subscriptions": {},
        "json_parameters": {"lookback_days": 30},
        "min_sharpe_to_save": 0.5,
        "name": "Alpha US",
        "off_time": {"hour": 22, "minute": 0, "second": 0, "nano": 0},
        "on_time": {"hour": 9, "minute": 0, "second": 0, "nano": 0},
        "replacement_of": 0,
        "short_sim_start": {
            "formatted": "2025-09-15T00:00:00Z",
            "nanos": 0,
            "seconds": 1757894400,
        },
        "sim_end": {
            "formatted": "2025-10-15T00:00:00Z",
            "nanos": 0,
            "seconds": 1760486400,
        },
        "sim_start": {
            "formatted": "2025-09-01T00:00:00Z",
            "nanos": 0,
            "seconds": 1756684800,
        },
        "simulation_priority": 10,
        "strategy_executor_class": "CoreStrategyExecutor",
        "strategy_time_zone": "America/New_York",
        "strategy_type": "EQUITY",
        "tag": "ALPHA_US",
        "trading_level": 1000000.0,
        "use_short_sim_start": True,
    },
    "PNLData": {
        "comment": "october run",
        "dailyPnlMap": {"2025-10-10": 12000, "2025-10-13": -2500, "2025-10-14": 1600},
        "end": {"formatted": "2025-10-15T17:00:00Z", "nanos": 0, "seconds": 1760538000},
        "riskWeight": 0.82,
        "series": {
            "data": {
                "2025-10-10T09:30:00": 1000,
                "2025-10-10T10:00:00": 1500,
                "2025-10-10T10:30:00": -200,
            },
            "end": {
                "formatted": "2025-10-15T17:00:00Z",
                "nanos": 0,
                "seconds": 1760538000,
            },
            "sampling": "30min",
            "start": {
                "formatted": "2025-10-10T09:30:00Z",
                "nanos": 0,
                "seconds": 1760079000,
            },
        },
        "stats": {"avg": 3500, "min": -5000, "max": 8000, "std": 2200},
        "status": "OK",
        "strategyId": 101,
    },
    "StrategyPNL": {
        "id": {
            "101": {
                "comment": "alpha-us",
                "dailyPnlMap": {"2025-10-10": 12000, "2025-10-14": 1600},
                "end": {
                    "formatted": "2025-10-15T17:00:00Z",
                    "nanos": 0,
                    "seconds": 1760538000,
                },
                "riskWeight": 0.82,
                "series": {
                    "data": {
                        "2025-10-10T09:30:00": 1000,
                        "2025-10-10T10:00:00": 1500,
                        "2025-10-10T10:30:00": -200,
                    },
                    "end": {
                        "formatted": "2025-10-15T17:00:00Z",
                        "nanos": 0,
                        "seconds": 1760538000,
                    },
                    "sampling": "30min",
                    "start": {
                        "formatted": "2025-10-10T09:30:00Z",
                        "nanos": 0,
                        "seconds": 1760079000,
                    },
                },
                "stats": {"avg": 3500, "min": -5000, "max": 8000, "std": 2200},
                "status": "OK",
                "strategyId": 101,
            },
            "202": {
                "comment": "beta-eu",
                "dailyPnlMap": {"2025-10-10": -800, "2025-10-14": 900},
                "end": {
                    "formatted": "2025-10-15T17:00:00Z",
                    "nanos": 0,
                    "seconds": 1760538000,
                },
                "riskWeight": 0.55,
                "series": {
                    "data": {"2025-10-10T09:30:00": -300, "2025-10-10T10:00:00": 200},
                    "end": {
                        "formatted": "2025-10-15T17:00:00Z",
                        "nanos": 0,
                        "seconds": 1760538000,
                    },
                    "sampling": "30min",
                    "start": {
                        "formatted": "2025-10-10T09:30:00Z",
                        "nanos": 0,
                        "seconds": 1760079000,
                    },
                },
                "stats": {"avg": 50, "min": -1000, "max": 1200, "std": 500},
                "status": "OK",
                "strategyId": 202,
            },
        }
    },
}


def perf_test_pure(n: int) -> dict[Any, Any]:
    import time

    data = SAMPLE_DATA.copy()
    d2: dict[Any, Any] = {}
    start = time.perf_counter()
    for _ in range(n):
        d2 = {
            "risk_weight": data["PNLData"]["riskWeight"],
            "trade_limit": [
                instr["instrument_execution_params"]["trade_size_limit_percent"]
                for instr in data["StrategyInfo"]["instruments"]  # type: ignore[index]
            ],
            "series_dates": [
                tuple(
                    v
                    for instr in data["StrategyPNL"]["id"].values()  # type: ignore[index]
                    for v in list(instr["series"]["data"].values())  # type: ignore[index]
                )
                for _ in range(20)
            ][:5],
        }

    end = time.perf_counter()
    print(
        f"{n} selects in {end - start:.2f}s ({n / (end - start):.0f}/s) [pure-python]"
    )
    return d2


def perf_test_frame(n: int):
    import time

    df = pc.Dict(SAMPLE_DATA.copy())
    data = {}
    start = time.perf_counter()
    e_risk = pc.key("PNLData").key("riskWeight").alias("risk_weight")
    trade_limit = (
        pc.key("StrategyInfo")
        .key("instruments")
        .apply(
            lambda lst: pc.Iter(lst)
            .pluck("instrument_execution_params", "trade_size_limit_percent")
            .into(list)
        )
        .alias("trade_limit")
    )
    series_dates_test = (
        pc.key("StrategyPNL")
        .key("id")
        .apply(
            lambda d: pc.Iter(d.values())
            .pluck("series", "data")
            .map(lambda d: d.values())
            .flatten()
            .repeat(20)
            .take(n=5)
            .into(list)
        )
        .alias("series_dates")
    )
    for _ in range(n):
        data = df.select(e_risk, trade_limit, series_dates_test).unwrap()
    end = time.perf_counter()
    print("Dict selects:")
    print(f"{n} selects in {end - start:.2f}s ({n / (end - start):.0f}/s)")
    return data


def perf_test(n: int) -> None:
    """
    Dict win thanks to lazy iterators (4x faster since it doesn't materialize un-needed lists).

    However function call overhead is still significant for small pipelines (same 4x factor in favor of pure python).

    Which all in all is fine since it's for data exploration, not a web backend with low latency requirements.
    """
    d1 = perf_test_frame(n)
    d2 = perf_test_pure(n)
    assert d1 == d2


def main(print_output: bool = False) -> None:
    df = pc.Dict(SAMPLE_DATA)

    # 1) select / expressions
    df1 = df.select(
        pc.key("StrategyPNL").key("id"),
        pc.key("PNLData").key("riskWeight").alias("risk_weight"),
    )
    if print_output:
        df1.pipe(print)

    # 2) update en profondeur
    jf2 = df.select(
        pc.key("StrategyInfo")
        .key("instruments")
        .apply(
            lambda x: pc.Iter(x)
            .pluck("instrument_execution_params", "trade_size_limit_percent")
            .into(list)
        )
    )
    if print_output:
        jf2.pipe(print)


if __name__ == "__main__":
    perf_test(500)
    # LAST TEST:
    # 100000 selects in 0.32s (309539/s)
    # 100000 selects in 0.03s (3151433/s) [pure-python]
    main(False)
