#!/usr/bin/env python3
"""
批量执行 Claude Code 命令的脚本 - 支持 DAG 格式
从template文件中提取任务并用claude执行
"""

import sys
import time
import subprocess
import argparse
import os
from typing import Tuple, List
from pathlib import Path
from batch_executor_base import BaseBatchExecutor, TaskResult
from dag_parser import DAGParser, TaskNode
from dag_executor import DAGExecutor


class ClaudeCodeBatchExecutor(BaseBatchExecutor):
    """Claude Code 批量执行器"""

    def __init__(self):
        super().__init__("batchcc.py")

    def build_command(self, task_description: str) -> str:
        """
        根据任务描述构建完整的cc命令

        Args:
            task_description: 任务描述

        Returns:
            cc命令字符串
        """
        # 转义内部的单引号，避免命令解析错误
        escaped_description = task_description.replace("'", "\\'")
        return f"cc '{escaped_description}'"

    def execute_command_parallel(self, args: Tuple[int, str, str]) -> TaskResult:
        """
        并行执行单个cc命令（重写以支持Claude命令转换）

        Args:
            args: (task_id, command, working_dir) 元组

        Returns:
            TaskResult: 任务执行结果
        """
        task_id, command, working_dir = args
        start_time = time.time()

        try:
            # 提取cc命令中的内容并转换为claude命令
            if command.startswith("cc '") and command.endswith("'"):
                content = command[4:-1]  # 移除 cc ' 和 '
                # 构建claude命令
                claude_cmd = [
                    "/Users/zhanglingxiao/.nvm/versions/node/v22.18.0/bin/claude",
                    "-p", content,
                    "--allowedTools", "*",
                    "--permission-mode", "acceptEdits"
                ]

                # 执行claude命令
                result = subprocess.run(
                    claude_cmd,
                    cwd=working_dir,
                    capture_output=True,  # 并行时捕获输出
                    text=True,
                    timeout=1800  # 30分钟超时
                )
            else:
                # 直接执行原命令
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=working_dir,
                    capture_output=True,
                    text=True,
                    timeout=1800
                )

            duration = time.time() - start_time
            success = result.returncode == 0
            output = result.stdout if success else ""
            error_msg = result.stderr if not success else ""

            return TaskResult(
                task_id=task_id,
                command=command,
                success=success,
                duration=duration,
                output=output,
                error_msg=error_msg
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return TaskResult(
                task_id=task_id,
                command=command,
                success=False,
                duration=duration,
                error_msg="命令执行超时 (30分钟)"
            )
        except Exception as e:
            duration = time.time() - start_time
            return TaskResult(
                task_id=task_id,
                command=command,
                success=False,
                duration=duration,
                error_msg=str(e)
            )

    def execute_command_serial(self, command: str, working_dir: str, task_id: int) -> bool:
        """
        串行执行单个cc命令（重写以支持Claude命令转换）

        Args:
            command: 要执行的cc命令
            working_dir: 工作目录
            task_id: 任务ID

        Returns:
            执行是否成功
        """
        print(f"\n{'=' * 80}")
        print(f"[{task_id}] 执行命令: {command}")
        print(f"工作目录: {working_dir}")
        print(f"{'=' * 80}")

        try:
            # 提取cc命令中的内容并转换为claude命令
            if command.startswith("cc '") and command.endswith("'"):
                content = command[4:-1]  # 移除 cc ' 和 '
                # 构建claude命令
                claude_cmd = [
                    "/Users/zhanglingxiao/.nvm/versions/node/v22.18.0/bin/claude",
                    "-p", content,
                    "--allowedTools", "*",
                    "--permission-mode", "acceptEdits"
                ]

                print(f"转换为claude命令: {' '.join(claude_cmd)}")

                # 执行claude命令
                result = subprocess.run(
                    claude_cmd,
                    cwd=working_dir,
                    capture_output=False,  # 实时显示输出
                    text=True
                )
            else:
                # 直接执行原命令
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=working_dir,
                    capture_output=False,
                    text=True
                )

            if result.returncode == 0:
                print("✅ 命令执行成功")
                return True
            else:
                print(f"❌ 命令执行失败，返回码: {result.returncode}")
                return False

        except Exception as e:
            print(f"❌ 执行命令时发生异常: {e}")
            return False

    def execute_dag_task(self, task: TaskNode) -> bool:
        """
        执行单个 DAG 任务

        Args:
            task: 任务节点

        Returns:
            执行是否成功
        """
        command = self.build_command(task.description)
        working_dir = os.getcwd()

        return self.execute_command_serial(command, working_dir, task.task_id)

    def execute_dag_batch_parallel(self, tasks: List[TaskNode], max_workers: int) -> List[TaskResult]:
        """
        并行执行一批 DAG 任务

        Args:
            tasks: 任务列表
            max_workers: 最大并发数

        Returns:
            执行结果列表
        """
        # 构建命令列表
        commands = [self.build_command(task.description) for task in tasks]
        working_dir = os.getcwd()

        # 使用基类的并行执行方法
        return self.execute_parallel(commands, working_dir, max_workers)


def is_dag_format(file_path: str) -> bool:
    """
    检查文件是否是 DAG 格式

    Args:
        file_path: 文件路径

    Returns:
        是否是 DAG 格式
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 简单检查：包含 ## STAGE ## 标记
            return '## STAGE ##' in content
    except:
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量执行 Claude Code 命令 - 支持 DAG 格式')
    parser.add_argument('template', nargs='?', help='template文件路径')
    parser.add_argument('-p', '--parallel', type=int, default=8,
                       help='并行执行的最大工作线程数 (默认: 8)')
    parser.add_argument('--single', action='store_true',
                       help='强制串行执行 (一次只执行一个任务)')
    parser.add_argument('--max-parallel', type=int, default=8,
                       help='允许的最大并行数 (默认: 8)')
    parser.add_argument('--dry-run', action='store_true',
                       help='仅显示执行计划，不实际执行')

    args = parser.parse_args()

    # 创建执行器
    executor = ClaudeCodeBatchExecutor()

    # 确定template文件路径
    if args.template:
        template_file = Path(args.template)
    else:
        template_file = executor.get_default_template_path()

    # 检查template文件是否存在
    if not template_file.exists():
        executor.print_usage_help(template_file)
        return 1

    # 检查是否是 DAG 格式
    if is_dag_format(str(template_file)):
        print(f"batchcc.py - DAG 模式")
        print(f"模板文件: {template_file}")
        print(f"当前工作目录: {os.getcwd()}")
        print()

        try:
            # 使用 DAG 执行器
            dag_executor = DAGExecutor(
                str(template_file),
                executor.execute_dag_task
            )

            if args.dry_run:
                # 显示执行计划
                dag_executor.print_plan()
                return 0
            else:
                # 执行任务
                success = dag_executor.execute(
                    lambda tasks, max_workers: executor.execute_dag_batch_parallel(tasks, max_workers)
                )
                return 0 if success else 1

        except Exception as e:
            print(f"❌ DAG 执行失败: {e}")
            import traceback
            traceback.print_exc()
            return 1

    else:
        # 原有的简单格式（## TASK ## 标记）
        print(f"batchcc.py - 简单模式")
        print(f"模板文件: {template_file}")
        print(f"当前工作目录: {os.getcwd()}")

        # 确定并行度
        if args.single:
            max_workers = 1
            is_parallel = False
        else:
            import multiprocessing as mp
            max_workers = min(args.parallel, args.max_parallel, mp.cpu_count())
            is_parallel = max_workers > 1

        print(f"执行模式: {'串行' if args.single else '并行'}")
        if is_parallel:
            print(f"并发数: {max_workers}")
        print()

        # 提取命令
        print("📋 解析模板文件...")
        commands = executor.extract_commands(str(template_file))

        if not commands:
            print("❌ 未找到任何命令")
            return 1

        print(f"✅ 找到 {len(commands)} 个命令:")
        for i, cmd in enumerate(commands, 1):
            preview = cmd[:80] + "..." if len(cmd) > 80 else cmd
            print(f"  {i}. {preview}")

        # 执行命令
        if is_parallel and len(commands) > 1:
            # 并行执行
            results = executor.execute_parallel(commands, os.getcwd(), max_workers)
            executor.print_parallel_results(results)
            success_count = sum(1 for r in results if r.success)
        else:
            # 串行执行
            success_count, _ = executor.execute_serial_batch(commands, os.getcwd())

        return 0 if success_count == len(commands) else 1


if __name__ == "__main__":
    sys.exit(main())
