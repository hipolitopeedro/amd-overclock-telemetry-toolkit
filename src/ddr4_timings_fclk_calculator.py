#!/usr/bin/env python3
"""
ddr4_timings_fclk_calculator.py
EN: Calculates true DDR4 (AM4) & DDR5 (AM5) memory latency in nanoseconds (ns),
    compares bandwidth against JEDEC baselines, evaluates AMD Infinity Fabric (FCLK)
    and Memory Controller (UCLK) ratios, and validates secondary timing rules.
PT: Calcula a latência real de memórias DDR4 (AM4) e DDR5 (AM5) em nanosegundos (ns),
    compara largura de banda contra perfis JEDEC, avalia a sincronia do Infinity Fabric (FCLK)
    e controlador (UCLK), e valida regras matemáticas de subtimings.
"""

import argparse


def cycles_to_ns(cycles: int, mts: int) -> float:
    """Converts memory clock cycles into true latency in nanoseconds: ns = (2000 * cycles) / MT/s."""
    return round((2000.0 * cycles) / mts, 2)


def theoretical_bandwidth_gbs(mts: int, channels: int = 2) -> float:
    """Calculates peak theoretical dual-channel bandwidth in GB/s."""
    return round((mts * 8.0 * channels) / 1000.0, 2)


def evaluate_memory_oc(
    gen: str,
    mts: int,
    fclk: int,
    tcl: int,
    trcdrd: int,
    trp: int,
    tras: int,
    trc: int,
    trfc: int,
    trrds: int,
    tfaw: int,
) -> None:
    mclk = mts // 2
    baseline_mts = 2400 if gen == "ddr4" else 4800
    baseline_tcl = 17 if gen == "ddr4" else 40

    base_bw = theoretical_bandwidth_gbs(baseline_mts)
    oc_bw = theoretical_bandwidth_gbs(mts)
    bw_gain_pct = round(((oc_bw - base_bw) / base_bw) * 100.0, 1)

    base_cas_ns = cycles_to_ns(baseline_tcl, baseline_mts)
    oc_cas_ns = cycles_to_ns(tcl, mts)
    trfc_ns = cycles_to_ns(trfc, mts)

    print("==========================================================================")
    print(f"  AMD RYZEN {gen.upper()} TIMINGS, LATENCY & INFINITY FABRIC (FCLK) CALCULATOR")
    print("==========================================================================")
    print(
        f"  JEDEC Baseline     : {gen.upper()}-{baseline_mts} CL{baseline_tcl} "
        f"({base_bw} GB/s | First-Word Latency: {base_cas_ns} ns)"
    )
    print(
        f"  Tuned OC Profile   : {gen.upper()}-{mts} CL{tcl}-{trcdrd}-{trp}-{tras}-{trc} "
        f"({oc_bw} GB/s | +{bw_gain_pct}% Bandwidth)"
    )
    print("--------------------------------------------------------------------------")

    print("\n[1] INFINITY FABRIC (FCLK) & MEMORY CONTROLLER (UCLK) TOPOLOGY")
    print(f"    Memory Clock (MCLK): {mclk} MHz | Infinity Fabric (FCLK): {fclk} MHz")
    if gen == "ddr4":
        if mclk == fclk:
            print("    AM4 Coupled Mode   : [1:1:1 SYNCHRONIZED] Optimal MCLK = UCLK = FCLK operation.")
        else:
            print("    AM4 Coupled Mode   : [DESYNCHRONIZED] Warning: MCLK != FCLK adds ~5-8 ns latency penalty!")
    else:
        uclk_mode = "1:1 (UCLK = MCLK)" if mclk <= 3200 else "1:2 (UCLK = MCLK/2)"
        ideal_fclk = round(mclk * (2.0 / 3.0))
        print(f"    AM5 Controller Mode: {uclk_mode} | Recommended 3:2 FCLK Ratio Target: ~{ideal_fclk} MHz")

    print("\n[2] TRUE TIMING LATENCY IN NANOSECONDS (ns)")
    print(f"    tCL     : {tcl:<4} cycles -> {oc_cas_ns:>6.2f} ns (vs {base_cas_ns:.2f} ns JEDEC)")
    print(f"    tRCDRD  : {trcdrd:<4} cycles -> {cycles_to_ns(trcdrd, mts):>6.2f} ns")
    print(f"    tRP     : {trp:<4} cycles -> {cycles_to_ns(trp, mts):>6.2f} ns")
    print(f"    tRAS    : {tras:<4} cycles -> {cycles_to_ns(tras, mts):>6.2f} ns")
    print(f"    tRC     : {trc:<4} cycles -> {cycles_to_ns(trc, mts):>6.2f} ns")
    print(f"    tRFC    : {trfc:<4} cycles -> {trfc_ns:>6.2f} ns")

    print("\n[3] SUBTIMING FORMULA & STABILITY AUDIT")
    min_tras = tcl + trcdrd
    if tras >= min_tras:
        print(f"    [OK] tRAS ({tras}) >= tCL + tRCDRD ({min_tras})")
    else:
        print(f"    [NOTE] Aggressive tRAS ({tras} < {min_tras}); verify stability with TestMem5 / Y-Cruncher.")

    ideal_trc = trp + tras
    if trc >= ideal_trc:
        print(f"    [OK] tRC ({trc}) >= tRP + tRAS ({ideal_trc})")
    else:
        print(f"    [WARN] tRC ({trc}) < tRP + tRAS ({ideal_trc}); may cause bank cycle errors.")

    ideal_tfaw = 4 * trrds
    if tfaw == ideal_tfaw:
        print(f"    [OK] tFAW ({tfaw}) == 4 x tRRDS ({trrds}) [Optimal Activate Window]")
    else:
        print(f"    [TIP] Set tFAW = {ideal_tfaw} (4 x tRRDS={trrds}).")
    print("==========================================================================")


def main() -> None:
    parser = argparse.ArgumentParser(description="AMD Ryzen DDR4 & DDR5 Timing Latency Calculator")
    parser.add_argument("--gen", choices=["ddr4", "ddr5"], default="ddr4", help="Memory generation (ddr4 or ddr5)")
    parser.add_argument("--mts", type=int, default=3600, help="Memory data rate in MT/s (e.g., 3600 or 6000)")
    parser.add_argument("--fclk", type=int, default=1800, help="Infinity Fabric clock in MHz (e.g., 1800 or 2000)")
    parser.add_argument("--tcl", type=int, default=16, help="CAS Latency (tCL)")
    parser.add_argument("--trcdrd", type=int, default=18, help="RAS to CAS Read Delay (tRCDRD)")
    parser.add_argument("--trp", type=int, default=18, help="Row Precharge Time (tRP)")
    parser.add_argument("--tras", type=int, default=36, help="Row Active Time (tRAS)")
    parser.add_argument("--trc", type=int, default=54, help="Row Cycle Time (tRC)")
    parser.add_argument("--trfc", type=int, default=480, help="Refresh Cycle Time (tRFC)")
    parser.add_argument("--trrds", type=int, default=4, help="Row to Row Delay Short (tRRDS)")
    parser.add_argument("--tfaw", type=int, default=16, help="Four Activate Window (tFAW)")
    args = parser.parse_args()

    evaluate_memory_oc(
        gen=args.gen,
        mts=args.mts,
        fclk=args.fclk,
        tcl=args.tcl,
        trcdrd=args.trcdrd,
        trp=args.trp,
        tras=args.tras,
        trc=args.trc,
        trfc=args.trfc,
        trrds=args.trrds,
        tfaw=args.tfaw,
    )


if __name__ == "__main__":
    main()
