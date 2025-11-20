# Claude Code 工具集

这个目录包含 Claude Code 和 Codex 相关的工具脚本和配置管理。

## 目录结构

```
~/.claude/my-scripts/
├── batch/                              # 批量执行工具
│   ├── batchcc.py                      # Claude Code 批量执行脚本
│   ├── batchcx.py                      # Codex 批量执行脚本
│   ├── batch_executor_base.py          # 批量执行基础类
│   └── batch-helpers.zsh               # 批量工具 ZSH 函数和别名
│
├── config-manager/                      # 配置管理
│   └── gac-manager.zsh                 # GAC 配置切换工具
│
└── README.md                            # 本文件
```

## 批量执行工具

### 命令

- `batchcc [template] [选项]` - 批量执行 Claude Code 命令
- `batchcx [template] [选项]` - 批量执行 Codex 命令
- `batchcc-todo <次数>` - 批量执行 /todo-doit 命令（强制串行）

### 选项

- `--single` - 强制串行执行（一次只执行一个任务）
- `-p N, --parallel N` - 自定义并发数（默认：8）
- `-h, --help` - 显示帮助信息

### 使用示例

```bash
# 默认8并发执行当前目录的template
batchcc

# 串行执行当前目录的template
batchcc --single

# 默认8并发执行指定template文件
batchcc my-template.md

# 串行执行指定template文件
batchcc my-template.md --single

# 4并发执行当前目录的template
batchcc -p 4

# 2并发执行指定template文件
batchcc my-template.md -p 2

# 串行执行5次 /todo-doit
batchcc-todo 5

# 串行执行10次 /todo-doit
batchcc-todo 10
```

## GAC 配置管理

### 命令

- `cc-gac-main` / `gacm` - 切换到主账户配置（高推理努力）
- `cc-gac-little` / `gacl` - 切换到小号配置（低推理努力）
- `cc-glm` / `glmg` - 切换到 GLM Claude Code 配置
- `cc-official` / `gaco` - 切换到官方 Claude Code 配置
- `gac-status` / `gacs` - 查看当前配置状态

### 配置说明

GAC 配置管理器允许你在不同的 Claude Code 配置之间快速切换：

- **主账户（main）**：使用 littletree0718@gmail.com，高推理努力级别
- **小号（little）**：使用 602788458@qq.com，低推理努力级别
- **GLM**：使用 GLM Claude Code 配置
- **官方（official）**：使用官方 Claude Code 配置

### 配置文件

- `~/.gaccode_profile` - 当前配置类型（main/little/glm/official）
- `~/.codex/config` - Codex 配置文件
- `~/.claudecode/config` - Claude Code 配置文件
- `~/.codex/config.toml` - 推理努力级别配置
- `~/.claude.json` - API Key 批准列表

## 加载方式

这些工具通过 `~/.zshrc` 自动加载：

```zsh
# 加载 Claude Code 相关工具
if [ -f $HOME/.claude/my-scripts/batch/batch-helpers.zsh ]; then
    source $HOME/.claude/my-scripts/batch/batch-helpers.zsh
fi

if [ -f $HOME/.claude/my-scripts/config-manager/gac-manager.zsh ]; then
    source $HOME/.claude/my-scripts/config-manager/gac-manager.zsh
fi
```

## 迁移说明

这些工具原本分散在不同位置：

- 批量工具：`~/LittleTree_Projects/python_test/projects/claude-code/`
- GAC 配置：`~/LittleTree_Projects/cs/zsh/claude-code.zsh`

现在统一整合到 `~/.claude/my-scripts/` 目录下，便于管理和维护。

## 环境变量

- `BATCH_TOOLS_ROOT`: `$HOME/.claude/my-scripts/batch`

## 依赖

- Python 3（用于批量执行脚本）
- jq（用于 JSON 处理，GAC 配置管理需要）
- zsh（shell 环境）
