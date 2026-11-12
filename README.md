# AMD Overclocking, Undervolting & Hardware Telemetry Toolkit

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PowerShell](https://img.shields.io/badge/PowerShell-5391FE?style=for-the-badge&logo=powershell&logoColor=white)
![AMD](https://img.shields.io/badge/AMD-Zen_3_%26_RDNA_2-ED1C24?style=for-the-badge&logo=amd&logoColor=white)

> **English:** Unified hardware diagnostics, telemetry analysis, and overclocking/undervolting stability toolkit tailored for the **AMD Ryzen (Zen 3 PBO2 / Curve Optimizer)**, **AMD Radeon (RDNA 2)**, and **DDR4 Memory Overclocking** ecosystem.
>
> **Português:** Kit unificado de diagnóstico de hardware, análise de telemetria e validação de estabilidade de Overclock/Undervolt desenvolvido para a plataforma **AMD Ryzen (Zen 3 PBO2 / Curve Optimizer)**, **AMD Radeon (RDNA 2)** e **Overclock de Memória DDR4**.

---

## Reference Hardware Testbed / Setup de Referência

| Component / Componente | Specification / Especificação | Tuning / Configuração |
| :--- | :--- | :--- |
| **CPU** | AMD Ryzen 7 5700X (8C / 16T, Zen 3 Vermeer) | PBO2 + Curve Optimizer (Per-Core Negative Offset) |
| **Motherboard** | Gigabyte B550M Aorus Elite | Custom PBO Limits (`PPT / TDC / EDC`) & LLC |
| **CPU Cooler** | Cooler Master V4 | Custom PWM Fan Curve |
| **Memory (RAM)** | 32GB (2x 16GB) Corsair Vengeance DDR4 | Stock `2400 MT/s CL16` -> **OC `3200 MT/s CL16` (1:1 FCLK 1600 MHz)** |
| **GPU** | XFX Speedster QICK 319 Radeon RX 6750 XT 12GB | RDNA 2 Core Undervolt + VRAM Fast Timings |
| **PSU** | Cooler Master 750W 80 Plus Gold | - |

---

## Included Tools / Ferramentas Inclusas

| File | Description (EN) | Descrição (PT-BR) |
| :--- | :--- | :--- |
| [`src/hwinfo_amd_oc_analyzer.py`](src/hwinfo_amd_oc_analyzer.py) | Parses HWiNFO64 CSV logs to detect **Zen 3 Clock Stretching** (Core Clock vs. Effective Clock delta), profile PBO2 limits (`PPT`, `TDC`, `EDC`, `SVI2 TFN Vcore`, `Tctl/Tdie`), evaluate **RX 6750 XT Core vs. Hotspot delta**, and check for **WHEA errors**. | Analisa logs CSV do HWiNFO64 para detectar **Clock Stretching no Zen 3**, perfilar limites do PBO2 (`PPT`, `TDC`, `EDC`, `Vcore`, `Tctl/Tdie`), avaliar o **delta entre GPU Core e Hotspot na RX 6750 XT** e verificar **erros WHEA**. |
| [`src/ddr4_timings_fclk_calculator.py`](src/ddr4_timings_fclk_calculator.py) | Calculates true DDR4 latency in nanoseconds (`ns`), bandwidth gains (e.g., `2400 MT/s` vs `3200 MT/s`), validates `1:1:1` Infinity Fabric (`MCLK:FCLK:UCLK`) synchronization, and checks secondary timing rules (`tRAS`, `tRC`, `tRFC`, `tFAW`). | Calcula a latência real da RAM DDR4 em nanosegundos (`ns`), ganho de largura de banda (`2400 MT/s` vs `3200 MT/s`), valida sincronia `1:1:1` do Infinity Fabric (`FCLK`) e confere regras matemáticas de subtimings. |
| [`scripts/Get-AMDWheaAndHardwareAudit.ps1`](scripts/Get-AMDWheaAndHardwareAudit.ps1) | PowerShell bare-metal auditor: inspects BIOS/AGESA and RAM speed via CIM/WMI, checks VBS status, and scans Windows Event Viewer for **`WHEA-Logger` (Event ID 18/19)**, translating the failing `APIC ID` to the exact physical Ryzen core that needs Curve Optimizer adjustment. | Auditor em PowerShell: verifica versão de BIOS e frequência da RAM via WMI, checa status do VBS e varre o Event Viewer atrás de erros **`WHEA-Logger` (ID 18/19)**, traduzindo o `APIC ID` para o núcleo físico exato do Ryzen que falhou no Curve Optimizer. |
| [`data/sample_5700x_6750xt_hwinfo.csv`](data/sample_5700x_6750xt_hwinfo.csv) | Sample HWiNFO64 telemetry log from a Ryzen 7 5700X + RX 6750 XT stress test session. | Log CSV de exemplo do HWiNFO64 em uma bateria de estresse com o Ryzen 7 5700X + RX 6750 XT. |

---

## Quick Start / Como Executar

### 1. Analyze HWiNFO64 Overclock & Undervolt Telemetry (Python)
```bash
python src/hwinfo_amd_oc_analyzer.py --log data/sample_5700x_6750xt_hwinfo.csv
```

### 2. Compare DDR4 2400 MT/s Stock vs. 3200 MT/s Overclock & FCLK Sync (Python)
```bash
python src/ddr4_timings_fclk_calculator.py \
    --mts 3200 --fclk 1600 \
    --tcl 16 --trcdrd 18 --trp 18 --tras 36 --trc 54 --trfc 560
```

### 3. Hunt WHEA-Logger Core Crashes & Audit Hardware in Windows (PowerShell)
```powershell
.\scripts\Get-AMDWheaAndHardwareAudit.ps1 -DaysBack 14
```
