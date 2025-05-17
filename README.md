# OKX Trading Bot

这是一个基于 OKX API 的自动交易机器人，支持简单的移动平均线交叉策略（Moving Average Crossover Strategy）。机器人能够实时获取市场数据、执行交易策略并自动下单，同时支持查看账户余额。

## 功能特性

- **实时行情获取**：通过 OKX API 获取最新的市场价格和 K 线数据。
- **交易策略**：实现了简单的移动平均线交叉策略。
- **自动下单**：根据策略信号自动执行买入或卖出操作。
- **账户余额查询**：支持查看账户中各币种的可用余额。
- **日志记录**：所有操作和错误信息都会记录到日志文件中。

## 文件结构
TBD

## 环境依赖

在运行此项目之前，请确保已安装以下依赖：

- Python 3.9 或更高版本
- 必要的 Python 库：
  - `okx`
  - `pandas`
  - `logging`
  - `json`
  - `time`

可以通过以下命令安装依赖：

```bash
pip install okx pandas
pip install python-okx --upgrade
```

## 配置文件

在运行机器人之前，您需要配置 API 密钥。请在项目根目录下创建一个名为 `api_key_demo.json` 的文件，并添加以下内容：

```json
{
  "api_key": "your_api_key_here",
  "secret_key": "your_secret_key_here",
  "passphrase": "your_passphrase_here"
}
```

请将 `your_api_key_here`、`your_secret_key_here` 和 `your_passphrase_here` 替换为您在 OKX 获取的实际 API 密钥、秘密和密码短语。

## 使用方法

1. 克隆项目
将项目克隆到本地：

```
git clone https://github.com/your_username/okx_trading_bot.git
cd okx_trading_bot
```

2. 运行程序
使用以下命令运行交易机器人：
```
python main.py
```

## 策略说明
机器人实现了简单的移动平均线交叉策略：

- 买入信号：短期均线从下方穿过长期均线。
- 卖出信号：短期均线从上方穿过长期均线。

策略的默认参数为：

- 短期均线窗口：5
- 长期均线窗口：20

您可以通过修改 `main.py` 中的 moving_average_crossover 函数调整这些参数。

## 注意事项
1. 风险提示

本项目仅供学习和研究使用，实际交易可能存在风险，请谨慎操作。

2. API 权限

确保您的 OKX API 密钥具有以下权限：

- 读取
- 交易

3. 测试环境

默认情况下，机器人运行在模拟交易环境（flag="1"）。如果需要切换到真实交易环境，请将 flag 设置为 "0"。

## 日志示例
日志文件 `trading_bot.log` 会在程序运行时自动生成，记录所有操作和错误信息。以下是日志文件 `trading_bot.log` 的示例内容：

```
2025-05-17 12:00:00,123 - INFO - 交易机器人启动
2025-05-17 12:00:01,456 - INFO - 获取最新价格成功: BTC-USDT 最新价格为 27000.5
2025-05-17 12:00:02,789 - INFO - 无交易信号
2025-05-17 12:00:03,012 - INFO - 产生买入信号
2025-05-17 12:00:03,345 - INFO - 下单成功，订单ID：123456789
2025-05-17 12:00:04,678 - INFO - 币种: BTC, 可用余额: 0.5
2025-05-17 12:00:05,901 - INFO - 币种: USDT, 可用余额: 1000.0
```

## 贡献
欢迎提交问题（Issues）或贡献代码（Pull Requests）来改进此项目。

## 许可证
本项目采用 MIT 许可证。