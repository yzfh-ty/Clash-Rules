# Clash Rules

根据本地 [yzfh-ty/Shadowrocket-Rules](https://github.com/yzfh-ty/Shadowrocket-Rules) 配置同步的 Mihomo（Clash.Meta）分流配置。参考小火箭的服务分组，代理入口统一使用「🚀 节点选择」，保留 AI 优先级、WebRTC 防泄露和苹果推送目标限制。

本配置面向 Mihomo 内核，不兼容旧版 Clash Premium。原项目：[LingJingMaster/Clash-Rules](https://github.com/LingJingMaster/Clash-Rules)。

## 快速开始

1. 下载 [`Clash.yaml`](https://raw.githubusercontent.com/yzfh-ty/Clash-Rules/refs/heads/main/Clash.yaml)。
2. 在本地将 `proxy-providers.subscription.url` 替换为自己的 **Clash / Mihomo 格式订阅地址**。
3. 导入使用 Mihomo 内核的客户端，更新节点和规则集。
4. 在「🚀 节点选择」中选择「✋ 手动选择」或「⚡ 自动选择」；具体节点统一放在「✋ 手动选择」中。

需要自动选择低延迟节点时，在「🚀 节点选择」中点选「⚡ 自动选择」；「🌍 非中国」和「🐟 漏网之鱼」也可直接选它。该组检查全部订阅节点，每 600 秒检测一次 `https://www.gstatic.com/generate_204`，切换容差为 0，选择最近一次检测中延迟最低的可用节点。此延迟针对测速地址，不代表所有网站的实际速度。

配置和 `rules/` 必须一起发布到本 fork 的 `main` 分支，上面的下载链接才会提供新版本。请勿将私人订阅地址提交到公开仓库。已有客户端保存的策略选择可能覆盖配置的默认值。

## 3x-ui 订阅模板

[`Clash.3x-ui.yaml`](Clash.3x-ui.yaml) 用于让 3x-ui 下发的 Clash/Mihomo 订阅自带本项目的分流规则。模板包含原配置的策略组、规则集、规则顺序、DNS 和 hosts；每个用户的节点由面板动态生成，无需在模板中填写私人订阅地址。

在 3x-ui 的订阅设置中启用 Clash/Mihomo 路由规则，将模板的**完整 YAML 内容**粘贴到规则输入框，保存并重载面板。然后让用户更新原来的 Clash/Mihomo 订阅。该方式已在 3x-ui 3.11.0 验证；普通 Base64 节点订阅不携带这些分流规则。

手动和自动选择组使用 `include-all-proxies: true` 收集当前订阅中的节点，主选择组仍保留手动、自动、DIRECT 和 REJECT 四个入口。模板不包含 `proxy-providers`、节点凭据、TUN、监听端口或外部控制接口，客户端自行管理这些运行设置。

请使用上述**内联 YAML**方式：面板的远程模板 URL 模式可能只合并部分配置字段，不能视为完全等价。编辑本地 YAML 文件后，也需要重新保存到面板并重载才会生效。规则集仍按原配置中的公开 URL 更新。

更新 `Clash.yaml` 后重新生成模板（Python 3，需安装 PyYAML）：

```sh
python scripts/build-3x-ui-template.py
python scripts/build-3x-ui-template.py --check
```

## 默认策略

| 分组 | 默认策略 |
|---|---|
| 🚀 节点选择 | ✋ 手动选择；仅显示手动、自动、DIRECT、REJECT 四项 |
| ✋ 手动选择 | 订阅中的第一个节点，可手动切换 |
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
| 🌍 非中国 | 🚀 节点选择 |
| 🐟 漏网之鱼 | 🚀 节点选择 |

Clash 不再创建额外的 `PROXY` 分组。小火箭首页本身提供手动选节点的入口；Clash 在转换时增加「✋ 手动选择」集中列出订阅节点。「🚀 节点选择」中的 `PROXY` 转为手动组，其他 `PROXY` 引用统一转为「🚀 节点选择」。「🌍 非中国」「🐟 漏网之鱼」和通用 DNS 默认跟随「🚀 节点选择」，切换手动 / 自动选择后一起生效。

谷歌、非苹果邮件、YouTube、Telegram、GitHub / GitLab / Atlassian、微软均使用「🌍 非中国」，移除旧版独立服务分组和地区组。AI 规则先于 Google、微软及代码托管规则匹配。苹果推送先于苹果常规规则匹配。

## 分流与转换边界

- WebRTC：UDP 3478、5349、19302–19309 的中国大陆目标先交给「🔒 国内服务」，其余交给默认拒绝的「🛡️ WebRTC 防泄露」；这不覆盖所有 WebRTC 流量。
- 苹果推送：TCP 5223 仅匹配苹果 `17.0.0.0/8` 和小火箭配置中的四个 APNs IPv6 地址段，另保留 `push.apple.com` 域名规则。IPv6 默认关闭。
- 保留 Clash 原有的 `dm.wo.com.cn` 拒绝规则及小红书国内 DNS 修复；保留 Grok 附件存储域名直连。
- 通用 DNS 使用经过「🚀 节点选择」的 Cloudflare / Google DoH，两者在 Mihomo 中并发查询，不等同于小火箭的主备顺序。直连 DNS 使用 `system`；小火箭 `[Host]` 中的系统 DNS 后缀转换为对应 DNS 策略和真实 IP 过滤。
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

2026-11-11：3x-ui 内联模板保留 15 个策略组、22 个规则集和 55 条规则。使用 Mihomo v1.19.34 加载全部非空规则集，确认手动、自动组包含当前订阅的全部节点、主选择组保持四个入口，并完成 HTTPS 代理实测。3x-ui 3.11.0 保存并重载后，实际订阅输出与模板一致；验证过程中的私人订阅样本未纳入仓库。

2026-11-08 简化入口后：主配置通过 Mihomo 语法检查；隔离实例确认无额外 `PROXY` 组、手动组直接列出订阅节点、主选择组保留四项，非中国和兜底默认跟随主选择组，并可切换到自动选择。两端路由规则未改动，转换结果可重复生成且分组引用无环。iOS 移除重复的手动组，继续通过首页选择节点。

2026-11-08 新增手动 / 自动选择后：Mihomo 隔离实例确认「节点选择」只显示四个入口、具体节点集中在「手动选择」；两个本地模拟节点实测约 351 ms / 21 ms，自动组选中 21 ms 节点。保留全部路由规则和规则集，未在 iOS 实机验证。

2026-11-08：使用本机 Mihomo v1.19.30 通过主配置语法检查；下载 14 个外部规则集、读取八个本地转换规则集，在关闭 TUN / DNS 监听的隔离实例中确认全部 22 个规则集完整加载、14 个组的默认选择正确。静态匹配检查覆盖 48 个 WebRTC 场景、21 个 APNs 边界场景和 22 个典型域名；重复同步输出保持字节一致，`git diff --check` 通过。自建规则集使用本地文件验证，未验证发布后的 Raw 链接；未使用真实订阅或验证客户端联网、系统 DNS、TUN 和运行时 GEOIP 分类。

## License

MIT
