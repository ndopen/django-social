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
Django带有一个内置的身份验证框架，可以处理用户身份验证，会话，权限和用户组。身份验证系统包括常见用户操作（如登录、注销、密码更改和密码重置）的视图。

身份验证框架位于 `django.contrib.auth` 上，并由其他 **Django** 贡献包使用。请记住，您已经在第 1 章 “构建博客应用进程”中使用了身份验证框架，为博客应用进程创建一个超级用户来访问管理站点。

当您使用 startproject 命令创建新的 Django 项目时，身份验证框架将包含在项目的默认设置中。 它由 `django.contrib.auth` 应用进程和以下两个中间件类组成，这些中间件类位于项目的中间件设置中：
- **AuthenticationMiddleware**: 使用会话将用户与请求相关联
- **SessionMiddleware**: 跨请求处理当前会话

中间件是具有在请求或响应阶段全局执行的方法的类。在本书中，您将多次使用中间件类，并将在第 14 章 “上线”中学习如何创建自定义中间件。

身份验证框架还包括以下模型：
- **User** : 具有基本字段的用户模型;此模型的主要字段是 username，password，email，first_name，last_name和is_active
- **Group** : 用于对用户进行分类的组模型
- **Permission** 用户或组执行某些操作的标志
该框架还包括默认的身份验证视图和窗体，稍后您将使用它们。

### 4.2.1 创建登录视图
我们将通过使用Django身份验证框架来允许用户登录您的网站来开始本节。您的视图应执行以下操作来登录用户：
- 获取用户使用登录表单发布的用户名和密码
- 根据数据库中存储的数据对用户进行身份验证
- 检查用户是否处于活动状态
- 将用户登录到网站并启动经过身份验证的会话

首先，您将创建一个登录表单。在帐户应用进程目录中创建新的 forms.py 文档，并向其中添加以下行：
```python
from django import forms

class LoginForm(forms.Form):
    '''User Login forms'''
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
```

此表单将用于根据数据库对用户进行身份验证。请注意，您可以使用“密码输入”小组件来呈现密码 HTML 元素。这将在 HTML 中包括 **type=“password”**，以便浏览器将其视为密码输入。

编辑帐户应用进程的 **views.py** 文档，并向其中添加以下代码：
```python
from django.shortcuts import render
from django.http import HttpResponse
from .forms import LoginForm
from django.contrib.auth import login, authenticate
# Create your views here.

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()

    return render(request, 'account/login.html', {'form': form})
```
这就是基本登录视图的作用：当使用 GET 请求调用user_login视图时，您可以使用 form = LoginForm（） 实例化一个新的登录窗体，以将其显示在模板中。当用户通过 POST 提交表单时，您可以执行以下操作：
- 使用提交的数据实例化表单 `form = LoginForm(request.POST)`
- 检查表单是否对 `form.is_valid（）` 有效。如果它无效，则在模板中显示表单错误（例如，如果用户未填写其中一个字段）。
- 如果提交的数据有效，则使用 authenticate（） 方法根据数据库对用户进行身份验证。此方法采用请求对象、用户名和密码参数，如果用户已成功通过身份验证，则返回 User 对象，否则返回 None。如果用户尚未经过身份验证，则返回原始 HttpResponse，并显示“登录无效”消息。
- 如果用户已成功通过身份验证，则可以通过访问is_active属性来检查用户是否处于活动状态。这是Django的用户模型的一个属性。如果用户未处于活动状态，则返回显示“已禁用帐户”消息的 HttpRes响应。
- 如果用户处于活动状态，则将用户登录到网站。您可以通过调用 login（） 方法在会话中设置用户，并返回“已成功通过身份验证”消息。

> 注意身份验证和登录之间的区别：authenticate（） 检查用户凭据并返回 User 对象（如果它们正确）;login（） 设置当前会话中的用户。

现在，您需要为此视图创建 URL 模式。在帐户应用进程目录中创建一个新的 urls.py 文档，并向其中添加以下代码：
```python
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login')
]

```
编辑位于书签项目目录中的主 **urls.py** 文档，导入包含并添加帐户应用进程的 URL 模式，如下所示：
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
]
```
现在可以通过 URL 访问登录视图。是时候为此视图创建模板了。由于您没有此项目的任何模板，因此您可以从创建可由登录模板扩展的基本模板开始。在帐户应用进程目录中创建以下文档和目录：
+ templates
 - account
    - login.html
 - base.html

编辑`base.html`模板并向其添加以下代码：
```python
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{% endblock  %}</title>
    <link rel="stylesheet" href="{% static "css/base.css" %}">
</head>
<body>
    <div id="header">
        <span class="logo">Bookmarks</span>
    </div>

    <div id="content">
        {% block content %}{% endblock  %}
    </div>
</body>
</html>
```
这将是网站的**base**模板。与在上一个项目中所做的那样，在主模板中包含 CSS 样式。您可以在本章附带的代码中找到这些静态文档。将帐户应用进程的 static/ 目录从分会的源代码复制到项目中的同一位置，以便您可以使用静态文档。您可以在 https://github.com/PacktPublishing/Django-3-by-Example/tree/master/Chapter04/bookmarks/account/static

base模板定义**title**和**content**块，这些标题栏和内容块可由从中延伸出来的模板填充内容。

让我们填写登录表单的模板。打开 account/login.html 模板并向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}Log-in{% endblock  %}

{% block content %}
    <h1>
        Log-in
    </h1>
    <p>
        Please, use the following form to log-in:
    </p>
    <form method="post">
        {{ form.as_p }}
        {% csrf_token %}
        <p>
            <input type="submit" value="Log-in">
        </p>
    </form>
{% endblock  %}
```
此模板包括在视图中实例化的窗体。由于您的表单将通过 POST 提交，因此您将包含 {% csrf_token %} 模板标记，用于跨站点请求伪造 （CSRF） 保护。您在第 2 章 “使用高级功能增强博客”中了解了 CSRF 保护。

数据库中还没有用户。您需要先创建超级用户，以便能够访问管理站点来管理其他用户。打开命令行并执行`python manage.py createsuperuser`。填写所需的用户名、电子邮件和密码。然后，使用 `python manage.py runserver` 器命令运行开发服务器，并在浏览器中打开 http://127.0.0.1:8000/admin/ 使用刚创建的用户的凭据访问管理站点。您将看到 Django 管理站点，包括 Django 身份验证框架的用户和组模型。

它看起来如下：
![backup  Authentication User Image]()

使用管理站点创建一个新用户，并在浏览器中打开 http://127.0.0.1:8000/account/login/。您应该会看到呈现的模板，包括登录表单：
![account Log-in Form Image]()

现在，提交表单，将其中一个字段留空。在这种情况下，您将看到表单无效并显示错误，如下所示：
![account login error image]()

请注意，某些现代浏览器会阻止您提交包含空白或错误字段的表单。这是因为浏览器根据字段类型和每个字段的限制执行表单验证。在这种情况下，将不会提交表单，浏览器将显示错误字段的错误消息。

如果您输入了不存在的用户或错误的密码，您将收到无效的登录消息。

如果输入有效的凭据，您将收到“已成功通过身份验证”消息，如下所示：
![account login successfully image]()


### 4.2.2 使用 Django 身份验证视图
Django在身份验证框架中包含几个表单和视图，您可以立即使用它们。您创建的登录视图是了解Django中用户身份验证过程的良好练习。但是，在大多数情况下，您可以使用默认的Django身份验证视图。

Django提供了以下基于类的视图来处理身份验证。 它们都位于`django.contrib.auth.views`
- **LoginView**: 处理登录表单并登录用户
- **LogoutView** 注销用户

Django提供了以下视图来处理密码更改：
- **PasswordChangeView** 处理表单以更改用户的密码
- **PasspwrdChangeDoneView** 成功更改密码后将用户重定向到的成功视图

Django还包括以下视图，使用户能够重置其密码：
- **PasswordResetView** 允许用户重置其密码。它使用令牌生成一次性链接，并将其发送到用户的电子邮件帐户。
- **PasswordResetDoneView** 告知用户已向他们发送了一封电子邮件（包括用于重置其密码的链接）。
- **PasswordResetConfirmView** 允许用户设置新密码。
- **PasswordResetCompleteView** 成功重置用户密码后，用户被重定向到的成功视图。

在使用用户帐户创建网站时，上述列表中列出的视图可以为您节省大量时间。视图使用可以重写的默认值，如要呈现的模板的位置或视图要使用的窗体。

您可以在 https://docs.djangoproject.com/en/4.0/topics/auth/default/#all 身份验证视图中获取有关内置身份验证视图的详细信息。

### 4.2.3 登录和注销视图
编辑帐户应用进程的 urls.py 文档，如下所示：
```python
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('login/', views.user_login, name='login'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
```
在上面的代码中，您注释掉了之前创建的user_login视图的 URL 模式，以使用 Django 身份验证框架的 LoginView 视图。您还可以为注销视图添加 URL 模式。

在帐户应用进程的模板目录中创建一个新目录，并将其命名为**registration**。这是 Django 身份验证视图期望您的身份验证模板的默认路径。

django.contrib.admin 模块包括一些用于管理站点的身份验证模板。您已将帐户应用进程放在INSTALLED_APPS设置的顶部，以便 Django 默认使用您的模板，而不是在其他应用进程中定义的任何身份验证模板。

在templates/registeration 目录中创建一个新文档，将其命名为**login.html**，并向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}
    Log-in
{% endblock  %}

{% block content %}
    <h1>Log-in</h1>
    {% if form.errors %}
        <p>
            Your username and password didn't match.
            Please try again.
        </p>
    {% else %}
        <p>
            Please, use the following form to log-in:
        </p>
    {% endif %}

    <div class="login-form">
        <form action="" method="post">
            {{ form.as_p }}
            {% csrf_token %}

            <input type="hidden" name="next" value="{{ next }}">
            <p>
                <input type="submit" value="Log-in">
            </p>
        </form>
    </div>
{% endblock  %}
```
此登录模板与您之前创建的模板非常相似。默认情况下，Django 使用位于**AuthenticationForm**表单。 此表单尝试对用户进行身份验证，如果登录失败，则会引发验证错误。在这种情况下，您可以使用模板中的 {% if form.errors %} 来查找错误，以检查提供的凭据是否错误。

请注意，您添加了一个隐藏的 HTML `<input>`素来提交名为 `next` 的变量的值。当您在请求中传递下一个参数时，此变量首先由登录视图设置（例如，http://127.0.0.1:8000/account/login/?next=/account/）。

`next`参数必须是 URL。如果给出此参数，Django登录视图将在成功登录后将用户重定向到给定的URL。

现在，在注册模板目录中创建一个**logged_out.html**模板，并使其如下所示：
```python
{% extends 'base.html' %}

{% block title %}
    Log-out
{% endblock  %}

{% block content %}
    <h1>Log-out</h1>

    <p>
        You have been successfully logged out.
        You can <a href="{% url 'login' %}">log-in again</a>
    </p>
{% endblock  %}
```
这是Django在用户注销后将显示的模板。

添加用于登录和注销视图的URL和模板后，您的网站现在已准备好供用户使用Django身份验证视图登录。


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