from dataclasses import dataclass
from pathlib import Path
import re
import sys
import time

from nuclear import CommandError, logger, shell


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
    lines = [line for line in lines if line]
    return _parse_makefile_lines(lines)


def _parse_makefile_lines(lines: list[str]) -> list[MakeStep]:
    step_header_regex = re.compile(r'^([a-zA-Z0-9_\-\.]+):( .+)?$')
    step_code_regex = re.compile(r'^(\s+)(.+)')
    steps: list[MakeStep] = []
    current_step: MakeStep | None = None
    for i, line in enumerate(lines):
        if match := step_header_regex.match(line):
            if line.startswith('.'):
                continue
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
    logger.info(f"Command: {cmd}")
    start_time = time.time()
    try:
        shell(cmd, raw_output=True, print_stdout=True, print_log=False)
    except CommandError as e:
        duration = format_duration(time.time() - start_time)
        logger.error('Command failed', cmd=cmd, exit_code=e.return_code, duration=duration)
        sys.exit(e.return_code)
    except KeyboardInterrupt:
        duration = format_duration(time.time() - start_time)
        logger.info('Interrupted', cmd=cmd, duration=duration)
    else:
        duration = format_duration(time.time() - start_time)
        logger.info('Command done', cmd=cmd, exit_code=0, duration=duration)


def format_duration(total_seconds: float) -> str:
    if total_seconds < 0:
        return format_duration(-total_seconds)
    millis = int(total_seconds * 1000) % 1000
    seconds = int(total_seconds % 60)
    minutes = int((total_seconds / 60) % 60)
    hours = int((total_seconds / 60 / 60) % 24)
    days = int(total_seconds / 60 / 60 / 24)

    parts = []
    if days > 0:
        parts.append(f'{days}d')
    if hours > 0:
        parts.append(f'{hours}h')
    if minutes > 0:
        parts.append(f'{minutes}m')
    if seconds > 0:
        parts.append(f'{seconds}s')
    if millis > 0:
        parts.append(f'{millis}ms')
    if not parts:
        return '0s'
    return ' '.join(parts)


def render_steps_list(steps: list[MakeStep], chosen_step: MakeStep | None):
    logger.info(f'{len(steps)} Makefile targets:')
    for step in steps:
        if step == chosen_step:
            print(f'> {step.name}')
        else:
            print(f'  {step.name}')
