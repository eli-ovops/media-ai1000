# 本地CLI：公开博主素材接入前提与证据层

当前更正：用户已接受任务单V2并授权独立研究包装及精确公开素材路径；首条已取得、完整音轨转录和66图实际读取，见[V2分析](V2内容分析/7685352868332817707.md)与[研究包装](V2本地读取/launch.mjs)。研究白名单只含已登记公开片，缓存和回执隔离；原工具白名单及验收只读。两项拒绝测试通过。下面保留标准确认前的接入设计记录，旧“尚未允许/待用户答复”不再是当前阻断。

2026-10-07本轮更新。结论：本地读取服务已有实测，无需再安装ASR或大模型；本研究尚未被允许将公开博主原片加入工具精确白名单，当前也未对研究样本运行ASR。原“完整动态＋直接听音”标准保持，是否接受转录＋采样/区间图由用户通过PMO确认。

已读原件：[工具README](/Volumes/EXTERNAL/自媒体/工具验证/video-mcp-20261007/README.md)、[工具验收](/Volumes/EXTERNAL/自媒体/工具验证/video-mcp-20261007/验收报告.md)、`allowed-files.json`、`read-video.mjs`、`evidence/acceptance.json`字段；[PMO接入结论](CLI接入复核/接入结论.md)。工具Owner验过ASR/图序列，PMO独立stdio调用`video_info`通过；本Owner未重跑两者，不将这份用户试拍计为AI博主研究样本。

## 公开素材接入的具体前提

1. 先由PMO确认用户是否接受新研究证据标准。未答复时，不新抽帧试拍、不改“全声画/深拆0”的计数。此选择不阻碍账号目录、页面数据和源回执整理。
2. 第一条候选可选老马`7685352868332817707`，页面时长38.010998秒、[公开原页面](https://www.douyin.com/video/7685352868332817707)。这只是拟验证对象，本轮未下载。正常浏览器导出成功后才登记确切本地MP4路径、video ID、原链接、文件字节/SHA、容器时长、声画轨和取得日期；失败先查阻断，不绕验证/安全拒绝。
3. 工具白名单目前只有一条用户试拍。URL输入、云ASR、旁文件写入和其他路径禁用。不能直接把抖音详情URL交给工具，不能把整目录通配符加进白名单。新增公开素材的精确路径需要由有权限的工具Owner/PMO处理，本研究Owner不改源码、配置、白名单、trust或系统。
4. `read-video.mjs`当前固定写工具目录的`evidence/cli-info.json`或`cli-analyze.json`。**不要直接运行它覆盖已有验收。**后续应复用PMO已实证的Node＋SDK＋`launch.mjs`标准stdio方式，将调用原始回执保存到本研究目录的该video ID独立证据路径；原工具证据保持只读。实际调用代码由获授权执行者在本目录准备，不能只把输出路径改在文档里便声称调用已隔离。
5. 首条仅先`video_info`核路径/时长/声画轨，再决定是否运行`video_analyze`。同一试拍不与PMO并行调用，不用旧缓存证明新文件；文件内容变化需新缓存键及SHA复核。

## 输入与原始输出合同

现有runtime：`/Users/USER/.local/nodejs/node-v22.16.0-darwin-arm64/bin/node`。SDK位于工具目录`upstream/node_modules/@modelcontextprotocol/sdk`，stdio启动器为`launch.mjs`。这是已存在的本地入口，自动MCP加载/trust不是CLI使用前提。

|调用|请求|保留字段|可支持的结论|
|---|---|---|---|
|`video_info`|`source=已登记且已批准的绝对路径`、JSON响应|durationSec/width/height/fps、hasAudio/hasVideo、codec、sizeBytes/warnings|文件元数据与轨道存在；不是内容读取|
|`video_analyze`|detailed、interval、max_frames=30、language=zh、skip_ocr=true、inline_images=true|info、transcript、frames(index/timeSec/path)、inlineCount/inlineIndices、warnings、timeline、elapsedMs|本地ASR与处理过的采样图；实际看图数量另记|
|`video_get_frame_burst`|仅针对已获准素材的明确区间，按已支持schema设置|frames、inlineCount/inlineIndices|该区间图序列；不能称整片连续动态观看|

研究数据应增加：`source_sha256`、`tool_call_id/原始回执路径`、`audio_processed_range`、`transcript_read_range`、`asr_uncertainties`、`frames_generated`、`frames_actually_read`、`frame_times`、`burst_ranges_read`、`unread_intervals`、`eye_contact_evidence`、`voice_prosody_evidence`、`coverage_standard_version`、`core_analysis_complete`。生成30图而内联只看6图必须记实际6，不计30；只读转录不能填声音语气/配乐。

## 当前工具限制与验证要求

工具Owner19.77秒试拍的一次`video_analyze`耗时63.42秒，只是该文件该次运行，不据此估1000条吞吐。本地处理已避免云端与付费调用；新增媒体缓存总量仍不超过2GiB，图/WAV/JSON逐路径登记，不清理其他Owner资产。内存需求和新公开片实际耗时/缓存量UNKNOWN，首条实测后记录。

默认ASR存在专名错词；词表补读时间戳0—30秒超过19.77秒原片，不能用于时序。新素材需检查每段end是否超时长、是否存在漏段/无字幕非语音内容，错词标不确定。`timeSec`是采样网格名义时间，不能当逐帧精确PTS。图片不能证明完整眼神、镜头运动或直接听到语调，字幕也不能替代BGM/音效。

若用户接受该标准，第一条提交“整音轨ASR＋实际看过的图/区间＋明确欠项”的样例供PMO审原件；名称应为该证据标准下的内容分析，不能追溯改称全动态声画已读。若用户仍坚持直接全片动态观看与听音，该服务保持文字/画面辅助层，完整声画通路继续受阻。任何情况下原1000条目标保持。
