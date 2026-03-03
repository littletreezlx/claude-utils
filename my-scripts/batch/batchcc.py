#!/usr/bin/env python3
"""
批量执行 Claude Code 命令的脚本 - 支持 DAG 格式

## 用途
从 template 文件中提取任务并用 Claude 批量执行，支持：
- 简单格式（## TASK ## 标记）：并行/串行执行
- DAG 格式（## STAGE ## 标记）：复杂的阶段化任务编排
- 自动断点续传：中断后可自动从未完成的任务继续
- 自动 git commit：任务成功后自动提交代码变更

## 基本用法
```bash
# 使用默认 template.md 文件
python batchcc.py

# 指定模板文件
python batchcc.py task-refactor.md

# 并行执行（默认2个线程）
python batchcc.py --parallel 4

# 强制串行执行
python batchcc.py --single

# 查看执行计划（不实际执行）
python batchcc.py --dry-run

# 重新开始（清空状态文件）
python batchcc.py --restart
```

## 文档参考
- ~/.claude/commands/templates/workflow/DAG_TASK_FORMAT.md: DAG 格式规范
- CLAUDE.md: 维护指南
"""

import sys
import time
import subprocess
import argparse
import os
import signal
import shutil
from typing import Tuple, List
from pathlib import Path
from batch_executor_base import BaseBatchExecutor, TaskResult
from dag_parser import DAGParser, TaskNode
from dag_executor import DAGExecutor


# 全局变量：跟踪当前运行的子进程
_current_process: subprocess.Popen = None
_interrupted = False


def _signal_handler(signum, frame):
    """
    处理 Ctrl+C 信号

    优雅退出：
    1. 终止当前运行的 Claude 子进程
    2. 保留状态文件（任务标记为 interrupted）
    3. 打印友好提示
    """
    global _interrupted, _current_process
    _interrupted = True

    print("\n\n⚠️  收到中断信号 (Ctrl+C)")

    if _current_process and _current_process.poll() is None:
        print("🛑 正在终止当前任务...")
        try:
            _current_process.terminate()
            _current_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _current_process.kill()
        except Exception:
            pass

    print("💾 状态已保存，下次运行将从断点继续")
    print("💡 使用 --restart 可以重新开始\n")
    sys.exit(130)  # 标准的 Ctrl+C 退出码


# 注册信号处理器
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


class ClaudeCodeBatchExecutor(BaseBatchExecutor):
    """Claude Code 批量执行器"""

    def __init__(self):
        super().__init__("batchcc.py")
        self.claude_bin = shutil.which("claude")
        if not self.claude_bin:
            print("❌ 未找到 claude 命令，请确认已安装并在 PATH 中")
            sys.exit(1)
        self.auto_commit = True  # 默认启用自动执行 git commit
        self.state_manager = None  # 状态管理器（由 DAGExecutor 注入）
        self.current_stage_id = None  # 当前执行的阶段ID
        # 上下文信息（由 DAGExecutor 注入）
        self.global_goal = ""  # 项目宏观目标
        self.stage_context = ""  # 当前阶段上下文
        self.current_verify_cmd = ""  # 当前任务的验证命令

    def set_state_manager(self, state_manager, stage_id: int = None):
        """
        注入状态管理器和当前阶段ID

        Args:
            state_manager: StateManager 实例
            stage_id: 当前执行的阶段ID
        """
        self.state_manager = state_manager
        self.current_stage_id = stage_id

    def set_context(self, global_goal: str, stage_context: str):
        """
        注入上下文信息

        Args:
            global_goal: 项目宏观目标
            stage_context: 当前阶段上下文
        """
        self.global_goal = global_goal
        self.stage_context = stage_context

    def _auto_commit_if_needed(self, task_description: str, task_id: int = None):
        """
        任务执行成功后自动执行 git commit

        Args:
            task_description: 任务描述
            task_id: 任务ID（可选）
        """

        try:
            # 检查是否有未提交的更改
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print(f"⚠️ 检查 git status 失败，跳过自动提交")
                return

            # 如果没有未提交的更改，则跳过
            if not result.stdout.strip():
                print(f"📝 无文件变更，跳过自动提交")
                return

            # 执行 git add
            subprocess.run(
                ["git", "add", "."],
                capture_output=True,
                text=True,
                check=True
            )

            # 构建提交信息
            task_desc = task_description.replace("\n", " ").strip()
            task_desc = task_desc[:80] + ("..." if len(task_desc) > 80 else "")

            if task_id:
                commit_message = f"任务 {task_id}: {task_desc}"
            else:
                commit_message = task_desc

            # 执行 git commit
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                capture_output=True,
                text=True,
                check=True
            )

            print(f"✅ 自动提交成功: {task_desc[:50]}...")

        except subprocess.CalledProcessError as e:
            print(f"⚠️ 自动提交失败: {e}")
        except Exception as e:
            print(f"⚠️ 自动提交异常: {e}")

    def _get_automation_prefix(self) -> str:
        """
        获取 DAG 自动化执行指示前缀

        这个前缀会被自动注入到每个 DAG 任务的描述前，
        包含三层上下文：项目目标 → 阶段目标 → 当前任务

        Returns:
            自动化执行指示文本
        """
        # 构建上下文部分
        context_section = ""

        if self.global_goal:
            context_section += f"""🎯 **项目宏观目标** (The Big Picture):
{self.global_goal}

"""

        if self.stage_context:
            context_section += f"""📍 **当前阶段目标** (Stage Context):
{self.stage_context}

"""

        # 构建验证命令部分
        verify_section = ""
        if self.current_verify_cmd:
            verify_section = f"""
🧪 **验证命令**：任务完成后必须执行 `{self.current_verify_cmd}` 确保无报错
"""

        return f"""⚠️ DAG 自动化任务执行模式

{context_section}🤖 **行为准则**：
1. **完全自主执行** - 不询问用户，直接决策并实施
2. **参考上下文** - 遇到不确定性时，优先参考上述宏观目标
3. **保持一致性** - 代码风格、命名约定与项目整体保持一致
4. **必须自测** - 任务完成前，必须运行测试/编译命令验证无报错
5. **善用工具** - 必须使用文件写入工具应用更改，不要只输出代码块
{verify_section}
❌ **严格禁止**：询问用户、列选项让用户选、等待确认

---

📋 **当前任务内容**：

"""

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

                # 添加自动化执行指示前缀
                automation_prefix = self._get_automation_prefix()
                enhanced_content = automation_prefix + content

                # 构建claude命令
                claude_cmd = [
                    self.claude_bin,
                    "-p", enhanced_content,
                    "--allowedTools", "*",
                    "--permission-mode", "bypassPermissions"
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
        global _current_process, _interrupted

        if _interrupted:
            return False

        print(f"\n{'=' * 80}")
        print(f"[{task_id}] 执行命令: {command}")
        print(f"工作目录: {working_dir}")
        print(f"{'=' * 80}")

        try:
            # 提取cc命令中的内容并转换为claude命令
            if command.startswith("cc '") and command.endswith("'"):
                content = command[4:-1]  # 移除 cc ' 和 '

                # 添加自动化执行指示前缀
                automation_prefix = self._get_automation_prefix()
                enhanced_content = automation_prefix + content

                # 构建claude命令
                claude_cmd = [
                    self.claude_bin,
                    "-p", enhanced_content,
                    "--allowedTools", "*",
                    "--permission-mode", "bypassPermissions"
                ]

                print(f"✅ 已注入自动化执行指示")

                # 使用 Popen 以便可以被信号处理器终止
                _current_process = subprocess.Popen(
                    claude_cmd,
                    cwd=working_dir,
                    text=True
                )
                returncode = _current_process.wait()
                _current_process = None
            else:
                # 直接执行原命令
                _current_process = subprocess.Popen(
                    command,
                    shell=True,
                    cwd=working_dir,
                    text=True
                )
                returncode = _current_process.wait()
                _current_process = None

            if _interrupted:
                return False

            if returncode == 0:
                print("✅ 命令执行成功")

                # 自动提交（如果启用）
                if command.startswith("cc '") and command.endswith("'"):
                    content = command[4:-1]  # 移除 cc ' 和 '
                    self._auto_commit_if_needed(content, task_id)

                return True
            else:
                print(f"❌ 命令执行失败，返回码: {returncode}")
                return False

        except Exception as e:
            _current_process = None
            print(f"❌ 执行命令时发生异常: {e}")
            return False

    def execute_dag_task(self, task: TaskNode) -> bool:
        """
        执行单个 DAG 任务（自动管理状态）

        这个方法封装了完整的任务执行流程：
        1. 自动标记任务开始
        2. 执行任务
        3. 自动标记任务完成

        Args:
            task: 任务节点

        Returns:
            执行是否成功
        """
        # 0. 设置当前任务的验证命令（用于注入到 Prompt）
        self.current_verify_cmd = task.verify_cmd if task.verify_cmd else ""

        # 1. 自动标记任务开始
        if self.state_manager and self.current_stage_id is not None:
            self.state_manager.start_task(self.current_stage_id, task.task_id)

        # 2. 构建命令并执行
        command = self.build_command(task.description)
        working_dir = os.getcwd()
        success = self.execute_command_serial(command, working_dir, task.task_id)

        # 3. 自动标记任务完成
        if self.state_manager and self.current_stage_id is not None:
            error_msg = None if success else "任务执行失败"
            self.state_manager.complete_task(self.current_stage_id, task.task_id, success, error_msg)

        return success

    def execute_dag_batch_parallel(self, tasks: List[TaskNode], max_workers: int) -> List[TaskResult]:
        """
        并行执行一批 DAG 任务（自动管理状态）

        这个方法封装了完整的批量任务执行流程：
        1. 自动标记所有任务开始
        2. 并行执行任务
        3. 自动标记所有任务完成

        Args:
            tasks: 任务列表
            max_workers: 最大并发数

        Returns:
            执行结果列表
        """
        # 1. 自动标记所有任务开始
        if self.state_manager and self.current_stage_id is not None:
            for task in tasks:
                self.state_manager.start_task(self.current_stage_id, task.task_id)

        # 2. 构建命令列表并并行执行
        commands = [self.build_command(task.description) for task in tasks]
        working_dir = os.getcwd()
        results = self.execute_parallel(commands, working_dir, max_workers)

        # 3. 自动标记所有任务完成
        if self.state_manager and self.current_stage_id is not None:
            for i, result in enumerate(results):
                task = tasks[i]
                error_msg = result.error_msg if not result.success else None
                self.state_manager.complete_task(self.current_stage_id, task.task_id, result.success, error_msg)

        # 4. 并行批次完成后统一提交一次（避免逐任务 commit 的竞态风险）
        success_tasks = [tasks[i] for i, r in enumerate(results) if r.success]
        if success_tasks:
            descriptions = [t.description.replace('\n', ' ').strip()[:50] for t in success_tasks]
            summary = f"并行批次完成 ({len(success_tasks)} 任务): {', '.join(descriptions)}"
            self._auto_commit_if_needed(summary)

        return results


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
    parser.add_argument('-p', '--parallel', type=int, default=2,
                       help='并行执行的最大工作线程数 (默认: 2)')
    parser.add_argument('--single', action='store_true',
                       help='强制串行执行 (一次只执行一个任务)')
    parser.add_argument('--max-parallel', type=int, default=2,
                       help='允许的最大并行数 (默认: 2)')
    parser.add_argument('--dry-run', action='store_true',
                       help='仅显示执行计划，不实际执行')
    parser.add_argument('--restart', action='store_true',
                       help='清空状态文件，从头开始')

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
            # 处理 --restart 参数
            if args.restart:
                from state_manager import StateManager
                state_manager = StateManager(str(template_file))
                state_manager.clear_state()
                print()

            # 使用 DAG 执行器（默认开启状态管理）
            dag_executor = DAGExecutor(
                str(template_file),
                executor.execute_dag_task,
                use_state=True
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

            # 并行批次完成后统一提交一次（避免竞态）
            success_count_commit = sum(1 for r in results if r.success)
            if success_count_commit > 0:
                executor._auto_commit_if_needed(f"并行批次完成 ({success_count_commit} 任务)")

            executor.print_parallel_results(results)
            success_count = sum(1 for r in results if r.success)
        else:
            # 串行执行
            success_count, _ = executor.execute_serial_batch(commands, os.getcwd())

        return 0 if success_count == len(commands) else 1


if __name__ == "__main__":
    sys.exit(main())
