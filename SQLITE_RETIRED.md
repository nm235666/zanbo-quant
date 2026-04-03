# SQLite 已退役

退役时间(UTC): 20260327T062346Z
当前主库: PostgreSQL (postgresql://zanbo@/stockapp)
Redis: redis://127.0.0.1:6379/0

归档目录:
- /home/zanbo/zanbotest/backups/sqlite_retired/20260327T062346Z

归档文件:
- /home/zanbo/zanbotest/backups/sqlite_retired/20260327T062346Z/stock_codes.db.20260327T062346Z.tar.gz
- /home/zanbo/zanbotest/backups/sqlite_retired/20260327T062346Z/stock_codes.db.20260327T062346Z.tar.gz.sha256

说明:
- PostgreSQL 是当前唯一主运行库，Redis 为当前缓存/消息链路
- 退役动作指的是“SQLite 不再作为运行主库”，而不是保证仓库工作区永远不存在任何 `.db` 文件
- 当前若在仓库工作区看到 `stock_codes.db` 或其他 SQLite 文件，应视为迁移源、兼容保留、测试文件或历史遗留，不改变 PostgreSQL 主库事实
- 如需重新从 SQLite 迁移，可使用归档目录中的旧库文件或仓库中兼容保留的 SQLite 文件
