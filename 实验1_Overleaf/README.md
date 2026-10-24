# 实验1：Web服务器搭建与HTTP协议分析

## Overleaf 编译

1. 在 Overleaf 新建项目，选择 **Upload Project / 上传项目**，上传本 ZIP。
2. 主文件选择根目录 `main.tex`。
3. 在项目设置中将编译器设为 **XeLaTeX**，建议使用当前可用的较新 TeX Live 版本。
4. 重新编译并下载 PDF，提交时保留 `06_实验1_姓名_学号.pdf` 的规范名称。

中文字体使用 TeX Live 提供的 Fandol，不依赖 Arch 本地字体或 Windows 的宋体；图片及文档使用相对路径。
本工程已在本机使用基于 XeTeX 的 Tectonic 0.17.0 实际编译，并在干净解压目录中复核。
没有替你上传到 Overleaf，也没有提交到课程平台。
正文内容栏有高度保护：超过栏目容量会产生明确的 `report-layout` 编译错误，不会隐藏溢出的文字；大量增加正文或更换版式时应相应调整分页。

## 文件说明

- `main.tex`：完整报告、封面和模板栏目的表格式排版。
- `assets/scu.png`、`assets/logo.png`：用户提供的四川大学校名字样与校徽。
- `assets/apache-browser.png`：真实隔离 Chromium 窗口，包含实际地址栏。
- `assets/apache-config.png`：实际终端中的 Apache 版本、关键配置、语法检查、监听及访问日志。
- `assets/http-*.png`：本次 Wireshark 的真实截图；`-crop` 版本裁掉无关空白和窗格，响应图保留报文详情区域，用于正文排版，完整原图同时保存。
- `evidence/http-experiment.pcapng`：本机实际捕获的原始38帧，过滤器限定为实验服务器 TCP 80 流量。
- `evidence/frame-*.txt`、`http-fields.tsv`、`http.json`、`all-http-details.txt`：TShark 从上述文件直接导出的帧详情与字段。
- `evidence/file1-body.html`、`file2-body.html`：从真实响应中导出的实体，分别为128和371字节。
- `evidence/software-provenance.txt`：Linux 软件包的官方来源、SHA-256 和独立签名验证输出。
- `evidence/environment.json`：当次路由、捕获过滤器与环境记录。
- `experiment/httpd.conf`、`experiment/www/index.html`：本次实际使用的服务器配置和自建页面。

## 核心实测结果

| 目标 | 请求帧 | 响应帧 | 结果 |
|---|---:|---:|---|
| file1 | 8 | 12 | HTTP/1.1，200 OK，HTML实体128字节 |
| file2 首次 | 20 | 23 | 200 OK，HTML实体371字节，给出Last-Modified和ETag |
| file2 普通刷新 | 28 | 29 | 自动发送两种验证器，304 Not Modified，无实体正文 |

### 在 Wireshark 复核

打开 `evidence/http-experiment.pcapng`，使用显示过滤器：

```text
http
```

只看目标页面的六个关键帧：

```text
frame.number == 8 || frame.number == 12 || frame.number == 20 || frame.number == 23 || frame.number == 28 || frame.number == 29
```

查看缓存验证的同一 TCP 流：

```text
tcp.stream == 1
```

帧14/15和25/26是浏览器请求 favicon 及其301响应，不是目标 HTML 页。
报文的日期字段用 GMT，终端/捕获界面可能使用本地时区，这不会改变报文字段本身。

## 本地实验服务器的运行范围

本次没有安装或启用系统级 Apache 服务，而是从 Arch 官方包验证签名后解包运行。
实际 Linux 运行文件位于 `/tmp/opencode/nc-cl-work/runtime`，不放进 Overleaf ZIP。
配置文件保存的是本次实验的真实绝对路径，因此不能直接在其他电脑上运行；这不影响 LaTeX 编译。
如需长期保留服务，应自行安装 Arch 的 `apache` 软件包，将配置中的运行库/模块路径换为系统安装路径，并保留仅回环监听的安全范围。

本次网页 URL：`http://127.0.0.1:8086/`。
实际部署目录：当前工程的 `experiment/www/`，默认页面 `index.html`。

## 尚未提供、应保持空白的栏目

教学周未提供；老师评议、成绩、签名应由教师填写，因此这些位置保留空白。
课时栏按给出的课程信息写“第3—4节”，未猜测额外课时。

## 隐私提醒

报告和页面按要求包含姓名、学号及课程信息，抓包还包含当次内网IP。
这些材料用于个人课程提交，不应直接公开发布原始工程或抓包。
