# Claude Code 模板库

本目录包含 Claude Code 使用的各类模板文件，分为文档模板和工作流模板两大类。

## 📁 目录结构

```
templates/
├── workflow/                       # DAG / 任务工作流模板
└── README.md                       # 本说明文档
```

## 📋 工作流模板 (workflow/)

### feature-planning.md
**用途**: 功能规划模板，供用户填写
**内容**: 功能概述、实施计划、技术路径、测试策略
**使用**: 用户复制模板到项目中填写，规划新功能开发

### debug-workflow.md
**用途**: Bug调试流程模板，供用户填写
**内容**: 问题分析、调试策略、修复记录、预防措施
**使用**: 用户复制模板到项目中填写，系统化解决问题

## 🎯 使用方式

### 复制到项目使用
将workflow模板复制到项目中填写：

```bash
# 功能规划
cp ~/.claude/commands/templates/workflow/feature-planning.md ./docs/features/new-feature.md

# Bug调试
cp ~/.claude/commands/templates/workflow/debug-workflow.md ./docs/bugs/issue-123.md
```

## 📝 模板设计原则

### 文档模板 (供AI参考)
- 提供结构框架和编写指导
- 包含完整示例和最佳实践
- AI根据实际项目自适应调整

### 工作流模板 (供用户填写)
- 清晰的填写指引和占位符
- 系统化的思考流程
- 便于追踪和归档

## 🔄 模板维护

### 更新原则
- 模板基于实际使用经验持续优化
- 保持模板简洁实用，避免过度设计
- 文档模板体现项目架构最佳实践

### 新增模板
如需新增模板类型，请遵循：
1. 明确模板用途和使用场景
2. 提供清晰的使用说明
3. 更新本 README 文档
4. 更新相关 command 引用

---

**维护者**: 根据 Claude Code 使用反馈持续优化
**更新日期**: 2025-10-10
