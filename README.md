# AMD Overclocking, Undervolting & Hardware Telemetry Toolkit (AM4 & AM5 / RDNA)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PowerShell](https://img.shields.io/badge/PowerShell-5391FE?style=for-the-badge&logo=powershell&logoColor=white)
![AMD](https://img.shields.io/badge/AMD-Ryzen_%26_Radeon-ED1C24?style=for-the-badge&logo=amd&logoColor=white)

> **Live Interactive DDR4/DDR5, WHEA & Telemetry Dashboard (GitHub Pages):** [https://hipolitopeedro.github.io/amd-overclock-telemetry-toolkit/](https://hipolitopeedro.github.io/amd-overclock-telemetry-toolkit/)
>
> **English:** Unified hardware diagnostics, telemetry analysis, and overclocking/undervolting stability toolkit designed for **AMD Ryzen platforms (AM4 Zen 3 & AM5 Zen 4 / Zen 5, 6-core to 16-core, including X3D)**, **AMD Radeon GPUs (RDNA 2 / RDNA 3)**, and **DDR4 / DDR5 Memory Overclocking**.
>
> **Português:** Kit unificado de diagnóstico de hardware, análise de telemetria e validação de estabilidade de Overclock/Undervolt desenvolvido para **plataformas AMD Ryzen (AM4 Zen 3 e AM5 Zen 4 / Zen 5, de 6 a 16 núcleos, incluindo X3D)**, **placas AMD Radeon (RDNA 2 / RDNA 3)** e **Overclock de Memória DDR4 / DDR5**.

---

## Supported Architectures / Arquiteturas Suportadas

| Subsystem / Subsistema | Supported Platforms / Plataformas Suportadas | Key Telemetry & Diagnostics / Diagnósticos Principais |
| :--- | :--- | :--- |
| **CPU (AMD Ryzen)** | AM4 (Ryzen 5000 Zen 3) & AM5 (Ryzen 7000/9000 Zen 4 & Zen 5, X3D) | Dynamic 6C to 16C detection, PBO2 (`PPT`, `TDC`, `EDC`), SVI2/SVI3 Vcore, and Per-Core Clock Stretching detection |
| **Memory (DDR4 & DDR5)** | AM4 DDR4 (`3200-4000 MT/s`) & AM5 DDR5 (`6000-8000 MT/s`) | True latency in nanoseconds (`ns`), AM4 `1:1:1` FCLK sync, AM5 `UCLK=MCLK` vs `UCLK=MCLK/2` & subtiming validation |
| **GPU (AMD Radeon)** | RDNA 2 (RX 6000 Series) & RDNA 3 (RX 7000 Series) | Edge vs. Hotspot (Junction) thermal delta, VRAM/Core clocks, and Total Board/ASIC Power |
| **OS / Bare-Metal** | Windows 10 / Windows 11 (WMI / CIM / Event Viewer) | `WHEA-Logger` (Event ID 18/19/46) APIC ID to Physical Core translator |

---

## Included Tools / Ferramentas Inclusas

| File | Description (EN) | Descrição (PT-BR) |
| :--- | :--- | :--- |
| [`src/hwinfo_amd_oc_analyzer.py`](src/hwinfo_amd_oc_analyzer.py) | Dynamically detects 6C/8C/12C/16C Ryzen CPUs in HWiNFO64 CSV logs to flag **Clock Stretching** (Core Clock vs. Effective Clock delta), profile PBO2 limits (`PPT`, `TDC`, `EDC`, `Tctl/Tdie`), evaluate **Radeon GPU Edge vs. Hotspot delta**, and check for **WHEA errors**. | Detecta automaticamente CPUs Ryzen de 6 a 16 núcleos em logs CSV do HWiNFO64 para identificar **Clock Stretching**, perfilar limites do PBO2 (`PPT`, `TDC`, `EDC`, `Tctl/Tdie`), avaliar o **delta térmico entre GPU Edge e Hotspot** e verificar **erros WHEA**. |
| [`src/ddr4_timings_fclk_calculator.py`](src/ddr4_timings_fclk_calculator.py) | Supports both **DDR4 (AM4)** and **DDR5 (AM5)**: calculates true latency in nanoseconds (`ns`), theoretical bandwidth (`GB/s`), Infinity Fabric (`FCLK`) & Memory Controller (`UCLK`) synchronization, and checks secondary timing formulas (`tRAS`, `tRC`, `tRFC`, `tFAW`). | Suporta **DDR4 (AM4)** e **DDR5 (AM5)**: calcula latência real em nanosegundos (`ns`), largura de banda (`GB/s`), sincronia do Infinity Fabric (`FCLK`) e controlador (`UCLK`), e valida fórmulas de subtimings. |
| [`scripts/Get-AMDWheaAndHardwareAudit.ps1`](scripts/Get-AMDWheaAndHardwareAudit.ps1) | PowerShell bare-metal auditor: inspects BIOS/AGESA and RAM speed via CIM/WMI, and scans Windows Event Viewer for **`WHEA-Logger` (Event ID 18/19)**, translating the failing `APIC ID` to the exact physical Ryzen core that failed under Curve Optimizer. | Auditor em PowerShell: verifica versão de BIOS/AGESA e frequência da RAM via WMI, e varre o Event Viewer atrás de erros **`WHEA-Logger` (ID 18/19)**, traduzindo o `APIC ID` para o núcleo físico exato do Ryzen que falhou no Curve Optimizer. |
| [`data/sample_ryzen_radeon_hwinfo.csv`](data/sample_ryzen_radeon_hwinfo.csv) | Sample HWiNFO64 telemetry log from an AMD Ryzen + Radeon stress test session. | Log CSV de exemplo do HWiNFO64 em uma bateria de estresse com AMD Ryzen + Radeon. |

---

## Quick Start / Como Executar

### 1. Analyze HWiNFO64 Overclock & Undervolt Telemetry (Python)
```bash
python src/hwinfo_amd_oc_analyzer.py --log data/sample_ryzen_radeon_hwinfo.csv
```

### 2. Calculate DDR4 (AM4) or DDR5 (AM5) Timings, Latency (ns) & FCLK/UCLK Sync
```bash
# AM4 DDR4-3600 CL16 (1:1 FCLK 1800 MHz)
python src/ddr4_timings_fclk_calculator.py --gen ddr4 --mts 3600 --fclk 1800 --tcl 16 --trcdrd 18 --trp 18 --tras 36 --trc 54 --trfc 480

# AM5 DDR5-6000 CL30 (UCLK=MCLK 3000 MHz, FCLK 2000 MHz)
python src/ddr4_timings_fclk_calculator.py --gen ddr5 --mts 6000 --fclk 2000 --tcl 30 --trcdrd 38 --trp 38 --tras 76 --trc 114 --trfc 500
```

### 3. Hunt WHEA-Logger Core Crashes & Audit Hardware in Windows (PowerShell)
```powershell
.\scripts\Get-AMDWheaAndHardwareAudit.ps1 -DaysBack 14
```
