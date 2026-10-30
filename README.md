# @petercjl/portable-skill-creator

面向具备所需能力的任意 Agent，创建、更新、审查和迁移可维护的 Skill。包含创作主线、按需读取的知识层、能力合同与确定性校验器。

## 安装

把下面的提示词发送给当前使用的 Agent：

> 请安装 @petercjl/portable-skill-creator。

当前 Agent 识别自己的 Skill 目录，完成包管理安装、资源同步与发现检查。所需环境为 Node.js 22+、Python 3.10+、文件与命令执行能力，以及宿主提供的基础 `skill-creator`。安装不授予其他服务权限。

## 更新

> 请更新 @petercjl/portable-skill-creator。

## 使用

> 请用 portable-skill-creator，把我提供的流程制作成可复用的 Skill。

也可提出审查、优化或迁移需求，并附上目标 Skill。创建时先梳理业务流程，再完善独立策略；自然语言、已有资料和可选脑图均可作为输入。

生成的 Skill 按用户熟悉的业务流程图展示运行台账，保留业务节点、顺序和分支；节点直接呈现状态、简短结果与产物入口，展开后查看策略、证据、历史和技术明细。策略更新时在相同业务图中标明受影响节点及沿用结果。台账记录包括：输入与策略依据、输出文件、结论、验收和历史轮次。可以查询某个节点的真实结果，追溯其上游证据，并规划受影响节点的局部重跑。文件型工作流提供独立的 Python 台账生成模板，目标 Skill 负责业务判断和执行授权。

> 请检查这个 Skill 中“用户需求”节点的输出、结论和依据，并说明需要重跑哪些节点。

普通任务入口会限时检查稳定版更新，每日缓存；更新提示由 Agent 展示，实际安装需要明确授权。

完整安装与恢复流程见 [INSTALL.md](INSTALL.md) 和 [UPDATE.md](UPDATE.md)。包提供物理独立的资源与运行入口；只操作当前 Agent 选定的目录。

## 兼容性与验证

调用资格取决于能力合同。基础 Skill Creator 由当前宿主动态提供；本包不复制它。通用安装接口支持合法 Agent 标识和显式目标目录。macOS 本机与跨平台 CI 证据分别记录在仓库 `docs/verification.md`；SealSeek 原生映射仍待验证，其他宿主需自行完成能力映射与发现检查。包级测试不等于所有宿主已验证。

## 开发者入口

运行 `portable-skill-creator capabilities --json` 读取版本化命令合同，`skill source --json` 获取规范资源路径。自动更新检测可用 `PORTABLE_SKILL_UPDATE_CHECK=0` 关闭；它不会自动安装。源码是本独立包的唯一维护来源。历史工作环境套件中的副本由其所有者另行迁移。
