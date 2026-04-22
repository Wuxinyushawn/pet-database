# Pet Adoption Center Management System
> CSC 3170 Database Project — Group [X] | CUHK 2026
 
## Table of Contents
1. [Project Overview](#project-overview)
2. [ER Design](#er-design)
3. [Relational Schema & Normalization](#relational-schema--normalization)
4. [Sample Data](#sample-data)
5. [Backend & SQL Queries](#backend--sql-queries)
6. [Frontend Demo](#frontend-demo)
7. [Bonus](#bonus)
8. [How to Run](#how-to-run)
 
---
 
## Project Overview
 
This project implements a database management system for a pet adoption center. The system supports the full operational workflow of a shelter, including pet registration, adoption applications, post-adoption follow-up, medical and vaccination records, and volunteer care scheduling.
 
The database was designed following standard normalization principles (3NF/BCNF) and implemented with a web-based frontend demo for demonstrating daily operations.
 
---

 
## ER Design
 
> See the file [ER Design for the Pet Adoption Center Management System.md](https://github.com/gnuhzy/pet-database/blob/2bcc63b18d6a3502cbfa35ccb2c622ac1ef64467/ER%20Design%20for%20the%20Pet%20Adoption%20Center%20Management%20System.md)
 
<!--
Suggested content:
- Brief explanation of design decisions and assumptions
- List of entities and their roles
- Description of key relationships and cardinalities
- Embedded ER diagram image: ![ER Diagram](./assets/er_diagram.png)
-->
 
---
 
## Relational Schema & Normalization
 
> See the file [ER Design for the Pet Adoption Center Management System.md](https://github.com/gnuhzy/pet-database/blob/2bcc63b18d6a3502cbfa35ccb2c622ac1ef64467/ER%20Design%20for%20the%20Pet%20Adoption%20Center%20Management%20System.md)
 
<!--
Suggested content:
- Full relational schemas with primary keys (underlined) and foreign keys noted
- Functional dependencies for each relation
- Normalization analysis (justify 3NF or BCNF for each table)
- Any indexing or hashing recommendations (Project requirement #8)
-->
 
---
 
## Sample Data
 
> *To be completed by the data member.*
 
<!--
Suggested content:
- Description of how data was generated (realistic assumptions made)
- Number of records per table
- Any notable data constraints or edge cases covered
- Link to SQL seed file: [seed.sql](./sql/seed.sql)
-->
 
---
 
## API Contract Governance

- OpenAPI contract file: `docs/api/openapi.yaml`.
- This contract is the only integration source of truth across frontend/backend.
- Any API change must update the OpenAPI file first, then implementation code.

---

## Backend & SQL Queries
 
> *To be completed by the backend member.*
 
<!--
Suggested content:
- Tech stack used (e.g., Python/Flask, Node.js/Express, etc.)
- Database system used (e.g., MySQL, PostgreSQL, SQLite)
- How to set up and run the backend server
- Operational SQL queries (Project requirement #6)
- Analytical/data mining queries if applicable (Project requirement #7)
-->
 
---
 
## Frontend Demo
 
The frontend is a self-contained single-file HTML demo (`pawtrack_demo.html`) that simulates the full management interface of the adoption center. It is built with plain HTML, CSS, and JavaScript — no frameworks or external dependencies are required.
 
### What it demonstrates
 
The demo covers five core modules drawn directly from the ER schema:
 
| Module | Entities covered | Key interactions |
|--------|-----------------|-----------------|
| Dashboard | — | Live statistics, recent activity feed, pet status overview |
| Pet management | `PET`, `SHELTER` | Searchable and filterable pet list, full pet profile view |
| Adoption applications | `ADOPTION_APPLICATION`, `APPLICANT` | New application form, application review (Approve / Reject) |
| Medical records | `MEDICAL_RECORD`, `VACCINATION` | Visit history, upcoming vaccination due dates |
| Volunteers | `VOLUNTEER`, `CARE_ASSIGNMENT` | Volunteer roster, daily care assignment schedule |
 
### Mock data strategy
 
Because the backend was developed in parallel, the demo uses **in-memory mock data** defined as JavaScript arrays at the top of the file. Every data operation (filtering, status updates, new record creation) runs against these arrays in the browser.
 
This approach was chosen deliberately so that replacing mock data with real API calls requires only minimal changes — each data-fetching logic is isolated in dedicated functions. For example, swapping `renderPets(pets)` for a `fetch('/api/pets')` call does not require changes to any rendering or UI logic.
 
### Key interactions
 
**Submitting a new adoption application**
 
Clicking `+ New application` opens a modal form. The pet dropdown is dynamically populated with only `Available` pets, enforcing the business rule from the ER design that a reserved or adopted pet cannot receive new applications. On submission, the selected pet's status is updated to `Reserved`, mirroring the SQL transaction:
 
```sql
INSERT INTO ADOPTION_APPLICATION (applicant_id, pet_id, ...) VALUES (...);
UPDATE PET SET status = 'Reserved' WHERE pet_id = ?;
```
 
**Reviewing a pending application**
 
Each `Pending` application displays a `Review` button. The reviewer must enter a decision note before choosing Approve or Reject — empty submissions are blocked. On confirmation, the application's status, reviewer name, reviewed date, and decision note are all updated in one operation, corresponding to:
 
```sql
UPDATE ADOPTION_APPLICATION
SET status = ?, reviewer_name = ?, reviewed_date = ?, decision_note = ?
WHERE application_id = ?;
```
 
### File structure
 
```
pawtrack_demo.html      ← the entire frontend (single file, no dependencies)
```
 
### How to open
 
Simply open `pawtrack_demo.html` in any modern browser. No server, installation, or internet connection is required.
 
```bash
# macOS
open pawtrack_demo.html
 
# Windows
start pawtrack_demo.html
 
# Linux
xdg-open pawtrack_demo.html
```
 
The file is fully self-contained and works correctly when opened directly via `file://`. All CSS variables are defined inline, so the interface renders consistently regardless of the environment.
 
---
 
## Bonus
 
> *To be completed by the bonus member.*
 
<!--
Indicate which bonus option was chosen:
  Option A — LLM + Database
  Option B — Security & Privacy + Database
 
Then describe the implementation.
-->
 
---
 
## How to Run
 
> *To be completed once backend is ready.*
 
<!--
Suggested structure:
 
### Prerequisites
- [e.g., Python 3.10+, Node.js 18+, MySQL 8.0+]
 
### 1. Set up the database
```bash
mysql -u root -p < sql/schema.sql
mysql -u root -p < sql/seed.sql
```
 
### 2. Start the backend server
```bash
cd backend
pip install -r requirements.txt
python app.py
```
 
### 3. Open the frontend
Navigate to http://localhost:5000 in your browser,
or open pawtrack_demo.html directly for the standalone demo.
-->

---

# 宠物领养中心管理系统
> CSC 3170 数据库项目 — 第 [X] 组 | 香港中文大学 2026

## 目录
1. [项目概述](#项目概述)
2. [ER 图设计](#er-图设计)
3. [关系模式与规范化](#关系模式与规范化)
4. [样本数据](#样本数据)
5. [后端与 SQL 查询](#后端与-sql-查询)
6. [前端演示](#前端演示)
7. [附加加分项](#附加加分项)
8. [运行说明](#运行说明)

---

## 项目概述

本项目为一家宠物领养中心设计并实现了一套数据库管理系统，覆盖收容所日常运营的完整业务流程，包括宠物档案注册、领养申请处理、领养后跟进记录、医疗与疫苗管理，以及志愿者护理排班。

数据库设计遵循标准规范化原则（3NF/BCNF），并配有基于网页的前端演示界面，用于展示系统的日常操作功能。

---


## ER 图设计

> **

<!--
建议包含以下内容：
- 设计决策说明与假设条件阐述
- 各实体的定义及其在业务中的作用
- 关键关系及其基数说明
- 嵌入 ER 图图片：![ER 图](./assets/er_diagram.png)
-->

---

## 关系模式与规范化

> **

<!--
建议包含以下内容：
- 完整关系模式列表（注明主键和外键）
- 各关系的函数依赖分析
- 规范化说明（论证每张表满足 3NF 或 BCNF）
- 索引与哈希建议（对应项目要求第 8 项）
-->

---

## 样本数据

> **

<!--
建议包含以下内容：
- 数据生成方式说明（真实性假设与依据）
- 各表的记录数量
- 数据中覆盖的特殊约束或边界情况
- SQL 种子文件链接：[seed.sql](./sql/seed.sql)
-->

---

## 后端与 SQL 查询

> **

<!--
建议包含以下内容：
- 技术栈说明（如 Python/Flask、Node.js/Express 等）
- 数据库系统说明（如 MySQL、PostgreSQL、SQLite）
- 后端服务器的搭建与启动方式
- 日常操作类 SQL 查询（对应项目要求第 6 项）
- 分析/数据挖掘类 SQL 查询（对应项目要求第 7 项，如适用）
-->

---

## 前端演示

前端为一个完全独立的单文件 HTML 演示页面（`pawtrack_demo.html`），模拟了领养中心管理系统的完整操作界面。页面使用纯 HTML、CSS 和 JavaScript 编写，无需任何框架或外部依赖。

### 功能模块概览

演示页面涵盖五个核心模块，均直接对应 ER 图中的实体设计：

| 模块 | 涉及实体 | 主要交互功能 |
|------|---------|------------|
| 仪表盘 | — | 实时统计数字、近期动态记录、宠物状态分布概览 |
| 宠物管理 | `PET`、`SHELTER` | 可搜索/筛选的宠物列表，宠物完整档案查看 |
| 领养申请 | `ADOPTION_APPLICATION`、`APPLICANT` | 新建申请表单，申请审核（通过 / 拒绝） |
| 医疗记录 | `MEDICAL_RECORD`、`VACCINATION` | 医疗访问历史，即将到期的疫苗接种提醒 |
| 志愿者管理 | `VOLUNTEER`、`CARE_ASSIGNMENT` | 志愿者名单，当日护理分配排班 |

### Mock 数据策略

由于前后端并行开发，演示页面采用**内存中的 Mock 数据**，以 JavaScript 数组的形式定义在文件顶部。所有数据操作（筛选、状态更新、新建记录）均在浏览器内对这些数组执行，无需连接真实数据库。

这一策略的核心优势在于：将数据获取逻辑集中封装在独立函数中，未来接入真实后端时，只需将对应函数的返回值替换为 `fetch('/api/...')` 的响应结果，页面的渲染逻辑和交互逻辑均无需改动。

### 核心交互说明

**新建领养申请**

点击 `+ New application` 按钮打开表单弹窗。宠物下拉列表会动态过滤，仅显示状态为 `Available` 的宠物，从前端层面落实了 ER 设计中"已预留或已领养的宠物不可接受新申请"的业务规则。

提交后，所选宠物的状态将同步更新为 `Reserved`，对应以下数据库事务：

```sql
INSERT INTO ADOPTION_APPLICATION (applicant_id, pet_id, application_date, reason, status)
VALUES (?, ?, ?, ?, 'Pending');

UPDATE PET
SET status = 'Reserved'
WHERE pet_id = ?;
```

**审核领养申请**

所有状态为 `Pending` 的申请行会显示 `Review` 审核按钮。审核员必须填写审核备注后，方可点击通过或拒绝——系统会拦截空备注的提交，避免无记录的审核操作。

确认后，申请的状态、审核人姓名、审核日期和审核备注将一并更新，对应以下 SQL 操作：

```sql
UPDATE ADOPTION_APPLICATION
SET status        = ?,
    reviewer_name = ?,
    reviewed_date = ?,
    decision_note = ?
WHERE application_id = ?;
```

### 文件结构

```
pawtrack_demo.html      ← 完整前端（单文件，零依赖）
```

### 打开方式

直接用任意现代浏览器打开 `pawtrack_demo.html` 即可，无需服务器、无需安装任何依赖、无需网络连接。

```bash
# macOS
open pawtrack_demo.html

# Windows
start pawtrack_demo.html

# Linux
xdg-open pawtrack_demo.html
```

文件完全自包含，通过 `file://` 协议直接打开时界面显示正常。所有 CSS 变量均在文件内部定义，不依赖外部环境注入，深色模式（`prefers-color-scheme: dark`）同样受支持。

---

## 附加加分项

> **

<!--
请注明选择的加分方案：
  方案一 — 大语言模型（LLM）与数据库结合
  方案二 — 安全与隐私保护结合数据库

然后描述具体实现内容。
-->

---

## 运行说明

> **

<!--
建议结构如下：

### 环境要求
- [例如：Python 3.10+、Node.js 18+、MySQL 8.0+]

### 第一步：初始化数据库
```bash
mysql -u root -p < sql/schema.sql
mysql -u root -p < sql/seed.sql
```

### 第二步：启动后端服务器
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 第三步：打开前端页面
在浏览器中访问 http://localhost:5000，
或直接打开 pawtrack_demo.html 使用独立演示版本。
-->
