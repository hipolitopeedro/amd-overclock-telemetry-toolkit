#!/usr/bin/env python3
"""
hwinfo_amd_oc_analyzer.py
EN: Analyzes HWiNFO64 CSV logs for AMD Ryzen (Zen 3 PBO2 / Curve Optimizer) and
    AMD Radeon (RDNA 2 RX 6750 XT) overclocking/undervolting stability:
    - Detects Zen 3 Clock Stretching (Core Clock vs. Effective Clock delta under load).
    - Profiles CPU PPT (W), TDC (A), EDC (A), SVI2 TFN Vcore, and Tctl/Tdie temperatures.
    - Evaluates RDNA 2 GPU Core vs. Hotspot (Junction) thermal delta and ASIC power.
    - Checks for silent Windows Hardware Errors (WHEA).
PT: Analisa logs CSV do HWiNFO64 para validação de Overclock/Undervolt em processadores
    AMD Ryzen (Zen 3 PBO2 / Curve Optimizer) e placas AMD Radeon (RDNA 2 RX 6750 XT).
"""

import argparse
import csv
from typing import Dict, List


def analyze_hwinfo_log(csv_path: str, stretch_threshold_mhz: float = 25.0) -> None:
    samples: List[Dict[str, float]] = []

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            samples.append({k: float(v) for k, v in row.items()})

    if not samples:
        print("[WARN] No samples found in CSV log.")
        return

    # CPU Metrics (Ryzen 7 5700X - 8 Cores)
    max_tctl = max(s["cpu_tctl_tdie_c"] for s in samples)
    max_ppt_w = max(s["cpu_ppt_w"] for s in samples)
    max_tdc_a = max(s["cpu_tdc_a"] for s in samples)
    max_edc_a = max(s["cpu_edc_a"] for s in samples)
    min_vcore = min(s["cpu_vcore_svi2_v"] for s in samples)
    max_vcore = max(s["cpu_vcore_svi2_v"] for s in samples)

    # Check Clock Stretching on Load Samples (PPT > 65W)
    load_samples = [s for s in samples if s["cpu_ppt_w"] >= 65.0]
    stretched_cores: Dict[int, float] = {}
    peak_effective_mhz = 0.0

    for core_idx in range(8):
        clock_key = f"core{core_idx}_clock_mhz"
        eff_key = f"core{core_idx}_eff_mhz"
        if clock_key in samples[0] and eff_key in samples[0]:
            peak_effective_mhz = max(peak_effective_mhz, max(s[eff_key] for s in samples))
            if load_samples:
                max_delta = max(s[clock_key] - s[eff_key] for s in load_samples)
                if max_delta > stretch_threshold_mhz:
                    stretched_cores[core_idx] = round(max_delta, 1)

    # GPU Metrics (Radeon RX 6750 XT)
    max_gpu_clock = max(s["gpu_clock_mhz"] for s in samples)
    max_vram_clock = max(s["gpu_vram_mhz"] for s in samples)
    max_gpu_edge = max(s["gpu_edge_temp_c"] for s in samples)
    max_gpu_hotspot = max(s["gpu_hotspot_temp_c"] for s in samples)
    max_gpu_delta = max(s["gpu_hotspot_temp_c"] - s["gpu_edge_temp_c"] for s in samples)
    max_gpu_power = max(s["gpu_asic_power_w"] for s in samples)

    total_whea = int(max(s["whea_total_errors"] for s in samples))

    print("=" * 84)
    print("  AMD RYZEN (ZEN 3) & RADEON (RDNA 2) OVERCLOCK / UNDERVOLT STABILITY REPORT")
    print("=" * 84)

    print("\n[1] CPU TELEMETRY: AMD RYZEN 7 5700X (PBO2 & CURVE OPTIMIZER)")
    print(f"    Peak Effective Boost : {peak_effective_mhz:.0f} MHz")
    print(f"    SVI2 TFN Vcore Range : {min_vcore:.3f} V (Load/Idle Min) -> {max_vcore:.3f} V (Peak Boost)")
    print(f"    Peak Package Temps   : {max_tctl:.1f} C (Thermal Limit: 90.0 C)")
    print(f"    Peak PBO2 Telemetry  : PPT = {max_ppt_w:.1f} W | TDC = {max_tdc_a:.1f} A | EDC = {max_edc_a:.1f} A")

    if not stretched_cores:
        print(
            f"    Clock Stretching     : [OK] No core exceeded {stretch_threshold_mhz:.0f} MHz delta under full load."
        )
    else:
        print("    Clock Stretching     : [WARN] Potential Curve Optimizer undervolt instability detected:")
        for c_id, delta in stretched_cores.items():
            print(f"      -> Core #{c_id} showed {delta} MHz difference between Core Clock and Effective Clock!")

    print("\n[2] GPU TELEMETRY: AMD RADEON RX 6750 XT 12GB (RDNA 2)")
    print(f"    Peak Core / VRAM     : {max_gpu_clock:.0f} MHz Core | {max_vram_clock:.0f} MHz VRAM")
    print(f"    Peak ASIC Power      : {max_gpu_power:.1f} W")
    print(
        f"    Thermal Profile      : Edge = {max_gpu_edge:.1f} C | Hotspot = {max_gpu_hotspot:.1f} C "
        f"(Max Delta: {max_gpu_delta:.1f} C)"
    )
    if max_gpu_hotspot >= 105.0:
        print("    Thermal Status       : [ALERT] GPU Hotspot approaching 110 C junction throttle limit!")
    elif max_gpu_delta >= 26.0:
        print("    Thermal Status       : [WARN] High Edge-to-Hotspot delta (>25 C). Check mounting pressure/paste.")
    else:
        print("    Thermal Status       : [OK] Healthy RDNA 2 thermal delta and junction temperature.")

    print("\n[3] HARDWARE ERROR AUDIT (WHEA)")
    if total_whea == 0:
        print("    WHEA Error Count     : 0 Errors [STABLE - FCLK & Curve Optimizer verified]")
    else:
        print(f"    WHEA Error Count     : {total_whea} Error(s) [UNSTABLE - Check FCLK or Curve Optimizer!]")
    print("=" * 84)


def main() -> None:
    parser = argparse.ArgumentParser(description="HWiNFO64 AMD Zen 3 & RDNA 2 Overclock Stability Analyzer")
    parser.add_argument(
        "--log",
        default="data/sample_5700x_6750xt_hwinfo.csv",
        help="Path to HWiNFO64 telemetry CSV file",
    )
    parser.add_argument(
        "--stretch-threshold",
        type=float,
        default=25.0,
        help="Max allowed Core vs Effective clock delta in MHz before flagging clock stretching",
    )
    args = parser.parse_args()
    analyze_hwinfo_log(args.log, args.stretch_threshold)


if __name__ == "__main__":
    main()
