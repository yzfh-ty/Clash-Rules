# Clash Rules

根据本地 [yzfh-ty/Shadowrocket-Rules](https://github.com/yzfh-ty/Shadowrocket-Rules) 配置同步的 Mihomo（Clash.Meta）分流配置。保留小火箭的服务分组、默认策略、AI 优先级、WebRTC 防泄露和苹果推送目标限制。

本配置面向 Mihomo 内核，不兼容旧版 Clash Premium。原项目：[LingJingMaster/Clash-Rules](https://github.com/LingJingMaster/Clash-Rules)。

## 快速开始

1. 下载 [`Clash.yaml`](https://raw.githubusercontent.com/yzfh-ty/Clash-Rules/refs/heads/main/Clash.yaml)。
2. 在本地将 `proxy-providers.subscription.url` 替换为自己的 **Clash / Mihomo 格式订阅地址**。
3. 导入使用 Mihomo 内核的客户端，更新节点和规则集。
4. 在「🚀 节点选择」中选择「✋ 手动选择」或「⚡ 自动选择」；具体节点统一放在「✋ 手动选择」中。

需要自动选择低延迟节点时，在「🚀 节点选择」中点选「⚡ 自动选择」；「🌍 非中国」和「🐟 漏网之鱼」也可直接选它。该组检查全部订阅节点，每 600 秒检测一次 `https://www.gstatic.com/generate_204`，切换容差为 0，选择最近一次检测中延迟最低的可用节点。此延迟针对测速地址，不代表所有网站的实际速度。

配置和 `rules/` 必须一起发布到本 fork 的 `main` 分支，上面的下载链接才会提供新版本。请勿将私人订阅地址提交到公开仓库。已有客户端保存的策略选择可能覆盖配置的默认值。

## 默认策略

| 分组 | 默认策略 |
|---|---|
| PROXY | 订阅中的第一个节点，可手动切换 |
| 🚀 节点选择 | ✋ 手动选择；仅显示手动、自动、DIRECT、REJECT 四项 |
| ✋ 手动选择 | PROXY，也可直接选择订阅节点 |
| ⚡ 自动选择 | 最近测速中延迟最低的可用订阅节点 |
| 🧱 DNS 防泄露 | REJECT |
| 🛡️ WebRTC 防泄露 | REJECT |
| 🤖 AI 服务 | 🚀 节点选择 |
| 🍏 苹果服务 | DIRECT |
| 🍎 苹果推送 | 🚀 节点选择 |
| 🏦 汇丰香港 | DIRECT |
| 🏦 香港银行 | DIRECT |
| 📈 券商服务 | 🚀 节点选择 |
| 🏠 私有网络 | DIRECT |
| 🔒 国内服务 | DIRECT |
| 🌍 非中国 | PROXY |
| 🐟 漏网之鱼 | PROXY |

Clash 中增加了独立的 `PROXY` 订阅选择组，对应小火箭的当前代理。「🌍 非中国」和「🐟 漏网之鱼」默认使用 `PROXY`；如果「✋ 手动选择」单独选了其他节点，这两个分组仍使用 `PROXY`。更改 `PROXY` 时，保持「🚀 节点选择 → ✋ 手动选择 → PROXY」的分组也会跟随。

谷歌、非苹果邮件、YouTube、Telegram、GitHub / GitLab / Atlassian、微软均使用「🌍 非中国」，移除旧版独立服务分组和地区组。AI 规则先于 Google、微软及代码托管规则匹配。苹果推送先于苹果常规规则匹配。

## 分流与转换边界

- WebRTC：UDP 3478、5349、19302–19309 的中国大陆目标先交给「🔒 国内服务」，其余交给默认拒绝的「🛡️ WebRTC 防泄露」；这不覆盖所有 WebRTC 流量。
- 苹果推送：TCP 5223 仅匹配苹果 `17.0.0.0/8` 和小火箭配置中的四个 APNs IPv6 地址段，另保留 `push.apple.com` 域名规则。IPv6 默认关闭。
- 保留 Clash 原有的 `dm.wo.com.cn` 拒绝规则及小红书国内 DNS 修复；保留 Grok 附件存储域名直连。
- 通用 DNS 使用经过 `PROXY` 的 Cloudflare / Google DoH，两者在 Mihomo 中并发查询，不等同于小火箭的主备顺序。直连 DNS 使用 `system`；小火箭 `[Host]` 中的系统 DNS 后缀转换为对应 DNS 策略和真实 IP 过滤。
- 保留 Clash 对全部 UDP / TCP 53 端口的 DNS 接管，并补齐小火箭的 TUN 排除网段。小火箭 `skip-proxy`、`bypass-system` 与 Mihomo 的 TUN / 规则机制并非完全相同，客户端系统代理绕过列表需按实际环境设置。
- 26 条 `USER-AGENT` 规则无法转换；渣打 `www.sc.com/hk/` 的路径规则扩大为整个 `www.sc.com` 主机。详细记录见 [`conversion-report.json`](conversion-report.json)。
- URL Rewrite / MITM 未转换。`block-quic=all-proxy`、不支持 UDP 时直接拒绝的设置未等价实现，不能认为已复制小火箭的全部防泄露行为。

语法依据：[Mihomo 路由规则](https://wiki.metacubex.one/config/rules/)、[DNS 配置](https://wiki.metacubex.one/config/dns/)、[代理组配置](https://wiki.metacubex.one/config/proxy-groups/)。

## 文件与同步

`Clash.yaml` 为主配置；`rules/` 包含从八个小火箭自建 `.list` 转换的 YAML，均通过本 fork 下载。blackmatrix7 外部规则继续使用其 Clash 格式。

后续从相邻目录的 `Shadowrocket-Rules` 重新同步（Python 3，需安装 PyYAML）：

```powershell
python scripts/sync-shadowrocket.py
```

也可以在命令末尾指定小火箭仓库路径。脚本会更新分组、规则顺序、自建规则集与转换报告，保留主配置中的订阅、TUN 和其他 DNS 设置。转换报告记录源配置及八个规则集的 SHA-256，便于核对来源。

## 验证记录

2026-11-08 新增手动 / 自动选择后：Mihomo 隔离实例确认「节点选择」只显示四个入口、具体节点集中在「手动选择」；两个本地模拟节点实测约 351 ms / 21 ms，自动组选中 21 ms 节点。保留全部路由规则和规则集，未在 iOS 实机验证。

2026-11-08：使用本机 Mihomo v1.19.30 通过主配置语法检查；下载 14 个外部规则集、读取八个本地转换规则集，在关闭 TUN / DNS 监听的隔离实例中确认全部 22 个规则集完整加载、14 个组的默认选择正确。静态匹配检查覆盖 48 个 WebRTC 场景、21 个 APNs 边界场景和 22 个典型域名；重复同步输出保持字节一致，`git diff --check` 通过。自建规则集使用本地文件验证，未验证发布后的 Raw 链接；未使用真实订阅或验证客户端联网、系统 DNS、TUN 和运行时 GEOIP 分类。

## License

MIT
