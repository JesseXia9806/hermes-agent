---
name: postgresql-native-deploy
description: Use when deploying optimized native PostgreSQL on Linux.
tags:
  - postgresql
  - database
  - deployment
  - rhel
---

# PostgreSQL Native Deployment (Bare-metal)

Use when: You need to deploy a high-performance DB node where avoiding Docker overhead (NAT network + OverlayFS) is necessary, especially on RHEL/Ubuntu dedicated servers.

## Installation for RHEL/Rocky Linux 9

```bash
# 1. Enable module and install (e.g., PG 16)
dnf module reset postgresql -y
dnf module enable postgresql:16 -y
dnf install postgresql-server postgresql-contrib -y

# 2. Init database
postgresql-setup --initdb

# 3. Configure Network Binding and Auth
PG_DATADIR="/var/lib/pgsql/data"
sed -i "s/^#listen_addresses = 'localhost'/listen_addresses = '*'/g" $PG_DATADIR/postgresql.conf
echo "host    all             all             0.0.0.0/0               scram-sha-256" >> $PG_DATADIR/pg_hba.conf

# 4. Start & enable
systemctl enable --now postgresql

# 5. Set Password
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'YourStrongPassword';"

# 6. Firewall rules
firewall-cmd --permanent --add-port=5432/tcp
firewall-cmd --reload
```

## Security Rule Context
- **Never execute destructive commands or database overwrites without explicit IT Manager approval ("只查不改" principle).**
- Keep data paths isolated (typically `/var/lib/pgsql/data/`).
- Recommend tracking authentication changes in `.hermes/secrets/` according to standard local policy.
