# my_sci_toolkit (chem-scitoolkit): 现代化科研计算与出版级绘图工具箱

[![CI](https://github.com/your-username/chem-scitoolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/chem-scitoolkit/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

`my_sci_toolkit`（发布包名：`chem-scitoolkit`）是一个遵循现代 Python 规范的科研计算与 Nature/JACS 级出图工具箱。它将反应动力学、谱学表征、电化学储能、分子动力学后处理与晶体结构计算进行了**系统级模块化重构**，消除了硬编码参数与跨平台路径隐患，并原生提供了**自然语言交互引擎 (Natural Language Interface)**。

---

## 目录索引

- [1. 安装与开源分发途径](#1-安装与开源分发途径)
  - [1.1 途径 A：GitHub 一行命令直装 (组内同行快速分发)](#11-途径-a-github-一行命令直装-组内同行快速分发)
  - [1.2 途径 B：本地开发可编辑安装 (pip install -e .)](#12-途径-b-本地开发可编辑安装-pip-install--e-)
  - [1.3 途径 C：PyPI 官方源打包与发布流程](#13-途径-c-pypi-官方源打包与发布流程)
- [2. 完整功能索引与 API 清单 (API Feature List)](#2-完整功能索引与-api-清单-api-feature-list)
  - [2.1 `kinetics` 反应动力学与热力学模块](#21-kinetics-反应动力学与热力学模块)
  - [2.2 `electrochem` 电化学储能模块](#22-electrochem-电化学储能模块)
  - [2.3 `spectro` 谱学表征模块](#23-spectro-谱学表征模块)
  - [2.4 `viz` 出版级图表绘制模块](#24-viz-出版级图表绘制模块)
  - [2.5 `core` 纯数值算法与信号处理模块](#25-core-纯数值算法与信号处理模块)
  - [2.6 `io` 结构与表格数据 I/O 模块](#26-io-结构与表格数据-io-模块)
  - [2.7 `structure` 晶体几何计算模块](#27-structure-晶体几何计算模块)
  - [2.8 `md` 分子动力学后处理模块](#28-md-分子动力学后处理模块)
  - [2.9 `ai_agent` 自然语言交互引擎](#29-ai_agent-自然语言交互引擎)
- [3. 典型场景代码示例](#3-典型场景代码示例)
- [4. 自然语言命令行调用 (CLI)](#4-自然语言命令行调用-cli)
- [5. GitHub 开源工程初始化与推送指南](#5-github-开源工程初始化与推送指南)

---

## 1. 安装与开源分发途径

### 1.1 途径 A：GitHub 一行命令直装 (组内同行快速分发)

任何同行或组内学生无需手动下载源码压缩包，只需在任何安装了 Python 环境的终端中运行：

```bash
# 基础核心安装 (含 numpy, scipy, pandas, matplotlib)
pip install git+https://github.com/<your-username>/chem-scitoolkit.git

# 附带理论计算与结构扩展 (包含 pymatgen, ase)
pip install "chem-scitoolkit[chem] @ git+https://github.com/<your-username>/chem-scitoolkit.git"

# 附带所有可选扩展 (含电化学阻抗、分子动力学及 Gemini AI 支持)
pip install "chem-scitoolkit[all] @ git+https://github.com/<your-username>/chem-scitoolkit.git"
```

### 1.2 途径 B：本地开发可编辑安装 (pip install -e .)

拉取本地源码并在项目根目录运行：

```bash
git clone https://github.com/<your-username>/chem-scitoolkit.git
cd chem-scitoolkit

# 推荐在独立虚拟环境安装
pip install -e ".[dev,all]"
```

### 1.3 途径 C：PyPI 官方源打包与发布流程

本项目正式发布包名推荐为：**`chem-scitoolkit`**（避免了个人化的 `my-` 前缀，更具学科通用性且不易在 PyPI 发生命名冲突）。

发布准备步骤：

```bash
# 1. 安装标准化构建与上传工具
pip install --upgrade build twine

# 2. 生成标准源码分发包 (.tar.gz) 与二进制轮子包 (.whl)
python -m build

# 3. 校验打包产物元数据完整性
twine check dist/*

# 4. (可选) 先发布到 PyPI 测试源 (TestPyPI) 验证
twine upload --repository testpypi dist/*

# 5. 正式上传发布到 PyPI 官方源
twine upload dist/*
```

发布成功后，全球任何学者即可像安装 SciPy 一样直接安装：
```bash
pip install chem-scitoolkit
```

---

## 2. 完整功能索引与 API 清单 (API Feature List)

### 2.1 `kinetics` 反应动力学与热力学模块

| 函数 / 接口 | 核心入参 (Signature) | 功能说明 | 快速调用示例 |
|---|---|---|---|
| `plot_free_energy_profile` | `pathways: dict, step_labels: list, energy_unit="eV"` | 绘制多路径反应自由能台阶图 (HER, CO2RR 等中间态) | `plot_free_energy_profile({"Path A": [0, -0.4, 0.2, -0.7]})` |
| `fit_reaction_kinetics` | `time_series, concentration_ratio, order=None` | 非线性拟合反应衰减曲线，估算反应速率常数 $k$ 与级数 $n$ | `res = fit_reaction_kinetics(t, c_c0, order=1)` |
| `fit_arrhenius_activation_energy` | `temperatures_kelvin, rate_constants` | 阿伦尼乌斯拟合计算活化能 $E_a\ (\text{kJ/mol})$ 与指前因子 $A$ | `res = fit_arrhenius_activation_energy([298, 313, 333], [0.01, 0.03, 0.09])` |
| `simulate_nucleation_growth` | `rate_constants=(k_n, k_gt, k_ga), duration=600, dt=1.0` | 耦合固体成核与生长微分方程求解相变进程 $\alpha(t)$ | `t, alpha = simulate_nucleation_growth([0.05, 0.0, 0.0], duration=60)` |
| `capillary_pressure` | `surface_tension_gamma=0.0728, contact_angle_deg=0, pore_diameter_m=5e-9` | 计算毛细凝聚液桥内静水负压张力 $-\Delta P_{\text{cap}}\ (\text{kPa})$ | `p_kpa = capillary_pressure(pore_diameter_m=4e-9)` |
| `nanoscale_solubility_ratio` | `radius_nm, surface_energy_J_m2=1.0, molar_volume_m3_mol=3.4e-5` | 基于 Ostwald-Freundlich 方程计算纳米晶体溶解度提升比率 | `ratio = nanoscale_solubility_ratio(radius_nm=2.5)` |
| `first_order_decay` | `t, k` | 一级反应解析衰减函数 $C/C_0 = \exp(-kt)$ | `y = first_order_decay(t, k=0.05)` |
| `nth_order_decay` | `t, k, n` | $n$ 级反应速率衰减解析函数 | `y = nth_order_decay(t, k=0.05, n=1.5)` |
| `avrami_nucleation` | `t, k, n` | JMAK 相变动力学方程 $\alpha = 1 - \exp(-k t^n)$ | `a = avrami_nucleation(t, k=0.001, n=2.5)` |
| `pseudo_second_order` | `t, k2, qe` | 准二级吸附动力学模型 | `qt = pseudo_second_order(t, k2=0.02, qe=120)` |

---

### 2.2 `electrochem` 电化学储能模块

| 函数 / 接口 | 核心入参 (Signature) | 功能说明 | 快速调用示例 |
|---|---|---|---|
| `plot_charge_discharge` | `capacity_mah_g, voltage_v, cycle_index=1, c_rate="0.1C"` | 绘制标准电池恒流充放电电压-比容量曲线 | `plot_charge_discharge(q, v, c_rate="0.2C")` |
| `calculate_dqdv` | `voltage, capacity, smooth_window=15` | 计算平滑后的微分电容 $dQ/dV\ (\text{mAh}\cdot\text{g}^{-1}\cdot\text{V}^{-1})$ 曲线 | `v_s, dqdv = calculate_dqdv(v, q)` |
| `plot_cycling_stability` | `cycles, discharge_capacity, coulombic_efficiency=None` | 绘制双 Y 轴循环稳定性图（容量保持率与库伦效率） | `plot_cycling_stability(cycles, cap, ce)` |
| `plot_cv_curve` | `potential_v, current_ma, scan_rate_mv_s=None` | 绘制循环伏安 (CV) 曲线，带电位零线对齐 | `plot_cv_curve(pot, cur, scan_rate_mv_s=50)` |
| `plot_nyquist_eis` | `z_real_ohm, z_imag_ohm` | 绘制等比例阻抗谱 Nyquist 图 ($-Z''$ vs $Z'$) | `plot_nyquist_eis(z_re, z_im)` |
| `active_material_moles` | `mass_active_g, molecular_weight_g_mol` | 活性材料质量折算摩尔量 | `n_mol = active_material_moles(0.015, 96.0)` |
| `theoretical_specific_capacity` | `n_electrons, molecular_weight_g_mol` | 计算电极理论比容量 ($\text{mAh/g}$) | `q_th = theoretical_specific_capacity(1, 157.7)` |

---

### 2.3 `spectro` 谱学表征模块

| 函数 / 接口 | 核心入参 (Signature) | 功能说明 | 快速调用示例 |
|---|---|---|---|
| `plot_xrd_pattern` | `two_theta, intensity, baseline_corr=True, normalize=True` | 绘制出版级 1D XRD 衍射图谱，自动基线校正与归一 | `plot_xrd_pattern(two_theta, inten)` |
| `plot_xrd_stack` | `two_theta, intensity_series, labels, offset=0.35` | 绘制多物相/原位 XRD 垂直瀑布层叠图 | `plot_xrd_stack(2theta, [y1, y2], ["1h", "2h"])` |
| `plot_vibrational_spectrum` | `wavenumber, intensity, spec_type="FTIR", trim_range=None` | 绘制 FTIR / Raman 振动光谱（FTIR 自动倒置 X 轴） | `plot_vibrational_spectrum(wn, int_ir)` |
| `deconvolute_peaks` | `x, y, initial_centers, initial_widths=None` | 高斯多峰拟合分解，自动填充各子峰并输出拟合图 | `deconvolute_peaks(x, y, [3610, 3640])` |
| `shirley_background` | `x, y, tol=1e-4, max_iter=50` | 迭代计算 XPS 非弹性电子散射 Shirley 非线性背景 | `bg = shirley_background(be, counts)` |
| `plot_epr_spectrum` | `magnetic_field_gauss, first_derivative_signal` | 绘制顺磁共振 (EPR) 一次微分特征图谱 | `plot_epr_spectrum(field, dI_dB)` |

---

### 2.4 `viz` 出版级图表绘制模块

| 函数 / 接口 | 核心入参 (Signature) | 功能说明 | 快速调用示例 |
|---|---|---|---|
| `plot_completion_time_bar` | `systems, times_h, unit_labels, y_label=...` | 绘制毛细凝聚 vs 体相水氧化完成时间 Nature 级对比柱状图 | `plot_completion_time_bar(["Capillary", "Bulk"], [0.667, 26], ["40 min", "26 h"])` |
| `plot_decay_curve` | `t_exp, c_exp, t_fit=None, c_fit=None, rate_constant_k=...` | 绘制反应浓度衰减曲线，支持误差棒与拟合曲线叠合 | `plot_decay_curve(t, c, t_fit, c_fit, rate_constant_k=0.07)` |
| `plot_conversion_alpha` | `t_exp, alpha_exp, simulations=None` | 绘制反应进程 $\alpha(t)$ (0~1) 散点与多组动力学仿真曲线 | `plot_conversion_alpha(t, a, simulations=[...])` |
| `create_panel_collage` | `image_paths, rows, cols, labels=None` | 拼接多张图片为出版级 Subfigure 复合面板 (a, b, c, d) | `create_panel_collage(["f1.png", "f2.png"], 1, 2)` |
| `apply_style` | `theme="nature", font_family="Arial", font_size=8` | 全局应用 Nature / JACS 出版样式规范 rcParams | `apply_style(theme="nature")` |
| `get_figure_dimensions` | `columns="single", aspect_ratio=0.80` | 计算单栏 (3.5 in) 或双栏 (7.2 in) 的标准物理尺寸 | `w, h = get_figure_dimensions("single")` |

---

### 2.5 `core` 纯数值算法与信号处理模块

| 函数 / 接口 | 核心入参 (Signature) | 功能说明 | 快速调用示例 |
|---|---|---|---|
| `normalize_sum` | `arr: Sequence[float]` | 数组归一化至总和为 1.0 ($\sum y_i = 1$) | `y_norm = normalize_sum(y)` |
| `normalize_minmax` | `arr: Sequence[float]` | 数组最大最小值线性归一化到 $[0, 1]$ | `y_norm = normalize_minmax(y)` |
| `baseline_correct` | `intensity, method="modpoly", degree=2` | 纯 NumPy 矢量化迭代多项式基线校正 | `y_cor = baseline_correct(y, degree=2)` |
| `smooth_spectrum` | `y, window_length=9, polyorder=3` | Savitzky-Golay 数字信号平滑滤波 | `y_sm = smooth_spectrum(y)` |
| `calculate_r_squared`| `y_true, y_pred` | 计算非线性回归决定系数 $R^2$ | `r2 = calculate_r_squared(y, y_hat)` |
| `fit_model` | `model_func, x_data, y_data, param_names, p0=...` | 通用非线性最小二乘拟合器，返回标准化 `FitResult` | `res = fit_model(func, x, y, ("k", "n"))` |
| `resolve_path` | `target, base_dir=None` | 安全解析相对与绝对路径，不改变全局工作目录 | `p = resolve_path("./data/1.txt")` |
| `list_files` | `directory, patterns=["*.xy"], sort=True` | 批量搜索文件并采用自然序号算法智能排序 | `files = list_files("./dir", ["*.xy"])` |
| `extract_time_from_stem` | `stem: str, slice_range=None` | 从文件名中稳健提取时间浮点数 | `t = extract_time_from_stem("time_120min.xy")` |

---

### 2.6 `io` 结构与表格数据 I/O 模块

| 函数 / 接口 | 核心入参 (Signature) | 功能说明 | 快速调用示例 |
|---|---|---|---|
| `read_xy` | `file_path, delimiter=None` | 快速读取两列 (X, Y) 谱图/动力学数据文件 | `x, y = read_xy("sample.xy")` |
| `read_xy_series_dir` | `directory, patterns=["*.xy"], time_slice=None` | 批量读取目录中时序谱图，返回统一 X 轴与时间序列 | `x, ys, ts = read_xy_series_dir("./insitu_xrd")` |
| `read_excel_columns` | `file_path, x_col=0, y_cols=1, sheet_name=0` | 从 Excel 文件中提取特定列向量 | `x, y = read_excel_columns("data.xlsx", 0, [1, 2])` |
| `save_publication_figure` | `fig, file_path, dpi=600, transparent=True` | 统一 600 DPI 无损高保真图像导出（png/tiff/pdf） | `save_publication_figure(fig, "fig1.png")` |
| `pdb_to_xyz` | `input_pdb, output_xyz` | 纯 Python 实现 PDB 坐标转换为标准 XYZ 轨迹 | `pdb_to_xyz("aimd.pdb", "traj.xyz")` |
| `xyz_to_pdb` | `input_xyz, output_pdb` | XYZ 格式逆向转换为标准 PDB 文件 | `xyz_to_pdb("traj.xyz", "model.pdb")` |

---

### 2.7 `structure` 晶体几何计算模块

| 函数 / 接口 | 核心入参 (Signature) | 功能说明 | 快速调用示例 |
|---|---|---|---|
| `calculate_d_spacing`| `crystal_system, a, b, c, h, k, l, alpha, beta, gamma` | 解析度量张量计算立方/四方/正交/六方/单斜的晶面间距 $d_{hkl}\ (\text{Å})$ | `d = calculate_d_spacing("cubic", 5.43, 5.43, 5.43, 1, 1, 1)` |

---

### 2.8 `md` 分子动力学后处理模块

| 函数 / 接口 | 核心入参 (Signature) | 功能说明 | 快速调用示例 |
|---|---|---|---|
| `calculate_diffusion_coefficient` | `time_ps, msd_angstrom2, dim=3, fit_range_fraction=(0.2, 0.8)` | 基于 Einstein 关系式由 MSD 曲线拟合自扩散系数 $D\ (10^{-9}\ \text{m}^2/\text{s})$ | `d, r2 = calculate_diffusion_coefficient(t, msd)` |

---

### 2.9 `ai_agent` 自然语言交互引擎

| 类 / 方法 | 核心入参 (Signature) | 功能说明 | 快速调用示例 |
|---|---|---|---|
| `Agent.run` | `prompt: str, dry_run: bool = False` | 解析科研自然语言指令，规划并调用底层函数，生成图件 | `res = Agent().run("帮我绘制 40min 毛细凝聚与 26h 体相水氧化的对比动力学图")` |
| `ToolRegistry.register` | `name=None, description=None, tags=None` | `@tool` 函数装饰器，自动抽取签名暴露给 LLM Schema | `@tool(name="my_calc", tags=["custom"])` |

---

## 3. 典型场景代码示例

```python
from my_sci_toolkit import (
    plot_completion_time_bar,
    plot_conversion_alpha,
    simulate_nucleation_growth,
    Agent,
)

# 场景 1: 直接调用底层绘制 40min 毛细凝聚与 26h 体相水完成时间柱状对比图
fig = plot_completion_time_bar(
    systems=["Capillary", "Bulk water", "Air"],
    times_h=[40.0 / 60.0, 26.0, 280.0],
    unit_labels=["40 min", "26 h", "280 h"],
    save_path="./outputs/completion_comparison.png",
)

# 场景 2: 耦合固体成核生长动力学仿真
t_fast, alpha_fast = simulate_nucleation_growth(rate_constants=[0.05, 0.0, 0.0], duration=60.0)
t_slow, alpha_slow = simulate_nucleation_growth(rate_constants=[0.001, 0.0, 0.0], duration=60.0)

fig_alpha = plot_conversion_alpha(
    t_exp=[0, 10, 20, 30, 40, 50, 60],
    alpha_exp=[0.0, 0.25, 0.58, 0.82, 0.98, 1.0, 1.0],
    simulations=[
        {"t": t_fast, "alpha": alpha_fast, "label": "Capillary (Fast)", "color": "#C0392B"},
        {"t": t_slow, "alpha": alpha_slow, "label": "Bulk (Slow)", "color": "#2980B9"},
    ],
    save_path="./outputs/conversion_alpha.png",
)
```

---

## 4. 自然语言命令行调用 (CLI)

安装包后，无需编写 Python 代码，直接在任何终端运行 `my-sci`：

```bash
# 1. 打印工具箱所有暴露的底层科学工具清单
my-sci --list-tools

# 2. 自然语言直接驱动出图
my-sci "帮我绘制 40min 毛细凝聚与 26h 体相水氧化的对比动力学图"

# 3. 预检执行计划 (Dry-run 模式，仅返回参数规划，不实际生成文件)
my-sci "生成反应中间体台阶图对比" --dry-run
```

---

## 5. GitHub 开源工程初始化与推送指南

若您需要将当前工程开源托管至 GitHub，可按如下标准步骤在项目根目录下操作：

```bash
# 步骤 1: 进入项目目录
cd e:\Code_rewrite

# 步骤 2: 初始化本地 git 仓库 (如果尚未初始化)
git init

# 步骤 3: 检查未跟踪文件并添加到暂存区
git add .gitignore LICENSE README.md pyproject.toml my_sci_toolkit/ examples/ tests/ .github/

# 步骤 4: 提交首次开源构建版本
git commit -m "feat: initial open-source release of chem-scitoolkit with modern architecture and AI agent"

# 步骤 5: 将主分支命名为 main
git branch -M main

# 步骤 6: 关联远程 GitHub 仓库 (请先在 GitHub 网页新建一个空的 chem-scitoolkit 仓库)
git remote add origin https://github.com/<your-username>/chem-scitoolkit.git

# 步骤 7: 推送代码到 GitHub
git push -u origin main
```
