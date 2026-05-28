
    let paretoFront = [
      { candidate: "hybrid_excitation_if_plus_20", label: "混合励磁 +20", meanScore: 0.6934436394, feasible: 1, loss: 4468.317, family: "混合励磁", color: "#d6b260" },
      { candidate: "baseline", label: "基线方案", meanScore: 0.6780609637, feasible: 1, loss: 4809.21, family: "内置式永磁同步电机基线", color: "#37c7b4" },
      { candidate: "winding_series_torque", label: "串联增矩", meanScore: 0.6734790967, feasible: 1, loss: 4915.7199, family: "绕组重构", color: "#62c486" },
      { candidate: "hybrid_excitation_if_minus_20", label: "混合励磁 -20", meanScore: 0.6623273423, feasible: 1, loss: 5170.347, family: "混合励磁", color: "#a88af0" },
      { candidate: "winding_parallel_speed", label: "并联高速", meanScore: 0.5000309486, feasible: 0, loss: 2083.93185, family: "绕组重构", color: "#d08b45" },
      { candidate: "variable_flux_psi70", label: "磁链 70%", meanScore: 0.4540878213, feasible: 0, loss: 2928.786, family: "可变磁链", color: "#ef6a73" },
      { candidate: "variable_flux_psi55", label: "磁链 55%", meanScore: 0.4235644211, feasible: 0, loss: 3588.795, family: "可变磁链", color: "#d96ba6" }
    ];

    let cycleRows = [
      ["hybrid_excitation_if_plus_20","urban_low_speed",1,1271.655,0.702303908],["baseline","urban_low_speed",1,1376.97,0.685405657],["winding_series_torque","urban_low_speed",1,1408.0878,0.680567206],["winding_parallel_speed","urban_low_speed",1,1455.03435,0.673395481],["hybrid_excitation_if_minus_20","urban_low_speed",1,1488.081,0.668437134],["variable_flux_psi70","urban_low_speed",1,1981.77,0.602195605],["variable_flux_psi55","urban_low_speed",1,2384.235,0.557182218],
      ["hybrid_excitation_if_plus_20","highway_high_speed",1,538.482,0.847821184],["baseline","highway_high_speed",1,592.62,0.835045176],["winding_series_torque","highway_high_speed",1,608.8446,0.83129099],["winding_parallel_speed","highway_high_speed",1,628.8975,0.826697365],["hybrid_excitation_if_minus_20","highway_high_speed",1,654.906,0.820814544],["variable_flux_psi70","highway_high_speed",1,947.016,0.760067859],["variable_flux_psi55","highway_high_speed",1,1204.56,0.713511045],
      ["hybrid_excitation_if_plus_20","launch_peak_torque",1,2658.18,0.530205826],["baseline","launch_peak_torque",1,2839.62,0.513732058],["winding_series_torque","launch_peak_torque",1,2898.7875,0.508579094],["hybrid_excitation_if_minus_20","launch_peak_torque",1,3027.36,0.49773035],["variable_flux_psi70","launch_peak_torque",0,0,0],["variable_flux_psi55","launch_peak_torque",0,0,0],["winding_parallel_speed","launch_peak_torque",0,0,0]
    ].map(([candidate, cycle, feasibleWeight, copperLoss, score]) => ({ candidate, cycle, feasibleWeight, copperLoss, score }));

    let ironLossRows = [
      [0,0,0],[1000,4298.75,59.49],[2000,15784.02,52.96],[3000,34363.88,45.81],[4000,60005.51,40.02],[5000,94605.11,35.45],[6000,138617.18,31.82],[7000,192612.02,28.6],[8000,null,null],[10000,null,null],[12000,null,null],[14000,null,null],[16000,null,null],[18000,null,null]
    ].map(([speed, ironLoss, efficiency]) => ({ speed, ironLoss, efficiency }));

    const routes = [
      ["IPMSM d-axis field weakening", "Mature control route for high-speed voltage margin.", 95, "top"],
      ["MTPA/FW/MTPV continuous control", "Continuous switch between low-speed current optimum and high-speed voltage limit.", 92, "top"],
      ["Nonlinear flux LUT", "Use psi_d/psi_q lookup tables to represent saturation and cross saturation.", 78, "high"],
      ["Magnetic circuit co-design", "Amplify flux modulation through pole ratio and bridge geometry.", 62, "medium"],
      ["Hybrid excitation", "Strong current Pareto result, with hardware, thermal and safety complexity.", 52, "medium"],
      ["Variable magnetization state", "Can change equivalent flux, but life, observability and pulse chain need verification.", 40, "medium"],
      ["Winding reconfiguration / multiphase", "May change equivalent turns and fault tolerance; switching transient is core risk.", 36, "mid-low"],
      ["Iron-loss thermal loop", "Determines real high-speed performance and should be a next scoring term.", 30, "support"]
    ];

    const cycleLabels = {
      urban_low_speed: "城市低速",
      highway_high_speed: "高速巡航",
      launch_peak_torque: "起步峰值"
    };

    let algorithmRows = [
      ["MTPA / 弱磁 / MTPV", "Input Vdc, Imax, Ld/Lq, flux and speed-torque limits; output id/iq trajectories.", "Controller trajectory table, voltage-margin map and calibration LUT.", "Keep high speed inside voltage margin."],
      ["Nonlinear flux LUT interpolation", "Input psi_d/psi_q tables, temperature axis and clipping rules.", "Flux lookup module, interpolation guard and extrapolation warning.", "Closer saturation and torque prediction."],
      ["Weighted workload Pareto scoring", "Input customer workload weights, feasible points, copper loss and candidate families.", "Candidate ranking, benefit chart and customer brief.", "Moves choice from experience to data ranking."],
      ["Bertotti 铁耗估算", "Input frequency, B peak and three iron-loss coefficients; output high-speed loss trend.", "Iron-loss sweep curve, high-speed risk threshold and material checklist.", "Expose high-speed efficiency risk earlier."],
      ["Safety boundary judgement", "Input voltage ellipse, current circle, demag and peak-workload constraints.", "Reachability radar, risk signal and protection strategy entry.", "Avoid optimizing efficiency while ignoring reliability."],
      ["Control LUT generation", "Input optimal trajectory and constraint boundary; output writable control lookup data.", "JSON LUT, calibration version and bench replay interface.", "Turn algorithm output into deliverable software asset."]
    ];

    let deliveryItems = [
      ["方案收益", "展示优化前后评分、铜耗、峰值可达性和高速风险。"],
      ["控制算法", "包含 MTPA、弱磁、MTPV 与控制 LUT 生成接口。"],
      ["数据证据", "包含实验 CSV、参数 JSON、模型限制和复核说明。"],
      ["验证路线", "明确有限元、硬件在环、台架和保护策略的下一步任务。"]
    ];

    const algorithmMaturityRows = [
      {
        id: "mtpa_fw_mtpv",
        name: "MTPA / 弱磁 / MTPV",
        stage: "控制轨迹可交付",
        currentFit: ["混合励磁", "内置式永磁同步电机基线"],
        dimensions: { model: 92, data: 78, api: 84, validation: 68 },
        data: "Vdc、Imax、Ld/Lq、磁链、转速转矩边界",
        interface: "控制轨迹表、标定 LUT、弱磁电压裕度接口",
        validation: "HIL 回放、台架电压椭圆、峰值电流保护",
        value: "把推荐方案转成可写入控制器的 id/iq 轨迹"
      },
      {
        id: "nonlinear_flux_lut",
        name: "非线性磁链 LUT",
        stage: "模型精度增强",
        currentFit: ["混合励磁", "可变磁链"],
        dimensions: { model: 78, data: 62, api: 72, validation: 54 },
        data: "psi_d/psi_q、温度轴、饱和与交叉饱和样本",
        interface: "插值守护、越界告警、温度修正查表服务",
        validation: "材料数据、FEA 磁密分布、热态扭矩复核",
        value: "降低饱和区预测偏差，解释为什么同一电流收益不同"
      },
      {
        id: "weighted_pareto",
        name: "加权工况 Pareto",
        stage: "客户决策已接入",
        currentFit: ["混合励磁", "绕组重构", "可变磁链", "内置式永磁同步电机基线"],
        dimensions: { model: 88, data: 86, api: 90, validation: 74 },
        data: "客户工况权重、铜耗、可达性、候选方案族",
        interface: "方案排序、收益瀑布、客户摘要和决策包导出",
        validation: "权重敏感性、离线回退、接口契约测试",
        value: "把经验选型变成可复算、可解释、可交付的客户决策"
      },
      {
        id: "bertotti_iron_loss",
        name: "Bertotti 铁耗估算",
        stage: "高速风险识别",
        currentFit: ["混合励磁", "可变磁链"],
        dimensions: { model: 72, data: 58, api: 64, validation: 48 },
        data: "频率、峰值磁密、kh/kc/ke 系数、PWM 谐波假设",
        interface: "铁耗扫描曲线、高速阈值、材料复核清单",
        validation: "硅钢片数据、频域损耗、温升和效率地图校准",
        value: "提前暴露高速效率风险，避免只按铜耗做推荐"
      },
      {
        id: "safety_boundary",
        name: "安全边界判断",
        stage: "准入门槛",
        currentFit: ["混合励磁", "绕组重构", "可变磁链"],
        dimensions: { model: 82, data: 70, api: 76, validation: 60 },
        data: "电压椭圆、电流圆、退磁边界、峰值工况约束",
        interface: "可达性雷达、风险闭环任务、阶段门状态",
        validation: "保护策略、短路边界、高温退磁和台架准入",
        value: "在收益展示前先说明哪些方案可以安全推进"
      }
    ];
    let activeAlgorithmMaturity = "weighted_pareto";

    const fmt = new Intl.NumberFormat("zh-CN", { maximumFractionDigits: 3 });
    const tooltip = document.getElementById("tooltip");
    let selected = "hybrid_excitation_if_plus_20";
    let compareCandidate = "baseline";
    let playbackTimer = null;
    let playbackIndex = 0;
    let latestBrief = "";
    let simulatedRecommendation = "hybrid_excitation_if_plus_20";
    let activePreset = "均衡客户";
    let activeDrilldown = "benefit";
    let benchmarkFamily = "全部路线";
    let backendHealth = null;
    let backendSchema = null;
    let backendScenarioState = null;
    let apiSyncLog = {};
    const benchmarkFamilies = ["全部路线", "混合励磁", "绕组重构", "可变磁链", "内置式永磁同步电机基线"];
    const businessAssumptions = {
      production: 50000,
      mileage: 15000,
      energyPrice: 0.8,
      validationInvestment: 180
    };
    const drilldownTabs = [
      ["benefit", "收益拆解", "评分、铜耗和工况收益", "01"],
      ["risk", "风险闭环", "可达性、高速和实测边界", "02"],
      ["delivery", "交付动作", "软件、数据和验证任务", "03"],
      ["evidence", "证据链路", "数据来源和复核节点", "04"]
    ];
    const presentationSteps = [
      ["benefits", "收益变化", "先讲优化前后的量化收益。", 25],
      ["solution-drilldown", "方案诊断", "再下钻到收益、风险和交付闭环。", 50],
      ["business-case", "商业 ROI", "把技术收益转成客户可决策的投入回收。", 75],
      ["evidence", "证据与边界", "最后回到数据来源、模型边界和复核路线。", 100]
    ];
    let presentationIndex = 0;
    const scenarioPresets = [
      ["均衡客户", { urban_low_speed: 40, highway_high_speed: 35, launch_peak_torque: 25 }],
      ["城市运营", { urban_low_speed: 60, highway_high_speed: 20, launch_peak_torque: 20 }],
      ["高速通勤", { urban_low_speed: 20, highway_high_speed: 60, launch_peak_torque: 20 }],
      ["性能起步", { urban_low_speed: 25, highway_high_speed: 20, launch_peak_torque: 55 }]
    ];
    const evidenceGapRows = [
      {
        id: "voltage_margin",
        title: "电压裕度闭环",
        owner: "控制算法",
        due: "T+3 天",
        evidence: "Vmax - |Vdq| 曲线、弱磁电压椭圆、峰值电流限制",
        action: "补齐高速弱磁段电压裕度，回填阶段门 G2 和风险边界。",
        impact: "证明方案不是只降低铜耗，而是在高速约束内可执行。",
        base: 82,
        cost: 38,
        routeFit: ["混合励磁", "可变磁链", "内置式永磁同步电机基线"]
      },
      {
        id: "demag_thermal",
        title: "退磁与温升证据",
        owner: "电磁与材料",
        due: "T+7 天",
        evidence: "高温退磁曲线、磁桥应力、FEA 磁密与热边界",
        action: "把材料牌号、温度轴和退磁裕度接入验证清单。",
        impact: "回答客户关于寿命、短路边界和高温可靠性的追问。",
        base: 76,
        cost: 54,
        routeFit: ["混合励磁", "可变磁链"]
      },
      {
        id: "iron_loss_material",
        title: "铁耗材料校准",
        owner: "损耗建模",
        due: "T+5 天",
        evidence: "硅钢片 kh/kc/ke、PWM 谐波、效率地图高转速切片",
        action: "把 Bertotti 系数从干净室假设切换到客户材料假设。",
        impact: "让高速效率风险从提醒项变成可量化决策项。",
        base: 70,
        cost: 42,
        routeFit: ["混合励磁", "绕组重构", "可变磁链", "内置式永磁同步电机基线"]
      },
      {
        id: "hil_bench_replay",
        title: "HIL 与台架回放",
        owner: "验证工程",
        due: "T+10 天",
        evidence: "控制 LUT 版本、HIL 回放记录、台架准入和保护策略日志",
        action: "把当前推荐方案导入 HIL 回放，再形成台架准入记录。",
        impact: "把看板结论转换成客户可以评审的验证记录。",
        base: 68,
        cost: 60,
        routeFit: ["混合励磁", "绕组重构", "可变磁链", "内置式永磁同步电机基线"]
      }
    ];
    let activeEvidenceGap = "voltage_margin";
    const reviewQuestionRows = [
      { id: "benefit", category: "收益", question: "这套方案能带来多少收益？", concern: "客户希望看到前后变化和 ROI", evidence: "收益瀑布 + ROI 测算", next: "导出决策包并固化客户工况权重" },
      { id: "risk", category: "风险", question: "为什么不能直接承诺量产收益？", concern: "客户关注模型边界和责任口径", evidence: "证据缺口优先级 + 阶段门", next: "补齐电压裕度、退磁、铁耗和台架证据" },
      { id: "algorithm", category: "算法", question: "算法具体落地到哪里？", concern: "客户担心只是概念展示", evidence: "算法成熟度矩阵 + 控制 LUT", next: "输出控制轨迹表和接口版本" },
      { id: "timeline", category: "验证", question: "下一轮验证怎么排期？", concern: "客户需要明确负责人和节奏", evidence: "阶段门 + 证据缺口", next: "按 T+3/T+5/T+7/T+10 天节奏补证" },
      { id: "comparison", category: "对比", question: "为什么不是选择铜耗最低的方案？", concern: "客户容易只盯单项指标", evidence: "方案对比 + 可达性雷达", next: "用权重模拟现场复算推荐排序" }
    ];
    let activeReviewQuestion = "benefit";
    const minutesModes = [
      { id: "technical", label: "技术评审", badge: "算法与证据", owner: "客户技术 / 电驱团队", focus: "聚焦算法落地、工况可达性和补证路径" },
      { id: "business", label: "商务评审", badge: "ROI 口径", owner: "客户项目 / 商务团队", focus: "聚焦年化收益、回收周期和量产承诺边界" },
      { id: "validation", label: "验证推进", badge: "阶段门", owner: "双方验证 / HIL 台架团队", focus: "聚焦责任人、截止时间、证据产物和闭环条件" }
    ];
    let activeMinutesMode = "technical";
    let activeValidationStep = "evidence_gap";
    let activeValidationRisk = "voltage";
    const OPENDESIGN_TOKENS = {
      product: "customer_dashboard",
      file: "reports/open_design_dashboard_spec.json",
      colors: {
        primary: "#d6b260",
        dataCyan: "#37c7b4",
        success: "#62c486",
        warning: "#d08b45",
        danger: "#ef6a73",
        surface: "#12141b",
        background: "#08090d",
        text: "#f8ecd2"
      },
      radius: { card: 8, control: 8 },
      components: ["panel", "kpi", "chart", "compare-card", "weight-control", "delivery-item", "decision-summary", "benefit-waterfall", "scenario-presets", "interactive-insights", "solution-drilldown", "confidence-meter", "evidence-ladder", "business-case", "roi-calculator", "presentation-mode", "decision-pack-export", "meeting-script", "sensitivity-matrix", "stage-gate-board", "evidence-gap-priority", "review-question-board", "decision-pack-preview", "customer-minutes-generator", "validation-action-timeline", "validation-risk-heatmap", "algorithm-maturity", "benchmark-board", "closure-board", "delivery-health"],
      states: ["待接入", "在线", "悬停", "选中", "导出中"],
      handoff: { status: "已接入", selector: "[data-design-system='opendesign-dashboard']" }
    };

    function byCandidate(id) { return paretoFront.find(d => d.candidate === id); }
    function svgEl(name, attrs = {}) {
      const el = document.createElementNS("http://www.w3.org/2000/svg", name);
      Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
      return el;
    }
    function svgText(svg, attrs, text) {
      const el = svgEl("text", attrs);
      el.textContent = text;
      svg.append(el);
      return el;
    }
    function clear(svg) { while (svg.firstChild) svg.removeChild(svg.firstChild); }
    function showTip(event, html) {
      tooltip.innerHTML = html;
      tooltip.style.left = `${Math.min(event.clientX + 14, window.innerWidth - 300)}px`;
      tooltip.style.top = `${event.clientY + 14}px`;
      tooltip.classList.add("visible");
    }
    function hideTip() { tooltip.classList.remove("visible"); }
    function scales(w, h, pad, xs, ys) {
      const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
      return {
        x: v => pad.l + ((v - minX) / (maxX - minX || 1)) * (w - pad.l - pad.r),
        y: v => h - pad.b - ((v - minY) / (maxY - minY || 1)) * (h - pad.t - pad.b),
        minX, maxX, minY, maxY
      };
    }
    function axes(svg, w, h, pad, xLabel, yLabel) {
      svg.append(svgEl("line", { class: "axis", x1: pad.l, y1: h - pad.b, x2: w - pad.r, y2: h - pad.b }));
      svg.append(svgEl("line", { class: "axis", x1: pad.l, y1: pad.t, x2: pad.l, y2: h - pad.b }));
      svgText(svg, { x: w - pad.r, y: h - 8, "text-anchor": "end" }, xLabel);
      svgText(svg, { x: 10, y: pad.t - 10 }, yLabel);
      for (let i = 1; i < 5; i++) {
        const y = pad.t + i * (h - pad.t - pad.b) / 5;
        svg.append(svgEl("line", { class: "grid-line", x1: pad.l, y1: y, x2: w - pad.r, y2: y }));
      }
    }
    function drawPareto() {
      const svg = document.getElementById("pareto-chart");
      clear(svg);
      const w = svg.clientWidth || 800, h = svg.clientHeight || 330, pad = { l: 58, r: 22, t: 24, b: 48 };
      svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
      axes(svg, w, h, pad, "加权铜耗 W（越低越好）", "综合得分");
      const s = scales(w, h, pad, paretoFront.map(d => d.loss), paretoFront.map(d => d.meanScore));
      paretoFront.forEach(d => {
        const dot = svgEl("circle", { class: `dot ${d.candidate === selected ? "active" : ""} ${d.candidate !== selected ? "dim" : ""}`, cx: s.x(d.loss), cy: s.y(d.meanScore), r: d.feasible ? 7 : 6, fill: d.color });
        dot.addEventListener("click", () => selectCandidate(d.candidate));
        dot.addEventListener("mousemove", e => showTip(e, `<strong>${d.label}</strong><br>综合得分 ${fmt.format(d.meanScore)}<br>加权铜耗 ${fmt.format(d.loss)} W<br>可达权重 ${d.feasible}`));
        dot.addEventListener("mouseleave", hideTip);
        svg.append(dot);
        svgText(svg, { x: s.x(d.loss) + 10, y: s.y(d.meanScore) - 8 }, d.label);
      });
    }
    function drawCycle() {
      const svg = document.getElementById("cycle-chart");
      clear(svg);
      const w = svg.clientWidth || 800, h = svg.clientHeight || 330, pad = { l: 54, r: 18, t: 24, b: 72 };
      svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
      axes(svg, w, h, pad, "客户工况", "得分");
      const cycles = ["urban_low_speed", "highway_high_speed", "launch_peak_torque"];
      const maxScore = Math.max(...cycleRows.map(d => d.score));
      const groupW = (w - pad.l - pad.r) / cycles.length;
      const barW = Math.max(5, groupW / paretoFront.length - 4);
      cycles.forEach((cycle, ci) => {
        svgText(svg, { x: pad.l + ci * groupW + groupW / 2, y: h - 22, "text-anchor": "middle" }, cycleLabels[cycle]);
        paretoFront.forEach((cand, bi) => {
          const row = cycleRows.find(d => d.candidate === cand.candidate && d.cycle === cycle);
          const bh = row.score / maxScore * (h - pad.t - pad.b);
          const x = pad.l + ci * groupW + 8 + bi * (barW + 4);
          const y = h - pad.b - bh;
          const bar = svgEl("rect", { class: `bar ${cand.candidate !== selected ? "dim" : ""}`, x, y, width: barW, height: bh, fill: cand.color });
          bar.addEventListener("click", () => selectCandidate(cand.candidate));
          bar.addEventListener("mousemove", e => showTip(e, `<strong>${cand.label}</strong><br>${cycleLabels[cycle]}<br>得分 ${fmt.format(row.score)}<br>铜耗 ${fmt.format(row.copperLoss)} W`));
          bar.addEventListener("mouseleave", hideTip);
          svg.append(bar);
        });
      });
    }
    function drawReach() {
      const svg = document.getElementById("reach-chart");
      clear(svg);
      const w = svg.clientWidth || 420, h = svg.clientHeight || 330, cx = w / 2, cy = h / 2 + 12, r = Math.min(w, h) * .32;
      svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
      const cycles = ["urban_low_speed", "highway_high_speed", "launch_peak_torque"];
      [0.33, 0.66, 1].forEach(level => svg.append(svgEl("circle", { cx, cy, r: r * level, fill: "none", stroke: "#e2e8f0" })));
      cycles.forEach((cycle, i) => {
        const a = -Math.PI / 2 + i * Math.PI * 2 / cycles.length;
        svg.append(svgEl("line", { x1: cx, y1: cy, x2: cx + Math.cos(a) * r, y2: cy + Math.sin(a) * r, stroke: "#cbd5e1" }));
        svgText(svg, { x: cx + Math.cos(a) * (r + 28), y: cy + Math.sin(a) * (r + 28), "text-anchor": "middle" }, cycleLabels[cycle]);
      });
      paretoFront.forEach(cand => {
        const points = cycles.map((cycle, i) => {
          const row = cycleRows.find(d => d.candidate === cand.candidate && d.cycle === cycle);
          const rr = r * row.feasibleWeight;
          const a = -Math.PI / 2 + i * Math.PI * 2 / cycles.length;
          return `${cx + Math.cos(a) * rr},${cy + Math.sin(a) * rr}`;
        }).join(" ");
        svg.append(svgEl("polygon", { points, fill: cand.color, opacity: cand.candidate === selected ? .22 : .035, stroke: cand.color, "stroke-width": cand.candidate === selected ? 3 : 1 }));
      });
    }
    function drawIronLoss() {
      const svg = document.getElementById("iron-loss-chart");
      clear(svg);
      const w = svg.clientWidth || 800, h = svg.clientHeight || 330, pad = { l: 58, r: 22, t: 24, b: 46 };
      svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
      axes(svg, w, h, pad, "转速（转/分）", "铁耗（瓦）");
      const valid = ironLossRows.filter(d => d.ironLoss !== null);
      const s = scales(w, h, pad, ironLossRows.map(d => d.speed), valid.map(d => d.ironLoss));
      const path = valid.map((d, i) => `${i ? "L" : "M"}${s.x(d.speed)},${s.y(d.ironLoss)}`).join(" ");
      svg.append(svgEl("path", { class: "line", d: path, stroke: "#ef6a73" }));
      valid.forEach(d => {
        const dot = svgEl("circle", { class: "dot", cx: s.x(d.speed), cy: s.y(d.ironLoss), r: 5, fill: "#ef6a73" });
        dot.addEventListener("mousemove", e => showTip(e, `<strong>${fmt.format(d.speed)} 转/分</strong><br>铁耗 ${fmt.format(d.ironLoss)} 瓦<br>效率 ${fmt.format(d.efficiency)}%`));
        dot.addEventListener("mouseleave", hideTip);
        svg.append(dot);
      });
      svg.append(svgEl("line", { x1: s.x(7000), y1: pad.t, x2: s.x(7000), y2: h - pad.b, stroke: "#d08b45", "stroke-dasharray": "5 5" }));
      svgText(svg, { x: s.x(7000) + 8, y: pad.t + 14 }, "100 Nm 可达边界");
    }
    function drawBenefit() {
      const svg = document.getElementById("benefit-chart");
      clear(svg);
      const w = svg.clientWidth || 800, h = svg.clientHeight || 330, pad = { l: 58, r: 24, t: 24, b: 56 };
      svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
      axes(svg, w, h, pad, "指标", "相对值");
      const baseline = byCandidate("baseline");
      const cand = byCandidate(selected);
      const launch = cycleRows.find(d => d.candidate === selected && d.cycle === "launch_peak_torque");
      const baseLaunch = cycleRows.find(d => d.candidate === "baseline" && d.cycle === "launch_peak_torque");
      const rows = [
        { name: "综合得分", before: baseline.meanScore, after: cand.meanScore, color: "#d6b260" },
        { name: "铜耗变化", before: 0, after: (baseline.loss - cand.loss) / baseline.loss, color: "#62c486" },
        { name: "峰值可达", before: baseLaunch.feasibleWeight, after: launch.feasibleWeight, color: "#d08b45" }
      ];
      const max = 1;
      const groupW = (w - pad.l - pad.r) / rows.length;
      rows.forEach((row, i) => {
        const x0 = pad.l + i * groupW + groupW * .24;
        const x1 = pad.l + i * groupW + groupW * .52;
        const bw = Math.max(18, groupW * .18);
        const beforeH = Math.max(0, row.before / max) * (h - pad.t - pad.b);
        const afterH = Math.max(0, row.after / max) * (h - pad.t - pad.b);
        svg.append(svgEl("rect", { class: "bar", x: x0, y: h - pad.b - beforeH, width: bw, height: beforeH, fill: "#94a3b8", opacity: .75 }));
        const after = svgEl("rect", { class: "bar", x: x1, y: h - pad.b - afterH, width: bw, height: afterH, fill: row.color });
        after.style.transformOrigin = `${x1 + bw / 2}px ${h - pad.b}px`;
        after.style.animation = "growBar .8s ease both";
        svg.append(after);
        svgText(svg, { x: pad.l + i * groupW + groupW / 2, y: h - 22, "text-anchor": "middle" }, row.name);
        svgText(svg, { x: x0 + bw / 2, y: h - pad.b + 14, "text-anchor": "middle" }, "前");
        svgText(svg, { x: x1 + bw / 2, y: h - pad.b + 14, "text-anchor": "middle" }, "后");
      });
    }
    function animateValue(selector, value, suffix = "", digits = 1) {
      const el = document.querySelector(selector);
      if (!el) return;
      const start = Number(el.dataset.current || 0);
      const duration = 700;
      const t0 = performance.now();
      function tick(now) {
        const t = Math.min(1, (now - t0) / duration);
        const eased = 1 - Math.pow(1 - t, 3);
        const current = start + (value - start) * eased;
        el.textContent = `${current > 0 && suffix === "%" ? "+" : ""}${current.toFixed(digits)}${suffix}`;
        if (t < 1) requestAnimationFrame(tick);
        else el.dataset.current = value;
      }
      requestAnimationFrame(tick);
    }
    function renderBenefits() {
      const baseline = byCandidate("baseline");
      const cand = byCandidate(selected);
      const launch = cycleRows.find(d => d.candidate === selected && d.cycle === "launch_peak_torque");
      const baseLaunch = cycleRows.find(d => d.candidate === "baseline" && d.cycle === "launch_peak_torque");
      const scoreGain = (cand.meanScore / baseline.meanScore - 1) * 100;
      const lossGain = (cand.loss / baseline.loss - 1) * 100;
      const reachGain = (launch.feasibleWeight - baseLaunch.feasibleWeight) * 100;
      const riskIndex = cand.feasible === 1 ? 2 : 7;
      animateValue('[data-animate="scoreGain"]', scoreGain, "%", 1);
      animateValue('[data-animate="lossGain"]', lossGain, "%", 1);
      animateValue('[data-animate="reachGain"]', reachGain, "%", 0);
      animateValue('[data-animate="riskIndex"]', riskIndex, "", 0);
      document.getElementById("customer-summary").textContent = `${cand.label} 相对基线综合评分变化 ${scoreGain.toFixed(1)}%，加权铜耗变化 ${lossGain.toFixed(1)}%，峰值工况可达变化 ${reachGain.toFixed(0)}%。`;
      renderDecisionSummary(scoreGain, lossGain, reachGain, riskIndex);
      renderBenefitWaterfall(scoreGain, lossGain, reachGain, riskIndex);
      renderCustomerBrief(cand, scoreGain, lossGain, reachGain, riskIndex);
      drawBenefit();
    }
    function renderDecisionSummary(scoreGain, lossGain, reachGain, riskIndex) {
      const cand = byCandidate(selected);
      const decision = cand.feasible === 1 && scoreGain >= 0 ? "建议进入下一轮验证" : "建议作为风险备选";
      const cards = [
        ["客户决策", decision, cand.feasible === 1 ? "约束可达，适合推进验证" : "峰值工况存在不可达风险"],
        ["收益方向", lossGain <= 0 ? "铜耗下降" : "铜耗上升", `相对基线 ${lossGain.toFixed(1)}%`],
        ["验证优先级", riskIndex <= 3 ? "高优先级" : "需先复核", `风险指数 ${riskIndex}/10`]
      ];
      document.getElementById("decision-grid").innerHTML = cards.map(([label, value, copy]) => `
        <article class="decision-card">
          <span>${label}</span>
          <strong>${value}</strong>
          <span>${copy}</span>
        </article>
      `).join("");
    }
    function renderBenefitWaterfall(scoreGain, lossGain, reachGain, riskIndex) {
      const rows = [
        ["评分提升", scoreGain, "%", scoreGain >= 0],
        ["铜耗变化", lossGain, "%", lossGain <= 0],
        ["峰值可达", reachGain, "%", reachGain >= 0],
        ["风险指数", -riskIndex * 10, "", riskIndex <= 3]
      ];
      document.getElementById("benefit-waterfall").innerHTML = rows.map(([label, value, suffix, positive]) => {
        const width = Math.min(100, Math.max(8, Math.abs(value)));
        const shown = suffix === "%" ? `${value >= 0 ? "+" : ""}${value.toFixed(1)}%` : `${Math.abs(value / 10).toFixed(0)}/10`;
        return `
          <div class="waterfall-row">
            <span>${label}</span>
            <span class="waterfall-track"><i class="waterfall-fill ${positive ? "" : "negative"}" style="width:${width}%"></i></span>
            <strong>${shown}</strong>
          </div>
        `;
      }).join("");
    }
    function renderCustomerBrief(cand, scoreGain, lossGain, reachGain, riskIndex) {
      latestBrief = [
        `当前推荐方案：${cand.label}。`,
        `相对基线综合评分变化 ${scoreGain.toFixed(1)}%，加权铜耗变化 ${lossGain.toFixed(1)}%，峰值工况可达权重变化 ${reachGain.toFixed(0)}%。`,
        "客户价值：用于优先筛选下一轮有限元、硬件在环和台架验证方案。",
        `风险提示：当前风险指数 ${riskIndex}/10，仍需接入材料、温升、逆变器损耗和实测台架数据。`
      ].join("");
      document.getElementById("customer-brief").textContent = latestBrief;
    }    function renderCompareBoard() {
      const current = byCandidate(selected);
      const compare = byCandidate(compareCandidate) || byCandidate("baseline");
      const currentLaunch = cycleRows.find(d => d.candidate === selected && d.cycle === "launch_peak_torque");
      const compareLaunch = cycleRows.find(d => d.candidate === compare.candidate && d.cycle === "launch_peak_torque");
      const scoreDiff = (current.meanScore - compare.meanScore) * 100;
      const lossDiff = ((compare.loss - current.loss) / compare.loss) * 100;
      const reachDiff = (currentLaunch.feasibleWeight - compareLaunch.feasibleWeight) * 100;
      document.getElementById("compare-board").innerHTML = [
        ["当前方案", `${current.label}`, `得分 ${fmt.format(current.meanScore)} · 铜耗 ${fmt.format(current.loss)} W`],
        ["对比方案", `${compare.label}`, `得分 ${fmt.format(compare.meanScore)} · 铜耗 ${fmt.format(compare.loss)} W`],
        ["差异结论", `${scoreDiff >= 0 ? "+" : ""}${scoreDiff.toFixed(1)} 分`, `铜耗收益 ${lossDiff.toFixed(1)}%，峰值可达变化 ${reachDiff.toFixed(0)}%`],
      ].map(([title, strong, copy]) => `
        <article class="compare-card">
          <strong>${title}</strong>
          <div style="font-size:22px;font-weight:820;line-height:1.1;margin-bottom:8px">${strong}</div>
          <p>${copy}</p>
        </article>
      `).join("");
      document.getElementById("compare-brief").textContent =
        `${current.label} 相比 ${compare.label} 综合评分差异 ${scoreDiff.toFixed(1)} 分，铜耗收益 ${lossDiff.toFixed(1)}%，建议结合峰值可达性与验证投入做路线判断。`;
    }
    function renderCompareSelector() {
      const select = document.getElementById("compare-target");
      if (!paretoFront.some(item => item.candidate === compareCandidate) || compareCandidate === selected) {
        compareCandidate = (paretoFront.find(item => item.candidate !== selected) || paretoFront[0]).candidate;
      }
      select.innerHTML = paretoFront
        .filter(item => item.candidate !== selected)
        .map(item => `<option value="${item.candidate}" ${item.candidate === compareCandidate ? "selected" : ""}>${item.label}</option>`)
        .join("");
    }
    function readScenarioWeights() {
      const raw = {};
      document.querySelectorAll("[data-weight-input]").forEach(input => {
        raw[input.dataset.weightInput] = Number(input.value || 0);
        const label = document.getElementById(`weight-${input.dataset.weightInput}`);
        if (label) label.textContent = `${raw[input.dataset.weightInput]}%`;
      });
      const total = Object.values(raw).reduce((sum, value) => sum + value, 0) || 1;
      return Object.fromEntries(Object.entries(raw).map(([key, value]) => [key, value / total]));
    }
    function calculateWeightedRanking() {
      const weights = readScenarioWeights();
      return paretoFront.map(candidate => {
        const rows = cycleRows.filter(row => row.candidate === candidate.candidate);
        const simulatedScore = rows.reduce((sum, row) => sum + row.score * (weights[row.cycle] || 0), 0);
        const simulatedFeasible = rows.reduce((sum, row) => sum + row.feasibleWeight * (weights[row.cycle] || 0), 0);
        return { ...candidate, simulatedScore, simulatedFeasible };
      }).sort((a, b) => b.simulatedScore - a.simulatedScore);
    }
    function setScenarioWeights(weights, presetName = "自定义") {
      Object.entries(weights).forEach(([key, value]) => {
        const input = document.querySelector(`[data-weight-input="${key}"]`);
        if (input) input.value = value;
      });
      activePreset = presetName;
      renderWeightSimulator();
    }
    function renderScenarioPresets() {
      const wrap = document.getElementById("scenario-presets");
      if (!wrap) return;
      wrap.innerHTML = scenarioPresets.map(([name]) => `
        <button class="preset-button ${name === activePreset ? "active" : ""}" type="button" data-scenario-preset="${name}">${name}</button>
      `).join("");
      wrap.querySelectorAll("[data-scenario-preset]").forEach(button => {
        button.addEventListener("click", () => {
          const preset = scenarioPresets.find(([name]) => name === button.dataset.scenarioPreset);
          if (preset) setScenarioWeights(preset[1], preset[0]);
        });
      });
    }
    function renderInteractiveInsights(ranking) {
      const current = byCandidate(selected);
      const top = ranking[0];
      const baselineRank = ranking.findIndex(item => item.candidate === "baseline") + 1;
      const selectedRank = ranking.findIndex(item => item.candidate === selected) + 1;
      const launch = cycleRows.find(row => row.candidate === selected && row.cycle === "launch_peak_torque");
      const insights = [
        ["推荐", top.candidate === selected ? "当前选中方案仍保持推荐位" : `模拟权重推荐 ${top.label}`],
        ["排名", `${current.label} 当前排名第 ${selectedRank}，基线排名第 ${baselineRank}`],
        ["约束", launch.feasibleWeight === 1 ? "起步峰值工况可达，适合继续比较收益" : "起步峰值不可达，需先复核电压和电流边界"]
      ];
      document.getElementById("interactive-insights").innerHTML = insights.map(([title, copy], index) => `
        <article class="insight-item">
          <b>${index + 1}</b>
          <span><strong>${title}</strong><span>${copy}</span></span>
        </article>
      `).join("");
    }
    function renderWeightSimulator() {
      const ranking = calculateWeightedRanking();
      const top = ranking[0];
      simulatedRecommendation = top.candidate;
      document.getElementById("weight-recommendation").textContent =
        `当前权重推荐 ${top.label}，模拟得分 ${fmt.format(top.simulatedScore)}，可达权重 ${fmt.format(top.simulatedFeasible)}。`;
      document.getElementById("simulated-ranking").innerHTML = ranking.slice(0, 5).map((item, index) => `
        <article class="ranking-row">
          <strong>${index + 1}</strong>
          <span><strong>${item.label}</strong><br>${item.family}</span>
          <strong>${fmt.format(item.simulatedScore)}</strong>
        </article>
      `).join("");
      renderScenarioPresets();
      renderInteractiveInsights(ranking);
    }    function renderDeliveryHealth() {
      const grid = document.getElementById("health-grid");
      if (!grid) return;
      const apiOnline = document.getElementById("api-status")?.textContent === "接口已连接";
      const healthCopy = backendHealth
        ? `运行时健康检查通过，页面${backendHealth.pageAvailable ? "已挂载" : "未挂载"}，后端返回 ${backendHealth.counts.paretoFront} 个方案、${backendHealth.counts.cycleRows} 条工况记录、${backendHealth.counts.ironLossRows} 条铁耗记录。`
        : "等待 /api/health 运行时健康检查";
      const schemaCopy = backendSchema
        ? `API schema verified: ${backendSchema.endpoints.length} endpoints aligned with frontend fetch paths.`
        : "Waiting for /api/schema contract check";
      const checks = [
        ["API contract", backendSchema ? "verified" : "pending", schemaCopy] ,
        ["接口联调", apiOnline ? "已连接" : "离线回退", apiOnline ? healthCopy : "使用本地回退数据"] ,
        ["OpenDesign", "已接入", "设计令牌、组件角色和规格可导出"] ,
        ["证据链", "已挂载", "EXP-010、EXP-011、Wiki 与设计 handoff 可追溯"] ,
        ["交互能力", "已启用", "对标、ROI、权重模拟、诊断和演示模式可用"] ,
        ["导出能力", "已启用", "摘要、设计规格和客户决策包可复制"]
      ];
      grid.innerHTML = checks.map(([title, state, copy]) => `
        <article class="health-item">
          <span><i class="health-dot"></i>${title}</span>
          <strong>${state}</strong>
          <span>${copy}</span>
        </article>
      `).join("");
      renderApiSyncLog();
    }
    function renderApiSyncLog() {
      const grid = document.getElementById("api-sync-log");
      if (!grid) return;
      const basePaths = ["/api/dashboard", "/api/health", "/api/schema", "/api/scenario-state", "/api/decision-pack", "/api/session-snapshot", "/api/customer-brief", "/api/design-spec"];
      const paths = ["/api/dashboard", "/api/health", "/api/schema", "/api/scenario-state", "/api/decision-pack", "/api/session-snapshot", "/api/customer-brief", "/api/design-spec"];
      paths.push(
        ...Object.keys(apiSyncLog).filter(path => path.startsWith("/api/") && !basePaths.includes(path))
      );
      grid.innerHTML = paths.map(path => {
        const item = apiSyncLog[path];
        const state = item ? (item.ok ? "ok" : "error") : "pending";
        const detail = item?.message || "waiting";
        return `
          <article class="api-sync-item ${item && !item.ok ? "error" : ""}">
            <strong>${path}</strong>
            <span>${state}</span>
            <span>${detail}</span>
          </article>
        `;
      }).join("");
    }
    function recordApiSync(path, ok, message = "synced") {
      apiSyncLog[path] = {
        ok,
        message,
        at: new Date().toISOString()
      };
      renderApiSyncLog();
    }
    function applySessionSnapshotApiSyncLog(savedLog) {
      if (!savedLog || typeof savedLog !== "object") return;
      Object.entries(savedLog).forEach(([path, item]) => {
        if (!path.startsWith("/api/") || !item || typeof item !== "object") return;
        apiSyncLog[path] = {
          ...item,
          ok: Boolean(item.ok),
          message: `restored: ${item.message || "saved session"}`
        };
      });
      renderApiSyncLog();
    }
    function renderSessionSnapshotStatus(metadata, candidate = "none") {
      const status = document.getElementById("session-snapshot-status");
      if (!status) return;
      if (!metadata?.snapshotId) {
        status.textContent = "session-snapshot: none";
        return;
      }
      const stamp = metadata.updatedAt || metadata.createdAt || "saved";
      status.textContent = `session-snapshot: ${candidate} | ${metadata.snapshotId} | ${stamp}`;
    }
    function renderClosureBoard() {
      const grid = document.getElementById("closure-grid");
      if (!grid) return;
      const ctx = calculateCandidateContext();
      const highRisk = !ctx.cand.feasible || ctx.feasibleCycles < 3;
      const tasks = [
        ["电压裕度复核", highRisk ? "高优先级" : "待接入", "高速弱磁段检查 Vmax - |Vdq|，确认不撞电压椭圆。", highRisk ? "risk" : ""],
        ["退磁裕度复核", "待复核", "高温、负 id 和短路边界用材料与 FEA 数据复核。", ""],
        ["铁耗系数校准", "进行中", "用硅钢片、频率、磁密分布和谐波数据校准 Bertotti 系数。", ""],
        ["台架闭环验证", ctx.confidence > 75 ? "可排期" : "需补证据", "把当前推荐方案进入 HIL、台架和保护策略联调。", ctx.confidence > 75 ? "done" : "risk"]
      ];
      grid.innerHTML = tasks.map(([title, status, copy, tone]) => `
        <article class="closure-card ${tone}">
          <span class="closure-status">${status}</span>
          <strong>${title}</strong>
          <span>当前方案 ${ctx.cand.label}</span>
          <p>${copy}</p>
        </article>
      `).join("");
    }    function renderBenchmarkBoard() {
      const toolbar = document.getElementById("benchmark-toolbar");
      const grid = document.getElementById("benchmark-grid");
      const summary = document.getElementById("benchmark-summary");
      if (!toolbar || !grid || !summary) return;
      toolbar.innerHTML = benchmarkFamilies.map(family => `
        <button class="preset-button ${family === benchmarkFamily ? "active" : ""}" type="button" data-benchmark-family="${family}">${family}</button>
      `).join("");
      toolbar.querySelectorAll("[data-benchmark-family]").forEach(button => {
        button.addEventListener("click", () => {
          benchmarkFamily = button.dataset.benchmarkFamily;
          renderBenchmarkBoard();
        });
      });
      const baseline = byCandidate("baseline");
      const items = paretoFront
        .filter(item => benchmarkFamily === "全部路线" || item.family === benchmarkFamily)
        .slice()
        .sort((a, b) => b.meanScore - a.meanScore);
      grid.innerHTML = items.map(item => {
        const scorePct = Math.max(0, Math.min(100, item.meanScore / 0.72 * 100));
        const lossGain = (baseline.loss - item.loss) / baseline.loss * 100;
        const riskPct = item.feasible ? 28 : 78;
        const feasibleText = item.feasible ? "工况可达" : "峰值待复核";
        return `
          <article class="benchmark-card ${item.candidate === selected ? "active" : ""}" data-benchmark-candidate="${item.candidate}">
            <span>${item.family}</span>
            <strong>${item.label}</strong>
            <span>加权铜耗 ${fmt.format(item.loss)} W · ${feasibleText}</span>
            <div class="benchmark-meter">
              <label><span>综合得分</span><strong>${fmt.format(item.meanScore)}</strong></label>
              <div class="benchmark-track"><i style="width:${scorePct}%"></i></div>
              <label><span>铜耗收益</span><strong>${lossGain.toFixed(1)}%</strong></label>
              <div class="benchmark-track"><i style="width:${Math.max(4, Math.min(100, Math.abs(lossGain) * 8))}%; background:${lossGain >= 0 ? "linear-gradient(90deg, #d6b260, #62c486)" : "linear-gradient(90deg, #d08b45, #ef6a73)"}"></i></div>
              <label><span>风险指数</span><strong>${riskPct}</strong></label>
              <div class="benchmark-track"><i style="width:${riskPct}%; background:${item.feasible ? "linear-gradient(90deg, #37c7b4, #62c486)" : "linear-gradient(90deg, #d08b45, #ef6a73)"}"></i></div>
            </div>
          </article>
        `;
      }).join("");
      grid.querySelectorAll("[data-benchmark-candidate]").forEach(card => {
        card.addEventListener("click", () => selectCandidate(card.dataset.benchmarkCandidate));
      });
      const current = byCandidate(selected);
      const familyRank = paretoFront.filter(item => item.family === current.family).sort((a, b) => b.meanScore - a.meanScore).findIndex(item => item.candidate === selected) + 1;
      summary.textContent = `${current.label} 属于 ${current.family} 路线，在该路线中排名第 ${familyRank}。当前对标视图用于解释“为什么推荐该路线”，不替代材料、热、逆变器和台架复核。`;
    }
    function readBusinessAssumptions() {
      document.querySelectorAll("[data-business-input]").forEach(input => {
        businessAssumptions[input.dataset.businessInput] = Number(input.value || 0);
      });
      document.getElementById("biz-production-label").textContent = `${fmt.format(businessAssumptions.production)}`;
      document.getElementById("biz-mileage-label").textContent = `${fmt.format(businessAssumptions.mileage)} km`;
      document.getElementById("biz-price-label").textContent = `${businessAssumptions.energyPrice.toFixed(2)} 元/kWh`;
      document.getElementById("biz-investment-label").textContent = `${fmt.format(businessAssumptions.validationInvestment)} 万元`;
      return businessAssumptions;
    }
    function computeBusinessCase(assumptions, candidateId = selected) {
      const baseline = byCandidate("baseline");
      const cand = byCandidate(candidateId) || byCandidate(selected);
      const savedWatts = baseline.loss - cand.loss;
      const normalizedKwhPer100km = savedWatts / 1000 * 1.8;
      const perVehicleAnnualKwh = normalizedKwhPer100km * assumptions.mileage / 100;
      const perVehicleAnnualSaving = perVehicleAnnualKwh * assumptions.energyPrice;
      const fleetAnnualSaving = perVehicleAnnualSaving * assumptions.production;
      const investmentYuan = assumptions.validationInvestment * 10000;
      const paybackMonths = fleetAnnualSaving > 0 ? investmentYuan / fleetAnnualSaving * 12 : Infinity;
      return { cand, assumptions, savedWatts, normalizedKwhPer100km, perVehicleAnnualKwh, perVehicleAnnualSaving, fleetAnnualSaving, investmentYuan, paybackMonths };
    }
    function calculateBusinessCase() {
      return computeBusinessCase(readBusinessAssumptions());
    }

    const sensitivityProfiles = [
      { id: "conservative", label: "保守假设", badge: "抗压", production: 0.55, mileage: 0.75, energyPrice: 0.8, validationInvestment: 1.25 },
      { id: "current", label: "当前假设", badge: "基准", production: 1, mileage: 1, energyPrice: 1, validationInvestment: 1 },
      { id: "upside", label: "积极假设", badge: "上行", production: 1.6, mileage: 1.25, energyPrice: 1.2, validationInvestment: 0.9 }
    ];
    function buildSensitivityAssumptions(profile) {
      return {
        production: Math.round(Math.max(5000, Math.min(200000, businessAssumptions.production * profile.production)) / 5000) * 5000,
        mileage: Math.round(Math.max(5000, Math.min(50000, businessAssumptions.mileage * profile.mileage)) / 1000) * 1000,
        energyPrice: Number(Math.max(0.3, Math.min(2, businessAssumptions.energyPrice * profile.energyPrice)).toFixed(2)),
        validationInvestment: Math.round(Math.max(20, Math.min(1000, businessAssumptions.validationInvestment * profile.validationInvestment)) / 20) * 20
      };
    }
    function renderSensitivityMatrix() {
      const grid = document.getElementById("sensitivity-grid");
      if (!grid) return;
      readBusinessAssumptions();
      const current = calculateBusinessCase();
      const best = sensitivityProfiles
        .map(profile => ({ profile, assumptions: buildSensitivityAssumptions(profile) }))
        .map(item => ({ ...item, result: computeBusinessCase(item.assumptions) }))
        .sort((a, b) => b.result.fleetAnnualSaving - a.result.fleetAnnualSaving)[0];
      document.getElementById("sensitivity-headline").textContent = best.result.fleetAnnualSaving > 0
        ? `最高场景年化收益约 ${fmt.format(best.result.fleetAnnualSaving / 10000)} 万元`
        : "当前三档假设均需复核 ROI";
      document.getElementById("sensitivity-copy").textContent = `基准场景年化收益 ${fmt.format(current.fleetAnnualSaving / 10000)} 万元，点击任一场景可回填到 ROI 滑块并联动讲解脚本。`;
      grid.innerHTML = sensitivityProfiles.map(profile => {
        const assumptions = buildSensitivityAssumptions(profile);
        const result = computeBusinessCase(assumptions);
        const payback = Number.isFinite(result.paybackMonths) ? `${result.paybackMonths.toFixed(1)} 月` : "需复核";
        return `
          <article class="sensitivity-card ${profile.id === "current" ? "active" : ""}" data-sensitivity-profile="${profile.id}">
            <header><b>${profile.label}</b><em>${profile.badge}</em></header>
            <span>车队年化收益</span>
            <strong>${result.fleetAnnualSaving > 0 ? `${fmt.format(result.fleetAnnualSaving / 10000)} 万元` : "需复核"}</strong>
            <span>回收周期：${payback}</span>
            <div class="sensitivity-assumptions">
              <label><span>年产量</span><strong>${fmt.format(assumptions.production)}</strong></label>
              <label><span>年里程</span><strong>${fmt.format(assumptions.mileage)} km</strong></label>
              <label><span>电价</span><strong>${assumptions.energyPrice.toFixed(2)} 元/kWh</strong></label>
              <label><span>验证投入</span><strong>${fmt.format(assumptions.validationInvestment)} 万元</strong></label>
            </div>
          </article>
        `;
      }).join("");
      grid.querySelectorAll("[data-sensitivity-profile]").forEach(card => {
        card.addEventListener("click", () => applySensitivityProfile(card.dataset.sensitivityProfile));
      });
    }
    function applySensitivityProfile(profileId) {
      const profile = sensitivityProfiles.find(item => item.id === profileId);
      if (!profile) return;
      const assumptions = buildSensitivityAssumptions(profile);
      Object.entries(assumptions).forEach(([key, value]) => {
        const input = document.querySelector(`[data-business-input="${key}"]`);
        if (input) input.value = value;
      });
      renderBusinessCase();
      renderSensitivityMatrix();
      renderEvidenceGapPriority();
      renderMeetingScript();
      renderStageGateBoard();
      renderDecisionPackPreview();
      renderCustomerMinutes();
      renderValidationTimeline();
      renderValidationRiskHeatmap();
    }
    function renderBusinessCase() {
      const box = document.getElementById("business-results");
      if (!box) return;
      const result = calculateBusinessCase();
      const positive = result.fleetAnnualSaving > 0;
      const cards = [
        ["单车年节省", positive ? `${fmt.format(result.perVehicleAnnualSaving)} 元` : "暂无节省", `${fmt.format(result.perVehicleAnnualKwh)} kWh / 年`],
        ["车队年化收益", positive ? `${fmt.format(result.fleetAnnualSaving / 10000)} 万元` : "需复核", `${fmt.format(businessAssumptions.production)} 台年产量假设`],
        ["投入回收周期", Number.isFinite(result.paybackMonths) ? `${result.paybackMonths.toFixed(1)} 月` : "不适用", "基于验证投入粗算"]
      ];
      box.innerHTML = cards.map(([label, value, copy]) => `
        <article class="business-card">
          <span>${label}</span>
          <strong>${value}</strong>
          <small>${copy}</small>
        </article>
      `).join("");
      document.getElementById("business-note").textContent = positive
        ? `${result.cand.label} 相比基线加权铜耗降低 ${fmt.format(result.savedWatts)} W。该测算只用于客户早期 ROI 沟通，量产收益需接入实测效率地图、整车能耗和工况分布。`
        : `${result.cand.label} 在当前加权铜耗口径下不产生直接节省，应作为风险或备选方案讲解。`;
    }


    function buildDecisionPackPreview() {
      const ctx = calculateCandidateContext();
      const business = calculateBusinessCase();
      const gapState = buildEvidenceGapPriority();
      const topGap = gapState.active;
      const review = buildReviewAnswer();
      const stage = buildStageGateState();
      const ranking = calculateWeightedRanking();
      const selectedRank = ranking.findIndex(item => item.candidate === selected) + 1;
      const saving = business.fleetAnnualSaving > 0 ? `${fmt.format(business.fleetAnnualSaving / 10000)} 万元/年` : "需复核";
      const payback = Number.isFinite(business.paybackMonths) ? `${business.paybackMonths.toFixed(1)} 个月` : "不适用";
      const evidenceScore = Math.round(Math.max(26, Math.min(98,
        ctx.confidence * .36
        + stage.readyScore * .28
        + Math.max(0, 100 - topGap.score) * .16
        + (business.fleetAnnualSaving > 0 ? 12 : 0)
        + (ctx.feasibleCycles === 3 ? 8 : 0)
      )));
      const headline = `${ctx.cand.label}客户决策包完整度 ${evidenceScore}%`;
      const summary = `${ctx.cand.family}当前排名第 ${selectedRank}、工况可达 ${ctx.feasibleCycles}/3、回收周期 ${payback}。最高优先级补证项是${topGap.title}。`;
      const kpis = [
        ["年化收益", saving],
        ["回收周期", payback],
        ["证据缺口", `${topGap.score.toFixed(0)}%`],
        ["现场问答", review.row.category]
      ];
      const items = [
        { id: "recommendation", title: "推荐结论", value: ctx.cand.label, state: "已生成", tone: "ready", copy: `综合评分 ${fmt.format(ctx.cand.meanScore)}，相对基线得分变化 ${ctx.scoreGain.toFixed(1)}%。` },
        { id: "business", title: "收益测算", value: saving, state: business.fleetAnnualSaving > 0 ? "可讲解" : "需复核", tone: business.fleetAnnualSaving > 0 ? "ready" : "watch", copy: `基于年产量 ${fmt.format(businessAssumptions.production)} 台和电价 ${businessAssumptions.energyPrice.toFixed(2)} 元/kWh。` },
        { id: "evidence", title: "关键补证", value: topGap.title, state: topGap.status, tone: topGap.state === "ready" ? "ready" : "watch", copy: `${topGap.owner}负责，${topGap.due}前回填到决策包。` },
        { id: "question", title: "评审问答", value: review.row.question, state: review.row.category, tone: "ready", copy: `回答已关联${review.row.evidence}，可直接复制到会议纪要。` },
        { id: "boundary", title: "交付边界", value: "方案筛选口径", state: "已标注", tone: "watch", copy: "必须保留不代表量产实机收益承诺的声明。" },
        { id: "next", title: "下一步", value: review.row.next, state: "待推进", tone: "watch", copy: `与${topGap.title}补证任务一起进入下轮评审。` }
      ];
      const copyText = [
        "客户决策包预览",
        `方案：${ctx.cand.label} / ${ctx.cand.family}`,
        `收益：${saving}，回收周期：${payback}`,
        `证据链完整度：${evidenceScore}%，最高补证项：${topGap.title}`,
        `评审问题：${review.row.question}`,
        `建议动作：${review.row.next}`,
        "声明：仅用于方案筛选和客户早期决策，不代表量产实机收益承诺。"
      ].join("\n");
      return { ctx, business, gapState, topGap, review, stage, ranking, selectedRank, saving, payback, evidenceScore, headline, summary, kpis, items, copyText };
    }
    function renderDecisionPackPreview() {
      const summary = document.getElementById("decision-pack-preview-summary");
      const score = document.getElementById("decision-pack-evidence-score");
      const list = document.getElementById("decision-pack-preview-list");
      if (!summary || !score || !list) return;
      const state = buildDecisionPackPreview();
      summary.innerHTML = `
        <span>客户决策包预览</span>
        <strong>${state.headline}</strong>
        <p>${state.summary}</p>
        <div class="pack-preview-kpis">
          ${state.kpis.map(([label, value]) => `
            <div class="pack-preview-kpi"><span>${label}</span><strong>${value}</strong></div>
          `).join("")}
        </div>
      `;
      score.innerHTML = `
        <div class="pack-score-ring" style="--score:${state.evidenceScore}%"><span>${state.evidenceScore}%</span></div>
        <div class="pack-score-copy">
          <strong>证据链完整度</strong>
          <span>综合沟通置信度、阶段门就绪度、关键缺口和 ROI 可讲解性计算。</span>
          <span>当前优先补证：${state.topGap.title} / ${state.topGap.due}</span>
        </div>
      `;
      list.innerHTML = state.items.map(item => `
        <article class="decision-pack-preview-card ${item.tone}" data-pack-preview-item="${item.id}">
          <header><b>${item.title}</b><em>${item.state}</em></header>
          <strong>${item.value}</strong>
          <p>${item.copy}</p>
        </article>
      `).join("");
    }
    async function copyDecisionPackPreview() {
      const toast = document.getElementById("decision-pack-preview-toast");
      try {
        await navigator.clipboard.writeText(buildDecisionPackPreview().copyText);
        if (toast) toast.textContent = "预览已复制";
      } catch (error) {
        if (toast) toast.textContent = "复制受限";
        console.info("Decision pack preview copy skipped", error);
      }
      window.setTimeout(() => {
        if (toast) toast.textContent = "";
      }, 1800);
    }

    function buildValidationRiskHeatmap() {
      const ctx = calculateCandidateContext();
      const business = calculateBusinessCase();
      const gapState = buildEvidenceGapPriority();
      const timeline = buildValidationTimeline();
      const savingPressure = business.fleetAnnualSaving > 0 ? 4 : 14;
      const feasibilityPressure = ctx.feasibleCycles < 3 ? 16 : 6;
      const risks = [
        {
          id: "voltage",
          title: "电压裕度",
          owner: "控制算法",
          evidence: "Vmax - |Vdq| 扫描 / 电压椭圆图",
          action: "复核高速弱磁段电压裕度，必要时回调 MTPV 边界。",
          target: "可达性雷达 / 阶段门",
          baseImpact: 82,
          baseUrgency: 78
        },
        {
          id: "demag",
          title: "退磁裕度",
          owner: "电磁 / 材料",
          evidence: "高温退磁曲线 / FEA 磁密图",
          action: "用材料曲线和 FEA 复核负 id 工况下的退磁边界。",
          target: "风险闭环 / 决策包声明",
          baseImpact: 88,
          baseUrgency: 70
        },
        {
          id: "iron_loss",
          title: "铁耗校准",
          owner: "损耗建模",
          evidence: "硅钢片 kh/kc/ke / PWM 谐波 / 效率地图",
          action: "将 Bertotti 系数从简化假设切到客户材料参数。",
          target: "铁耗曲线 / ROI 测算",
          baseImpact: 76,
          baseUrgency: 66
        },
        {
          id: "bench",
          title: "HIL/台架回放",
          owner: "验证工程",
          evidence: "HIL 回放记录 / 台架准入清单",
          action: "将当前推荐方案进入 HIL 回放，并形成台架准入结论。",
          target: "验证时间轴 / 客户评审纪要",
          baseImpact: 80,
          baseUrgency: 74
        }
      ].map(item => {
        const selectedGapBoost = gapState.active.title.includes(item.title.slice(0, 2)) ? 10 : 0;
        const timelineBoost = timeline.active.title.includes(item.title.slice(0, 2)) ? 6 : 0;
        const routeBoost = ctx.cand.family === "混合励磁" && item.id === "demag" ? 8 : 0;
        const impact = Math.max(20, Math.min(98, item.baseImpact + savingPressure + routeBoost));
        const urgency = Math.max(20, Math.min(98, item.baseUrgency + feasibilityPressure + selectedGapBoost + timelineBoost));
        const heat = Math.round(impact * .56 + urgency * .44);
        const tone = heat >= 86 ? "high" : heat >= 72 ? "medium" : "low";
        const status = heat >= 86 ? "高风险" : heat >= 72 ? "需跟进" : "持续观察";
        return { ...item, impact, urgency, heat, tone, status };
      }).sort((a, b) => b.heat - a.heat);
      const active = risks.find(item => item.id === activeValidationRisk) || risks[0];
      activeValidationRisk = active.id;
      const top = risks[0];
      const owners = risks.reduce((acc, item) => {
        acc[item.owner] = (acc[item.owner] || 0) + 1;
        return acc;
      }, {});
      const summary = `${ctx.cand.label}当前最高验证风险为${top.title}，热度 ${top.heat}%，责任人${top.owner}，需回填到${top.target}。`;
      const ownerCards = Object.entries(owners).map(([owner, count]) => [owner, `${count} 项风险`]);
      const copyText = [
        "验证风险热力图 / 责任矩阵",
        summary,
        ...risks.map((risk, index) => `${index + 1}. ${risk.title}：热度 ${risk.heat}%，责任人 ${risk.owner}，动作 ${risk.action}，回填目标 ${risk.target}`)
      ].join("\n");
      return { ctx, business, gapState, timeline, risks, active, top, ownerCards, summary, copyText };
    }
    function renderValidationRiskHeatmap() {
      const summary = document.getElementById("validation-risk-summary");
      const grid = document.getElementById("validation-risk-grid");
      const detail = document.getElementById("validation-risk-detail");
      if (!summary || !grid || !detail) return;
      const state = buildValidationRiskHeatmap();
      summary.innerHTML = `
        <span>责任矩阵</span>
        <strong>${state.top.title} ${state.top.heat}%</strong>
        <p>${state.summary}</p>
        <div class="risk-owner-grid">
          ${state.ownerCards.map(([owner, value]) => `<div class="risk-owner-card"><span>${owner}</span><strong>${value}</strong></div>`).join("")}
        </div>
      `;
      grid.innerHTML = state.risks.map(risk => `
        <article class="validation-risk-card ${risk.tone} ${risk.id === activeValidationRisk ? "active" : ""}" data-validation-risk="${risk.id}">
          <header><b>${risk.owner}</b><em>${risk.status}</em></header>
          <strong>${risk.title}</strong>
          <p>${risk.action}</p>
          <div class="risk-heat-meter">
            <label><span>影响 ${risk.impact}%</span><strong>紧急 ${risk.urgency}%</strong></label>
            <div class="risk-heat-track"><i style="width:${risk.heat}%"></i></div>
          </div>
        </article>
      `).join("");
      detail.innerHTML = `
        <h3>${state.active.title}</h3>
        <p>${state.active.action}</p>
        <div class="risk-detail-grid">
          <div class="risk-detail-card"><span>责任人</span><strong>${state.active.owner}</strong></div>
          <div class="risk-detail-card"><span>证据产物</span><strong>${state.active.evidence}</strong></div>
          <div class="risk-detail-card"><span>风险热度</span><strong>${state.active.heat}% / ${state.active.status}</strong></div>
          <div class="risk-detail-card"><span>回填目标</span><strong>${state.active.target}</strong></div>
        </div>
      `;
      grid.querySelectorAll("[data-validation-risk]").forEach(card => {
        card.addEventListener("click", () => {
          activeValidationRisk = card.dataset.validationRisk;
          renderValidationRiskHeatmap();
        });
      });
    }
    async function copyValidationRiskHeatmap() {
      const toast = document.getElementById("validation-risk-toast");
      try {
        await navigator.clipboard.writeText(buildValidationRiskHeatmap().copyText);
        if (toast) toast.textContent = "风险矩阵已复制";
      } catch (error) {
        if (toast) toast.textContent = "复制受限";
        console.info("Validation risk heatmap copy skipped", error);
      }
      window.setTimeout(() => {
        if (toast) toast.textContent = "";
      }, 1800);
    }

    function buildValidationTimeline() {
      const ctx = calculateCandidateContext();
      const business = calculateBusinessCase();
      const gapState = buildEvidenceGapPriority();
      const gap = gapState.active;
      const review = buildReviewAnswer();
      const stage = buildStageGateState();
      const saving = business.fleetAnnualSaving > 0 ? `${fmt.format(business.fleetAnnualSaving / 10000)} 万元/年` : "需复核";
      const payback = Number.isFinite(business.paybackMonths) ? `${business.paybackMonths.toFixed(1)} 个月` : "不适用";
      const steps = [
        {
          id: "workload_freeze",
          due: "T+3 天",
          owner: "应用工程",
          title: "工况权重冻结",
          status: "可启动",
          evidence: "客户工况权重确认单",
          action: `固化${ctx.cand.label}的客户工况权重和推荐排序。`,
          value: `把现场讨论变成可复算的权重假设，年化收益口径为${saving}。`,
          target: "权重模拟器 / 决策包预览"
        },
        {
          id: "evidence_gap",
          due: gap.due,
          owner: gap.owner,
          title: gap.title,
          status: gap.status,
          evidence: gap.evidence,
          action: gap.action,
          value: gap.impact,
          target: "证据缺口 / 阶段门 / 决策包"
        },
        {
          id: "review_answer",
          due: "T+7 天",
          owner: "销售工程 + 算法工程",
          title: "评审问答回填",
          status: review.row.category,
          evidence: review.row.evidence,
          action: review.row.next,
          value: `回答客户问题：${review.row.question}`,
          target: "客户评审问题清单 / 评审纪要"
        },
        {
          id: "bench_gate",
          due: "T+10 天",
          owner: "验证工程",
          title: "HIL/台架准入",
          status: stage.readyScore >= 75 ? "可排期" : "需补证",
          evidence: "HIL 回放记录 / 台架准入清单 / 保护策略日志",
          action: `按阶段门就绪度 ${stage.readyScore}% 决定是否进入 HIL 和台架联调。`,
          value: `将回收周期 ${payback}、证据缺口和控制 LUT 一起纳入下轮评审。`,
          target: "阶段门 / 客户决策包 / 会后纪要"
        }
      ];
      const active = steps.find(step => step.id === activeValidationStep) || steps[1];
      activeValidationStep = active.id;
      const readiness = Math.round(Math.max(18, Math.min(96, stage.readyScore * .46 + ctx.confidence * .34 + Math.max(0, 100 - gap.score) * .20)));
      const summary = `${ctx.cand.label}当前验证推进就绪度 ${readiness}%，优先回填${gap.title}，客户现场问题聚焦${review.row.category}。`;
      const meta = [
        ["当前方案", ctx.cand.label],
        ["收益口径", saving],
        ["阶段门", `${stage.readyScore}%`],
        ["优先补证", gap.title]
      ];
      const copyText = [
        "客户验证行动时间轴",
        summary,
        ...steps.map((step, index) => `${index + 1}. ${step.due} / ${step.owner} / ${step.title}：${step.action}；证据：${step.evidence}；回填目标：${step.target}`)
      ].join("\n");
      return { ctx, business, gap, review, stage, steps, active, readiness, summary, meta, copyText };
    }
    function renderValidationTimeline() {
      const summary = document.getElementById("validation-timeline-summary");
      const rail = document.getElementById("validation-timeline-rail");
      const detail = document.getElementById("validation-timeline-detail");
      if (!summary || !rail || !detail) return;
      const state = buildValidationTimeline();
      summary.innerHTML = `
        <span>验证推进概览</span>
        <strong>${state.readiness}% 就绪</strong>
        <p>${state.summary}</p>
        <div class="timeline-summary-grid">
          ${state.meta.map(([label, value]) => `<div class="timeline-summary-card"><span>${label}</span><strong>${value}</strong></div>`).join("")}
        </div>
      `;
      rail.innerHTML = state.steps.map((step, index) => `
        <button class="validation-step-button ${step.id === activeValidationStep ? "active" : ""}" type="button" data-validation-step="${step.id}">
          <b>${step.due}</b>
          <span><strong>${step.title}</strong><span>${step.owner}</span></span>
          <em>${step.status}</em>
        </button>
      `).join("");
      detail.innerHTML = `
        <h3>${state.active.title}</h3>
        <p>${state.active.value}</p>
        <div class="validation-detail-grid">
          <div class="validation-detail-card"><span>责任人</span><strong>${state.active.owner}</strong></div>
          <div class="validation-detail-card"><span>截止节奏</span><strong>${state.active.due}</strong></div>
          <div class="validation-detail-card"><span>证据产物</span><strong>${state.active.evidence}</strong></div>
          <div class="validation-detail-card"><span>补证动作</span><strong>${state.active.action}</strong></div>
        </div>
        <div class="validation-target-line"><b>回填目标</b>：${state.active.target}</div>
      `;
      rail.querySelectorAll("[data-validation-step]").forEach(button => {
        button.addEventListener("click", () => {
          activeValidationStep = button.dataset.validationStep;
          renderValidationTimeline();
          renderValidationRiskHeatmap();
        });
      });
    }
    async function copyValidationTimeline() {
      const toast = document.getElementById("validation-timeline-toast");
      try {
        await navigator.clipboard.writeText(buildValidationTimeline().copyText);
        if (toast) toast.textContent = "时间轴已复制";
      } catch (error) {
        if (toast) toast.textContent = "复制受限";
        console.info("Validation timeline copy skipped", error);
      }
      window.setTimeout(() => {
        if (toast) toast.textContent = "";
      }, 1800);
    }

    function buildCustomerMinutes() {
      const mode = minutesModes.find(item => item.id === activeMinutesMode) || minutesModes[0];
      activeMinutesMode = mode.id;
      const ctx = calculateCandidateContext();
      const business = calculateBusinessCase();
      const gapState = buildEvidenceGapPriority();
      const gap = gapState.active;
      const review = buildReviewAnswer();
      const stage = buildStageGateState();
      const preview = buildDecisionPackPreview();
      const saving = business.fleetAnnualSaving > 0 ? `${fmt.format(business.fleetAnnualSaving / 10000)} 万元/年` : "需复核";
      const payback = Number.isFinite(business.paybackMonths) ? `${business.paybackMonths.toFixed(1)} 个月` : "不适用";
      const conclusionByMode = {
        technical: `建议以${ctx.cand.label}作为下一轮技术复核基准，重点闭合${gap.title}和算法接口版本。`,
        business: `建议按${saving}和${payback}作为早期 ROI 沟通口径，同时保留量产边界声明。`,
        validation: `建议把${gap.title}列为首个闭环项，按${gap.due}节奏回填决策包。`
      };
      const meta = [
        ["会议类型", mode.label],
        ["当前方案", ctx.cand.label],
        ["收益口径", saving],
        ["证据完整度", `${preview.evidenceScore}%`]
      ];
      const actions = [
        ["方案", `固化${ctx.cand.label}作为评审基准版`, "会后即刻"],
        ["证据", `${gap.owner}补齐${gap.title}`, gap.due],
        ["问答", `回复客户问题：${review.row.question}`, "纪要同步"],
        ["阶段门", `按${stage.readyScore}%就绪度推进下轮评审`, "下个节点"]
      ];
      const risks = [
        ["收益边界", "仅代表方案筛选收益，量产需实测效率地图复核", "必须声明"],
        ["技术缺口", `${gap.title}当前优先级 ${gap.score.toFixed(0)}%`, gap.status],
        ["客户关切", `${review.row.category}问题需回到${review.row.evidence}`, "已关联"],
        ["交付前提", "材料、FEA、HIL、台架和保护策略需闭环", "待验证"]
      ];
      const copyText = [
        `客户评审纪要 - ${mode.label}`,
        `参与对象：${mode.owner}`,
        `聚焦事项：${mode.focus}`,
        `结论：${conclusionByMode[mode.id]}`,
        `当前方案：${ctx.cand.label}，收益：${saving}，回收周期：${payback}`,
        `证据缺口：${gap.title}，负责人：${gap.owner}，节奏：${gap.due}`,
        `客户问题：${review.row.question}；建议回答：${review.answer.split("\n")[1]}`,
        "行动项：",
        ...actions.map(([owner, item, due], index) => `${index + 1}. ${owner}：${item}（${due}）`),
        "风险与边界：",
        ...risks.map(([title, item, status]) => `- ${title}：${item}（${status}）`)
      ].join("\n");
      return { mode, ctx, business, gap, review, stage, preview, saving, payback, conclusion: conclusionByMode[mode.id], meta, actions, risks, copyText };
    }
    function renderCustomerMinutes() {
      const tabs = document.getElementById("customer-minutes-mode-tabs");
      const summary = document.getElementById("customer-minutes-summary");
      const actions = document.getElementById("customer-minutes-actions");
      const risks = document.getElementById("customer-minutes-risks");
      if (!tabs || !summary || !actions || !risks) return;
      const state = buildCustomerMinutes();
      tabs.innerHTML = minutesModes.map((mode, index) => `
        <button class="customer-minutes-mode ${mode.id === activeMinutesMode ? "active" : ""}" type="button" data-minutes-mode="${mode.id}">
          <b>${String(index + 1).padStart(2, "0")}</b>
          <span><strong>${mode.label}</strong><span>${mode.focus}</span></span>
          <em>${mode.badge}</em>
        </button>
      `).join("");
      summary.innerHTML = `
        <h3>${state.mode.label}：${state.ctx.cand.label}</h3>
        <p>${state.conclusion}</p>
        <div class="minutes-meta-grid">
          ${state.meta.map(([label, value]) => `<div class="minutes-meta-card"><span>${label}</span><strong>${value}</strong></div>`).join("")}
        </div>
      `;
      actions.innerHTML = `
        <h4>行动项闭环</h4>
        <div class="minutes-action-list">
          ${state.actions.map(([owner, item, due]) => `<div class="minutes-action-item"><b>${owner}</b><span>${item}</span><em>${due}</em></div>`).join("")}
        </div>
      `;
      risks.innerHTML = `
        <h4>风险与边界</h4>
        <div class="minutes-risk-list">
          ${state.risks.map(([title, item, status]) => `<div class="minutes-risk-item"><b>${title}</b><span>${item}</span><em>${status}</em></div>`).join("")}
        </div>
      `;
      tabs.querySelectorAll("[data-minutes-mode]").forEach(button => {
        button.addEventListener("click", () => {
          activeMinutesMode = button.dataset.minutesMode;
          renderCustomerMinutes();
      renderValidationTimeline();
      renderValidationRiskHeatmap();
        });
      });
    }
    async function copyCustomerMinutes() {
      const toast = document.getElementById("customer-minutes-toast");
      try {
        await navigator.clipboard.writeText(buildCustomerMinutes().copyText);
        if (toast) toast.textContent = "纪要已复制";
      } catch (error) {
        if (toast) toast.textContent = "复制受限";
        console.info("Customer minutes copy skipped", error);
      }
      window.setTimeout(() => {
        if (toast) toast.textContent = "";
      }, 1800);
    }

    function buildStageGateState() {
      const ctx = calculateCandidateContext();
      const business = calculateBusinessCase();
      const apiReady = document.getElementById("api-status")?.textContent === "接口已连接";
      const savingReady = business.fleetAnnualSaving > 0;
      const gates = [
        {
          index: "G1",
          title: "工况权重冻结",
          state: "ready",
          status: "可冻结",
          copy: `当前权重已能重算推荐排名，${ctx.cand.label}可作为会议基准方案。`,
          evidence: "权重模拟 + 排名列表"
        },
        {
          index: "G2",
          title: "材料与 FEA 复核",
          state: ctx.feasibleCycles === 3 ? "watch" : "blocked",
          status: ctx.feasibleCycles === 3 ? "可排期" : "先补边界",
          copy: ctx.feasibleCycles === 3 ? "工况可达性基本闭合，下一步复核磁密、温升和退磁边界。" : "峰值工况尚未完全可达，需先闭合电压椭圆和电流圆。",
          evidence: "Vmax - |Vdq| / 退磁 / 热模型"
        },
        {
          index: "G3",
          title: "HIL 与台架准入",
          state: ctx.confidence >= 70 && apiReady ? "ready" : "watch",
          status: ctx.confidence >= 70 && apiReady ? "可准入" : "需补证据",
          copy: apiReady ? `接口已连接，当前沟通置信度 ${ctx.confidence.toFixed(0)}%，可继续推进联调。` : "接口尚处于离线回退，先确保后端契约与会话状态恢复。",
          evidence: "接口契约 / 会话快照 / HIL 任务"
        },
        {
          index: "G4",
          title: "决策包评审",
          state: savingReady && ctx.feasibleCycles === 3 ? "ready" : "watch",
          status: savingReady ? "可评审" : "需 ROI 复核",
          copy: savingReady ? `年化节省约 ${fmt.format(business.fleetAnnualSaving / 10000)} 万元，可导出决策包进行评审。` : "ROI 暂不支撑直接推进，需调整客户产量、里程或能耗假设。",
          evidence: "决策包 / 客户摘要 / ROI"
        }
      ];
      const readyScore = gates.reduce((sum, gate) => sum + (gate.state === "ready" ? 25 : gate.state === "watch" ? 14 : 6), 0);
      const headline = readyScore >= 80 ? "可进入客户联合评审" : readyScore >= 56 ? "可带条件推进验证" : "需先闭合硬约束边界";
      const copy = `${ctx.cand.label}当前阶段门就绪度 ${readyScore}%，工况可达 ${ctx.feasibleCycles}/3，沟通置信度 ${ctx.confidence.toFixed(0)}%。`;
      return { gates, readyScore, headline, copy };
    }
    function renderStageGateBoard() {
      const grid = document.getElementById("stage-gate-grid");
      if (!grid) return;
      const state = buildStageGateState();
      document.getElementById("stage-gate-headline").textContent = state.headline;
      document.getElementById("stage-gate-copy").textContent = state.copy;
      document.getElementById("stage-gate-score").textContent = `${state.readyScore}%`;
      document.getElementById("stage-gate-progress").style.width = `${state.readyScore}%`;
      grid.innerHTML = state.gates.map(gate => `
        <article class="stage-gate-card ${gate.state}">
          <header><b>${gate.index}</b><span class="stage-gate-status">${gate.status}</span></header>
          <strong>${gate.title}</strong>
          <p>${gate.copy}</p>
          <small>${gate.evidence}</small>
        </article>
      `).join("");
    }
    function buildEvidenceGapPriority() {
      const ctx = calculateCandidateContext();
      const business = calculateBusinessCase();
      const apiReady = document.getElementById("api-status")?.textContent === "接口已连接";
      const savingPressure = business.fleetAnnualSaving > 0 ? 0 : 12;
      const riskPressure = ctx.feasibleCycles < 3 ? 16 : 4;
      const lossPressure = ctx.lossGain > 0 ? 10 : 0;
      const rows = evidenceGapRows.map(row => {
        const routeBoost = row.routeFit.includes(ctx.cand.family) ? 12 : 0;
        const apiBoost = row.id === "hil_bench_replay" && !apiReady ? 10 : 0;
        const thermalBoost = row.id === "demag_thermal" && ctx.cand.family === "混合励磁" ? 8 : 0;
        const score = Math.max(24, Math.min(98, row.base + routeBoost + riskPressure + savingPressure + lossPressure + apiBoost + thermalBoost - row.cost * 0.18));
        const state = score >= 86 ? "urgent" : score >= 68 ? "watch" : "ready";
        const status = score >= 86 ? "优先补证" : score >= 68 ? "排期补证" : "持续跟踪";
        return { ...row, score, state, status };
      }).sort((a, b) => b.score - a.score);
      const active = rows.find(row => row.id === activeEvidenceGap) || rows[0];
      activeEvidenceGap = active.id;
      return { rows, active, ctx, business, apiReady };
    }
    function applyEvidenceGap(id) {
      activeEvidenceGap = id;
      renderEvidenceGapPriority();
      renderDecisionPackPreview();
      renderCustomerMinutes();
      renderValidationTimeline();
      renderValidationRiskHeatmap();
    }
    function renderEvidenceGapPriority() {
      const grid = document.getElementById("evidence-gap-grid");
      if (!grid) return;
      const state = buildEvidenceGapPriority();
      const top = state.rows[0];
      const active = state.active;
      document.getElementById("evidence-gap-headline").textContent = `${top.title}：${top.status}`;
      document.getElementById("evidence-gap-copy").textContent = `${state.ctx.cand.label} 当前最高缺口分 ${top.score.toFixed(0)}，优先补证后可回填阶段门、讲解脚本和决策包。`;
      document.getElementById("evidence-gap-focus").innerHTML = [
        ["负责人", active.owner],
        ["截止节奏", active.due],
        ["证据产物", active.evidence],
        ["补证动作", active.action],
        ["客户价值", active.impact]
      ].map(([label, value]) => `<span>${label}<b>${value}</b></span>`).join("");
      grid.innerHTML = state.rows.map(row => `
        <article class="evidence-gap-card ${row.id === activeEvidenceGap ? "active" : ""} ${row.state}" data-evidence-gap="${row.id}">
          <header><b>${row.owner}</b><em>${row.status}</em></header>
          <strong>${row.title}</strong>
          <p>${row.action}</p>
          <div class="gap-meter">
            <label><span>优先级分数</span><strong>${row.score.toFixed(0)}%</strong></label>
            <div class="gap-track"><i style="width:${row.score}%"></i></div>
          </div>
          <div class="gap-meta">
            <span>截止节奏<b>${row.due}</b></span>
            <span>证据产物<b>${row.evidence}</b></span>
          </div>
        </article>
      `).join("");
      grid.querySelectorAll("[data-evidence-gap]").forEach(card => {
        card.addEventListener("click", () => applyEvidenceGap(card.dataset.evidenceGap));
      });
    }
    function buildReviewAnswer() {
      const row = reviewQuestionRows.find(item => item.id === activeReviewQuestion) || reviewQuestionRows[0];
      activeReviewQuestion = row.id;
      const ctx = calculateCandidateContext();
      const business = calculateBusinessCase();
      const gap = buildEvidenceGapPriority().rows[0];
      const saving = business.fleetAnnualSaving > 0 ? `${fmt.format(business.fleetAnnualSaving / 10000)} 万元/年` : "需复核";
      const payback = Number.isFinite(business.paybackMonths) ? `${business.paybackMonths.toFixed(1)} 个月` : "不适用";
      const answer = `${row.question}\n推荐回答：当前选中 ${ctx.cand.label}，综合评分 ${fmt.format(ctx.cand.meanScore)}，加权铜耗相对基线 ${ctx.lossGain.toFixed(1)}%。按当前 ROI 假设，车队年化收益 ${saving}，回收周期 ${payback}。\n证据引用：${row.evidence}；当前最高补证项为 ${gap.title}。\n下一步：${row.next}。\n注意：以上仅用于方案筛选沟通，不代表量产实机收益承诺。`;
      const cards = [
        ["当前方案", ctx.cand.label, `工况可达 ${ctx.feasibleCycles}/3`],
        ["商务口径", saving, `回收周期 ${payback}`],
        ["最高补证", gap.title, gap.status]
      ];
      const flow = [
        ["客户问题", row.question],
        ["回答口径", `先讲当前方案，再讲收益和边界，最后落到 ${row.next}`],
        ["证据引用", row.evidence],
        ["补证动作", `${gap.owner} 负责 ${gap.title}，${gap.due} 回填决策包`]
      ];
      return { row, ctx, business, gap, answer, cards, flow };
    }
    function renderReviewQuestionBoard() {
      const list = document.getElementById("review-question-list");
      const panel = document.getElementById("review-question-answer");
      if (!list || !panel) return;
      const state = buildReviewAnswer();
      list.innerHTML = reviewQuestionRows.map((row, index) => `
        <button class="review-question-button ${row.id === activeReviewQuestion ? "active" : ""}" type="button" data-review-question="${row.id}">
          <b>${String(index + 1).padStart(2, "0")}</b>
          <span><strong>${row.question}</strong><span>${row.concern}</span></span>
          <em>${row.category}</em>
        </button>
      `).join("");
      panel.innerHTML = `
        <h3>${state.row.question}</h3>
        <p>${state.answer.split("\n")[1].replace("推荐回答：", "")}</p>
        <div class="review-answer-grid">
          ${state.cards.map(([label, value, copy]) => `
            <article class="review-answer-card">
              <span>${label}</span>
              <strong>${value}</strong>
              <span>${copy}</span>
            </article>
          `).join("")}
        </div>
        <div class="review-answer-flow">
          ${state.flow.map(([label, value]) => `<span><b>${label}</b><span>${value}</span></span>`).join("")}
        </div>
        <div class="review-answer-actions">
          <span class="review-answer-toast" id="review-answer-toast"></span>
        </div>
      `;
      list.querySelectorAll("[data-review-question]").forEach(button => {
        button.addEventListener("click", () => {
          activeReviewQuestion = button.dataset.reviewQuestion;
          renderReviewQuestionBoard();
          renderDecisionPackPreview();
          renderCustomerMinutes();
      renderValidationTimeline();
      renderValidationRiskHeatmap();
        });
      });
    }
    async function copyReviewAnswer() {
      const toast = document.getElementById("review-answer-toast");
      try {
        await navigator.clipboard.writeText(buildReviewAnswer().answer);
        if (toast) toast.textContent = "回答已复制";
      } catch (error) {
        if (toast) toast.textContent = "复制受限";
        console.info("Review answer copy skipped", error);
      }
      window.setTimeout(() => {
        if (toast) toast.textContent = "";
      }, 1800);
    }
    function buildMeetingScript() {
      const ctx = calculateCandidateContext();
      const business = calculateBusinessCase();
      const ranking = calculateWeightedRanking();
      const top = ranking[0];
      const lossCopy = ctx.lossGain <= 0
        ? `加权铜耗较基线下降 ${Math.abs(ctx.lossGain).toFixed(1)}%`
        : `加权铜耗较基线上升 ${ctx.lossGain.toFixed(1)}%`;
      const savingCopy = business.fleetAnnualSaving > 0
        ? `按当前假设，车队年化节省约 ${fmt.format(business.fleetAnnualSaving / 10000)} 万元，投入回收约 ${business.paybackMonths.toFixed(1)} 个月。`
        : `按当前假设暂不产生直接年化节省，适合作为风险或备选方案讲解。`;
      const weightCopy = top.candidate === ctx.cand.candidate
        ? `当前客户工况权重下，${ctx.cand.label}仍保持首推位。`
        : `当前权重下，模拟首推会切换到 ${top.label}，需现场解释工况偏好。`;
      const riskCopy = ctx.feasibleCycles === 3
        ? `三类工况均可达，可推进材料、热、逆变器和台架复核。`
        : `当前仅 ${ctx.feasibleCycles}/3 类工况可达，要先闭合电压裕度、退磁和峰值电流边界。`;
      const headline = `${ctx.cand.label}：${lossCopy}，${weightCopy}`;
      const metrics = [
        ["推荐口径", ctx.cand.feasible ? "可推进验证" : "风险备选", riskCopy],
        ["收益证据", lossCopy, savingCopy],
        ["权重敏感", top.label, `模拟得分 ${fmt.format(top.simulatedScore)}，可达权重 ${fmt.format(top.simulatedFeasible)}`],
        ["沟通置信", `${ctx.confidence.toFixed(0)}%`, `工况可达 ${ctx.feasibleCycles}/3，风险指数 ${ctx.cand.feasible ? 2 : 7}/10`]
      ];
      const path = [
        ["01", "开场结论", `建议先看 ${ctx.cand.label}，它在当前模型下的综合得分为 ${fmt.format(ctx.cand.meanScore)}。`],
        ["02", "证据链路", `排序来自 EXP-010，高速风险参考 EXP-011，OpenDesign 和接口状态已接入看板。`],
        ["03", "商业价值", savingCopy],
        ["04", "风险闭环", riskCopy]
      ];
      const objections = [
        ["能否承诺量产收益？", "不承诺。当前是方案筛选口径，需接入实测材料、热模型和台架数据。"],
        ["为什么不选铜耗最低？", "铜耗不是唯一目标，峰值可达性、高速边界和验证投入同样纳入判断。"],
        ["下一步怎么落地？", "固化客户工况权重，导出决策包，然后进入 FEA、HIL、台架和保护策略联调。"]
      ];
      const nextActions = ["固化工况权重", "导出决策包", "复核电压与退磁", "排期 HIL/台架"];
      const copyText = [
        "客户决策讲解脚本",
        `推荐方案：${ctx.cand.label}`,
        `核心结论：${headline}`,
        ...path.map(([index, title, copy]) => `${index} ${title}：${copy}`),
        `下一步：${nextActions.join(" / ")}`,
        "注意：本脚本仅用于方案筛选沟通，不代表量产实机收益承诺。"
      ].join("\n");
      return { headline, copy: `${lossCopy}。${savingCopy}`, metrics, path, objections, nextActions, copyText };
    }
    function renderMeetingScript() {
      const headline = document.getElementById("meeting-script-headline");
      if (!headline) return;
      const script = buildMeetingScript();
      headline.textContent = script.headline;
      document.getElementById("meeting-script-copy").textContent = script.copy;
      document.getElementById("meeting-script-metrics").innerHTML = script.metrics.map(([label, value, copy]) => `
        <article class="meeting-metric">
          <span>${label}</span>
          <strong>${value}</strong>
          <span>${copy}</span>
        </article>
      `).join("");
      document.getElementById("meeting-script-path").innerHTML = script.path.map(([index, title, copy]) => `
        <article class="meeting-step">
          <b>${index}</b>
          <span><strong>${title}</strong><span>${copy}</span></span>
        </article>
      `).join("");
      document.getElementById("meeting-objections").innerHTML = script.objections.map(([title, copy]) => `
        <article class="meeting-objection">
          <strong>${title}</strong>
          <span>${copy}</span>
        </article>
      `).join("");
      document.getElementById("meeting-next-actions").innerHTML = script.nextActions.map(item => `<span>${item}</span>`).join("");
    }
    async function copyMeetingScript() {
      const toast = document.getElementById("meeting-script-toast");
      try {
        await navigator.clipboard.writeText(buildMeetingScript().copyText);
        toast.textContent = "脚本已复制";
      } catch (error) {
        toast.textContent = "复制受限";
        console.info("Meeting script copy skipped", error);
      }
      window.setTimeout(() => {
        toast.textContent = "";
      }, 1800);
    }
    function bindBusinessCase() {
      document.querySelectorAll("[data-business-input]").forEach(input => {
        input.addEventListener("input", () => {
          renderBusinessCase();
          renderSensitivityMatrix();
          renderEvidenceGapPriority();
          renderMeetingScript();
          renderStageGateBoard();
          renderDecisionPackPreview();
          renderCustomerMinutes();
      renderValidationTimeline();
      renderValidationRiskHeatmap();
        });
      });
    }
    function getCandidateCycleRows(candidateId = selected) {
      return cycleRows.filter(row => row.candidate === candidateId);
    }
    function calculateCandidateContext() {
      const cand = byCandidate(selected);
      const baseline = byCandidate("baseline");
      const rows = getCandidateCycleRows(selected);
      const launch = rows.find(row => row.cycle === "launch_peak_torque");
      const bestCycle = rows.reduce((best, row) => row.score > best.score ? row : best, rows[0]);
      const scoreGain = (cand.meanScore / baseline.meanScore - 1) * 100;
      const lossGain = (cand.loss / baseline.loss - 1) * 100;
      const feasibleCycles = rows.filter(row => row.feasibleWeight === 1).length;
      const confidence = Math.max(18, Math.min(92, 42 + cand.feasible * 22 + Math.max(0, scoreGain) * 3 + feasibleCycles * 5 - (cand.loss > baseline.loss ? 10 : 0)));
      return { cand, baseline, rows, launch, bestCycle, scoreGain, lossGain, feasibleCycles, confidence };
    }
    function renderDrilldownTabs() {
      const wrap = document.getElementById("drilldown-tabs");
      if (!wrap) return;
      wrap.innerHTML = drilldownTabs.map(([id, title, copy, index]) => `
        <button class="drilldown-tab ${id === activeDrilldown ? "active" : ""}" type="button" data-drilldown-tab="${id}">
          <b>${index}</b>
          <span><strong>${title}</strong><span>${copy}</span></span>
        </button>
      `).join("");
      wrap.querySelectorAll("[data-drilldown-tab]").forEach(button => {
        button.addEventListener("click", () => {
          activeDrilldown = button.dataset.drilldownTab;
          renderSolutionDrilldown();
        });
      });
    }
    function renderMetricCards(cards) {
      return `<div class="diagnostic-grid">${cards.map(([label, value, copy]) => `
        <article class="diagnostic-card">
          <span>${label}</span>
          <strong>${value}</strong>
          <span>${copy}</span>
        </article>
      `).join("")}</div>`;
    }
    function renderConfidenceMeter(label, value) {
      return `
        <div class="confidence-meter">
          <label><span>${label}</span><strong>${value.toFixed(0)}%</strong></label>
          <div class="confidence-track"><i style="width:${value}%"></i></div>
        </div>
      `;
    }
    function renderEvidenceLadder(items) {
      return `<div class="evidence-ladder">${items.map(([title, copy, state], index) => `
        <article class="evidence-step">
          <b>${index + 1}</b>
          <span><strong>${title}</strong><span>${copy}</span></span>
          <em>${state}</em>
        </article>
      `).join("")}</div>`;
    }
    function renderSolutionDrilldown() {
      const panel = document.getElementById("drilldown-panel");
      if (!panel) return;
      const ctx = calculateCandidateContext();
      const { cand, launch, bestCycle, scoreGain, lossGain, feasibleCycles, confidence } = ctx;
      renderDrilldownTabs();
      if (activeDrilldown === "risk") {
        panel.innerHTML = `
          <h3>风险闭环 · ${cand.label}</h3>
          <p>将客户最关心的可达性、高速损耗和实测边界拆成可执行检查项。</p>
          ${renderMetricCards([
            ["工况可达", `${feasibleCycles}/3`, "三类客户工况的约束通过情况"],
            ["峰值状态", launch.feasibleWeight === 1 ? "可达" : "需复核", "起步峰值工况的硬约束判断"],
            ["高速提醒", cand.feasible === 1 ? "中等" : "偏高", "需结合铁耗、电压裕度和温升"]
          ])}
          ${renderEvidenceLadder([
            ["电压裕度", "高速弱磁段需同步检查 Vmax - |Vdq|", "待接入"],
            ["退磁裕度", "高温、负 id 和短路边界需 FEA 复核", "待复核"],
            ["铁耗信度", "需用材料和谐波数据校准 Bertotti 系数", "进行中"]
          ])}
        `;
        return;
      }
      if (activeDrilldown === "delivery") {
        panel.innerHTML = `
          <h3>交付动作 · ${cand.label}</h3>
          <p>把方案判断转成软件、数据和验证任务，避免只停留在结论页。</p>
          ${renderMetricCards([
            ["软件产物", "LUT + API", "控制轨迹表和客户权重接口"],
            ["数据产物", "CSV + JSON", "实验结果、参数和设计规格"],
            ["验证任务", "4 项", "有限元、HIL、台架和保护策略"]
          ])}
          ${renderEvidenceLadder([
            ["第 1 步", "固化客户工况权重和当前推荐方案", "已具备"],
            ["第 2 步", "导出控制 LUT 和验证边界清单", "待执行"],
            ["第 3 步", "进入材料、热和台架复核", "待推进"]
          ])}
        `;
        return;
      }
      if (activeDrilldown === "evidence") {
        panel.innerHTML = `
          <h3>证据链路 · ${cand.label}</h3>
          <p>所有客户结论都要能回到原始实验、简化模型和待复核边界。</p>
          ${renderEvidenceLadder([
            ["EXP-010", "加权效率 Pareto 数据，支撑方案排序", "CSV"],
            ["EXP-011", "铁耗扫描数据，支撑高速风险识别", "CSV"],
            ["Wiki", "研究计划和工程边界说明", "MD"],
            ["OpenDesign", "黑金主题令牌和组件 handoff", "JSON"]
          ])}
          ${renderConfidenceMeter("当前证据完整度", confidence)}
        `;
        return;
      }
      panel.innerHTML = `
        <h3>收益拆解 · ${cand.label}</h3>
        <p>用客户能听懂的口径解释当前方案为什么被推荐，以及收益从哪些工况来。</p>
        ${renderMetricCards([
          ["综合评分", `${fmt.format(cand.meanScore)}`, `相对基线 ${scoreGain >= 0 ? "+" : ""}${scoreGain.toFixed(1)}%`],
          ["加权铜耗", `${fmt.format(cand.loss)} W`, `相对基线 ${lossGain.toFixed(1)}%`],
          ["最优工况", `${cycleLabels[bestCycle.cycle]}`, `得分 ${fmt.format(bestCycle.score)}`]
        ])}
        ${renderConfidenceMeter("客户沟通置信度", confidence)}
      `;
    }    async function loadCustomerBrief() {
      try {
        const response = await fetch("/api/customer-brief", {
          method: "POST",
          headers: { "Accept": "application/json", "Content-Type": "application/json" },
          body: JSON.stringify(buildDecisionPackState())
        });
        if (!response.ok) throw new Error(`customer-brief ${response.status}`);
        const payload = await response.json();
        if (payload?.source !== "backend-api" || payload?.schemaVersion !== 1 || !payload.brief) {
          throw new Error("customer-brief schema incompatible");
        }
        recordApiSync("/api/customer-brief", true, payload.candidate || selected);
        return payload.brief;
      } catch (error) {
        recordApiSync("/api/customer-brief", false, error.message);
        console.info("Customer brief API fallback", error);
        return latestBrief;
      }
    }
    async function exportCustomerBrief() {
      const toast = document.getElementById("export-toast");
      try {
        await navigator.clipboard.writeText(await loadCustomerBrief());
        toast.textContent = "摘要已复制";
      } catch (error) {
        toast.textContent = "复制受限，请手动选择文本";
      }
      window.setTimeout(() => {
        toast.textContent = "";
      }, 2200);
    }    function renderFilters() {
      const wrap = document.getElementById("candidate-filters");
      wrap.innerHTML = "";
      paretoFront.forEach(d => {
        const btn = document.createElement("button");
        btn.className = `filter-button ${d.candidate === selected ? "active" : ""}`;
        btn.type = "button";
        btn.textContent = d.label;
        btn.style.borderColor = d.candidate === selected ? d.color : "";
        btn.style.background = d.candidate === selected ? d.color : "";
        btn.addEventListener("click", () => selectCandidate(d.candidate));
        wrap.append(btn);
      });
    }
    function renderMetrics() {
      const cand = byCandidate(selected);
      document.getElementById("winner-name").textContent = cand.label;
      document.getElementById("winner-score").textContent = fmt.format(cand.meanScore);
      document.getElementById("winner-copy").textContent = `${cand.family} · 可达权重 ${cand.feasible} · 加权铜耗 ${fmt.format(cand.loss)} W`;
      const rows = [
        ["综合得分", cand.meanScore, 0.85],
        ["可达权重", cand.feasible, 1],
        ["损耗优势", 1 - cand.loss / 6000, 1],
      ];
      const box = document.getElementById("candidate-metrics");
      box.innerHTML = rows.map(([name, value, max]) => `
        <div class="metric-row">
          <span>${name}</span>
          <span class="track"><i class="fill" style="width:${Math.max(0, Math.min(100, value / max * 100))}%; background:${cand.color}"></i></span>
          <strong>${fmt.format(value)}</strong>
        </div>
      `).join("");
    }    function renderRoutes() {
      const wrap = document.getElementById("route-matrix");
      wrap.innerHTML = routes.map(([title, copy, maturity, priority]) => `
        <article class="route">
          <span class="pill">${priority}</span>
          <strong>${title}</strong>
          <p>${copy}</p>
          <div class="maturity"><i style="width:${maturity}%"></i></div>
        </article>
      `).join("");
    }
    function renderAlgorithmMap() {
      const wrap = document.querySelector("#algorithm-map .algorithm-table");
      wrap.innerHTML = algorithmRows.map(([name, input, output, value]) => `
        <article class="algorithm-row">
          <div><strong>${name}</strong><span>算法模块</span></div>
          <div><strong>输入与计算</strong><span>${input}</span></div>
          <div><strong>落地交付</strong><span>${output}</span></div>
          <div><strong>客户价值</strong><span>${value}</span></div>
        </article>
      `).join("");
    }
    function getAlgorithmMaturityScore(row) {
      const values = Object.values(row.dimensions);
      return values.reduce((sum, value) => sum + value, 0) / values.length;
    }
    function applyAlgorithmMaturity(id) {
      activeAlgorithmMaturity = id;
      renderAlgorithmMaturity();
    }
    function renderAlgorithmMaturity() {
      const grid = document.getElementById("algorithm-maturity-grid");
      if (!grid) return;
      const cand = byCandidate(selected);
      const relevant = algorithmMaturityRows.filter(row => row.currentFit.includes(cand.family));
      const activeRow = algorithmMaturityRows.find(row => row.id === activeAlgorithmMaturity) || relevant[0] || algorithmMaturityRows[0];
      activeAlgorithmMaturity = activeRow.id;
      const avgScore = relevant.length
        ? relevant.reduce((sum, row) => sum + getAlgorithmMaturityScore(row), 0) / relevant.length
        : getAlgorithmMaturityScore(activeRow);
      document.getElementById("algorithm-maturity-headline").textContent = `${cand.label} 算法落地均值 ${avgScore.toFixed(0)}%`;
      document.getElementById("algorithm-maturity-copy").textContent = `${cand.family} 当前关联 ${relevant.length} 个算法能力，点击矩阵行可聚焦数据、接口、验证和客户价值。成熟度代表方案筛选阶段的落地准备度，不代表量产完成度。`;
      document.getElementById("algorithm-maturity-focus").innerHTML = [
        ["模型成熟度", `${activeRow.dimensions.model}%`],
        ["数据成熟度", `${activeRow.dimensions.data}%`],
        ["接口成熟度", `${activeRow.dimensions.api}%`],
        ["验证成熟度", `${activeRow.dimensions.validation}%`],
        ["客户价值", activeRow.value]
      ].map(([label, value]) => `<span>${label}<b>${value}</b></span>`).join("");
      grid.innerHTML = algorithmMaturityRows.map(row => {
        const score = getAlgorithmMaturityScore(row);
        const isRelevant = row.currentFit.includes(cand.family);
        const dimensions = [
          ["模型成熟度", row.dimensions.model],
          ["数据成熟度", row.dimensions.data],
          ["接口成熟度", row.dimensions.api],
          ["验证成熟度", row.dimensions.validation]
        ];
        return `
          <article class="maturity-card ${row.id === activeAlgorithmMaturity ? "active" : ""} ${isRelevant ? "relevant" : ""}" data-maturity-algorithm="${row.id}">
            <header>
              <span class="maturity-pill">${isRelevant ? "当前方案相关" : "可复用能力"}</span>
              <strong>${row.name}</strong>
              <span>${row.stage}</span>
              <p>${row.data}</p>
            </header>
            <div class="maturity-dimensions">
              ${dimensions.map(([label, value]) => `
                <div class="maturity-dimension">
                  <label><span>${label}</span><b>${value}%</b></label>
                  <div class="maturity-bar"><i style="width:${value}%"></i></div>
                </div>
              `).join("")}
            </div>
            <div class="maturity-score">
              <span>${row.interface}</span>
              <strong>${score.toFixed(0)}%</strong>
              <span>${row.validation}</span>
              <button type="button" data-maturity-focus="${row.id}">聚焦价值</button>
            </div>
          </article>
        `;
      }).join("");
      grid.querySelectorAll("[data-maturity-algorithm], [data-maturity-focus]").forEach(item => {
        item.addEventListener("click", event => {
          event.stopPropagation();
          applyAlgorithmMaturity(item.dataset.maturityAlgorithm || item.dataset.maturityFocus);
        });
      });
    }
    function renderDemoFlow() {
      const cand = byCandidate(selected);
      const rows = cycleRows.filter(d => d.candidate === selected);
      const bestCycle = rows.reduce((best, row) => row.score > best.score ? row : best, rows[0]);
      const launch = rows.find(d => d.cycle === "launch_peak_torque");
      const baseline = byCandidate("baseline");
      const scoreGain = (cand.meanScore / baseline.meanScore - 1) * 100;
      const steps = [
        ["客户工况输入", `${cycleLabels[bestCycle.cycle]} 权重样本`, `${fmt.format(bestCycle.score)} 分`],
        ["算法计算", `${cand.family} + 加权评分`, `${scoreGain >= 0 ? "+" : ""}${scoreGain.toFixed(1)}%`],
        ["约束校验", `峰值可达权重 ${launch.feasibleWeight}`, launch.feasibleWeight === 1 ? "通过" : "需复核"],
        ["收益输出", `加权铜耗 ${fmt.format(cand.loss)} 瓦`, cand.feasible === 1 ? "可推进" : "高风险"]
      ];
      document.getElementById("flow-steps").innerHTML = steps.map(([title, copy, value]) => `
        <article class="flow-step">
          <strong>${title}</strong>
          <span>${copy}</span>
          <b class="flow-value">${value}</b>
        </article>
      `).join("");
      document.getElementById("scenario-tabs").innerHTML = paretoFront.map((item, index) => `
        <button class="filter-button ${item.candidate === selected ? "active" : ""}" type="button" data-demo-candidate="${item.candidate}" data-demo-index="${index}">${item.label}</button>
      `).join("");
      document.querySelectorAll("[data-demo-candidate]").forEach(button => {
        button.addEventListener("click", () => {
          stopPlayback();
          playbackIndex = Number(button.dataset.demoIndex);
          selectCandidate(button.dataset.demoCandidate);
        });
      });
    }    function renderDeliveryList() {
      document.getElementById("delivery-list").innerHTML = deliveryItems.map(([title, copy], index) => `
        <article class="delivery-item">
          <span class="delivery-index">${index + 1}</span>
          <span><strong>${title}</strong><span>${copy}</span></span>
        </article>
      `).join("");
    }
    function renderOpenDesignTokens() {
      const tokens = [
        ["主色", OPENDESIGN_TOKENS.colors.primary, "关键操作与选中态"],
        ["数据色", OPENDESIGN_TOKENS.colors.dataCyan, "工程数据与次级曲线"],
        ["成功色", OPENDESIGN_TOKENS.colors.success, "收益、通过、可推进"],
        ["风险色", OPENDESIGN_TOKENS.colors.danger, "不可达、高风险、告警"]
      ];
      document.getElementById("design-token-grid").innerHTML = tokens.map(([name, color, usage]) => `
        <article class="design-token">
          <i style="background:${color}"></i>
          <strong>${name}</strong>
          <span>${color} · ${usage}</span>
        </article>
      `).join("");
    }
    async function loadOpenDesignSpec() {
      try {
        const response = await fetch("/api/design-spec", { headers: { "Accept": "application/json" } });
        if (!response.ok) throw new Error(`design-spec ${response.status}`);
        const payload = await response.json();
        if (payload?.source !== "backend-api" || payload?.schemaVersion !== 1 || !payload.spec) {
          throw new Error("design-spec schema incompatible");
        }
        recordApiSync("/api/design-spec", true, payload.file || "loaded");
        return payload;
      } catch (error) {
        recordApiSync("/api/design-spec", false, error.message);
        console.info("OpenDesign spec API fallback", error);
        return { source: "local", schemaVersion: 1, file: OPENDESIGN_TOKENS.file, spec: OPENDESIGN_TOKENS };
      }
    }
    async function exportOpenDesignSpec() {
      const button = document.getElementById("export-design-spec");
      try {
        const payload = await loadOpenDesignSpec();
        await navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
        button.textContent = "规格已复制";
      } catch (error) {
        button.textContent = "规格可导出";
        console.info("OpenDesign spec copy skipped", error);
      }
      window.setTimeout(() => {
        button.textContent = "导出设计规格";
      }, 1800);
    }    function buildDecisionPack() {
      const business = calculateBusinessCase();
      const context = calculateCandidateContext();
      const ranking = calculateWeightedRanking().slice(0, 5).map((item, index) => ({
        rank: index + 1,
        candidate: item.candidate,
        label: item.label,
        simulatedScore: Number(item.simulatedScore.toFixed(4)),
        simulatedFeasible: Number(item.simulatedFeasible.toFixed(4))
      }));
      return {
        schemaVersion: 1,
        generatedAt: new Date().toISOString(),
        dashboard: "controllable_flux_motor_kb.html",
        theme: "premium black-gold engineering dashboard",
        selected: {
          candidate: context.cand.candidate,
          label: context.cand.label,
          family: context.cand.family,
          meanScore: context.cand.meanScore,
          weightedCopperLossW: context.cand.loss,
          feasible: context.cand.feasible
        },
        gains: {
          scoreGainPercent: Number(context.scoreGain.toFixed(2)),
          copperLossChangePercent: Number(context.lossGain.toFixed(2)),
          feasibleCycles: context.feasibleCycles,
          confidencePercent: Number(context.confidence.toFixed(0))
        },
        businessCase: {
          assumptions: { ...businessAssumptions },
          perVehicleAnnualSavingYuan: Number(business.perVehicleAnnualSaving.toFixed(2)),
          fleetAnnualSavingYuan: Number(business.fleetAnnualSaving.toFixed(2)),
          paybackMonths: Number.isFinite(business.paybackMonths) ? Number(business.paybackMonths.toFixed(2)) : null
        },
        ranking,
        evidence: ["EXP-010 weighted efficiency Pareto", "EXP-011 iron loss sweep", "wiki research plan", "OpenDesign black-gold handoff"],
        disclaimer: "仅用于客户方案筛选和早期决策，不代表量产实机收益承诺。"
      };
    }
    function buildDecisionPackQuery() {
      readBusinessAssumptions();
      const params = new URLSearchParams();
      params.set("candidate", selected);
      Object.entries(businessAssumptions).forEach(([key, value]) => {
        params.set(key, String(value));
      });
      document.querySelectorAll("[data-weight-input]").forEach(input => {
        params.set(input.dataset.weightInput, String(Number(input.value || 0)));
      });
      return params.toString();
    }
    function buildDecisionPackState() {
      readBusinessAssumptions();
      const weights = {};
      document.querySelectorAll("[data-weight-input]").forEach(input => {
        weights[input.dataset.weightInput] = Number(input.value || 0);
      });
      return {
        candidate: selected,
        businessAssumptions: { ...businessAssumptions },
        weights
      };
    }
    function applyScenarioState(state) {
      if (!state || typeof state !== "object") return;
      if (state.candidate && paretoFront.some(item => item.candidate === state.candidate)) {
        selected = state.candidate;
      }
      if (state.businessAssumptions && typeof state.businessAssumptions === "object") {
        Object.entries(state.businessAssumptions).forEach(([key, value]) => {
          if (Object.hasOwn(businessAssumptions, key)) {
            businessAssumptions[key] = Number(value);
            const input = document.querySelector(`[data-business-input="${key}"]`);
            if (input) input.value = String(value);
          }
        });
      }
      if (state.weights && typeof state.weights === "object") {
        Object.entries(state.weights).forEach(([key, value]) => {
          const input = document.querySelector(`[data-weight-input="${key}"]`);
          if (input) input.value = String(value);
        });
      }
      readBusinessAssumptions();
    }
    function renderScenarioStateStatus() {
      const status = document.getElementById("scenario-state-status");
      if (!status) return;
      if (!backendScenarioState || !backendScenarioState.stateAvailable) {
        status.textContent = "scenario-state: none";
        return;
      }
      status.textContent = `scenario-state: ${backendScenarioState.stateSource}`;
    }
    async function clearScenarioState() {
      const button = document.getElementById("clear-scenario-state");
      if (button) button.disabled = true;
      try {
        const response = await fetch("/api/scenario-state", { method: "DELETE", headers: { "Accept": "application/json" } });
        if (!response.ok) throw new Error(`scenario-state clear ${response.status}`);
        applyScenarioStatePayload(await response.json());
        recordApiSync("/api/scenario-state", true, "cleared");
      } catch (error) {
        backendScenarioState = null;
        renderScenarioStateStatus();
        recordApiSync("/api/scenario-state", false, error.message);
        console.info("Scenario state clear skipped", error);
      } finally {
        if (button) button.disabled = false;
      }
    }
    function applyScenarioStatePayload(payload) {
      if (payload?.source !== "backend-api" || payload?.schemaVersion !== 1) {
        throw new Error("scenario-state schema incompatible");
      }
      backendScenarioState = {
        stateAvailable: Boolean(payload.stateAvailable),
        stateSource: payload.stateSource || "none"
      };
      if (payload.stateAvailable) applyScenarioState(payload.state);
      renderScenarioStateStatus();
    }
    async function loadScenarioState() {
      try {
        const response = await fetch("/api/scenario-state", { headers: { "Accept": "application/json" } });
        if (!response.ok) throw new Error(`scenario-state ${response.status}`);
        const payload = await response.json();
        applyScenarioStatePayload(payload);
        recordApiSync("/api/scenario-state", true, payload.stateSource || "none");
      } catch (error) {
        backendScenarioState = null;
        renderScenarioStateStatus();
        recordApiSync("/api/scenario-state", false, error.message);
        console.info("Scenario state restore skipped", error);
      }
    }
    function validateDecisionPackPayload(payload) {
      if (payload?.source !== "backend-api" || payload?.schemaVersion !== 1 || !payload.selected || !payload.businessCase?.assumptions) {
        throw new Error("decision-pack schema incompatible");
      }
      return payload;
    }
    async function loadDecisionPack() {
      try {
        const response = await fetch("/api/decision-pack", {
          method: "POST",
          headers: { "Accept": "application/json", "Content-Type": "application/json" },
          body: JSON.stringify(buildDecisionPackState())
        });
        if (!response.ok) throw new Error(`decision-pack ${response.status}`);
        const payload = validateDecisionPackPayload(await response.json());
        recordApiSync("/api/decision-pack", true, "POST");
        return payload;
      } catch (error) {
        recordApiSync("/api/decision-pack", false, `POST ${error.message}`);
        console.info("Decision pack POST fallback", error);
        try {
          const response = await fetch(`/api/decision-pack?${buildDecisionPackQuery()}`, { headers: { "Accept": "application/json" } });
          if (!response.ok) throw new Error(`decision-pack ${response.status}`);
          const payload = validateDecisionPackPayload(await response.json());
          recordApiSync("/api/decision-pack", true, "GET fallback");
          return payload;
        } catch (fallbackError) {
          recordApiSync("/api/decision-pack", false, `GET ${fallbackError.message}`);
          console.info("Decision pack API fallback", fallbackError);
          return buildDecisionPack();
        }
      }
    }
    async function buildSessionSnapshot() {
      return {
        ...buildDecisionPackState(),
        decisionPack: await loadDecisionPack(),
        apiSyncLog: { ...apiSyncLog }
      };
    }
    async function saveSessionSnapshot() {
      const button = document.getElementById("save-session-snapshot");
      if (button) button.disabled = true;
      try {
        const response = await fetch("/api/session-snapshot", {
          method: "POST",
          headers: { "Accept": "application/json", "Content-Type": "application/json" },
          body: JSON.stringify(await buildSessionSnapshot())
        });
        if (!response.ok) throw new Error(`session-snapshot ${response.status}`);
        const payload = await response.json();
        if (payload?.source !== "backend-api" || payload?.schemaVersion !== 1 || !payload.snapshotAvailable) {
          throw new Error("session-snapshot schema incompatible");
        }
        const snapshot = payload.snapshot;
        if (!payload.metadata?.snapshotId || snapshot.metadata?.snapshotId !== payload.metadata.snapshotId) {
          throw new Error("session-snapshot metadata incompatible");
        }
        renderSessionSnapshotStatus(payload.metadata, snapshot.candidate || "saved");
        recordApiSync("/api/session-snapshot", true, snapshot.candidate || "saved");
        button.textContent = "会话已保存";
      } catch (error) {
        recordApiSync("/api/session-snapshot", false, error.message);
        if (button) button.textContent = "保存受限";
        console.info("Session snapshot save skipped", error);
      } finally {
        window.setTimeout(() => {
          if (button) {
            button.disabled = false;
            button.textContent = "保存会话";
          }
        }, 1800);
      }
    }
    async function clearSessionSnapshot() {
      const button = document.getElementById("clear-session-snapshot");
      if (button) button.disabled = true;
      try {
        const response = await fetch("/api/session-snapshot", { method: "DELETE", headers: { "Accept": "application/json" } });
        if (!response.ok) throw new Error(`session-snapshot clear ${response.status}`);
        const payload = await response.json();
        if (payload?.source !== "backend-api" || payload?.schemaVersion !== 1 || payload.snapshotAvailable) {
          throw new Error("session-snapshot clear schema incompatible");
        }
        renderSessionSnapshotStatus(null);
        recordApiSync("/api/session-snapshot", true, "cleared");
        button.textContent = "会话已清空";
      } catch (error) {
        recordApiSync("/api/session-snapshot", false, error.message);
        if (button) button.textContent = "清空受限";
        console.info("Session snapshot clear skipped", error);
      } finally {
        window.setTimeout(() => {
          if (button) {
            button.disabled = false;
            button.textContent = "清空会话";
          }
        }, 1800);
      }
    }
    function applySessionSnapshotPayload(payload) {
      if (payload?.source !== "backend-api" || payload?.schemaVersion !== 1) {
        throw new Error("session-snapshot schema incompatible");
      }
      if (payload.snapshotAvailable) {
        if (!payload.metadata?.snapshotId || payload.snapshot?.metadata?.snapshotId !== payload.metadata.snapshotId) {
          throw new Error("session-snapshot metadata incompatible");
        }
        applyScenarioState(payload.snapshot);
        applySessionSnapshotApiSyncLog(payload.snapshot?.apiSyncLog);
        renderSessionSnapshotStatus(payload.metadata, payload.snapshot?.candidate || "restored");
      } else {
        renderSessionSnapshotStatus(null);
      }
    }
    async function loadSessionSnapshot() {
      try {
        const response = await fetch("/api/session-snapshot", { headers: { "Accept": "application/json" } });
        if (!response.ok) throw new Error(`session-snapshot ${response.status}`);
        const payload = await response.json();
        applySessionSnapshotPayload(payload);
        recordApiSync("/api/session-snapshot", true, payload.snapshot?.candidate || "none");
      } catch (error) {
        recordApiSync("/api/session-snapshot", false, error.message);
        console.info("Session snapshot restore skipped", error);
      }
    }
    async function exportDecisionPack() {
      const button = document.getElementById("export-decision-pack");
      if (!button) return;
      const text = JSON.stringify(await loadDecisionPack(), null, 2);
      try {
        await navigator.clipboard.writeText(text);
        button.textContent = "决策包已复制";
      } catch (error) {
        button.textContent = "复制受限";
        console.info("Decision pack copy skipped", error);
      }
      window.setTimeout(() => {
        button.textContent = "导出决策包";
      }, 1800);
    }
    function renderPresentationState() {
      const [target, title, copy, progress] = presentationSteps[presentationIndex];
      document.getElementById("presentation-title").textContent = `客户演示模式 | ${title}`;
      document.getElementById("presentation-copy").textContent = copy;
      document.getElementById("presentation-progress").style.width = `${progress}%`;
      document.getElementById("presentation-toggle").textContent = document.body.classList.contains("presentation-mode") ? "退出演示" : "进入演示";
      return target;
    }
    function focusPresentationStep() {
      const target = renderPresentationState();
      const el = document.getElementById(target);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
      if (target === "solution-drilldown") activeDrilldown = "risk";
      if (target === "business-case") renderBusinessCase();
      renderSolutionDrilldown();
    }
    function nextPresentationStep() {
      presentationIndex = (presentationIndex + 1) % presentationSteps.length;
      focusPresentationStep();
    }
    function bindPresentationMode() {
      const toggle = document.getElementById("presentation-toggle");
      if (!toggle) return;
      renderPresentationState();
      toggle.addEventListener("click", () => {
        const entering = !document.body.classList.contains("presentation-mode");
        document.body.classList.toggle("presentation-mode", entering);
        if (entering) {
          presentationIndex = 0;
          startPlayback();
          focusPresentationStep();
        } else {
          stopPlayback();
          renderPresentationState();
        }
      });
    }
    function startPlayback() {
      if (playbackTimer) return;
      document.getElementById("play-toggle").textContent = "暂停演示";
      playbackTimer = window.setInterval(() => {
        playbackIndex = (playbackIndex + 1) % paretoFront.length;
        selectCandidate(paretoFront[playbackIndex].candidate);
        if (document.body.classList.contains("presentation-mode")) nextPresentationStep();
      }, 2200);
    }
    function stopPlayback() {
      if (!playbackTimer) return;
      window.clearInterval(playbackTimer);
      playbackTimer = null;
      document.getElementById("play-toggle").textContent = "自动演示";
    }
    function bindPlayback() {
      document.getElementById("play-toggle").addEventListener("click", () => {
        if (playbackTimer) stopPlayback();
        else startPlayback();
      });
    }
    function bindWeightSimulator() {
      document.querySelectorAll("[data-weight-input]").forEach(input => {
        input.addEventListener("input", () => {
          activePreset = "自定义";
          renderWeightSimulator();
          renderDecisionPackPreview();
          renderCustomerMinutes();
      renderValidationTimeline();
      renderValidationRiskHeatmap();
        });
      });
      document.getElementById("apply-recommendation").addEventListener("click", () => {
        stopPlayback();
        selectCandidate(simulatedRecommendation);
      });
    }
    function applyDashboardPayload(payload) {
      if (!payload || !Array.isArray(payload.paretoFront) || !Array.isArray(payload.cycleRows)) {
        throw new Error("接口数据结构不完整");
      }
      if (payload.meta?.source !== "backend-api" || payload.meta?.schemaVersion !== 1) {
        throw new Error("接口版本不兼容");
      }
      paretoFront = payload.paretoFront;
      cycleRows = payload.cycleRows;
      ironLossRows = payload.ironLossRows || ironLossRows;
      algorithmRows = payload.algorithmRows || algorithmRows;
      deliveryItems = payload.deliveryItems || deliveryItems;
      selected = paretoFront.some(item => item.candidate === selected)
        ? selected
        : paretoFront[0].candidate;
      playbackIndex = Math.max(0, paretoFront.findIndex(item => item.candidate === selected));
    }
    async function loadDashboardData() {
      const status = document.getElementById("api-status");
      const refresh = document.getElementById("refresh-data");
      try {
        status.textContent = "正在同步";
        refresh.disabled = true;
        const response = await fetch("/api/dashboard", { headers: { "Accept": "application/json" } });
        if (!response.ok) throw new Error(`接口状态 ${response.status}`);
        applyDashboardPayload(await response.json());
        recordApiSync("/api/dashboard", true, "loaded");
        status.textContent = "接口已连接";
        status.classList.remove("offline");
      } catch (error) {
        status.textContent = "离线回退数据";
        recordApiSync("/api/dashboard", false, error.message);
        status.classList.add("offline");
      } finally {
        refresh.disabled = false;
      }
    }
    function applyBackendHealth(payload) {
      if (!payload || payload.status !== "ok" || !payload.counts) {
        throw new Error("健康检查数据结构不完整");
      }
      backendHealth = payload;
    }
    function includesAll(values, required) {
      return Array.isArray(values) && required.every(key => values.includes(key));
    }
    function validateDashboardSchema(endpoint) {
      if (!endpoint || !includesAll(endpoint.methods, ["GET"])) {
        throw new Error("API dashboard schema contract incomplete");
      }
      if (!includesAll(endpoint.responseKeys, ["meta", "paretoFront", "cycleRows", "ironLossRows", "algorithmRows", "deliveryItems"])) {
        throw new Error("API dashboard schema contract incomplete");
      }
      if (!includesAll(endpoint.responseObjectKeys?.paretoFront, ["candidate", "label", "meanScore", "feasible", "loss", "family", "color"])) {
        throw new Error("API dashboard schema contract incomplete");
      }
      if (!includesAll(endpoint.responseObjectKeys?.cycleRows, ["candidate", "cycle", "feasibleWeight", "copperLoss", "score"])) {
        throw new Error("API dashboard schema contract incomplete");
      }
      if (!includesAll(endpoint.responseObjectKeys?.ironLossRows, ["speed", "targetFeasible", "ironLoss", "efficiency"])) {
        throw new Error("API dashboard schema contract incomplete");
      }
      if (endpoint.responseTupleLengths?.algorithmRows !== 4 || endpoint.responseTupleLengths?.deliveryItems !== 2) {
        throw new Error("API dashboard schema contract incomplete");
      }
    }
    function validateDecisionPackSchema(endpoint) {
      const businessKeys = ["production", "mileage", "energyPrice", "validationInvestment"];
      const weightKeys = ["urban_low_speed", "highway_high_speed", "launch_peak_torque"];
      if (!endpoint || !includesAll(endpoint.methods, ["GET", "POST"])) {
        throw new Error("API decision-pack schema contract incomplete");
      }
      if (!includesAll(endpoint.getQueryKeys, ["candidate", ...businessKeys, ...weightKeys])) {
        throw new Error("API decision-pack schema contract incomplete");
      }
      if (!includesAll(endpoint.postJson?.requiredKeys, ["candidate", "businessAssumptions", "weights"])) {
        throw new Error("API decision-pack schema contract incomplete");
      }
      if (!includesAll(endpoint.postJson?.businessAssumptionKeys, businessKeys) || !includesAll(endpoint.postJson?.weightKeys, weightKeys)) {
        throw new Error("API decision-pack schema contract incomplete");
      }
      if (!includesAll(endpoint.responseObjectKeys?.selected, ["candidate", "label", "family", "meanScore", "weightedCopperLossW", "feasible"])) {
        throw new Error("API decision-pack schema contract incomplete");
      }
      if (!includesAll(endpoint.responseObjectKeys?.businessCase, ["assumptions", "perVehicleAnnualSavingYuan", "fleetAnnualSavingYuan", "paybackMonths"])) {
        throw new Error("API decision-pack schema contract incomplete");
      }
      if (!includesAll(endpoint.responseObjectKeys?.weights, weightKeys)) {
        throw new Error("API decision-pack schema contract incomplete");
      }
      if (!includesAll(endpoint.responseObjectKeys?.ranking, ["candidate", "label", "family", "simulatedScore", "simulatedFeasible", "rank"])) {
        throw new Error("API decision-pack schema contract incomplete");
      }
    }
    function validateHealthSchema(endpoint) {
      if (!endpoint || !includesAll(endpoint.methods, ["GET"])) {
        throw new Error("API health schema contract incomplete");
      }
      if (!includesAll(endpoint.responseKeys, ["status", "source", "schemaVersion", "page", "pageAvailable", "counts"])) {
        throw new Error("API health schema contract incomplete");
      }
      if (!includesAll(endpoint.responseObjectKeys?.counts, ["paretoFront", "cycleRows", "ironLossRows", "algorithmRows", "deliveryItems"])) {
        throw new Error("API health schema contract incomplete");
      }
    }
    function validateScenarioStateSchema(endpoint) {
      if (!endpoint || !includesAll(endpoint.methods, ["GET", "DELETE"])) {
        throw new Error("API scenario-state schema contract incomplete");
      }
      if (!includesAll(endpoint.responseKeys, ["source", "schemaVersion", "stateAvailable", "stateSource", "state"])) {
        throw new Error("API scenario-state schema contract incomplete");
      }
      if (!includesAll(endpoint.responseObjectKeys?.state, ["candidate", "businessAssumptions", "weights"])) {
        throw new Error("API scenario-state schema contract incomplete");
      }
    }
    function validateSessionSnapshotSchema(endpoint) {
      if (!endpoint || !includesAll(endpoint.methods, ["GET", "POST", "DELETE"])) {
        throw new Error("API session-snapshot schema contract incomplete");
      }
      if (!includesAll(endpoint.requestStateKeys, ["candidate", "businessAssumptions", "weights", "decisionPack", "apiSyncLog"])) {
        throw new Error("API session-snapshot schema contract incomplete");
      }
      if (!includesAll(endpoint.responseKeys, ["source", "schemaVersion", "snapshotAvailable", "snapshot", "metadata"])) {
        throw new Error("API session-snapshot schema contract incomplete");
      }
      if (!includesAll(endpoint.responseObjectKeys?.snapshot, ["candidate", "businessAssumptions", "weights", "decisionPack", "apiSyncLog", "metadata"])) {
        throw new Error("API session-snapshot schema contract incomplete");
      }
      if (!includesAll(endpoint.metadataKeys, ["snapshotId", "createdAt", "updatedAt", "source", "schemaVersion", "apiContractVersion"])) {
        throw new Error("API session-snapshot schema contract incomplete");
      }
    }
    function validateCustomerBriefSchema(endpoint) {
      if (!endpoint || !includesAll(endpoint.methods, ["GET", "POST"])) {
        throw new Error("API customer-brief schema contract incomplete");
      }
      if (!includesAll(endpoint.requestStateKeys, ["candidate", "businessAssumptions", "weights"])) {
        throw new Error("API customer-brief schema contract incomplete");
      }
      if (!includesAll(endpoint.responseKeys, ["source", "schemaVersion", "candidate", "brief", "decisionPack"])) {
        throw new Error("API customer-brief schema contract incomplete");
      }
      if (!includesAll(endpoint.responseObjectKeys?.decisionPack, ["source", "schemaVersion", "selected", "gains", "businessCase", "weights", "ranking"])) {
        throw new Error("API customer-brief schema contract incomplete");
      }
    }
    function validateDesignSpecSchema(endpoint) {
      if (!endpoint || !includesAll(endpoint.methods, ["GET"])) {
        throw new Error("API design-spec schema contract incomplete");
      }
      if (!includesAll(endpoint.responseKeys, ["source", "schemaVersion", "file", "spec"])) {
        throw new Error("API design-spec schema contract incomplete");
      }
      if (!includesAll(endpoint.responseObjectKeys?.spec, ["name", "product", "page", "design_system", "audience", "tokens", "components"])) {
        throw new Error("API design-spec schema contract incomplete");
      }
    }
    function applyBackendSchema(payload) {
      const required = ["/api/dashboard", "/api/health", "/api/schema", "/api/scenario-state", "/api/decision-pack", "/api/session-snapshot", "/api/customer-brief", "/api/design-spec"];
      const endpoints = payload?.endpoints || [];
      const paths = new Set(endpoints.map(endpoint => endpoint.path));
      if (payload?.source !== "backend-api" || payload?.schemaVersion !== 1 || !required.every(path => paths.has(path))) {
        throw new Error("API schema contract incomplete");
      }
      validateDashboardSchema(endpoints.find(endpoint => endpoint.path === "/api/dashboard"));
      validateHealthSchema(endpoints.find(endpoint => endpoint.path === "/api/health"));
      validateScenarioStateSchema(endpoints.find(endpoint => endpoint.path === "/api/scenario-state"));
      validateDecisionPackSchema(endpoints.find(endpoint => endpoint.path === "/api/decision-pack"));
      validateSessionSnapshotSchema(endpoints.find(endpoint => endpoint.path === "/api/session-snapshot"));
      validateCustomerBriefSchema(endpoints.find(endpoint => endpoint.path === "/api/customer-brief"));
      validateDesignSpecSchema(endpoints.find(endpoint => endpoint.path === "/api/design-spec"));
      backendSchema = payload;
    }
    async function loadBackendHealth() {
      try {
        const response = await fetch("/api/health", { headers: { "Accept": "application/json" } });
        if (!response.ok) throw new Error(`健康检查状态 ${response.status}`);
        applyBackendHealth(await response.json());
        recordApiSync("/api/health", true, "ok");
      } catch (error) {
        recordApiSync("/api/health", false, error.message);
        backendHealth = null;
      }
    }
    async function loadBackendSchema() {
      try {
        const response = await fetch("/api/schema", { headers: { "Accept": "application/json" } });
        if (!response.ok) throw new Error(`schema ${response.status}`);
        applyBackendSchema(await response.json());
        recordApiSync("/api/schema", true, "verified");
      } catch (error) {
        backendSchema = null;
        recordApiSync("/api/schema", false, error.message);
      }
    }
    async function loadRuntimeData() {
      await Promise.all([loadDashboardData(), loadBackendHealth(), loadBackendSchema(), loadOpenDesignSpec()]);
      await loadScenarioState();
      await loadSessionSnapshot();
    }
    function selectCandidate(candidate) {
      selected = candidate;
      renderFilters();
      renderMetrics();
      renderBenefits();
      renderCompareSelector();
      renderCompareBoard();
      renderWeightSimulator();
      renderDemoFlow();
      renderOpenDesignTokens();
      renderAlgorithmMaturity();
      renderSolutionDrilldown();
      renderBusinessCase();
      renderSensitivityMatrix();
      renderMeetingScript();
      renderStageGateBoard();
      renderEvidenceGapPriority();
      renderReviewQuestionBoard();
      renderDecisionPackPreview();
      renderCustomerMinutes();
      renderValidationTimeline();
      renderValidationRiskHeatmap();
      renderBenchmarkBoard();
      renderClosureBoard();
      renderDeliveryHealth();
      renderPresentationState();
      drawPareto();
      drawCycle();
      drawReach();
    }
    function renderAll() {
      renderFilters();
      renderMetrics();
      renderRoutes();
      renderAlgorithmMap();
      renderAlgorithmMaturity();
      renderDeliveryList();
      renderBenefits();
      renderCompareSelector();
      renderCompareBoard();
      renderWeightSimulator();
      renderDemoFlow();
      renderOpenDesignTokens();
      renderSolutionDrilldown();
      renderBusinessCase();
      renderSensitivityMatrix();
      renderMeetingScript();
      renderStageGateBoard();
      renderEvidenceGapPriority();
      renderReviewQuestionBoard();
      renderDecisionPackPreview();
      renderCustomerMinutes();
      renderValidationTimeline();
      renderValidationRiskHeatmap();
      renderBenchmarkBoard();
      renderClosureBoard();
      renderDeliveryHealth();
      drawPareto();
      drawCycle();
      drawReach();
      drawIronLoss();
    }
    window.addEventListener("resize", renderAll);
    bindPlayback();
    bindWeightSimulator();
    bindBusinessCase();
    bindPresentationMode();
    document.getElementById("export-decision-pack")?.addEventListener("click", exportDecisionPack);
    document.getElementById("copy-meeting-script")?.addEventListener("click", copyMeetingScript);
    document.getElementById("copy-review-answer")?.addEventListener("click", copyReviewAnswer);
    document.getElementById("copy-decision-pack-preview")?.addEventListener("click", copyDecisionPackPreview);
    document.getElementById("copy-customer-minutes")?.addEventListener("click", copyCustomerMinutes);
    document.getElementById("copy-validation-timeline")?.addEventListener("click", copyValidationTimeline);
    document.getElementById("copy-validation-risk")?.addEventListener("click", copyValidationRiskHeatmap);
    document.getElementById("clear-scenario-state")?.addEventListener("click", clearScenarioState);
    document.getElementById("save-session-snapshot")?.addEventListener("click", saveSessionSnapshot);
    document.getElementById("clear-session-snapshot")?.addEventListener("click", clearSessionSnapshot);
    document.getElementById("compare-target").addEventListener("change", (event) => {
      compareCandidate = event.target.value;
      renderCompareBoard();
    });
    document.getElementById("refresh-data").addEventListener("click", () => {
      loadRuntimeData().finally(renderAll);
    });
    document.getElementById("export-brief").addEventListener("click", exportCustomerBrief);
    document.getElementById("export-design-spec").addEventListener("click", exportOpenDesignSpec);
    loadRuntimeData().finally(renderAll);
  