#!/usr/bin/env python3
"""
批量命令执行器基类 - 通用逻辑抽象
提供串行和并行执行能力的基础框架
"""

import os
import subprocess
import time
import threading
import multiprocessing as mp
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple, Dict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass


@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: int
    command: str
    success: bool
    duration: float
    output: str = ""
    error_msg: str = ""


class ProgressMonitor:
    """进度监控器"""

    def __init__(self, total_tasks: int):
        self.total_tasks = total_tasks
        self.completed_tasks = 0
        self.running_tasks: Dict[int, str] = {}
        self.lock = threading.Lock()
        self.start_time = time.time()

    def start_task(self, task_id: int, command: str):
        """开始任务"""
        with self.lock:
            self.running_tasks[task_id] = command
            self._print_status()

    def complete_task(self, task_id: int, success: bool):
        """完成任务"""
        _ = success  # 预留参数，将来可用于统计
        with self.lock:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            self.completed_tasks += 1
            self._print_status()

    def _print_status(self):
        """打印当前状态"""
        elapsed = time.time() - self.start_time
        progress = (self.completed_tasks / self.total_tasks) * 100
        running_count = len(self.running_tasks)

        print(f"\r🚀 进度: {self.completed_tasks}/{self.total_tasks} ({progress:.1f}%) | "
              f"运行中: {running_count} | 耗时: {elapsed:.1f}s", end="", flush=True)

        if self.completed_tasks == self.total_tasks:
            print()  # 完成后换行


class BaseBatchExecutor(ABC):
    """批量命令执行器基类"""

    def __init__(self, script_name: str):
        self.script_name = script_name

    def extract_tasks(self, template_file: str) -> List[str]:
        """
        从模板文件中提取任务描述 (通用方法)

        Args:
            template_file: 模板文件路径

        Returns:
            任务描述列表
        """
        tasks = []

        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 使用 ## TASK ## 标记分割任务
            task_sections = content.split('## TASK ##')

            for section in task_sections:
                section = section.strip()
                if section:  # 跳过空段落
                    # 清理任务描述，移除多余的空行
                    lines = [line.strip() for line in section.split('\n') if line.strip()]
                    if lines:
                        # 将多行任务描述合并为单行，用空格分隔
                        task_description = ' '.join(lines)
                        tasks.append(task_description)

        except FileNotFoundError:
            print(f"错误: 找不到文件 {template_file}")
            return []
        except Exception as e:
            print(f"错误: 读取文件时发生异常 {e}")
            return []

        return tasks

    def extract_commands(self, template_file: str) -> List[str]:
        """
        从模板文件中提取并构建命令 (使用新的任务提取逻辑)

        Args:
            template_file: 模板文件路径

        Returns:
            命令列表
        """
        tasks = self.extract_tasks(template_file)
        commands = []

        for task in tasks:
            command = self.build_command(task)
            commands.append(command)

        return commands

    @abstractmethod
    def build_command(self, task_description: str) -> str:
        """
        根据任务描述构建完整的可执行命令

        Args:
            task_description: 任务描述

        Returns:
            完整的可执行命令
        """
        pass

    def execute_command_parallel(self, args: Tuple[int, str, str]) -> TaskResult:
        """
        并行执行单个命令的包装函数

        Args:
            args: (task_id, command, working_dir) 元组

        Returns:
            TaskResult: 任务执行结果
        """
        task_id, command, working_dir = args
        start_time = time.time()

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,  # 并行时捕获输出
                text=True,
                timeout=1800  # 30分钟超时
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
        串行执行单个命令 (保持原有输出格式)

        Args:
            command: 要执行的命令
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
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=False,  # 实时显示输出
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

    def execute_parallel(self, commands: List[str], working_dir: str, max_workers: int) -> List[TaskResult]:
        """
        并行执行所有命令

        Args:
            commands: 命令列表
            working_dir: 工作目录
            max_workers: 最大并行工作线程数

        Returns:
            任务结果列表
        """
        print(f"\n🚀 开始并行执行 {len(commands)} 个命令，最大并发数: {max_workers}")

        # 创建进度监控器
        monitor = ProgressMonitor(len(commands))

        # 准备任务参数
        tasks = [(i + 1, cmd, working_dir) for i, cmd in enumerate(commands)]

        results = []

        # 使用进程池并行执行
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_task = {executor.submit(self.execute_command_parallel, task): task for task in tasks}

            # 启动任务监控
            for task in tasks:
                task_id, command, _ = task
                monitor.start_task(task_id, command)

            # 收集结果
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                task_id = task[0]

                try:
                    result = future.result()
                    results.append(result)
                    monitor.complete_task(task_id, result.success)
                except Exception as e:
                    # 创建失败结果
                    failed_result = TaskResult(
                        task_id=task_id,
                        command=task[1],
                        success=False,
                        duration=0,
                        error_msg=f"任务执行异常: {e}"
                    )
                    results.append(failed_result)
                    monitor.complete_task(task_id, False)

        # 按task_id排序结果
        results.sort(key=lambda x: x.task_id)
        return results

    def print_parallel_results(self, results: List[TaskResult]):
        """
        打印并行执行结果详情

        Args:
            results: 任务结果列表
        """
        print(f"\n{'=' * 80}")
        print("📋 详细执行结果")
        print(f"{'=' * 80}")

        success_count = sum(1 for r in results if r.success)
        total_duration = sum(r.duration for r in results)
        avg_duration = total_duration / len(results) if results else 0

        for result in results:
            status = "✅" if result.success else "❌"
            display_cmd = result.command[:60] + "..." if len(result.command) > 60 else result.command
            print(f"{status} [{result.task_id:2d}] {display_cmd}")
            print(f"     耗时: {result.duration:.2f}s")

            if not result.success and result.error_msg:
                print(f"     错误: {result.error_msg}")

            if result.success and result.output:
                # 显示输出的前几行
                output_lines = result.output.strip().split('\n')[:3]
                for line in output_lines:
                    if line.strip():
                        print(f"     输出: {line.strip()}")
            print()

        print(f"📊 统计信息:")
        print(f"   总任务数: {len(results)}")
        print(f"   成功执行: {success_count}")
        print(f"   执行失败: {len(results) - success_count}")
        print(f"   平均耗时: {avg_duration:.2f}s")
        print(f"   总计耗时: {total_duration:.2f}s")

    def execute_serial_batch(self, commands: List[str], working_dir: str):
        """
        串行批量执行命令

        Args:
            commands: 命令列表
            working_dir: 工作目录

        Returns:
            (success_count, failed_commands): 成功数量和失败命令列表
        """
        success_count = 0
        failed_commands = []

        for i, command in enumerate(commands, 1):
            print(f"\n[{i}/{len(commands)}] 正在执行...")

            if self.execute_command_serial(command, working_dir, i):
                success_count += 1
            else:
                failed_commands.append((i, command))

        # 串行执行结果汇总
        print(f"\n{'=' * 80}")
        print("📊 执行结果汇总")
        print(f"{'=' * 80}")
        print(f"总命令数: {len(commands)}")
        print(f"成功执行: {success_count}")
        print(f"执行失败: {len(failed_commands)}")

        if failed_commands:
            print("\n❌ 失败的命令:")
            for i, cmd in failed_commands:
                print(f"  {i}. {cmd}")

        return success_count, failed_commands

    def get_default_template_path(self) -> Path:
        """获取默认模板文件路径"""
        script_dir = Path(__file__).parent
        return script_dir / "template"

    def print_usage_help(self, template_file: Path):
        """打印使用帮助信息"""
        print(f"❌ 模板文件不存在: {template_file}")
        print("用法:")
        print(f"  python {self.script_name} [template_path] [选项]")
        print("示例:")
        print(f"  python {self.script_name}                    # 默认8并发执行")
        print(f"  python {self.script_name} --single           # 强制串行执行")
        print(f"  python {self.script_name} -p 4               # 自定义4个并发")
        print(f"  python {self.script_name} template -p 2      # 指定文件和并发数")

    def run(self, template_file_arg: str = None, parallel: int = 8, single: bool = False, max_parallel: int = 8) -> int:
        """
        运行批量执行器

        Args:
            template_file_arg: 模板文件路径参数
            parallel: 并行工作线程数
            single: 是否强制串行执行
            max_parallel: 最大并行数

        Returns:
            退出码 (0表示成功)
        """
        # 确定template文件路径
        if template_file_arg:
            template_file = Path(template_file_arg)
        else:
            template_file = self.get_default_template_path()

        # 确定并行度
        if single:
            max_workers = 1
            is_parallel = False
        else:
            max_workers = min(parallel, max_parallel, mp.cpu_count())
            is_parallel = max_workers > 1

        print(f"{self.script_name.title()} 批量执行脚本 - 增强版")
        print(f"模板文件: {template_file}")
        print(f"当前工作目录: {os.getcwd()}")
        print(f"执行模式: {'串行' if single else '并行'}")
        if is_parallel:
            print(f"并发数: {max_workers}")

        # 检查template文件是否存在
        if not template_file.exists():
            self.print_usage_help(template_file)
            return 1

        # 提取命令
        print("\n📋 解析模板文件...")
        commands = self.extract_commands(str(template_file))

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
            results = self.execute_parallel(commands, os.getcwd(), max_workers)
            self.print_parallel_results(results)
            success_count = sum(1 for r in results if r.success)
        else:
            # 串行执行
            success_count, _ = self.execute_serial_batch(commands, os.getcwd())

        return 0 if success_count == len(commands) else 1