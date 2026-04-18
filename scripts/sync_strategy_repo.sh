#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${TARGET_DIR:-${ROOT_DIR}/external/strategy}"
REPO_URL="${STRATEGY_REPO_URL:-https://github.com/WealthCodePro/Strategy.git}"
REPO_BRANCH="${STRATEGY_REPO_BRANCH:-}"
USE_SSH="${STRATEGY_REPO_USE_SSH:-0}"
SSH_KEY_PATH="${STRATEGY_REPO_SSH_KEY:-${HOME}/.ssh/id_ed25519_github_nm235666}"
TOKEN="${STRATEGY_REPO_TOKEN:-}"

if [[ "${USE_SSH}" == "1" ]]; then
  # Convert https://github.com/org/repo.git -> git@github.com:org/repo.git
  if [[ "${REPO_URL}" =~ ^https://github.com/(.+)$ ]]; then
    REPO_URL="git@github.com:${BASH_REMATCH[1]}"
  fi
fi

AUTH_REPO_URL="${REPO_URL}"
if [[ -n "${TOKEN}" && "${REPO_URL}" =~ ^https://github.com/(.+)$ ]]; then
  AUTH_REPO_URL="https://x-access-token:${TOKEN}@github.com/${BASH_REMATCH[1]}"
fi

mkdir -p "$(dirname "${TARGET_DIR}")"

GIT_CMD=(git)
if [[ "${USE_SSH}" == "1" ]]; then
  GIT_CMD=(env "GIT_SSH_COMMAND=ssh -i ${SSH_KEY_PATH} -o IdentitiesOnly=yes" git)
fi

echo "[strategy-sync] target=${TARGET_DIR}"
echo "[strategy-sync] repo=${REPO_URL}"

if [[ -d "${TARGET_DIR}/.git" ]]; then
  echo "[strategy-sync] existing repo detected, pulling latest..."
  "${GIT_CMD[@]}" -C "${TARGET_DIR}" remote set-url origin "${AUTH_REPO_URL}"
  "${GIT_CMD[@]}" -C "${TARGET_DIR}" fetch --all --prune
  if [[ -n "${REPO_BRANCH}" ]]; then
    "${GIT_CMD[@]}" -C "${TARGET_DIR}" checkout "${REPO_BRANCH}"
    "${GIT_CMD[@]}" -C "${TARGET_DIR}" pull --ff-only origin "${REPO_BRANCH}"
  else
    current_branch="$("${GIT_CMD[@]}" -C "${TARGET_DIR}" rev-parse --abbrev-ref HEAD)"
    "${GIT_CMD[@]}" -C "${TARGET_DIR}" pull --ff-only origin "${current_branch}"
  fi
else
  rm -rf "${TARGET_DIR}"
  echo "[strategy-sync] cloning..."
  if [[ -n "${REPO_BRANCH}" ]]; then
    "${GIT_CMD[@]}" clone --branch "${REPO_BRANCH}" "${AUTH_REPO_URL}" "${TARGET_DIR}"
  else
    "${GIT_CMD[@]}" clone "${AUTH_REPO_URL}" "${TARGET_DIR}"
  fi
fi

commit_sha="$("${GIT_CMD[@]}" -C "${TARGET_DIR}" rev-parse HEAD)"
echo "[strategy-sync] done, commit=${commit_sha}"
