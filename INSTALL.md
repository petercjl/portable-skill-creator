# 安装合同

用户入口：

> 请安装 @petercjl/portable-skill-creator。

当前 Agent 执行以下交接。npm 安装成功只完成引导包，完整安装还包括所选 Skill 与宿主发现。

1. 识别当前宿主的命令、文件操作能力及自己的实际 Skill 发现目录；解析出绝对、精确的目标 Skill 目录和合法 Agent 标识。缺失目录信息时请求该信息，不选取其他宿主目录。
2. 安装 npm 包并读取 `capabilities --json` 和 `skill source --json`。如 npm 禁用了脚本，仍执行相同流程。
3. 预检目标。已存在的非本包托管目录保持原样；经用户授权迁移时先检查、完整备份并验证，再从原路径移出。托管文件的本地改动需先核对和保留。
4. 按合同调用 `skill install --agent <agent> --target <absolute exact directory> --json`。完整复制 Skill、脚本、知识资源与 `.runtime` 中独立运行入口。所选目录外的其他 Agent 不参与同步。
5. 使用返回的目标专属入口核对 `version --json`、`doctor --json`、`skill status`。确认包、Skill 自述版本和回执一致，哈希 verified/current，物理资源与运行入口齐全。Node.js 22+、Python 3.10+ 为外部运行时；可用 `--python` 或 `PORTABLE_SKILL_PYTHON` 指定已验证的宿主管理 Python。
6. 当前 Agent 通过自己的目录/目录注册机制加载完整 SKILL.md；按精确逻辑名解析基础 `skill-creator` 并读取全部指令，确认发现有效。需要重开会话时明确报告 host discovery pending，不将 CLI 回执当作原生发现证据。

包命令只负责确定性资源管理与校验；创作判断、授权和实际产物验收由 Skill 与当前 Agent 承接。缺少宿主能力或基础 Skill 时返回明确依赖错误。
