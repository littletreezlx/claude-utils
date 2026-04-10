#!/usr/bin/env python3
# Purpose: 回归测试 execute_dag_batch_parallel 的 per-task 状态持久化
# Created: 2026-04-10
#
# 验证修复的 bug: 并行批次中 Ctrl+C 后，已完成任务状态丢失，恢复时全部重跑
#
# 测试策略：monkey-patch execute_command_parallel 替换 claude CLI 调用为本地
# 模拟逻辑，然后：
#   (1) 正常跑完：验证状态文件中所有任务 = completed
#   (2) 部分完成后抛 KeyboardInterrupt：验证已完成的任务 = completed，
#       未完成的任务保持 pending（没有被错误地标成 in_progress）

import os
import sys
import json
import time
from pathlib import Path

# 插入 batch 目录到 path
BATCH_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BATCH_DIR))

from batch_executor_base import TaskResult
from dag_parser import TaskNode
from state_manager import StateManager
import batchcc

# 测试时用 ThreadPoolExecutor 替换 ProcessPoolExecutor，避免跨进程 pickle 限制
# （test 中的 closure hook 无法跨进程序列化）
from concurrent.futures import ThreadPoolExecutor
batchcc.ProcessPoolExecutor = ThreadPoolExecutor


class FakeExecutor(batchcc.ClaudeCodeBatchExecutor):
    """测试用子类：override execute_command_parallel 避免实际调 claude CLI。
    必须用 class-level override 才能跨 ProcessPoolExecutor 的 pickle 边界。
    实例属性 lambda 在 ProcessPoolExecutor 跨进程时无法 pickle。
    """

    def execute_command_parallel(self, args):
        task_id, cmd, wd = args
        time.sleep(0.02 * task_id)
        return TaskResult(
            task_id=task_id,
            command=cmd,
            success=True,
            duration=0.02,
            output="ok",
        )

    def _auto_commit_if_needed(self, task_description, task_id=None):
        # 测试时禁用 git commit，避免污染测试目录或误提交开发中的 batchcc.py
        pass


def make_task(task_id: int, desc: str) -> TaskNode:
    return TaskNode(
        task_id=task_id,
        description=desc,
        files=[],
        excludes=[],
        verify_cmd="",
    )


def make_stage(tasks):
    from dag_parser import StageNode
    return StageNode(
        stage_id=0,
        name="test",
        mode="parallel",
        max_workers=4,
        tasks=tasks,
    )


def write_task_file(path: Path):
    content = """# 测试 per-task 状态持久化

## STAGE ## name="test-parallel" mode="parallel" max_workers="4"

## TASK ##
任务一

## TASK ##
任务二

## TASK ##
任务三

## TASK ##
任务四
"""
    path.write_text(content)


def run_test_normal_completion(tmp_dir: Path):
    """场景 1: 4 个任务全部成功完成，状态全部落盘为 completed"""
    print("\n=== 测试 1: 正常完成场景 ===")

    task_file = tmp_dir / "test-normal.md"
    write_task_file(task_file)
    state_file = Path(str(task_file) + ".state.json")
    if state_file.exists():
        state_file.unlink()

    executor = FakeExecutor()
    # 禁用 auto_commit 避免干扰 git

    # 配置 state manager
    sm = StateManager(str(task_file))
    tasks = [make_task(i, f"任务{i}") for i in range(1, 5)]
    stage = make_stage(tasks)
    sm.init_stages([stage])
    executor.set_state_manager(sm, stage_id=0)

    results = executor.execute_dag_batch_parallel(tasks, max_workers=4)

    print(f"  返回结果数: {len(results)}")
    assert len(results) == 4, f"期望 4 个结果，实际 {len(results)}"
    assert all(r.success for r in results), "期望全部成功"

    # 验证状态文件
    with open(state_file) as f:
        state = json.load(f)
    tasks_state = state["stages"][0]["tasks"]
    for t in tasks_state:
        assert t["status"] == "completed", f"task {t['task_id']} 状态={t['status']}，期望 completed"
    print(f"  ✅ 所有 4 个任务状态=completed")
    state_file.unlink()
    return True


def run_test_interrupt_mid_batch(tmp_dir: Path):
    """场景 2: 4 个任务中跑到第 3 个时抛 KeyboardInterrupt，
    验证前 2 个已落盘 completed，后 2 个仍是 pending（init 后的初始状态）。
    """
    print("\n=== 测试 2: 中断场景（已完成任务状态必须保留）===")

    task_file = tmp_dir / "test-interrupt.md"
    write_task_file(task_file)
    state_file = Path(str(task_file) + ".state.json")
    if state_file.exists():
        state_file.unlink()

    executor = FakeExecutor()
    # 中断模拟：parent 在 complete_task 第 2 次调用后抛 KeyboardInterrupt
    call_count = {"n": 0}

    # 配置 state manager，hook complete_task 在第 2 次调用后抛中断
    sm = StateManager(str(task_file))
    tasks = [make_task(i, f"任务{i}") for i in range(1, 5)]
    stage = make_stage(tasks)
    sm.init_stages([stage])

    original_complete = sm.complete_task

    def hooked_complete_task(stage_id, task_id, success, error=None):
        original_complete(stage_id, task_id, success, error)
        call_count["n"] += 1
        if call_count["n"] == 2:
            # 模拟：2 个任务完成后用户按 Ctrl+C
            raise KeyboardInterrupt()

    sm.complete_task = hooked_complete_task
    executor.set_state_manager(sm, stage_id=0)

    interrupted = False
    try:
        executor.execute_dag_batch_parallel(tasks, max_workers=4)
    except KeyboardInterrupt:
        interrupted = True

    assert interrupted, "期望捕获 KeyboardInterrupt"

    # 验证状态：前 2 个 completed，后 2 个仍是 pending（绝不能是 in_progress）
    with open(state_file) as f:
        state = json.load(f)
    tasks_state = state["stages"][0]["tasks"]
    completed = [t for t in tasks_state if t["status"] == "completed"]
    pending = [t for t in tasks_state if t["status"] == "pending"]
    in_progress = [t for t in tasks_state if t["status"] == "in_progress"]

    print(f"  completed: {len(completed)}")
    print(f"  pending: {len(pending)}")
    print(f"  in_progress: {len(in_progress)}")

    assert len(completed) == 2, f"期望 2 个 completed，实际 {len(completed)}"
    assert len(in_progress) == 0, f"期望 0 个 in_progress（这是原 bug 的症状），实际 {len(in_progress)}"
    assert len(pending) == 2, f"期望 2 个 pending，实际 {len(pending)}"

    print(f"  ✅ 2 个已完成任务状态持久化正确，2 个未跑任务保持 pending")
    state_file.unlink()
    return True


def run_test_no_in_progress_predefine(tmp_dir: Path):
    """场景 3: 验证去掉了批次预写 in_progress 的改动——
    在任务执行过程中（尚未完成时）检查状态应该是 pending，不应是 in_progress。
    """
    print("\n=== 测试 3: 不预写 in_progress ===")

    task_file = tmp_dir / "test-no-predefine.md"
    write_task_file(task_file)
    state_file = Path(str(task_file) + ".state.json")
    if state_file.exists():
        state_file.unlink()

    executor = FakeExecutor()
    sm = StateManager(str(task_file))
    tasks = [make_task(i, f"任务{i}") for i in range(1, 3)]
    stage = make_stage(tasks)
    sm.init_stages([stage])

    # 在第一个任务 complete 时，检查当前 stage 中还没完成的任务状态
    checked = {"done": False}

    original_complete = sm.complete_task

    def hooked_complete_task(stage_id, task_id, success, error=None):
        if not checked["done"]:
            # 检查状态文件里其他任务的状态（应该是 pending，不是 in_progress）
            with open(sm.state_file) as f:
                state = json.load(f)
            other_tasks = [t for t in state["stages"][0]["tasks"] if t["task_id"] != task_id]
            for t in other_tasks:
                assert t["status"] in ("pending", "completed"), \
                    f"其他任务状态应该是 pending/completed，实际 {t['status']}（旧 bug）"
            checked["done"] = True
        original_complete(stage_id, task_id, success, error)

    sm.complete_task = hooked_complete_task
    executor.set_state_manager(sm, stage_id=0)

    executor.execute_dag_batch_parallel(tasks, max_workers=2)
    assert checked["done"], "未触发状态检查"
    print(f"  ✅ 未发现批次预写的 in_progress")
    state_file.unlink()
    return True


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        tmp_dir = Path(td)
        try:
            run_test_normal_completion(tmp_dir)
            run_test_interrupt_mid_batch(tmp_dir)
            run_test_no_in_progress_predefine(tmp_dir)
            print("\n✅ 所有回归测试通过")
        except AssertionError as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ 测试异常: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
