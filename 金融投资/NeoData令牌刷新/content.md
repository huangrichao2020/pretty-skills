# NeoData 令牌刷新 · 金融数据管道鉴权运维

> NeoData 金融搜索服务的鉴权 token 12 小时过期，失效时依赖它的 skill（机会挖掘等）会走「模板降级」、输出假数据。本文是把 2026-08-20 实战踩出的「token 刷新 SOP」沉淀为可复用运维流程：connect_cloud_service 拿 tempToken → query.py --save-token 写缓存 → 重跑验证。
> 适用于所有调用 NeoData 的 agent / skill。

---

## P0 · 概览与定位

- **一句话**：NeoData token 12h 过期，失效时 skill 走模板降级，必须手动刷新才能恢复真数据。
- **来源**：idea-trade-qa v0.4.0 实战（2026-08-20）· NeoData token 刷新 SOP。
- **定位**：数据管道鉴权运维 · 12h 周期性失效 · 影响所有依赖 NeoData 的 skill。
- **触发信号**：skill 报「数据拉取失败」→ 降级方案 → 检查 `.neodata_token` 时间戳。
- **影响范围**：机会挖掘 / 任何调 NeoData 的 agent（金融问答、板块监控）。
- **调用链路**：connect_cloud_service → tempToken → query.py --save-token → 重跑 skill。
- **认知锚点**：一个沙漏（12h）压在「NeoData 数据管道」阀门上，阀门关闭=降级，刷新=重新打开，强调「周期性失效」。

## P1 · 失效信号与判定

- **核心主张**：skill 输出突然变「模板降级」/ 报数据拉取失败 = token 大概率过期。
- **信号①**：idea_trade_qa.py 返回「❌ 数据拉取失败，请检查 NeoData 凭证或网络连接」。
- **信号②**：NeoData query.py 直接返回 401 / token invalid。
- **判定**：看 `~/.workbuddy/skills/.neodata_token` 的 saved_at，超过 12h 即失效。
- **误判排除**：先排除网络问题（WebSearch 还能用 = 网络正常，问题在 token）。
- **认知锚点**：一个仪表盘亮起红色「401」灯，旁边对比「WebSearch 绿灯」，说明网络通、唯独 NeoData 凭证挂了。

## P2 · 刷新 step1 · 拿 tempToken

- **核心主张**：第一步用 connect_cloud_service 工具拿临时 token（24h 有效）。
- **操作**：调 connect_cloud_service → 返回 tempToken 字符串。
- **时效**：tempToken 24h 有效（比 12h 缓存宽裕，留刷新窗口）。
- **实测**：2026-08-20 拿到 `tk_2Q2p3TbahZ4rQmJddSnvK6pr0zAPV8n3`。
- **注意**：这是「临时」凭证，必须立刻写进缓存文件才持久生效。
- **认知锚点**：一只手从「IDE 会话」里接过一个发光的临时令牌，标注 24h，强调「临时、要立刻落地」。

## P3 · 刷新 step2 · 写入缓存

- **核心主张**：第二步用 query.py --save-token 把 token 写进缓存文件（权限 600）。
- **命令**：`python3 ~/.workbuddy/skills/NeoData金融搜索服务/scripts/query.py --save-token "<token>"`。
- **落点**：`SKILLS_DIR/.neodata_token`（JSON `{token, saved_at}`）或兼容旧纯文本。
- **权限**：写入时 600，避免 token 泄露到其它用户/进程。
- **校验**：重跑 query.py 不带参数应能读到有效 token（非 None）。
- **认知锚点**：一个保险箱（权限 600）把令牌锁进去，旁边打勾「持久化成功」，强调「落盘才生效」。

## P4 · 刷新 step3 · 验证

- **核心主张**：第三步重跑 skill，确认真数据恢复（不再降级）。
- **验证**：`python3 idea_trade_qa.py --query "..."` → 出现真实板块/涨停数据。
- **预期**：emit_intraday_section 输出真 `sector_leaders` / `limit_up_stocks`。
- **兜底**：仍失败 → 检查 token 是否复制完整（首尾无空格、无换行截断）。
- **认知锚点**：刷新后阀门重新打开，数据流从「降级灰」变回「真数据绿」，强调「验证闭环」。

## P5 · 自动化与监控建议

- **核心主张**：把「12h 刷新」做成定时/自愈，别每次人工救火。
- **思路①**：类似 git-pull-safe，包装脚本在调 NeoData 前自动 detect 过期并刷新。
- **思路②**：cron 每 11h 跑一次 `--save-token`（用固定 tempToken 源）。
- **监控**：skill 启动先 probe token 有效性，失效即告警而不是默默降级。
- **注意**：tempToken 本身 24h，缓存写 12h 有效期是 query.py 内部逻辑，别混。
- **认知锚点**：一个自动巡检机器人定时给沙漏「续命」，强调「自愈优于救火」。

## P6 · 踩坑与收束

- **核心主张**：别用 gh auth login 修 NeoData token（两码事）；token 文件别进 git。
- **不要做**：`gh auth login`（那是 GitHub 凭证，与 NeoData 完全无关，修了也白修）。
- **不要做**：把 `.neodata_token` 提交到 git（含密钥，污染公开仓）。
- **跨仓独立**：info-hub 的 GitHub PAT 与 NeoData token 是两套体系，别混为一谈。
- **收尾**：刷新后重跑验证 + skill 末尾「非投资建议」声明照旧。
- **认知锚点**：一个「禁止」标志同时挡住 gh auth login 和 git add token，强调「别走错路、别泄露」。

### Shot List

必画 ≤6 张（防画册陷阱，写给 AI 出图 prompt 用）：

1. 12h 沙漏压在数据阀门上（P0）
2. 401 红灯 vs WebSearch 绿灯（P1）
3. 接过 24h 临时令牌（P2）
4. 600 保险箱锁令牌（P3）
5. 阀门重开数据变绿（P4）
6. 禁止 gh login / 禁止 git add token（P6）

选画：自动巡检续命机器人（P5）
