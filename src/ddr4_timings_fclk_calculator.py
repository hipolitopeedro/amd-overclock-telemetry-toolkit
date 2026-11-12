#!/usr/bin/env python3
"""
ddr4_timings_fclk_calculator.py
EN: Calculates true DDR4 latency in nanoseconds (ns), compares bandwidth gain against
    a baseline profile (e.g., Corsair Vengeance 2400 MT/s CL16 -> 3200 MT/s CL16 OC),
    verifies AMD Ryzen 1:1:1 Infinity Fabric (MCLK:FCLK:UCLK) coupling, and checks
    secondary timing formulas (tRAS, tRC, tRFC, tFAW).
PT: Calcula latência real DDR4 em nanosegundos (ns), compara ganho de banda contra o
    perfil stock (ex: Corsair Vengeance 2400 MT/s CL16 -> 3200 MT/s CL16 OC), verifica
    sincronia 1:1:1 do Infinity Fabric (FCLK) e valida fórmulas de subtimings.
"""

import argparse


def cycles_to_ns(cycles: int, mts: int) -> float:
    """Converts memory clock cycles into true latency in nanoseconds: ns = (2000 * cycles) / MT/s."""
    return round((2000.0 * cycles) / mts, 2)


def theoretical_bandwidth_gbs(mts: int, channels: int = 2) -> float:
    """Calculates peak theoretical dual-channel bandwidth in GB/s (8 bytes per 64-bit channel)."""
    return round((mts * 8.0 * channels) / 1000.0, 2)


def evaluate_ddr4_oc(
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
    baseline_mts: int = 2400,
    baseline_tcl: int = 16,
) -> None:
    mclk = mts // 2
    synced_1_to_1 = mclk == fclk

    base_bw = theoretical_bandwidth_gbs(baseline_mts)
    oc_bw = theoretical_bandwidth_gbs(mts)
    bw_gain_pct = round(((oc_bw - base_bw) / base_bw) * 100.0, 1)

    base_cas_ns = cycles_to_ns(baseline_tcl, baseline_mts)
    oc_cas_ns = cycles_to_ns(tcl, mts)
    trfc_ns = cycles_to_ns(trfc, mts)

    print("==========================================================================")
    print("  AMD RYZEN DDR4 OVERCLOCKING & INFINITY FABRIC (FCLK) CALCULATOR")
    print("==========================================================================")
    print(f"  Baseline Profile   : DDR4-{baseline_mts} CL{baseline_tcl} ({base_bw} GB/s | First-Word Latency: {base_cas_ns} ns)")
    print(f"  Overclock Profile  : DDR4-{mts} CL{tcl}-{trcdrd}-{trp}-{tras}-{trc} ({oc_bw} GB/s | +{bw_gain_pct}% Bandwidth)")
    print("--------------------------------------------------------------------------")

    print("\n[1] INFINITY FABRIC (MCLK : FCLK : UCLK) SYNCHRONIZATION")
    print(f"    Memory Clock (MCLK): {mclk} MHz | Infinity Fabric (FCLK): {fclk} MHz")
    if synced_1_to_1:
        print("    Coupled Mode       : [1:1:1 SYNCHRONIZED] Optimal low-latency Zen 3 operation.")
    else:
        print("    Coupled Mode       : [DESYNCHRONIZED] Warning: MCLK != FCLK incurs ~5-8 ns latency penalty!")

    print("\n[2] TRUE TIMING LATENCY IN NANOSECONDS (ns)")
    print(f"    tCL     : {tcl:<4} cycles -> {oc_cas_ns:>6.2f} ns (vs {base_cas_ns:.2f} ns stock)")
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
        print(f"    [WARN] tRAS ({tras}) is tighter than tCL + tRCDRD ({min_tras}); test carefully for corruption.")

    ideal_trc = trp + tras
    if trc >= ideal_trc:
        print(f"    [OK] tRC ({trc}) >= tRP + tRAS ({ideal_trc})")
    else:
        print(f"    [WARN] tRC ({trc}) < tRP + tRAS ({ideal_trc}); may cause bank cycle instability.")

    ideal_tfaw = 4 * trrds
    if tfaw == ideal_tfaw:
        print(f"    [OK] tFAW ({tfaw}) == 4 x tRRDS ({trrds}) [Optimal Eight-Bank Activation Window]")
    else:
        print(f"    [TIP] Consider setting tFAW = {ideal_tfaw} (4 x tRRDS={trrds}).")
    print("==========================================================================")


def main() -> None:
    parser = argparse.ArgumentParser(description="AMD Ryzen DDR4 Overclocking & Timing Latency Calculator")
    parser.add_argument("--mts", type=int, default=3200, help="Overclocked DDR4 data rate in MT/s (default: 3200)")
    parser.add_argument("--fclk", type=int, default=1600, help="Infinity Fabric clock in MHz (default: 1600)")
    parser.add_argument("--tcl", type=int, default=16, help="CAS Latency (tCL)")
    parser.add_argument("--trcdrd", type=int, default=18, help="RAS to CAS Read Delay (tRCDRD)")
    parser.add_argument("--trp", type=int, default=18, help="Row Precharge Time (tRP)")
    parser.add_argument("--tras", type=int, default=36, help="Row Active Time (tRAS)")
    parser.add_argument("--trc", type=int, default=54, help="Row Cycle Time (tRC)")
    parser.add_argument("--trfc", type=int, default=560, help="Refresh Cycle Time (tRFC)")
    parser.add_argument("--trrds", type=int, default=4, help="Row to Row Delay Short (tRRDS)")
    parser.add_argument("--tfaw", type=int, default=16, help="Four Activate Window (tFAW)")
    args = parser.parse_args()

    evaluate_ddr4_oc(
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
