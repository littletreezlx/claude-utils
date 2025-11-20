# 简单测试 - DAG 任务编排
# 生成时间: 2025-11-10 17:00
# 总阶段数: 3
# 预计任务数: 6

## STAGE ## name="创建测试目录" mode="serial"
# 阶段说明：必须先创建目录结构

## TASK ## id="create-dirs" on_failure="stop"
创建测试目录结构

验证: ls -la /tmp/dag_test/

## STAGE ## name="创建测试文件" mode="parallel" max_workers="3" depends_on="stage:1"
# 阶段说明：各个文件独立，可以并行创建

## TASK ## id="file-a" on_failure="continue"
创建测试文件 A

验证: test -f /tmp/dag_test/file_a.txt && echo "File A created"

## TASK ## id="file-b" on_failure="continue"
创建测试文件 B

验证: test -f /tmp/dag_test/file_b.txt && echo "File B created"

## TASK ## id="file-c" on_failure="continue"
创建测试文件 C

验证: test -f /tmp/dag_test/file_c.txt && echo "File C created"

## STAGE ## name="验证和汇总" mode="serial" depends_on="stage:2"
# 阶段说明：必须等所有文件创建完成后才能验证

## TASK ## id="count" depends_on="file-a,file-b,file-c" on_failure="stop"
统计创建的文件数量

验证: test $(ls /tmp/dag_test/*.txt | wc -l) -eq 3 && echo "All 3 files created successfully"

## TASK ## id="summary" depends_on="count" on_failure="stop"
生成测试报告

验证: test -f /tmp/dag_test/summary.txt && echo "Summary report generated"
