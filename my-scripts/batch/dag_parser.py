#!/usr/bin/env python3
"""
DAG 任务文件解析器 - 简化版
解析 STAGE 和 TASK 标记，支持文件冲突检测

格式容错说明：
- STAGE: 仅支持 `## STAGE ##` 格式
- TASK: 支持多种格式（容错）
  - `## TASK ##` (标准格式)
  - `## TASK ##:` (带冒号)
  - `## TASK:` (简化格式，兼容)
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Set
from pathlib import Path
import fnmatch


@dataclass
class TaskNode:
    """任务节点（简化版）"""
    task_id: int  # 任务序号（自动生成）
    description: str  # 任务描述
    files: List[str]  # 文件范围（glob 模式）
    excludes: List[str]  # 排除文件（glob 模式）
    verify_cmd: str  # 验证命令

    def __repr__(self):
        return f"Task#{self.task_id}: {self.description[:50]}"


@dataclass
class StageNode:
    """阶段节点（简化版）"""
    stage_id: int  # 阶段序号（自动生成）
    name: str  # 阶段名称
    mode: str  # serial 或 parallel
    max_workers: int  # 最大并发数（仅 parallel 模式）
    tasks: List[TaskNode]  # 任务列表

    def __repr__(self):
        return f"Stage#{self.stage_id}: {self.name} [{self.mode}] ({len(self.tasks)} tasks)"


class DAGParser:
    """DAG 任务文件解析器"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.stages: List[StageNode] = []
        # 文件引用的基准目录（使用当前工作目录，而非文件所在目录）
        self.base_dir = Path.cwd()

    def parse(self) -> List[StageNode]:
        """
        解析 DAG 任务文件

        Returns:
            阶段列表（按顺序）
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise ValueError(f"文件不存在: {self.file_path}")
        except Exception as e:
            raise ValueError(f"读取文件失败: {e}")

        # 处理文件引用（@文件路径）
        content = self._resolve_file_references(content)

        # 按 ## STAGE ## 分割
        stage_sections = re.split(r'^## STAGE ##', content, flags=re.MULTILINE)

        stage_id = 0
        # 跳过第一段（文件头）
        for section in stage_sections[1:]:
            section = section.strip()
            if not section:
                continue

            # 解析 STAGE
            stage_node = self._parse_stage(section, stage_id)
            if stage_node:
                self.stages.append(stage_node)
                stage_id += 1

        if not self.stages:
            raise ValueError("未找到任何 STAGE 定义")

        return self.stages

    def _parse_stage(self, section: str, stage_id: int) -> StageNode:
        """解析单个 STAGE"""
        lines = section.split('\n')
        if not lines:
            return None

        # 第一行是 STAGE 参数（可能包含前导空格）
        # 因为 split('## STAGE ##') 后，参数在同一行
        first_line = section.split('\n')[0].strip()

        # 如果第一行为空，可能是分割后的空白
        if not first_line:
            return None

        # 提取参数
        name = self._extract_param(first_line, 'name', required=True)
        mode = self._extract_param(first_line, 'mode', required=True)
        max_workers = int(self._extract_param(first_line, 'max_workers', default='4'))

        # 验证 mode
        if mode not in ['serial', 'parallel']:
            raise ValueError(f"STAGE mode 必须是 'serial' 或 'parallel'，当前: {mode}")

        # 解析 TASK
        tasks = self._parse_tasks(section)

        return StageNode(
            stage_id=stage_id,
            name=name,
            mode=mode,
            max_workers=max_workers,
            tasks=tasks
        )

    def _parse_tasks(self, stage_section: str) -> List[TaskNode]:
        """解析 STAGE 中的所有 TASK

        支持多种 TASK 标记格式（容错设计）：
        - `## TASK ##` (标准格式，推荐)
        - `## TASK ##:` (带冒号)
        - `## TASK:` (简化格式，兼容旧版)

        注意：只匹配行首的标记，避免误匹配文本中的内容
        """
        # 使用正则支持多种 TASK 格式
        # 匹配行首: ## TASK ## 或 ## TASK ##: 或 ## TASK:
        # ^表示行首（配合 MULTILINE 标志）
        task_sections = re.split(r'^## TASK\s*##\s*:?|^## TASK\s*:', stage_section, flags=re.MULTILINE)

        tasks = []
        task_id = 1

        for section in task_sections[1:]:  # 跳过第一段（STAGE 参数）
            section = section.strip()
            if not section:
                continue

            task_node = self._parse_task(section, task_id)
            if task_node:
                tasks.append(task_node)
                task_id += 1

        return tasks

    def _parse_task(self, section: str, task_id: int) -> TaskNode:
        """解析单个 TASK"""
        lines = section.split('\n')

        # 提取任务描述（第一行非空内容）
        description = ""
        files = []
        excludes = []
        verify_cmd = ""

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # 提取字段
            if line.startswith('文件:'):
                file_list = line[3:].strip()
                files.extend([f.strip() for f in file_list.split(',') if f.strip()])
            elif line.startswith('排除:'):
                exclude_list = line[3:].strip()
                excludes.extend([e.strip() for e in exclude_list.split(',') if e.strip()])
            elif line.startswith('验证:'):
                verify_cmd = line[3:].strip()
            elif not description:
                # 第一行非字段内容作为描述
                description = line

        if not description:
            description = f"Task {task_id}"

        return TaskNode(
            task_id=task_id,
            description=description,
            files=files,
            excludes=excludes,
            verify_cmd=verify_cmd
        )

    def _extract_param(self, line: str, param_name: str, required: bool = False, default: str = "") -> str:
        """提取参数值"""
        pattern = rf'{param_name}="([^"]*)"'
        match = re.search(pattern, line)

        if match:
            return match.group(1)
        elif required:
            raise ValueError(f"缺少必需参数: {param_name}")
        else:
            return default

    def _resolve_file_references(self, content: str) -> str:
        """
        解析文件引用（@文件路径）

        将 @文件路径 替换为文件的实际内容

        Args:
            content: 原始内容

        Returns:
            解析后的内容
        """
        lines = content.split('\n')
        result_lines = []

        for line in lines:
            stripped = line.strip()

            # 检查是否是文件引用行
            if stripped.startswith('@'):
                # 提取文件路径
                ref_path = stripped[1:].strip()

                # 构建完整路径（相对于主任务文件的目录）
                full_path = self.base_dir / ref_path

                # 读取引用的文件
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        ref_content = f.read()
                    # 递归解析引用文件中的引用（支持嵌套引用）
                    ref_content = self._resolve_file_references_recursive(ref_content, full_path.parent)
                    result_lines.append(ref_content)
                except FileNotFoundError:
                    # 文件不存在，保留原始引用行并添加警告注释
                    result_lines.append(f"# ⚠️ 文件引用失败: {ref_path} (文件不存在)")
                    result_lines.append(line)
                except Exception as e:
                    # 读取失败，保留原始引用行并添加错误注释
                    result_lines.append(f"# ⚠️ 文件引用失败: {ref_path} (错误: {e})")
                    result_lines.append(line)
            else:
                # 非引用行，直接保留
                result_lines.append(line)

        return '\n'.join(result_lines)

    def _resolve_file_references_recursive(self, content: str, base_dir: Path) -> str:
        """
        递归解析文件引用（支持嵌套引用）

        Args:
            content: 文件内容
            base_dir: 基准目录

        Returns:
            解析后的内容
        """
        lines = content.split('\n')
        result_lines = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith('@'):
                ref_path = stripped[1:].strip()
                full_path = base_dir / ref_path

                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        ref_content = f.read()
                    # 继续递归解析
                    ref_content = self._resolve_file_references_recursive(ref_content, full_path.parent)
                    result_lines.append(ref_content)
                except:
                    result_lines.append(f"# ⚠️ 嵌套引用失败: {ref_path}")
                    result_lines.append(line)
            else:
                result_lines.append(line)

        return '\n'.join(result_lines)


class ConflictDetector:
    """文件冲突检测器"""

    @staticmethod
    def detect_conflicts(tasks: List[TaskNode]) -> Dict[int, List[int]]:
        """
        检测任务间的文件冲突

        Args:
            tasks: 任务列表

        Returns:
            冲突映射 {task_id: [冲突的task_id列表]}
        """
        conflicts = {}

        for i, task_a in enumerate(tasks):
            conflicting_tasks = []

            for j, task_b in enumerate(tasks):
                if i >= j:  # 避免重复检测
                    continue

                if ConflictDetector._has_conflict(task_a, task_b):
                    conflicting_tasks.append(task_b.task_id)

            if conflicting_tasks:
                conflicts[task_a.task_id] = conflicting_tasks

        return conflicts

    @staticmethod
    def _has_conflict(task_a: TaskNode, task_b: TaskNode) -> bool:
        """检查两个任务是否有文件冲突"""
        # 获取有效文件范围（排除 excludes）
        files_a = ConflictDetector._get_effective_files(task_a)
        files_b = ConflictDetector._get_effective_files(task_b)

        # 检查是否有重叠
        for pattern_a in files_a:
            for pattern_b in files_b:
                if ConflictDetector._patterns_overlap(pattern_a, pattern_b):
                    return True

        return False

    @staticmethod
    def _get_effective_files(task: TaskNode) -> Set[str]:
        """获取有效文件范围（排除 excludes）"""
        return set(task.files) - set(task.excludes)

    @staticmethod
    def _patterns_overlap(pattern_a: str, pattern_b: str) -> bool:
        """
        检查两个 glob 模式是否重叠

        简化实现（严格模式）：
        1. 精确匹配
        2. 一个是另一个的完整子路径（包含 * 通配符）
        """
        # 精确匹配
        if pattern_a == pattern_b:
            return True

        # 标准化路径
        path_a = str(pattern_a).rstrip('/')
        path_b = str(pattern_b).rstrip('/')

        # 检查是否一个模式完全包含另一个（带通配符）
        # 例如：src/modules/**/*.ts 包含 src/modules/user/
        if '*' in path_a or '*' in path_b:
            # 简化：只有父目录完全相同的通配符模式才算冲突
            # 例如：src/modules/**/*.ts 和 src/modules/**/*.js 冲突
            #       但 src/modules/user/**/*.ts 和 src/modules/order/**/*.ts 不冲突

            # 移除通配符部分，比较目录路径
            dir_a = path_a.split('*')[0].rstrip('/')
            dir_b = path_b.split('*')[0].rstrip('/')

            # 如果目录路径完全相同，认为可能冲突
            if dir_a == dir_b:
                return True

            # 如果一个目录是另一个的父目录，认为可能冲突
            if dir_a in dir_b or dir_b in dir_a:
                return True
        else:
            # 都是具体文件路径，只有完全相同才冲突
            pass

        return False

    @staticmethod
    def create_batches(tasks: List[TaskNode], conflicts: Dict[int, List[int]]) -> List[List[TaskNode]]:
        """
        根据冲突关系创建并行批次

        无冲突的任务可以在同一批次并行执行
        有冲突的任务必须在不同批次

        Returns:
            批次列表，每个批次是一组可并行的任务
        """
        if not tasks:
            return []

        # 如果没有冲突，所有任务可以并行
        if not conflicts:
            return [tasks]

        batches = []
        remaining_tasks = set(task.task_id for task in tasks)
        task_map = {task.task_id: task for task in tasks}

        while remaining_tasks:
            # 当前批次：选择没有冲突的任务
            current_batch = []
            current_batch_ids = set()

            for task_id in list(remaining_tasks):
                # 检查是否与当前批次中的任务冲突
                has_conflict = False

                if task_id in conflicts:
                    for conflict_id in conflicts[task_id]:
                        if conflict_id in current_batch_ids:
                            has_conflict = True
                            break

                # 反向检查
                for batch_task_id in current_batch_ids:
                    if batch_task_id in conflicts and task_id in conflicts[batch_task_id]:
                        has_conflict = True
                        break

                if not has_conflict:
                    current_batch.append(task_map[task_id])
                    current_batch_ids.add(task_id)
                    remaining_tasks.remove(task_id)

            if current_batch:
                batches.append(current_batch)
            else:
                # 防止死循环：强制添加一个任务
                task_id = remaining_tasks.pop()
                batches.append([task_map[task_id]])

        return batches


if __name__ == "__main__":
    # 测试代码
    import sys

    if len(sys.argv) < 2:
        print("用法: python dag_parser.py <dag-file>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        parser = DAGParser(file_path)
        stages = parser.parse()

        print(f"✅ 解析成功: {len(stages)} 个阶段")
        print()

        for stage in stages:
            print(f"📋 {stage}")
            for task in stage.tasks:
                print(f"   - {task}")
                if task.files:
                    print(f"     文件: {', '.join(task.files)}")
                if task.excludes:
                    print(f"     排除: {', '.join(task.excludes)}")
            print()

    except Exception as e:
        print(f"❌ 解析失败: {e}")
        sys.exit(1)
