#!/usr/bin/env bash
set -euo pipefail

TARGET_HOST="${TARGET_HOST:-mail.tianbo.asia}"
TARGET_IP="${TARGET_IP:-1.13.197.180}"
HOSTS_FILE="${HOSTS_FILE:-/etc/hosts}"
ROUTE_GATEWAY="${ROUTE_GATEWAY:-192.168.5.1}"
ROUTE_INTERFACE="${ROUTE_INTERFACE:-$(ip route | awk '/^default / {print $5; exit}')}"
NETPLAN_FILE="${NETPLAN_FILE:-/etc/netplan/99-mail-tianbo-route.yaml}"

if [[ "${EUID}" -eq 0 ]]; then
  SUDO=""
else
  SUDO="sudo"
fi

tmp_file="$(mktemp)"
trap 'rm -f "${tmp_file}"' EXIT

${SUDO} cp "${HOSTS_FILE}" "${HOSTS_FILE}.bak.$(date -u +%Y%m%dT%H%M%SZ)"

${SUDO} awk -v host="${TARGET_HOST}" '
  {
    for (i = 1; i <= NF; i++) {
      if ($i == host) {
        next
      }
    }
    print
  }
' "${HOSTS_FILE}" > "${tmp_file}"

{
  cat "${tmp_file}"
  printf "%s %s\n" "${TARGET_IP}" "${TARGET_HOST}"
} > "${tmp_file}.new"

${SUDO} install -m 0644 "${tmp_file}.new" "${HOSTS_FILE}"

cat > "${tmp_file}.route" <<EOF
network:
  version: 2
  ethernets:
    ${ROUTE_INTERFACE}:
      routes:
        - to: ${TARGET_IP}/32
          via: ${ROUTE_GATEWAY}
EOF

${SUDO} install -m 0600 "${tmp_file}.route" "${NETPLAN_FILE}"
${SUDO} netplan apply

resolved_ip="$(getent ahostsv4 "${TARGET_HOST}" | awk 'NR==1 {print $1}')"
if [[ "${resolved_ip}" != "${TARGET_IP}" ]]; then
  echo "Resolution verification failed: ${TARGET_HOST} -> ${resolved_ip:-<empty>} (expected ${TARGET_IP})" >&2
  exit 1
fi

routed_via="$(ip route get "${TARGET_IP}" | awk '/via/ {for (i = 1; i <= NF; i++) if ($i == "via") {print $(i+1); exit}}')"
if [[ "${routed_via}" != "${ROUTE_GATEWAY}" ]]; then
  echo "Route verification failed: ${TARGET_IP} via ${routed_via:-<empty>} (expected ${ROUTE_GATEWAY})" >&2
  exit 1
fi

echo "Updated ${HOSTS_FILE}: ${TARGET_HOST} -> ${TARGET_IP}"
echo "Installed persistent host route in ${NETPLAN_FILE}: ${TARGET_IP}/32 via ${ROUTE_GATEWAY} dev ${ROUTE_INTERFACE}"
echo "Verification:"
getent ahostsv4 "${TARGET_HOST}" | sed -n '1,3p'
ip route get "${TARGET_IP}" | sed -n '1p'
