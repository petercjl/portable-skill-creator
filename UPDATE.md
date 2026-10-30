# 更新合同

用户入口：

> 请更新 @petercjl/portable-skill-creator。

当前 Agent 先从本次明确选定的 Skill 目录读取托管回执，核对 `skill status`，并确认目标、所有权与本地改动。完整匹配的当前回执可用于只读验证，宿主发现独立核对。

授权更新后，使用所选目标的 `.runtime/bin/portable-skill-creator.mjs` 入口，按 `capabilities --json` 中的合同调用 `update install`，携带合法 Agent、绝对精确目标和 `--yes`。在任何包替换前解析目标，保护编辑，创建完整恢复快照。查询稳定 latest，获取精确版本，校验包身份后同步所选目标。版本相同仍修复缺失文件、旧回执或旧 Skill；当前一致时保持只读 no-op。用户自己的 UI 元数据与非托管文件被保留。

返回的目标专属运行入口代表已激活的新版本。全局 npm 包是引导入口，后续业务和更新使用目标自有入口，不依赖引导包继续存在。若希望更新全局引导包，当前 Agent在上述预检后安装相同精确版本，再复核所选目标。

注册/刷新由当前宿主完成。核对 CLI、Skill manifest、回执版本与哈希后，再加载新 Skill；其他 Agent 保持各自安装。

## 恢复

离线、超时或无效注册表响应保留现有安装。更新获取后同步失败时，错误回执给出 transaction 与 candidateEntry；读取 transaction/operation.json 和实际目标状态，复用该候选入口执行 `skill update`，避免再次获取。完整原始快照位于 transaction/before 或安装回执的 backup/skill。迁移失败、编辑冲突和锁竞争保持未完成状态，先检查证据再恢复。恢复备份或删除锁前核实所有权与运行任务。回滚时保留当前目录的新备份，再以验证过的旧快照恢复，并复核状态。

检测策略为建议更新、稳定 latest、每日缓存和 1.5 秒网络超时；缓存可通过 `--state-dir` 放在宿主管理位置。`update status` 公开策略，`PORTABLE_SKILL_UPDATE_CHECK=0` 关闭检测。当前版本未提供自动安装模式。
