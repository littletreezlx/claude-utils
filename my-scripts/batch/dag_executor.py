#!/usr/bin/env python3
"""
DAG 执行引擎 - 简化版
顺序执行 STAGE，STAGE 内根据 mode 选择串行或并行
"""

import time
from typing import List, Callable, Any, Optional
from dag_parser import DAGParser, StageNode, TaskNode, ConflictDetector
from state_manager import StateManager


class DAGExecutor:
    """DAG 执行引擎（简化版）"""

    def __init__(self, file_path: str, task_executor: Callable[[TaskNode], bool], use_state: bool = True):
        """
        Args:
            file_path: DAG 任务文件路径
            task_executor: 任务执行函数，接受 TaskNode，返回是否成功
            use_state: 是否使用状态管理（断点续传）
        """
        self.file_path = file_path
        self.task_executor = task_executor
        self.parser = DAGParser(file_path)
        self.stages: List[StageNode] = []
        self.use_state = use_state
        self.state_manager = StateManager(file_path) if use_state else None
        self.global_goal: str = ""  # 项目宏观目标（从 parser 获取）

    def parse(self) -> List[StageNode]:
        """解析 DAG 文件"""
        self.stages = self.parser.parse()
        self.global_goal = self.parser.global_goal  # 获取项目宏观目标
        return self.stages

    def print_plan(self):
        """打印执行计划（--dry-run）"""
        if not self.stages:
            self.parse()

        print(f"\n{'=' * 80}")
        print(f"📊 DAG 执行计划")
        print(f"{'=' * 80}")
        print(f"文件: {self.file_path}")
        print(f"阶段数: {len(self.stages)}")
        print()

        total_tasks = sum(len(stage.tasks) for stage in self.stages)
        print(f"总任务数: {total_tasks}")
        print()

        for stage in self.stages:
            print(f"{'─' * 80}")
            print(f"Stage {stage.stage_id + 1}: {stage.name} [{stage.mode.upper()}]")
            print(f"{'─' * 80}")

            if stage.mode == 'parallel':
                # 检测冲突
                conflicts = ConflictDetector.detect_conflicts(stage.tasks)
                batches = ConflictDetector.create_batches(stage.tasks, conflicts)

                print(f"模式: 并行执行（最大 {stage.max_workers} 并发）")
                print(f"任务数: {len(stage.tasks)}")
                print(f"并行批次: {len(batches)}")
                print()

                if conflicts:
                    print("⚠️  检测到冲突:")
                    for task_id, conflict_ids in conflicts.items():
                        task = next(t for t in stage.tasks if t.task_id == task_id)
                        print(f"   Task {task_id} 与 {conflict_ids} 冲突")
                        print(f"   → {task.description[:60]}")
                    print()

                # 显示批次
                for i, batch in enumerate(batches, 1):
                    if len(batches) > 1:
                        print(f"  [Batch {i}] ({len(batch)} 任务并行)")
                    for task in batch:
                        print(f"    - Task {task.task_id}: {task.description[:60]}")
                        if task.files:
                            print(f"      文件: {', '.join(task.files[:3])}")
                    if i < len(batches):
                        print(f"    ⬇️  等待批次 {i} 完成")
                    print()

            else:  # serial
                print(f"模式: 串行执行")
                print(f"任务数: {len(stage.tasks)}")
                print()

                for task in stage.tasks:
                    print(f"  → Task {task.task_id}: {task.description[:60]}")
                    if task.files:
                        print(f"    文件: {', '.join(task.files[:3])}")
                print()

        print(f"{'=' * 80}")
        print("执行方式:")
        print("  python batchcc.py <file>  # 执行所有任务")
        print(f"{'=' * 80}\n")

    def execute(self, parallel_executor: Callable[[List[TaskNode], int], List[Any]] = None) -> bool:
        """
        执行所有阶段和任务

        Args:
            parallel_executor: 并行执行函数（可选）
                             接受 (tasks, max_workers)，返回执行结果列表

        Returns:
            是否全部成功
        """
        if not self.stages:
            self.parse()

        # 状态管理：自动检测并继续
        start_stage_id = 0
        if self.use_state and self.state_manager:
            has_state = self.state_manager.load_state()

            if has_state and self.state_manager.has_incomplete_tasks():
                # 自动从断点继续
                resume_stage = self.state_manager.get_resume_stage()
                if resume_stage is not None:
                    start_stage_id = resume_stage
                    print(f"\n💡 检测到未完成的任务，将从 Stage {start_stage_id + 1} 继续执行")
                    print(f"💡 如需重新开始，请先删除状态文件: {self.state_manager.state_file}\n")
            else:
                # 初始化状态
                self.state_manager.init_stages(self.stages)

        print(f"\n{'=' * 80}")
        print(f"🚀 开始执行 DAG 任务")
        print(f"{'=' * 80}")
        print(f"文件: {self.file_path}")
        print(f"阶段数: {len(self.stages)}")
        if start_stage_id > 0:
            print(f"起始阶段: Stage {start_stage_id + 1}")
        print(f"{'=' * 80}\n")

        overall_start = time.time()
        all_success = True

        for stage in self.stages:
            # 跳过已完成的阶段
            if stage.stage_id < start_stage_id:
                print(f"⏭️  跳过 Stage {stage.stage_id + 1}: {stage.name} (已完成)")
                continue

            # 状态管理：检查是否应该跳过整个阶段
            if self.use_state and self.state_manager and self.state_manager.should_skip_stage(stage.stage_id):
                print(f"⏭️  跳过 Stage {stage.stage_id + 1}: {stage.name} (已完成)")
                continue
            print(f"\n{'─' * 80}")
            print(f"📋 Stage {stage.stage_id + 1}/{len(self.stages)}: {stage.name} [{stage.mode.upper()}]")
            print(f"{'─' * 80}\n")

            stage_start = time.time()

            # 状态管理：标记阶段开始
            if self.use_state and self.state_manager:
                self.state_manager.start_stage(stage.stage_id)

            # 注入状态管理器到任务执行器（如果执行器支持）
            self._inject_state_to_executor(stage.stage_id)

            if stage.mode == 'serial':
                # 串行执行
                success = self._execute_stage_serial(stage)
            else:
                # 并行执行
                success = self._execute_stage_parallel(stage, parallel_executor)

            stage_duration = time.time() - stage_start

            # 状态管理：标记阶段完成
            if self.use_state and self.state_manager:
                self.state_manager.complete_stage(stage.stage_id, success)

            if success:
                print(f"\n✅ Stage {stage.stage_id + 1} 完成 (耗时: {stage_duration:.1f}s)")
            else:
                print(f"\n❌ Stage {stage.stage_id + 1} 失败 (耗时: {stage_duration:.1f}s)")
                print(f"⛔ 停止执行（失败即停止策略）")
                all_success = False
                break

        overall_duration = time.time() - overall_start

        # 状态管理：标记整体完成
        if self.use_state and self.state_manager:
            self.state_manager.complete_all(all_success)

        # 成功后清理文件
        if all_success:
            self._cleanup()

        print(f"\n{'=' * 80}")
        if all_success:
            print(f"✅ 所有任务执行完成")
        else:
            print(f"❌ 任务执行失败")
        print(f"总耗时: {overall_duration:.1f}s")
        print(f"{'=' * 80}\n")

        return all_success

    def _execute_stage_serial(self, stage: StageNode) -> bool:
        """串行执行阶段"""
        print(f"模式: 串行执行 ({len(stage.tasks)} 任务)")
        print()

        for i, task in enumerate(stage.tasks, 1):
            # 状态管理：检查是否应该跳过任务
            if self.use_state and self.state_manager and self.state_manager.should_skip_task(stage.stage_id, task.task_id):
                print(f"[{i}/{len(stage.tasks)}] ⏭️  跳过: {task.description[:60]} (已完成)")
                continue

            print(f"[{i}/{len(stage.tasks)}] 执行: {task.description[:60]}")

            # 任务执行器会自动管理状态（start_task 和 complete_task）
            success = self.task_executor(task)

            if not success:
                print(f"❌ Task {task.task_id} 失败")
                return False

            print(f"✅ Task {task.task_id} 完成")
            print()

        return True

    def _execute_stage_parallel(self, stage: StageNode, parallel_executor: Callable = None) -> bool:
        """并行执行阶段（带冲突检测）"""
        print(f"模式: 并行执行（最大 {stage.max_workers} 并发）")

        # 检测冲突
        conflicts = ConflictDetector.detect_conflicts(stage.tasks)
        batches = ConflictDetector.create_batches(stage.tasks, conflicts)

        print(f"任务数: {len(stage.tasks)}")
        print(f"并行批次: {len(batches)}")

        if conflicts:
            print(f"⚠️  检测到 {len(conflicts)} 个冲突，任务将分批执行")

        print()

        # 逐批次执行
        for batch_idx, batch in enumerate(batches, 1):
            if len(batches) > 1:
                print(f"{'─' * 40}")
                print(f"📦 Batch {batch_idx}/{len(batches)} ({len(batch)} 任务)")
                print(f"{'─' * 40}")
                print()

            if parallel_executor and len(batch) > 1:
                # 使用并行执行器
                success = self._execute_batch_parallel(batch, stage.max_workers, parallel_executor)
            else:
                # 串行执行（单个任务或没有并行执行器）
                success = self._execute_batch_serial(batch)

            if not success:
                return False

            if batch_idx < len(batches):
                print(f"\n⬇️  继续下一批次...\n")

        return True

    def _execute_batch_serial(self, batch: List[TaskNode]) -> bool:
        """串行执行批次中的任务"""
        for task in batch:
            # 获取task所属的stage_id（从task中获取或通过遍历stages查找）
            stage_id = self._get_stage_id_for_task(task)

            # 状态管理：检查是否应该跳过任务
            if self.use_state and self.state_manager and stage_id is not None:
                if self.state_manager.should_skip_task(stage_id, task.task_id):
                    print(f"⏭️  跳过: {task.description[:60]} (已完成)")
                    continue

            print(f"执行: {task.description[:60]}")

            # 任务执行器会自动管理状态（start_task 和 complete_task）
            success = self.task_executor(task)

            if not success:
                print(f"❌ Task {task.task_id} 失败")
                return False

            print(f"✅ Task {task.task_id} 完成")
            print()

        return True

    def _execute_batch_parallel(self, batch: List[TaskNode], max_workers: int, parallel_executor: Callable) -> bool:
        """并行执行批次中的任务"""
        # 过滤掉已完成的任务
        tasks_to_execute = []
        stage_id = self._get_stage_id_for_task(batch[0]) if batch else None

        for task in batch:
            if self.use_state and self.state_manager and stage_id is not None:
                if self.state_manager.should_skip_task(stage_id, task.task_id):
                    print(f"⏭️  跳过: {task.description[:60]} (已完成)")
                    continue
            tasks_to_execute.append(task)

        if not tasks_to_execute:
            print("✅ 批次中所有任务已完成")
            return True

        print(f"🚀 并行执行 {len(tasks_to_execute)} 个任务 (最大 {max_workers} 并发)")
        print()

        # 并行执行器会自动管理状态（start_task 和 complete_task）
        results = parallel_executor(tasks_to_execute, max_workers)

        # 检查结果
        success_count = sum(1 for r in results if r.success)

        if success_count == len(tasks_to_execute):
            print(f"✅ 批次完成: {success_count}/{len(tasks_to_execute)} 成功")
            return True
        else:
            print(f"❌ 批次失败: {success_count}/{len(tasks_to_execute)} 成功")
            # 显示失败的任务
            for result in results:
                if not result.success:
                    print(f"   ❌ Task {result.task_id}: {result.error_msg}")
            return False

    def _inject_state_to_executor(self, stage_id: int):
        """
        将状态管理器和上下文注入到任务执行器（如果执行器支持）

        Args:
            stage_id: 当前阶段ID
        """
        # 检查 task_executor 是否是一个绑定方法
        if not hasattr(self.task_executor, '__self__'):
            return

        executor_obj = self.task_executor.__self__

        # 注入状态管理器
        if self.use_state and self.state_manager:
            if hasattr(executor_obj, 'set_state_manager'):
                executor_obj.set_state_manager(self.state_manager, stage_id)

        # 注入上下文（global_goal + stage 信息）
        if hasattr(executor_obj, 'set_context'):
            stage = self.stages[stage_id] if stage_id < len(self.stages) else None
            stage_context = f"Stage: {stage.name}\n{stage.description}" if stage else ""
            executor_obj.set_context(self.global_goal, stage_context)

    def _get_stage_id_for_task(self, task: TaskNode) -> Optional[int]:
        """
        获取任务所属的阶段ID

        Args:
            task: 任务节点

        Returns:
            阶段ID，如果找不到返回None
        """
        for stage in self.stages:
            for stage_task in stage.tasks:
                if stage_task.task_id == task.task_id and stage_task.description == task.description:
                    return stage.stage_id
        return None

    def _cleanup(self):
        """清理任务产物

        新格式（.task-xxx/dag.md）→ 删整个 .task-xxx/ 目录（一刀切，聚合清理）
        旧格式（裸文件）→ 分别删 task 文件和 state 文件（向后兼容）

        安全护栏：目录清理仅在 `.task-` 前缀命中时执行，避免误删。
        """
        import os
        import shutil
        from pathlib import Path

        task_path = Path(self.file_path)
        parent_dir = task_path.parent

        # 新格式：删整个 .task-xxx/ 目录
        if parent_dir.name.startswith('.task-') and parent_dir.is_dir():
            try:
                shutil.rmtree(parent_dir)
                print(f"🗑️  已清理任务目录: {parent_dir}")
            except Exception as e:
                print(f"⚠️  清理任务目录失败: {e}")
            return

        # 旧格式兼容：分别清理
        if self.state_manager and os.path.exists(self.state_manager.state_file):
            try:
                os.remove(self.state_manager.state_file)
                print(f"🗑️  已清理状态文件: {self.state_manager.state_file}")
            except Exception as e:
                print(f"⚠️  清理状态文件失败: {e}")

        if os.path.exists(self.file_path):
            try:
                os.remove(self.file_path)
                print(f"🗑️  已清理任务文件: {self.file_path}")
            except Exception as e:
                print(f"⚠️  清理任务文件失败: {e}")


if __name__ == "__main__":
    # 测试代码
    import sys

    if len(sys.argv) < 2:
        print("用法: python dag_executor.py <dag-file> [--dry-run]")
        sys.exit(1)

    file_path = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    # 简单的任务执行器（测试用）
    def simple_executor(task: TaskNode) -> bool:
        print(f"  执行任务: {task.description}")
        time.sleep(0.1)  # 模拟执行
        return True

    try:
        executor = DAGExecutor(file_path, simple_executor)

        if dry_run:
            executor.print_plan()
        else:
            executor.execute()

    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
