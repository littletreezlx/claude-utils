# [任务名称] - DAG 执行计划
# 生成时间: [YYYY-MM-DD HH:mm]
# 总阶段数: [N]
# 预计任务数: [M]

## STAGE ## name="阶段名称" mode="serial" depends_on=""
# 阶段说明：[为什么这样设计这个阶段]

## TASK ## id="task-id" depends_on="" on_failure="stop" retry="0"
[任务描述]

文件: [文件范围，使用 glob 模式]
排除: [排除的文件]
验证: [验证命令]

## TASK ## id="another-task" depends_on="" on_failure="stop"
[下一个任务描述]

文件: [文件范围]
验证: [验证命令]

## STAGE ## name="下一个阶段" mode="parallel" max_workers="4" depends_on="stage:1"
# 阶段说明：[为什么可以并行]

## TASK ## id="parallel-task-1" on_failure="continue"
[并行任务 1 描述]

文件: [文件范围]
排除: [排除的文件，避免冲突]
验证: [验证命令]

## TASK ## id="parallel-task-2" on_failure="continue"
[并行任务 2 描述]

文件: [文件范围]
排除: [排除的文件]
验证: [验证命令]

## STAGE ## name="测试阶段" mode="serial" depends_on="stage:2"
# 阶段说明：[为什么必须等前面完成]

## TASK ## id="test-task" on_failure="retry" retry="2"
[测试任务描述]

文件: [文件范围]
验证: [验证命令]
