为当前Flutter项目建立标准化的UI文档架构系统，解决UI文档过大、维护困难、AI协作低效等问题。

## 执行流程

### 第一步：项目检查（2分钟）

检查当前目录是否为Flutter项目：

**验证条件**：
- 存在 `pubspec.yaml` 文件
- 包含 `flutter` 依赖
- 项目结构符合Flutter标准

**特殊情况处理**：
- 如果不是Flutter项目：提示用户确认是否继续
- 如果已有UI_SHOWCASE.md：检查文件大小，>200行建议重构

### 第二步：创建文档架构（5分钟）

创建完整的UI文档结构：

**文件结构**：
```
项目根目录/
├── UI_SHOWCASE.md              # 主索引导航 (~150行)
├── claude-ui-config.md         # AI协作配置片段
└── docs/ui/
    ├── screens.md              # 界面设计详情
    ├── components.md           # 组件库详情
    ├── theme.md                # 设计系统
    └── responsive.md           # 响应式规范
```

### 第三步：生成内容模板（10分钟）

基于项目特征生成文档内容：

**UI_SHOWCASE.md**：
- 应用概览（从pubspec.yaml提取项目信息）
- UI架构总览图（提供标准模板）
- 专题文档导航链接
- 快速参考信息

**专题文档**：
- 使用LittleTree AI的成熟文档作为模板
- 根据项目类型调整（mobile/web/desktop）
- 预留定制化标记

### 第四步：配置AI协作（3分钟）

生成AI协作配置：

**claude-ui-config.md**：
- UI修改关键词触发机制
- 专题文档映射关系
- 完整闭环流程说明
- 集成到CLAUDE.md的指导

### 第五步：后续指导（5分钟）

提供完善指导：

**定制化建议**：
- 需要用户手动完善的内容清单
- 优先级排序（界面设计 > 组件库 > 主题系统）
- 参考资源链接

## 使用方法

在Flutter项目根目录执行：
```
/init_ui_showcase
```

## 输出要求

- 生成的文档必须包含完整的内容结构
- 提供清晰的后续完善指导
- 确保AI协作配置正确
- 标注所有需要用户定制的内容

## ⚠️ 注意事项

- 如果项目已有UI_SHOWCASE.md且内容丰富，建议先备份
- 生成的文档是框架，需要根据项目具体内容填充
- 生成后需要将claude-ui-config.md内容集成到项目CLAUDE.md中

## 预期效果

- **查找效率**: UI信息定位时间减少80%
- **维护成本**: UI文档维护工作量降低60%
- **AI协作**: Claude识别UI修改需求的准确率提升到95%
- **标准化**: 与其他Flutter项目保持一致的文档标准

## 相关资源

- 详细架构设计: `docs/ui-architecture/UI_DOCUMENTATION_SYSTEM.md`
- 最佳实践指南: `docs/ui-architecture/BEST_PRACTICES.md`