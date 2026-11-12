# diary-api-tests

日记平台自动化测试项目，独立于 Java 后端工程，包含 **Pytest + requests + YAML + Pydantic + Allure** 接口测试和 **Selenium** UI 测试。

## 技术说明

- `pytest`：测试用例组织、断言与报告
- `requests`：HTTP 客户端，统一封装 Session、超时和请求
- `PyYAML`：存放稳定的接口测试入参和简单预期字段
- `pydantic`：响应数据建模，校验接口返回结构
- `allure-pytest`：记录测试步骤、请求响应附件并生成 Allure 结果
- `selenium`：浏览器 UI 自动化
- `pytest-html`：生成 UI HTML 测试报告

## 目录结构

```text
diary-api-tests/
├── conftest.py           # 根级全局参数：--browser、--headless、--base-url
├── api/                  # 测试框架核心
│   ├── client.py         # requests Session 接口客户端
│   ├── allure_utils.py   # Allure 请求/响应附件
│   ├── yaml_loader.py    # YAML 加载与 Pydantic 校验
│   └── schemas.py        # Pydantic 响应模型
├── test_data/api/        # 稳定的 YAML 测试数据
│   └── diaries_list.yaml
├── tests/                # 接口测试（一个接口一个文件）
│   ├── conftest.py       # 公共夹具
│   ├── test_api_diaries_list.py     # GET /api/diaries 查询
│   ├── test_api_diaries_get.py      # GET /api/diaries/{id} 单查
│   ├── test_api_diaries_create.py   # POST /api/diaries 新增
│   ├── test_api_diaries_update.py   # PUT /api/diaries/{id} 编辑
│   └── test_api_diaries_delete.py   # DELETE /api/diaries/{id} 删除
├── ui_tests/             # UI 测试
│   ├── conftest.py       # driver、页面对象夹具
│   ├── pages/            # 页面对象，与用例分离
│   └── test_diary_ui.py  # UI 场景用例
├── run-api-tests.sh      # 接口测试和 Allure 报告入口
├── run-ui-tests.sh       # UI 测试和 HTML 报告入口
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

运行接口测试并生成 Allure 原始结果：

```bash
./run-api-tests.sh
```

如果本机已安装 Allure CLI，脚本会同时生成 HTML 报告：

```text
reports/allure-report/index.html
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

## YAML 数据驱动

稳定的接口入参放在 `test_data/api/`，目前查询接口示例位于 `test_data/api/diaries_list.yaml`。YAML 只保存参数、预期状态码和简单预期字段，加载后会经过 Pydantic 结构校验。

动态数据、时间范围、随机数据和接口串联仍放在 Python 用例中，例如 `test_api_diaries_list.py` 里的提交人/内容/时间筛选，以及 `test_api_diaries_update.py` 里的查询后编辑。

新增 YAML 用例时请保持：

- 每个 case 有唯一的 `id`
- `params` 只放稳定输入
- `expected_fields` 只放可以直接比较的字段
- 复杂断言继续写在 Python 中

## Allure 报告

通过 `./run-api-tests.sh` 运行接口测试时，会把 Allure 结果写入：

```text
reports/allure-results
```

请求方法、URL、状态码、请求体和响应体都会作为 Allure 附件记录，敏感请求头会自动脱敏。

本地查看报告需要安装 Allure CLI，例如：

```bash
brew install allure
```

生成并打开报告：

```bash
./run-api-tests.sh
allure serve reports/allure-results
```

也可以直接打开脚本生成的：

```text
reports/allure-report/index.html
```

## UI 自动化

UI 测试位于 `ui_tests/`，默认 `pytest` 只运行 `tests/` 下的接口测试，不会混跑 UI 用例。执行 UI 测试：

```bash
sh run-ui-tests.sh --browser chrome --headless
```

支持的浏览器参数：`chrome`、`firefox`、`edge`、`safari`。默认使用 Chrome，`--headless` 表示无头模式。服务地址可通过 `--base-url` 指定：

```bash
sh run-ui-tests.sh --browser chrome --headless --base-url http://127.0.0.1:8080
```

运行结果会生成 HTML 报告：

```text
reports/ui-report.html
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
