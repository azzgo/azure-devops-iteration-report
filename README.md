# Azure Devops Iteration Report

这是我用来查看 Azure Devops 迭代进展的关键报表的简单工具项目

主要由于我项目的诉求，不一定适用于你的项目，可基于你的需求进行修改

效果如下

![image](./images/azure-devops-iteration-report.png)


## 功能介绍

这个项目主要通过累计流程(CFD Cumulative Flow Diagram)和燃尽图(BurnDown Chart)形式展示 Azure Devops 迭代进展

## 开发缘由

- 这里的累计流程图是基于故事点的累计，并且仅统计当前迭代的各阶段栏位的累计值，和通常的累计流程图不一样
   - 这也是我们没有使用 Azure Devops 默认的累计流程图的原因
- 燃尽图则是因为我们使用 Board 的栏位来管理敏捷故事的流转，而不是基于 Azure Devops 的 state，Azure Devops 的燃尽图无法结合项目情况个性化定制

## 使用说明

### 准备

首先你在运行项目前，你需要获取 Azure Devops 的 Personal token
- 获取方式参考[官方文档](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows)

然后你需要复制项目的 `.env.example` 文件到 `.env` 文件, 并修改其中的内容

### 安装

项目使用 [pdm](https://github.com/pdm-project/pdm) 进行依赖管理，进入项目目录下，运行 `pdm install` 即可安装依赖

### 运行

运行 `pdm run start` 即可在 http://localhost:3001 查看报表

### 定制化

如果你的项目和我的敏捷故事板的栏位不一样, 你可以修改 `assemble.py`
