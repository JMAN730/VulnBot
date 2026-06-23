# AIAI security testing guidance - AI security testing guidance

> AI security testing guidance: AISSAI security testing guidance | AI security testing guidance ai-baseline-security.md
> AI security testing guidance: AI security testing guidance/AI security testing guidance/AI security testing guidance AI security testing guidance

## AI security testing guidance、AI security testing guidance

> AI security testing guidanceAIAI security testing guidance（Docker/Sysbox/Daytona/Kubernetes）AI security testing guidance
> **AI security testing guidance**: WebAI security testing guidance → [web-deployment-security.md §AI security testing guidance](web-deployment-security.md)

### AI security testing guidance、AI security testing guidance

```
AI security testing guidance → AI security testing guidance → AI security testing guidance → AI security testing guidance → AI security testing guidance → AI security testing guidance → AI security testing guidance
```

### AI security testing guidance、AI security testing guidance

#### 2.1 AI security testing guidance

| AI security testing guidance | AI security testing guidance | AI security testing guidance |
|--------|------|----------|
| AI security testing guidance | `cat /proc/1/cgroup` | AI security testing guidance`docker`/`kubepods`/`containerd` |
| DockerAI security testing guidance | `ls /.dockerenv` | AI security testing guidanceDockerAI security testing guidance |
| AI security testing guidance | `cat /proc/1/cgroup \| head` | `sysbox-fs`→Sysbox, `docker`→Docker |
| AI security testing guidance | `uname -r` | AI security testing guidanceCVEAI security testing guidance |
| User Namespace | `cat /proc/self/uid_map` | `0 0 4294967295`→AI security testing guidance(AI security testing guidance) |
| Capabilities | `cat /proc/self/status \| grep Cap` | AI security testing guidanceCap |
| Seccomp | `cat /proc/self/status \| grep Seccomp` | 0=disabled, 2=filter |
| AppArmor | `cat /proc/self/attr/current` | `unconfined`→AI security testing guidance |
| AI security testing guidance | `mount \| grep -v overlay` | AI security testing guidance |

#### 2.2 Sysbox AI security testing guidance

| AI security testing guidance | AI security testing guidance | AI security testing guidance |
|--------|------|----------|
| CE vs EEAI security testing guidance | `sysbox-runc --version` AI security testing guidanceUIDAI security testing guidance | CEAI security testing guidance |
| UIDAI security testing guidance | `cat /proc/self/uid_map`, CEAI security testing guidance`0 165536 65536`(AI security testing guidance) | AI security testing guidance→AI security testing guidance |
| AI security testing guidance/proc | `ls /proc/sys/net/` | SysboxAI security testing guidance |
| Docker-in-Docker | `docker ps 2>/dev/null` | AI security testing guidanceDockerAI security testing guidance |
| /dev/kvm | `ls /dev/kvm` | KVMAI security testing guidance→AI security testing guidance |

### AI security testing guidance、AI security testing guidance

#### 3.1 AI security testing guidance

```bash
# PID NamespaceAI security testing guidance
ps aux   # AI security testing guidance/AI security testing guidance
ls /proc/*/cmdline   # AI security testing guidance

# AI security testing guidancePID 1AI security testing guidanceinitAI security testing guidancesystemd/dockerd → AI security testing guidance
cat /proc/1/cmdline | tr '\0' ' '
```

#### 3.2 AI security testing guidance

```bash
# AI security testing guidance
ip addr   # AI security testing guidanceIPAI security testing guidance
ip route  # AI security testing guidance，AI security testing guidance

# AI security testing guidance(AI security testing guidance)
for i in $(seq 1 254); do
  (ping -c 1 -W 1 $SUBNET.$i &>/dev/null && echo "$SUBNET.$i alive") &
done; wait

# AI security testing guidanceDNSAI security testing guidance
cat /etc/resolv.conf
nslookup kubernetes.default.svc.cluster.local 2>/dev/null
```

#### 3.3 AI security testing guidance

```bash
# AI security testing guidance
mount | grep -E "ext4|xfs|btrfs" | grep -v overlay
findmnt

# AI security testing guidance
ls -la /var/lib/sysbox/ 2>/dev/null
ls -la /var/lib/docker/ 2>/dev/null
ls -la /run/containerd/ 2>/dev/null

# AI security testing guidance
ln -s /proc/1/root/etc/shadow /tmp/test_escape
cat /tmp/test_escape 2>&1  # AI security testing guidance→AI security testing guidance
```

### AI security testing guidance、AI security testing guidance

| AI security testing guidance | AI security testing guidance | AI security testing guidance | AI security testing guidance |
|----------|----------|----------|----------|
| cgroup release_agent | CAP_SYS_ADMIN + cgroup v1 | Critical | AI security testing guidancerelease_agentAI security testing guidance |
| Docker Socket | /var/run/docker.sockAI security testing guidance | Critical | AI security testing guidanceAPIAI security testing guidance |
| /proc/1/root | PID NamespaceAI security testing guidance | Critical | AI security testing guidance |
| AI security testing guidance | --privilegedAI security testing guidance | Critical | mountAI security testing guidance |
| runc fdAI security testing guidance | CVE-2024-21626 | High | AI security testing guidance/proc/self/fdAI security testing guidance |
| Dirty Pipe | CVE-2022-0847, 5.8≤kernel≤5.16.11 | High | AI security testing guidance |
| OverlayFS | CVE-2023-0386, 5.11≤kernel≤6.2 | High | SUIDAI security testing guidance |
| AI security testing guidance | AI security testing guidancemountAI security testing guidance | High | AI security testing guidance |
| CAP_DAC_READ_SEARCH | CapabilityAI security testing guidance | Medium | open_by_handle_atAI security testing guidance |
| CAP_SYS_PTRACE | CapabilityAI security testing guidance | Medium | AI security testing guidance |
| Docker-in-Docker | AI security testing guidanceDockerAI security testing guidance | Medium | AI security testing guidance |

### AI security testing guidance、AI security testing guidance

> AI security testing guidance（AI security testing guidanceDaytona）

| AI security testing guidance | AI security testing guidance1AI security testing guidance | AI security testing guidance2AI security testing guidance | AI security testing guidance |
|--------|-----------|-----------|-------------|
| .bashrcAI security testing guidance | `echo 'malicious_cmd' >> ~/.bashrc` | AI security testing guidanceshellAI security testing guidance | AI security testing guidance/AI security testing guidance |
| Crontab | `echo "* * * * * cmd" \| crontab -` | `crontab -l` | CrontabAI security testing guidance |
| SSHAI security testing guidance | AI security testing guidance~/.ssh/authorized_keys | SSHAI security testing guidance | SSHAI security testing guidance |
| AI security testing guidance | `nohup cmd &` | `ps aux \| grep cmd` | AI security testing guidance |
| AI security testing guidance | AI security testing guidance | AIAI security testing guidance | AIAI security testing guidance |
| AI security testing guidance | AI security testing guidanceshellAI security testing guidance | `cat ~/.bash_history` | AI security testing guidance |
| AI security testing guidance | `export SECRET=leaked` | `echo $SECRET` | AI security testing guidance |

### AI security testing guidance、AI security testing guidance

```
AI security testing guidance → AI security testing guidance → AI security testing guidance/AI security testing guidance/APIAI security testing guidance → AI security testing guidance
         ↓
         AI security testing guidance(169.254.169.254) → IAMAI security testing guidance → AI security testing guidance
         ↓
         K8s API(kubernetes.default.svc) → PodAI security testing guidance/SecretAI security testing guidance
```

| AI security testing guidance | AI security testing guidance | AI security testing guidance |
|------|----------|----------|
| AI security testing guidance | `curl 169.254.169.254` | AI security testing guidanceIAMAI security testing guidance |
| K8s API | `curl -k https://kubernetes.default.svc` | AI security testing guidancePod/AI security testing guidanceSecret |
| K8s ServiceAccount | `cat /var/run/secrets/kubernetes.io/serviceaccount/token` | AI security testing guidanceK8s API |
| AI security testing guidance | `echo \| nc DB_HOST 5432` | AI security testing guidance |
| Redis | `redis-cli -h REDIS_HOST ping` | AI security testing guidance |
| Docker Registry | `curl http://REGISTRY:5000/v2/_catalog` | AI security testing guidance |

### AI security testing guidance、AI security testing guidanceChecklist

```
[ ] AI security testing guidancerootAI security testing guidance(AI security testing guidanceUser NamespaceAI security testing guidance)
[ ] AI security testing guidanceCapabilities(AI security testing guidance: AI security testing guidanceNET_BIND_SERVICEAI security testing guidance)
[ ] Seccomp profileAI security testing guidance(AI security testing guidancedisabled)
[ ] AppArmor/SELinuxAI security testing guidanceunconfined
[ ] /var/run/docker.sockAI security testing guidance
[ ] AI security testing guidance--privilegedAI security testing guidance
[ ] AI security testing guidance(/、/etc、/var/run)
[ ] AI security testing guidanceCVEAI security testing guidance
[ ] cgroup v2AI security testing guidancerelease_agentAI security testing guidance
[ ] PID NamespaceAI security testing guidance(AI security testing guidance)
[ ] Network Policy/AI security testing guidance
[ ] 169.254.169.254AI security testing guidance
[ ] AI security testing guidance(history/credentials)AI security testing guidance
[ ] AI security testing guidance
[ ] SysboxAI security testing guidanceEEAI security testing guidanceUIDAI security testing guidance
```

---
