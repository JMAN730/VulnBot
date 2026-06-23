# LFI/RFIfile security testing guidance
English: LFI/RFI File Inclusion
- Entry Count: 12
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## file security testing guidance
- ID: lfi-basic
- Difficulty: intermediate
- Subcategory: file security testing guidance
- Tags: lfi, local, file, inclusion
- Original Extracted Source: original extracted web-security-wiki source/lfi-basic.md
Description:
file security testing guidance
Prerequisites:
- file security testing guidance
- file security testing guidance
Execution Outline:
1. 1. file security testing guidanceLFI
2. 2. file security testing guidance
3. 3. PHPfile security testing guidance
4. 4. file security testing guidance
## file security testing guidance
- ID: rfi-basic
- Difficulty: intermediate
- Subcategory: file security testing guidance
- Tags: rfi, remote, file, inclusion
- Original Extracted Source: original extracted web-security-wiki source/rfi-basic.md
Description:
file security testing guidance
Prerequisites:
- file security testing guidance
- allow_url_include=On
- file security testing guidance
Execution Outline:
1. 1. file security testing guidanceRFI
2. 2. file security testing guidance
3. 3. file security testing guidanceShell
4. 4. file security testing guidancedatafile security testing guidance
## file security testing guidanceLFI
- ID: lfi-log-poison
- Difficulty: intermediate
- Subcategory: file security testing guidance
- Tags: lfi, log, poison, rce
- Original Extracted Source: original extracted web-security-wiki source/lfi-log-poison.md
Description:
file security testing guidanceLFIfile security testing guidanceRCE
Prerequisites:
- file security testing guidanceLFIfile security testing guidance
- file security testing guidance
- file security testing guidance
Execution Outline:
1. 1. file security testing guidance
2. 2. file security testing guidanceUser-Agent
3. 3. file security testing guidance
4. 4. file security testing guidance
## PHPfile security testing guidance
- ID: lfi-wrapper
- Difficulty: intermediate
- Subcategory: file security testing guidance
- Tags: lfi, wrapper, php, protocol
- Original Extracted Source: original extracted web-security-wiki source/lfi-wrapper.md
Description:
file security testing guidancePHPfile security testing guidanceLFIfile security testing guidance
Prerequisites:
- file security testing guidanceLFIfile security testing guidance
- PHPfile security testing guidance
- file security testing guidance
Execution Outline:
1. 1. php://filter
2. 2. php://input
3. 3. data://file security testing guidance
4. 4. phar://file security testing guidance
## file security testing guidance
- ID: lfi-traversal
- Difficulty: beginner
- Subcategory: file security testing guidance
- Tags: lfi, traversal, bypass, path
- Original Extracted Source: original extracted web-security-wiki source/lfi-traversal.md
Description:
LFIfile security testing guidance
Prerequisites:
- file security testing guidanceLFIfile security testing guidance
- file security testing guidance
Execution Outline:
1. 1. file security testing guidance
2. 2. file security testing guidance../
3. 3. URLfile security testing guidance
4. 4. Unicodefile security testing guidance
## PHP Filterfile security testing guidance
- ID: lfi-php-filter
- Difficulty: intermediate
- Subcategory: PHP Filter
- Tags: lfi, php, filter, chain
- Original Extracted Source: original extracted web-security-wiki source/lfi-php-filter.md
Description:
file security testing guidancePHP Filterfile security testing guidanceLFIfile security testing guidance
Prerequisites:
- file security testing guidanceLFIfile security testing guidance
- PHPfile security testing guidance
- filterfile security testing guidance
Execution Outline:
1. 1. file security testing guidance
2. 2. file security testing guidance
3. 3. Filterfile security testing guidanceRCE
4. 4. file security testing guidance
## PHP Inputfile security testing guidance
- ID: lfi-php-input
- Difficulty: intermediate
- Subcategory: PHP Input
- Tags: lfi, php, input, rce
- Original Extracted Source: original extracted web-security-wiki source/lfi-php-input.md
Description:
file security testing guidancephp://inputfile security testing guidancePHPfile security testing guidance
Prerequisites:
- file security testing guidanceLFIfile security testing guidance
- allow_url_include=On
- POSTfile security testing guidance
Execution Outline:
1. 1. file security testing guidance
2. 2. file security testing guidance
3. 3. file security testing guidance
4. 4. file security testing guidanceShell
## PHP Datafile security testing guidance
- ID: lfi-php-data
- Difficulty: intermediate
- Subcategory: PHP Data
- Tags: lfi, php, data, protocol
- Original Extracted Source: original extracted web-security-wiki source/lfi-php-data.md
Description:
file security testing guidancedata://file security testing guidancePHPfile security testing guidance
Prerequisites:
- file security testing guidanceLFIfile security testing guidance
- allow_url_include=On
- datafile security testing guidance
Execution Outline:
1. 1. file security testing guidance
2. 2. Base64file security testing guidance
3. 3. file security testing guidance
4. 4. file security testing guidanceShell
## PHP Zipfile security testing guidance
- ID: lfi-php-zip
- Difficulty: intermediate
- Subcategory: PHP Zip
- Tags: lfi, php, zip, archive
- Original Extracted Source: original extracted web-security-wiki source/lfi-php-zip.md
Description:
file security testing guidancezip://file security testing guidanceLFIfile security testing guidance
Prerequisites:
- file security testing guidanceLFIfile security testing guidance
- file security testing guidancezipfile security testing guidance
- zipfile security testing guidance
Execution Outline:
1. 1. file security testing guidanceZip
2. 2. file security testing guidanceZipfile security testing guidance
3. 3. file security testing guidanceZipfile security testing guidance
4. 4. file security testing guidance
## Pharfile security testing guidance
- ID: lfi-phar
- Difficulty: advanced
- Subcategory: Pharfile security testing guidance
- Tags: lfi, phar, deserialization, rce
- Original Extracted Source: original extracted web-security-wiki source/lfi-phar.md
Description:
file security testing guidancePharfile security testing guidanceRCE
Prerequisites:
- file security testing guidanceLFIfile security testing guidance
- PHPfile security testing guidance
- pharfile security testing guidance
Execution Outline:
1. 1. file security testing guidancePharfile security testing guidance
2. 2. file security testing guidance
3. 3. file security testing guidancePhar
4. 4. file security testing guidanceGadgetfile security testing guidance
## Sessionfile security testing guidance
- ID: lfi-session
- Difficulty: intermediate
- Subcategory: Sessionfile security testing guidance
- Tags: lfi, session, file, inclusion
- Original Extracted Source: original extracted web-security-wiki source/lfi-session.md
Description:
file security testing guidanceSessionfile security testing guidanceLFIfile security testing guidance
Prerequisites:
- file security testing guidanceLFIfile security testing guidance
- file security testing guidanceSessionfile security testing guidance
- file security testing guidanceSessionfile security testing guidance
Execution Outline:
1. 1. file security testing guidanceSessionfile security testing guidance
2. 2. file security testing guidanceSessionfile security testing guidance
3. 3. file security testing guidanceSessionfile security testing guidance
4. 4. Sessionfile security testing guidance
## Procfile security testing guidance
- ID: lfi-proc
- Difficulty: intermediate
- Subcategory: Procfile security testing guidance
- Tags: lfi, proc, linux, environ
- Original Extracted Source: original extracted web-security-wiki source/lfi-proc.md
Description:
file security testing guidance/procfile security testing guidanceLFIfile security testing guidance
Prerequisites:
- file security testing guidanceLFIfile security testing guidance
- Linuxfile security testing guidance
- /procfile security testing guidance
Execution Outline:
1. 1. file security testing guidance
2. 2. file security testing guidance
3. 3. file security testing guidancefdfile security testing guidance
4. 4. file security testing guidance

