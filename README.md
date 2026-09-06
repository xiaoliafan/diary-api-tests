# diary-api-tests

日记平台后端接口自动化测试项目，独立于 Java 后端工程，基于 **Pytest + HTTPX + Pydantic** 搭建。

## 技术说明

- `pytest`：测试用例组织、断言与报告
- `httpx`：HTTP 客户端，统一封装接口请求
- `pydantic`：响应数据建模，校验接口返回结构

## 目录结构

```text
diary-api-tests/
├── api/                  # 测试框架核心
│   ├── client.py         # HTTPX 接口客户端
│   └── schemas.py        # Pydantic 响应模型
├── tests/                # 测试用例（一个接口一个文件）
│   ├── conftest.py       # 公共夹具
│   ├── test_api_diaries_list.py     # GET /api/diaries 查询
│   ├── test_api_diaries_get.py      # GET /api/diaries/{id} 单查
│   ├── test_api_diaries_create.py   # POST /api/diaries 新增
│   ├── test_api_diaries_update.py   # PUT /api/diaries/{id} 编辑
│   └── test_api_diaries_delete.py   # DELETE /api/diaries/{id} 删除
├── requirements.txt
└── pytest.ini
```

## 运行

先启动日记平台后端，然后在项目目录执行：

```bash
cd diary-api-tests
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

只运行某个演示用例：

```bash
pytest -k test_create_and_get_diary -v
```

## 配置

后端地址默认是 `http://127.0.0.1:8080`，可用环境变量覆盖：

```bash
DIARY_API_BASE_URL=http://127.0.0.1:18080 pytest
```

## 覆盖率统计

要统计接口测试对 Java 后端的 JaCoCo 覆盖率，先在项目根目录停止 `./run.sh` 启动的后端进程，再在 `MotoTest` 根目录执行：

```bash
./run-api-coverage.sh
```

脚本会自动下载 JaCoCo、以 agent 方式启动后端、运行本目录全部用例，并在 `../target/jacoco-api-report/index.html` 生成报告。

## 用例组织

一个接口对应一个测试文件，文件内覆盖正常入参、边界值和异常入参：

| 文件 | 接口 | 覆盖重点 |
| --- | --- | --- |
| `test_api_diaries_list.py` | `GET /api/diaries` | 默认分页、自定义分页、提交人/内容/时间筛选、pageSize 上下限与超限钳制、非法数字回退、越界页码 |
| `test_api_diaries_get.py` | `GET /api/diaries/{id}` | 按 id 单查、不存在返回 404 |
| `test_api_diaries_create.py` | `POST /api/diaries` | 新增成功并回读 |
| `test_api_diaries_update.py` | `PUT /api/diaries/{id}` | 编辑内容、修改时间更新 |
| `test_api_diaries_delete.py` | `DELETE /api/diaries/{id}` | 删除成功、删除后查询 404 |

## 扩展方式

新增接口时，按“一个接口一个文件”的约定在 `tests/` 下新建 `test_api_<接口名>.py`，在 `api/schemas.py` 添加响应模型，在 `api/client.py` 添加请求方法。
