#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/zanbo/zanbotest"
DB_BASENAME="stock_codes.db"
DB_PATH="${BASE_DIR}/${DB_BASENAME}"
WAL_PATH="${DB_PATH}-wal"
SHM_PATH="${DB_PATH}-shm"
BACKUP_ROOT="${BASE_DIR}/backups/sqlite_retired"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
ARCHIVE_DIR="${BACKUP_ROOT}/${STAMP}"
ARCHIVE_FILE="${ARCHIVE_DIR}/${DB_BASENAME}.${STAMP}.tar.gz"
CHECKSUM_FILE="${ARCHIVE_FILE}.sha256"
EXECUTE=0

usage() {
  cat <<EOF
用法:
  bash /home/zanbo/zanbotest/retire_sqlite.sh --execute

说明:
  1. 校验 PostgreSQL 主库可用
  2. 打包压缩 SQLite 旧库及 wal/shm
  3. 生成 sha256 校验文件
  4. 将旧库从主目录移到归档目录
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --execute)
      EXECUTE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "未知参数: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

. "${BASE_DIR}/runtime_env.sh"

mkdir -p "${ARCHIVE_DIR}"

echo "[check] PostgreSQL 主库: ${DATABASE_URL}"
python3 - <<'PY'
import db_compat as sqlite3
conn = sqlite3.connect('stock_codes.db')
try:
    print('[check] stock_codes rows =', conn.execute('SELECT COUNT(*) FROM stock_codes').fetchone()[0])
finally:
    conn.close()
PY

FILES=()
for f in "$DB_PATH" "$WAL_PATH" "$SHM_PATH"; do
  if [[ -f "$f" ]]; then
    FILES+=("$f")
  fi
done

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "[skip] 未找到可退役的 SQLite 文件"
  exit 0
fi

echo "[plan] 将归档以下文件:"
for f in "${FILES[@]}"; do
  echo "  - $f"
done

echo "[plan] 归档输出: ${ARCHIVE_FILE}"

if [[ "$EXECUTE" -ne 1 ]]; then
  echo "[dry-run] 未执行移动。加 --execute 才会真正退役 SQLite 文件。"
  exit 0
fi

if command -v lsof >/dev/null 2>&1; then
  echo "[check] 当前打开这些文件的进程:"
  lsof "$DB_PATH" "$WAL_PATH" "$SHM_PATH" 2>/dev/null || true
fi

TAR_INPUTS=()
for f in "${FILES[@]}"; do
  TAR_INPUTS+=("$(basename "$f")")
done
(
  cd "$BASE_DIR"
  tar -czf "$ARCHIVE_FILE" "${TAR_INPUTS[@]}"
)
sha256sum "$ARCHIVE_FILE" > "$CHECKSUM_FILE"

for f in "${FILES[@]}"; do
  mv "$f" "$ARCHIVE_DIR/"
done

cat > "${BASE_DIR}/SQLITE_RETIRED.md" <<EOF
# SQLite 已退役

退役时间(UTC): ${STAMP}
当前主库: PostgreSQL (${DATABASE_URL})
Redis: ${REDIS_URL}

归档目录:
- ${ARCHIVE_DIR}

归档文件:
- ${ARCHIVE_FILE}
- ${CHECKSUM_FILE}

说明:
- 主目录中的 stock_codes.db 已移出，不再作为运行主库
- 如需重新从 SQLite 迁移，可使用归档目录中的旧库文件
EOF

echo "[done] SQLite 已退役，归档目录: ${ARCHIVE_DIR}"
