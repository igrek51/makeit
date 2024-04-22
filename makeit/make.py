import re
from pathlib import Path
from dataclasses import dataclass

from nuclear import logger, shell


@dataclass
class MakeStep:
    name: str
    dependencies: str | None
    code: list[str]
    raw_lines: list[str]
    comment: str | None = None


def read_make_steps() -> list[MakeStep]:
    makefile_path = Path('Makefile')
    assert makefile_path.is_file(), "'Makefile' not found"
    lines: list[str] = makefile_path.read_text(encoding='utf-8').splitlines()
    lines = [l for l in lines if l]
    return _parse_makefile_lines(lines)


def _parse_makefile_lines(lines: list[str]) -> list[MakeStep]:
    step_header_regex = re.compile(r'^(\w+):( .+)?$')
    step_code_regex = re.compile(r'^(\t|\s+)(.+)')
    steps: list[MakeStep] = []
    current_step: MakeStep | None = None
    for i, line in enumerate(lines):
        if match := step_header_regex.match(line):
            dependencies = (match.group(2) or '').strip()
            current_step = MakeStep(
                name=match.group(1),
                dependencies=dependencies if dependencies else None,
                code=[],
                raw_lines=[line],
                comment=None,
            )
            if i > 0 and lines[i - 1].startswith('#'):
                current_step.comment = lines[i - 1]
            steps.append(current_step)
        elif match := step_code_regex.match(line):
            if current_step:
                current_step.code.append(match.group(2))
                current_step.raw_lines.append(line)
    return steps


def run_make_step(step: MakeStep) -> None:
    cmd = f'make {step.name}'
    logger.info(f"{cmd}")
    shell(cmd, raw_output=True, print_stdout=True, print_log=False)
