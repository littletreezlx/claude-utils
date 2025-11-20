#!/usr/bin/env python3
"""
DAG 任务状态管理器
支持断点续传和状态持久化
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class TaskState:
    """任务状态"""
    task_id: int
    description: str
    status: str  # pending, in_progress, completed, failed, skipped
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error: Optional[str] = None
    duration: Optional[float] = None

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class StageState:
    """阶段状态"""
    stage_id: int
    name: str
    mode: str
    status: str  # pending, in_progress, completed, failed, skipped
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[float] = None
    tasks: List[TaskState] = None

    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []

    def to_dict(self) -> Dict:
        """转换为字典"""
        data = {k: v for k, v in asdict(self).items() if v is not None and k != 'tasks'}
        data['tasks'] = [task.to_dict() for task in self.tasks]
        return data


class StateManager:
    """状态管理器"""

    def __init__(self, task_file: str):
        """
        Args:
            task_file: 任务文件路径
        """
        self.task_file = task_file
        self.state_file = f"{task_file}.state.json"
        self.state: Dict[str, Any] = {
            'task_file': task_file,
            'start_time': None,
            'last_update': None,
            'overall_status': 'pending',
            'stages': []
        }

    def load_state(self) -> bool:
        """
        加载状态文件

        Returns:
            是否成功加载
        """
        if not os.path.exists(self.state_file):
            return False

        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
            return True
        except Exception as e:
            print(f"⚠️  加载状态文件失败: {e}")
            return False

    def save_state(self):
        """保存状态文件"""
        try:
            self.state['last_update'] = self._now()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  保存状态文件失败: {e}")

    def clear_state(self):
        """清空状态文件"""
        if os.path.exists(self.state_file):
            try:
                os.remove(self.state_file)
                print(f"✅ 已清空状态文件: {self.state_file}")
            except Exception as e:
                print(f"⚠️  清空状态文件失败: {e}")

    def has_incomplete_tasks(self) -> bool:
        """检查是否有未完成的任务"""
        if not os.path.exists(self.state_file):
            return False

        if not self.load_state():
            return False

        # 检查是否有未完成的阶段
        for stage_data in self.state.get('stages', []):
            if stage_data.get('status') not in ['completed', 'skipped']:
                return True

        return False

    def init_stages(self, stages: List[Any]):
        """
        初始化阶段状态

        Args:
            stages: StageNode 列表
        """
        self.state['start_time'] = self._now()
        self.state['overall_status'] = 'in_progress'
        self.state['stages'] = []

        for stage in stages:
            stage_state = StageState(
                stage_id=stage.stage_id,
                name=stage.name,
                mode=stage.mode,
                status='pending',
                tasks=[]
            )

            for task in stage.tasks:
                task_state = TaskState(
                    task_id=task.task_id,
                    description=task.description,
                    status='pending'
                )
                stage_state.tasks.append(task_state)

            self.state['stages'].append(stage_state.to_dict())

        self.save_state()

    def should_skip_stage(self, stage_id: int) -> bool:
        """
        判断是否应该跳过某个阶段

        Args:
            stage_id: 阶段ID

        Returns:
            是否跳过
        """
        if stage_id >= len(self.state['stages']):
            return False

        stage_status = self.state['stages'][stage_id].get('status')
        return stage_status == 'completed'

    def should_skip_task(self, stage_id: int, task_id: int) -> bool:
        """
        判断是否应该跳过某个任务

        Args:
            stage_id: 阶段ID
            task_id: 任务ID（从1开始）

        Returns:
            是否跳过
        """
        if stage_id >= len(self.state['stages']):
            return False

        tasks = self.state['stages'][stage_id].get('tasks', [])
        # task_id 从1开始，数组索引从0开始
        task_index = task_id - 1

        if task_index >= len(tasks):
            return False

        task_status = tasks[task_index].get('status')
        return task_status == 'completed'

    def start_stage(self, stage_id: int):
        """标记阶段开始"""
        if stage_id < len(self.state['stages']):
            self.state['stages'][stage_id]['status'] = 'in_progress'
            self.state['stages'][stage_id]['start_time'] = self._now()
            self.save_state()

    def complete_stage(self, stage_id: int, success: bool):
        """标记阶段完成"""
        if stage_id < len(self.state['stages']):
            stage = self.state['stages'][stage_id]
            stage['status'] = 'completed' if success else 'failed'
            stage['end_time'] = self._now()

            # 计算耗时
            if stage.get('start_time'):
                start = datetime.fromisoformat(stage['start_time'])
                end = datetime.fromisoformat(stage['end_time'])
                stage['duration'] = (end - start).total_seconds()

            self.save_state()

    def start_task(self, stage_id: int, task_id: int):
        """标记任务开始"""
        if stage_id < len(self.state['stages']):
            tasks = self.state['stages'][stage_id].get('tasks', [])
            task_index = task_id - 1

            if task_index < len(tasks):
                tasks[task_index]['status'] = 'in_progress'
                tasks[task_index]['start_time'] = self._now()
                self.save_state()

    def complete_task(self, stage_id: int, task_id: int, success: bool, error: str = None):
        """标记任务完成"""
        if stage_id < len(self.state['stages']):
            tasks = self.state['stages'][stage_id].get('tasks', [])
            task_index = task_id - 1

            if task_index < len(tasks):
                task = tasks[task_index]
                task['status'] = 'completed' if success else 'failed'
                task['end_time'] = self._now()

                if error:
                    task['error'] = error

                # 计算耗时
                if task.get('start_time'):
                    start = datetime.fromisoformat(task['start_time'])
                    end = datetime.fromisoformat(task['end_time'])
                    task['duration'] = (end - start).total_seconds()

                self.save_state()

    def complete_all(self, success: bool):
        """标记整体完成"""
        self.state['overall_status'] = 'completed' if success else 'failed'
        self.save_state()

    def print_resume_info(self):
        """打印恢复信息"""
        print(f"\n{'=' * 80}")
        print(f"📋 检测到未完成的任务")
        print(f"{'=' * 80}")
        print(f"任务文件: {self.state.get('task_file')}")
        print(f"开始时间: {self.state.get('start_time')}")
        print(f"上次更新: {self.state.get('last_update')}")
        print()

        total_stages = len(self.state.get('stages', []))
        completed_stages = sum(1 for s in self.state['stages'] if s.get('status') == 'completed')

        print(f"阶段进度: {completed_stages}/{total_stages}")
        print()

        # 显示每个阶段的状态
        for stage_data in self.state['stages']:
            status_icon = self._get_status_icon(stage_data.get('status'))
            print(f"{status_icon} Stage {stage_data['stage_id'] + 1}: {stage_data['name']}")

            tasks = stage_data.get('tasks', [])
            completed_tasks = sum(1 for t in tasks if t.get('status') == 'completed')
            print(f"   任务进度: {completed_tasks}/{len(tasks)}")

            # 显示失败的任务
            for task in tasks:
                if task.get('status') == 'failed':
                    print(f"   ❌ Task {task['task_id']}: {task['description'][:50]}")
                    if task.get('error'):
                        print(f"      错误: {task['error']}")

        print(f"{'=' * 80}\n")

    def get_resume_stage(self) -> Optional[int]:
        """
        获取应该恢复的阶段ID

        Returns:
            阶段ID，如果全部完成则返回None
        """
        for stage_data in self.state.get('stages', []):
            if stage_data.get('status') not in ['completed', 'skipped']:
                return stage_data['stage_id']
        return None

    def _get_status_icon(self, status: str) -> str:
        """获取状态图标"""
        icons = {
            'pending': '⏸️ ',
            'in_progress': '🔄',
            'completed': '✅',
            'failed': '❌',
            'skipped': '⏭️ '
        }
        return icons.get(status, '❓')

    def _now(self) -> str:
        """获取当前时间字符串"""
        return datetime.now().isoformat(timespec='seconds')


if __name__ == "__main__":
    # 测试代码
    import sys

    if len(sys.argv) < 2:
        print("用法: python state_manager.py <task-file>")
        sys.exit(1)

    task_file = sys.argv[1]
    manager = StateManager(task_file)

    if manager.load_state():
        print("✅ 状态文件加载成功")
        manager.print_resume_info()
    else:
        print("❌ 状态文件不存在或加载失败")
