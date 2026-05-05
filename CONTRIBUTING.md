# Contributing Guidelines

## Branch Strategy

- main: stable release branch
- dev: integration branch
- feature/*: feature branches

## Workflow

1. Create a feature branch from dev:
   git checkout dev
   git pull
   git checkout -b feature/your-feature-name

2. Push feature branch:
   git push -u origin feature/your-feature-name

3. Open Pull Request into dev.

4. At least 1 team member reviews before merge.

5. CI must be green before merge.

6. dev merges into main only at agreed milestones.

## Rules

- Do not push directly to main.
- Do not push directly to dev.
- All merges must go through PR.
- Keep commits small and descriptive.
