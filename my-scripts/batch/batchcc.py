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
from typing import Tuple, List, Optional
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from batch_executor_base import BaseBatchExecutor, TaskResult, ProgressMonitor
from dag_parser import DAGParser, TaskNode
from dag_executor import DAGExecutor


# 全局变量：跟踪当前运行的子进程
_current_process: subprocess.Popen = None
_interrupted = False


def _signal_handler(signum, frame):
    """
    处理 Ctrl+C 信号

    策略：不直接 sys.exit，而是 terminate 当前子进程 + 抛 KeyboardInterrupt，
    让主循环有机会 graceful shutdown 并持久化已收集的结果。

    第二次 Ctrl+C 时直接硬退出。
    """
    global _interrupted, _current_process

    if _interrupted:
        print("\n💀 再次收到 Ctrl+C，强制退出", flush=True)
        os._exit(130)

    _interrupted = True
    print("\n\n⚠️  收到中断信号 (Ctrl+C)", flush=True)

    if _current_process and _current_process.poll() is None:
        print("🛑 正在终止当前任务...", flush=True)
        try:
            _current_process.terminate()
        except Exception:
            pass

    print("💾 正在保存已完成任务的状态，再次 Ctrl+C 可强制退出\n", flush=True)
    raise KeyboardInterrupt()


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

    # 任务过程/进度产物的 pathspec 排除规则
    # 这些文件是 batchcc 或 DAG 命令运行时的编排/状态/中间结果，本质是过程文件，
    # 不应单独 commit（最后由 DAGExecutor._cleanup() 删除 .task-xxx/ 目录；
    # 命令级 state 跨运行保留但每次 TASK 都改，作为业务 commit 没有回溯价值）
    #
    # 排除分两类：
    # (a) batchcc 任务目录及裸入口文件
    # (b) 命令级跨运行 state（命名约定：以 -state.json 或 .state.json 结尾的 JSON）
    #     例：docs/quality-review-state.json、task-foo.state.json
    _TASK_ARTIFACT_EXCLUDES = [
        # (a) batchcc 任务产物
        ":!.task-*",                            # 新格式：.task-xxx/ 任务目录（顶层）
        ":!.task-*/**",                         # 新格式：目录内所有内容
        ":!task-*",                             # 旧格式：项目根的裸入口文件
        # (b) 命令级跨运行 state（实战教训：doc-quality-review 把进度写在 docs/
        #     quality-review-state.json，每个 Stage 1 TASK 都改它，被当业务 commit）
        ":(exclude,glob)**/*-state.json",       # 跨目录匹配：xxx-state.json
        ":(exclude,glob)**/*.state.json",       # 跨目录匹配：xxx.state.json
    ]

    def _auto_commit_if_needed(self, task_description: str, task_id: int = None):
        """
        任务执行成功后自动执行 git commit

        规则（2026-04-15 修订，决策记录 docs/decisions/2026-04-15-03）：
        - **排除 batchcc 任务过程产物**（.task-*/、task-* 裸文件、state.json）—
          这些是 batchcc 运行时的临时编排/状态文件，不该形成独立 commit；
          最后由 DAGExecutor._cleanup() 删除整个 .task-xxx/ 目录即可
        - 只 commit 业务文件实质变更（代码/文档/配置/命令级 state）
        - 暂存区为空（仅任务过程文件变化）→ 跳过 commit，避免产生空内容/
          仅含进度状态的"任务 N: ..." commit 污染 git history

        Args:
            task_description: 任务描述
            task_id: 任务ID（可选）
        """
        try:
            # 1. add 业务文件，显式排除 batchcc 任务过程产物
            add_result = subprocess.run(
                ["git", "add", "-A", "--", "."] + self._TASK_ARTIFACT_EXCLUDES,
                capture_output=True,
                text=True
            )
            if add_result.returncode != 0:
                err = add_result.stderr.strip()[:200]
                print(f"⚠️ git add 失败（{err}），跳过自动提交")
                return

            # 2. 检查暂存区：只有业务变更才 commit
            diff_result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True
            )
            if diff_result.returncode != 0:
                print(f"⚠️ 检查 git diff --cached 失败，跳过自动提交")
                return

            staged_files = diff_result.stdout.strip()
            if not staged_files:
                print(f"📝 仅任务过程文件变化（无业务改动），跳过自动提交")
                return

            # 3. 构建提交信息
            task_desc = task_description.replace("\n", " ").strip()
            task_desc = task_desc[:80] + ("..." if len(task_desc) > 80 else "")
            commit_message = f"任务 {task_id}: {task_desc}" if task_id else task_desc

            # 4. 执行 git commit
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                capture_output=True,
                text=True
            )
            if commit_result.returncode != 0:
                err = commit_result.stderr.strip()[:200]
                print(f"⚠️ git commit 失败（{err}）")
                return

            file_count = len(staged_files.splitlines())
            print(f"✅ 自动提交成功（{file_count} 个业务文件）: {task_desc[:50]}...")

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
        并行执行一批 DAG 任务（per-task 状态持久化）

        设计要点：
        - 不预写 in_progress：只在拿到 result 那一刻才 complete_task
        - ProcessPoolExecutor 在主线程单线程收 future 结果，git commit 天然无竞态
        - Ctrl+C 时 already-completed 的任务状态已落盘，不会丢失
        - 捕获 KeyboardInterrupt 后 cancel_futures 并 re-raise 给顶层 main
        """
        working_dir = os.getcwd()
        commands = [self.build_command(task.description) for task in tasks]
        total = len(tasks)

        print(f"\n🚀 并行执行 {total} 个任务 (最大 {max_workers} 并发)\n")

        monitor = ProgressMonitor(total)
        results: List[Optional[TaskResult]] = [None] * total
        executor = ProcessPoolExecutor(max_workers=max_workers)
        shutdown_done = False

        try:
            future_to_index = {}
            for idx, (task, cmd) in enumerate(zip(tasks, commands)):
                args = (task.task_id, cmd, working_dir)
                future = executor.submit(self.execute_command_parallel, args)
                future_to_index[future] = idx
                monitor.start_task(task.task_id, cmd)

            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                task = tasks[idx]
                try:
                    result = future.result()
                except Exception as e:
                    result = TaskResult(
                        task_id=task.task_id,
                        command=commands[idx],
                        success=False,
                        duration=0,
                        error_msg=f"任务执行异常: {e}"
                    )

                results[idx] = result
                monitor.complete_task(task.task_id, result.success)

                # 立即持久化 + 单任务 commit（主线程串行，无 git lock 竞态）
                if self.state_manager and self.current_stage_id is not None:
                    err = result.error_msg if not result.success else None
                    self.state_manager.complete_task(
                        self.current_stage_id, task.task_id, result.success, err
                    )
                if result.success:
                    self._auto_commit_if_needed(task.description, task.task_id)

        except KeyboardInterrupt:
            done = sum(1 for r in results if r is not None)
            print(f"\n⚠️  批次被中断：已持久化 {done}/{total} 任务的状态", flush=True)
            executor.shutdown(wait=False, cancel_futures=True)
            shutdown_done = True
            raise
        finally:
            if not shutdown_done:
                executor.shutdown(wait=True)

        return [r for r in results if r is not None]


def resolve_task_entry(arg: str) -> Optional[Path]:
    """
    解析任务入口，支持以下写法（按优先级）：

    1. `batchcc task-xxx`          → 查找 `.task-xxx/dag.md`（新格式主路径）
    2. `batchcc .task-xxx`         → 等价于 1
    3. `batchcc .task-xxx/dag.md`  → 直接使用
    4. `batchcc some-file.md`      → 简单 TASK 格式（向后兼容）
    5. `batchcc some-file`         → 自动补 `.md`（向后兼容）

    Returns:
        入口文件的 Path；未找到则返回 None（调用方打印帮助）
    """
    p = Path(arg)

    # 1. 传入目录：找 dag.md
    if p.is_dir():
        entry = p / "dag.md"
        if entry.exists():
            return entry
        return None

    # 2. `task-xxx`（无 . 前缀、不存在同名文件）→ 试 .task-xxx/dag.md
    if not p.exists() and not p.name.startswith('.'):
        hidden_dir = p.parent / f".{p.name}"
        if hidden_dir.is_dir():
            entry = hidden_dir / "dag.md"
            if entry.exists():
                return entry

    # 3/4. 直接文件存在
    if p.exists() and p.is_file():
        return p

    # 5. 补 .md 后缀
    p_md = Path(str(p) + '.md')
    if p_md.exists():
        return p_md

    return None


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
            # 检查 DAG 格式标记（兼容多种写法）
            # 标准: ## STAGE ## name="xxx"
            # 变体: ## STAGE 1 或 ## STAGE: name
            has_stage = '## STAGE' in content and '##' in content
            has_task = '## TASK' in content
            return has_stage and has_task
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

    # 解析入口（支持 .task-xxx/ 目录入口 + 旧版裸文件）
    if args.template:
        resolved = resolve_task_entry(args.template)
        if resolved is None:
            print(f"❌ 未找到任务入口: {args.template}")
            print("支持的写法:")
            print("  batchcc task-xxx            # 自动解析到 .task-xxx/dag.md")
            print("  batchcc .task-xxx           # 等价")
            print("  batchcc .task-xxx/dag.md    # 显式路径")
            print("  batchcc some-file.md        # 简单 TASK 格式")
            return 1
        template_file = resolved
    else:
        template_file = executor.get_default_template_path()
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

        except KeyboardInterrupt:
            print("\n⚠️  任务被用户中断")
            print("💡 下次运行将从断点继续，或使用 --restart 重新开始\n")
            return 130
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
