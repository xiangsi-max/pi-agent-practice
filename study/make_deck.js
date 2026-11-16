// Minimal 2-slide deck built with pptxgenjs, following the pptx skill's "structured deck" guidance.
const path = require("path");
const PptxGenJS = require("pptxgenjs");

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_16x9";
pptx.author = "Pi Agent 实践课";
pptx.title = "Pi Agent 实践课 1 成果汇报";

const NAVY = "1B2A41";
const BLUE = "0066CC";
const GREY = "5A6472";

// ---------- Slide 1: title ----------
const s1 = pptx.addSlide();
s1.background = { color: "FFFFFF" };
s1.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.33, h: 0.28, fill: { color: BLUE } });
s1.addText("Pi Agent 实践课 1", {
  x: 0.9, y: 1.9, w: 11.5, h: 1.0,
  fontSize: 44, bold: true, color: NAVY, align: "left",
});
s1.addText("安装、配置与基础使用成果汇报", {
  x: 0.9, y: 3.0, w: 11.5, h: 0.7,
  fontSize: 22, color: GREY, align: "left",
});
s1.addShape(pptx.ShapeType.line, {
  x: 0.9, y: 3.95, w: 3.2, h: 0,
  line: { color: BLUE, width: 3 },
});
s1.addText("Node.js 26.13.1  ·  Pi 1.5.2  ·  Windows", {
  x: 0.9, y: 4.3, w: 11.5, h: 0.5,
  fontSize: 14, color: GREY, align: "left",
});

// ---------- Slide 2: results table ----------
const s2 = pptx.addSlide();
s2.background = { color: "FFFFFF" };
s2.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.33, h: 0.28, fill: { color: BLUE } });
s2.addText("六项任务完成情况", {
  x: 0.9, y: 0.7, w: 11.5, h: 0.7,
  fontSize: 32, bold: true, color: NAVY, align: "left",
});

const H = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: BLUE } } });
const C = (t) => ({ text: t, options: {} });

const rows = [
  [H("任务"), H("结果"), H("关键证据")],
  [C("1 安装并启动"), C("完成"), C("Pi 1.5.2，工作目录 pi-test")],
  [C("2 配置模型与会话"), C("完成"), C("deepseek-flash 回复「你好」")],
  [C("3 切换模型/思考级别"), C("完成"), C("flash ⇄ v4-pro，thinking off→high")],
  [C("4 @引用 与 粘贴图片"), C("完成"), C("hello.py 解释+输出 5；识别蓝色方块 7")],
  [C("5 安装并试用插件"), C("完成"), C("pi-web-access 取到 Example Domain")],
  [C("6 PPT Skill（选做）"), C("完成"), C("/skill:pptx 发现并调用成功")],
];

s2.addTable(rows, {
  x: 0.6, y: 1.7, w: 12.0,
  colW: [3.0, 1.4, 7.6],
  border: { type: "solid", color: "D8DEE9", pt: 1 },
  fontSize: 13,
  color: NAVY,
  valign: "middle",
  rowH: 0.55,
  autoPage: false,
});

const out = path.join(__dirname, "pi-agent-report.pptx");
pptx.writeFile({ fileName: out }).then((f) => console.log("wrote " + f));
