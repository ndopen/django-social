# Chapter 4 构建一个**social**站点
在上一章中，您学习了如何创建**SiteMap**和**Feeds**，并为博客应用构建了**搜索引擎**。在本章中，您将了解如何开发**社交应用**，这意味着用户能够加入在线平台并通过共享内容相互交互。在接下来的几章中，我们将重点介绍如何构建图片共享平台。用户将能够为互联网上的任何图片添加书签并与他人共享。他们还将能够看到他们关注的用户在平台上的活动，并且喜欢/不喜欢他们共享的图片。

在本章中，我们将首先为用户创建一个功能，用于登录，注销，编辑其密码和重置其密码。您将学习如何为用户创建自定义配置文档，并将向您的网站添加社交身份验证。

本章将涵盖以下主题：
- 使用 Django 身份验证框架
- 创建用户注册视图
- 使用自定义配置文档模型扩展用户模型
- 使用 **Python Social Auth** 添加社交身份验证

让我们从创建新项目开始。

## 4.1 创建社交网站项目
您将创建一个社交应用进程，该应用进程将允许用户共享他们在互联网上找到的图像。您需要为此项目生成以下元素：
- 供用户注册、登录、编辑个人资料以及更改或重置密码的身份验证系统
- 一个关注系统，允许用户在网站上相互关注
- 显示共享图像并实现书签的功能，供用户从任何网站共享图像
- 一个活动流，允许用户查看他们关注的人上传的内容

本章将讨论清单上的第一点。

### 4.1.1 开始您的社交网站项目
创建项目目录结构，创建**python**虚拟环境，初始化**git**及配置`.gitignore`
```shell
mkdir -p project && cd project
```

创建python虚拟环境
```shell
python3 -m venv venv .

source venv/bin/activate
```

初始化**git**，配置`.gitignore`文件，关于python的配置预设内容可以在[GitHub官方仓库](https://github.com/github/gitignore)中查询
```shell
git init

touch .gitignore
```

使用以下命令在您的虚拟环境中安装 Django：
```shell
pip install django==4.0.*
```

运行以下命令以创建新项目：
```shell
django-admin startproject bookmarks .
```

初始项目结构已创建。使用以下命令进入项目目录并创建一个名为 account 的新应用进程：
```shell
python manage.py startapp account
```

请记住，将应用进程的名称添加到 settings.py 文档中的INSTALLED_APPS设置，将新应用进程添加到项目中。将其放在INSTALLED_APPS列表中任何其他已安装的应用进程之前：
```python
INSTALLED_APPS = [
    'account.apps.AccountConfig',
]
```
稍后您将定义 Django 身份验证模板。通过将应用进程放在“INSTALLED_APPS”设置中的第一位，可以确保默认情况下将使用身份验证模板，而不是其他应用进程中包含的任何其他身份验证模板。Django在INSTALLED_APPS设置中按应用进程出现的顺序查找模板。

运行下一个命令，将数据库与INSTALLED_APPS设置中包含的默认应用进程的模型同步：
```shell
python manage.py migrate
```

您将看到所有初始 Django 数据库迁移都已应用。接下来，您将使用 Django 身份验证框架将身份验证系统构建到项目中。

此时您的项目文件如下
+ projectroot
    - account
    - bookmarks
    - docker-compose.yml
    - .git
    - .gitignore
    - venv
    - manage.py
    - db.sqlite3


## 4.2 使用 Django 身份验证框架

### 4.2.1 创建登录视图

### 4.2.2 使用 Django 身份验证视图

### 4.2.3 登录和注销视图

### 4.2.4 更改密码视图

### 4.2.5 重置密码视图



## 4.3 用户注册和用户配置文档

### 4.3.1 用户注册

### 4.3.2 扩展用户模型

#### 4.3.2.1 使用自定义用户模型

### 4.3.3 使用消息框架


## 4.4 构建自定义身份验证后端


## 4.5 向网站添加社交身份验证

### 4.5.1 通过 HTTPS 运行开发服务器

### 4.5.2 使用脸书进行身份验证

### 4.5.3 使用推特进行身份验证

### 4.5.4 使用谷歌进行身份验证


## 4.6 概述