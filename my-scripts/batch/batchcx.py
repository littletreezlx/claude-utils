#!/usr/bin/env python3
"""
批量执行 Codex 命令的脚本 - 基于通用基类实现
从template文件中提取任务并用codex exec执行
"""

import sys
import time
import subprocess
import argparse
from typing import Tuple
from batch_executor_base import BaseBatchExecutor, TaskResult


class CodexBatchExecutor(BaseBatchExecutor):
    """Codex 批量执行器"""

    def __init__(self):
        super().__init__("batchcx.py")

    def build_command(self, task_description: str) -> str:
        """
        根据任务描述构建完整的codex exec命令

        Args:
            task_description: 任务描述

        Returns:
            完整的codex exec命令
        """
        # 转义内部的双引号，避免命令解析错误
        escaped_description = task_description.replace('"', '\\"')
        return f'codex exec "{escaped_description}" --skip-git-repo-check --yolo'

    def execute_command_parallel(self, args: Tuple[int, str, str]) -> TaskResult:
        """
        并行执行单个codex命令（重写以支持Codex命令转换）

        Args:
            args: (task_id, command, working_dir) 元组

        Returns:
            TaskResult: 任务执行结果
        """
        task_id, command, working_dir = args
        start_time = time.time()

        try:
            # 提取codex命令中的内容并转换为完整路径命令
            if command.startswith('codex exec "') and command.endswith('" --skip-git-repo-check --yolo'):
                content = command[12:-31]  # 移除 'codex exec "' 和 '" --skip-git-repo-check --yolo'
                content = content.replace('\\"', '"')  # 反转义双引号

                # 构建codex命令（使用完整路径）
                codex_cmd = [
                    "/Users/zhanglingxiao/.nvm/versions/node/v22.18.0/bin/codex",
                    "exec", content,
                    "--skip-git-repo-check", "--yolo"
                ]

                # 执行codex命令
                result = subprocess.run(
                    codex_cmd,
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
        串行执行单个codex命令（重写以支持Codex命令转换）

        Args:
            command: 要执行的codex命令
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
            # 提取codex命令中的内容并转换为完整路径命令
            if command.startswith('codex exec "') and command.endswith('" --skip-git-repo-check --yolo'):
                content = command[12:-31]  # 移除前缀和后缀
                content = content.replace('\\"', '"')  # 反转义双引号

                # 构建codex命令
                codex_cmd = [
                    "/Users/zhanglingxiao/.nvm/versions/node/v22.18.0/bin/codex",
                    "exec", content,
                    "--skip-git-repo-check", "--yolo"
                ]

                print(f"转换为codex命令: {' '.join(codex_cmd)}")

                # 执行codex命令
                result = subprocess.run(
                    codex_cmd,
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


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量执行 Codex 命令 - 默认并行执行')
    parser.add_argument('template', nargs='?', help='template文件路径')
    parser.add_argument('-p', '--parallel', type=int, default=8,
                       help='并行执行的最大工作线程数 (默认: 8)')
    parser.add_argument('--single', action='store_true',
                       help='强制串行执行 (一次只执行一个任务)')
    parser.add_argument('--max-parallel', type=int, default=8,
                       help='允许的最大并行数 (默认: 8)')

    args = parser.parse_args()

    # 创建执行器并运行
    executor = CodexBatchExecutor()
    return executor.run(
        template_file_arg=args.template,
        parallel=args.parallel,
        single=args.single,
        max_parallel=args.max_parallel
    )


if __name__ == "__main__":
    sys.exit(main())