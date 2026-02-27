# AI Image Downloader & Prompt Generator

自动化的电商详情页复刻流程。
利用 火山引擎 TOS 作为云图床，将本地图片转化为公网可以访问的url 链接
Doubao (Seed) 等大模型分析详情页构图详情，
DeepSeek V3 将构图详情转换成nano banana pro的提示词。

## ✨ 功能特点

- 批量复刻整套电商详情页
- 为每一页详情图生成一段nano banana pro 的提示词
- 支持通过 `config.py` 轻松切换 API 密钥和存储配置，实现开箱即用

## 🛠️ 环境配置

- Python 3.12+
- 有效的 DeepSeek API Key
- 有效的 Doubao API Key
- 对象存储访问密钥

## 📦 安装步骤

1. **克隆项目**
   ```bash
第一步：
   git clone https://github.com/yanshizhao/Batch-Reprinting-Process-for-Details-Page-of-Footwear-and-Boots-E-commerce.git

第二步：
   在 product_image 文件夹中新建 detail_page_template 文件夹
   在 detail_page_template 文件夹中创建需要复刻的产品详情页文件夹，为每一套详情页建立一个单独的文件夹
   将 模板详情页(即，想要复刻的模板)放在对应的产品详情页文件夹中，一次支持复刻6页
   
第二步：
   cd <项目文件夹>
   执行 python main.py
