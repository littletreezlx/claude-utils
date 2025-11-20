# 状态管理测试任务

## STAGE ## name="阶段1" mode="serial"
# 🎯 阶段目标：测试串行任务的状态管理
# 📥 输入：无
# 📤 输出：创建的测试文件

## TASK ##
创建目录

**📖 背景**：
测试状态管理功能的第一个任务

**🔨 要做什么**：
1. 创建测试目录 /tmp/state_test
2. 清空目录内容

**✅ 完成标志**：
- 目录存在
- 目录为空

文件: /tmp/state_test/

## TASK ##
创建文件A

**📖 背景**：
测试串行任务的状态记录

**🔨 要做什么**：
1. 在 /tmp/state_test/ 创建文件 file_a.txt
2. 写入内容 "Task A completed"

**✅ 完成标志**：
- 文件存在
- 内容正确

**📥 输入依赖**：
- ⬆️ 前一任务创建的目录

**📤 输出状态**：
- ✅ 文件 A 已创建
- ➡️ 为下一任务提供：可以创建更多文件

文件: /tmp/state_test/file_a.txt

## TASK ##
创建文件B（模拟失败）

**📖 背景**：
测试失败任务的状态记录和错误信息

**🔨 要做什么**：
1. 尝试创建文件 /tmp/state_test/file_b.txt
2. 故意使用错误命令导致失败

**✅ 完成标志**：
- 这个任务会失败，用于测试断点续传

**📥 输入依赖**：
- ⬆️ 前面任务创建的目录和文件

文件: /tmp/state_test/file_b.txt

## STAGE ## name="阶段2" mode="parallel" max_workers="2"
# 🎯 阶段目标：测试并行任务的状态管理
# 📥 输入：阶段1创建的文件
# 📤 输出：更多测试文件

## TASK ##
创建文件C

**📖 背景**：
测试并行任务1

**🔨 要做什么**：
1. 创建文件 /tmp/state_test/file_c.txt
2. 写入内容 "Task C completed"

**✅ 完成标志**：
- 文件存在
- 内容正确

文件: /tmp/state_test/file_c.txt

## TASK ##
创建文件D

**📖 背景**：
测试并行任务2

**🔨 要做什么**：
1. 创建文件 /tmp/state_test/file_d.txt
2. 写入内容 "Task D completed"

**✅ 完成标志**：
- 文件存在
- 内容正确

文件: /tmp/state_test/file_d.txt
