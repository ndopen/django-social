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

现在，您将创建一个新视图，以便在用户登录其帐户时显示仪表板。打开帐户应用进程的 views.py 文档，并向其中添加以下代码：
```python
from django.contrib.auth.decorators import login_required
@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html', {'section': 'dashboard'})
```

使用身份验证框架的login_required修饰器修饰视图。login_required装饰器检查当前用户是否已通过身份验证。如果用户已通过身份验证，它将执行修饰视图;如果用户未经过身份验证，则会将用户重定向到登录 URL，并将最初请求的 URL 作为名为 next 的 GET 参数。

通过执行此操作，登录视图会将用户重定向到他们在成功登录后尝试访问的 URL。请记住，您为此目的以登录模板的形式添加了隐藏的输入。

您还可以定义节变量。您将使用此变量来跟踪用户正在浏览的网站部分。多个视图可能对应于同一部分。这是定义每个视图所对应的部分的简单方法。

接下来，您需要为仪表板视图创建一个模板。在**templates/account**目录中创建一个新文档，并将其命名为**dashboard.html**。让它看起来像这样：
```python
{% extends 'base.html' %}

{% block title %}Dashboard{% endblock  %}

{% block  content%}
    <h1>Dashboard</h1>
    <p>welcome to your Dashboard</p>
{% endblock  %}
```
然后，在帐户应用进程的 urls.py 文档中添加此视图的以下 URL 模式：
```python
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
]
```

编辑项目的 settings.py 文档，并向其中添加以下代码：
```python
LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
```

上述代码中定义的设置如下所示：
- **LOGIN_REDIRECT_URL** 如果请求中不存在下一个参数，则告诉 Django 在成功登录后将用户重定向到哪个 URL
- **LOGIN_URL** 用于重定向用户以登录的 URL（例如，使用login_required装饰器的视图）
- **LOGOUT_URL** 重定向用户以注销的 URL

您使用的是以前使用 path（） 函数的 name 属性定义的 URL 模式的名称。硬编码的 URL（而不是 URL 名称）也可用于这些设置。

让我们总结一下到目前为止您所做的工作：
- 您已将内置的 Django 身份验证登录和注销视图添加到您的项目中
- 您已经为这两个视图创建了自定义模板，并定义了一个简单的仪表板视图，以便在用户登录后重定向用户
- 最后，您已经将 Django 的设置配置为默认使用这些 URL

现在，您将添加指向基本模板的登录和注销链接，以将所有内容放在一起。为此，您必须确定当前用户是否已登录，以便为每种情况显示适当的链接。当前用户由身份验证中间件在 `HttpRequest` 对象中设置。您可以使用请` request.user` 访问它。您将在请求中找到 User 对象，即使该用户未经过身份验证也是如此。未经身份验证的用户在请求中设置为匿名用户的实例。检查当前用户是否经过身份验证的最佳方法是访问只读属性 `is_authenticated`。

编辑您的**base.html**模板，并使用标头 ID 修改`<div>`元素，如下所示：
```python
<div id="header">
    <span class="logo">Bookmarks</span>

    {% if request.user.is_authenticated %}
        <ul class='menu'>
            <li {% if section == 'dashboard' %} class='deshboard' {% endif %}>
                <a href="{% url 'dashboard' %}"> Dashboard</a>
            </li>
            <li {% if section == 'images' %} class='deshboard' {% endif %}>
                <a href="#"> IMAGES </a>
            </li>
            <li {% if section == 'dashboard' %} class='deshboard' {% endif %}>
                <a href="#"> PEOPLE</a>
            </li>
        </ul>
    {% endif %}

    <span class="user">
        {% if request.user.is_authenticated %}
            Hello {{ request.user.first_name }}
            <a href="{% url 'logout' %}"> Logout</a>
        {% else %}
        <a href="{% url 'login' %}">Login</a>
        {% endif %}
    </span>
</div>
```
如上述代码所示，您仅向经过身份验证的用户显示站点的菜单。您还可以检查当前部分以将选定的类属性添加到相应的`<li>`项，以便使用CSS突出显示菜单中的当前部分。显示用户的名字和用于注销的链接（如果用户已通过身份验证），或显示用于以其他方式登录的链接。

现在，在浏览器中打开 http://127.0.0.1:8000/account/login/。您应该会看到登录页面。输入有效的用户名和密码，然后单击“登录”按钮。您应看到以下输出：
![account dashborad image]()

您可以看到“我的仪表板”部分使用 CSS 突出显示，因为它具有选定的类。由于用户已通过身份验证，因此用户的名字将显示在标头的右侧。单击注销链接。您应该看到以下页面：
![logout page images]()

在上述屏幕截图的页面中，您可以看到用户已注销，因此，不再显示网站的菜单。现在，标题右侧的链接显示“登录”。

> 如果您看到 Django 管理站点的已注销页面，而不是您自己的注销页面，请检查项目的INSTALLED_APPS设置，并确保 `django.contrib.admin` 在 `account.apps.AccountConfig` 应用进程之后出现。两个模板都位于相同的相对路径中，Django模板加载进程将使用它找到的第一个模板。

### 4.2.4 更改密码视图
您还需要您的用户能够在登录到您的网站后更改其密码。您将集成Django身份验证视图以更改密码。

打开帐户应用进程的 **urls.py** 文档，并向其添加以下 URL 模式：
```python
urlpatterns = [
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]
```
`PasswordChangeView`视图将处理表单以更改密码，而`PasswordChangeDoneView`视图将在用户成功更改其密码后显示一条成功消息。让我们为每个视图创建一个模板。

在帐户应用进程的*templates/registration*目录中添加一个新文档，并将其命名为**password_change_form.html**。向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}Change your Password{% endblock  %}

{% block content %}
    <h1>Change Your Password</h1>
    <p>use the form below change your password</p>
    <form method="post">
        {{ form.as_p }}
        <input type="submit" value="Change">
        {% csrf_token %}
    </form>
{% endblock  %}
```
**password_change_form.html**模板包含用于更改密码的表单。

现在，在同一目录中创建另一个文档，并将其命名为**password_change_done.html** 向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}Password changed{% endblock  %}

{% block content %}
    <h1>Password Changed</h1>
    <p>Your Password has been successfully changed.</p>
{% endblock  %}
```
**password_change_done.html**模板仅包含用户成功更改其密码时显示的成功消息。

在浏览器中打开 http://127.0.0.1:8000/account/password_change/。 如果您尚未登录，浏览器会将您重定向到登录页面。成功通过身份验证后，您将看到以下更改密码页面
![account PasswordChangeForm Image]()

在表单中填写您的当前密码和新密码，然后单击“更改”按钮。您将看到以下成功页面：
![Account PasswordChange SuccessFully Image]()
注销并使用新密码再次登录，以验证一切是否按预期工作。

### 4.2.5 重置密码视图
将以下用于Password reset的 URL 模式添加到帐户应用进程的 **urls.py** 文档中：
```python
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
```
在帐户应用进程**templates/registration/**中添加一个新文档，并将其命名为**password_reset_form.html**。向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}
    Reset Your Password
{% endblock  %}

{% block content %}
    <h1>Rest Your Password</h1>
    <p>Enter your e-mail address to obtain a new password.</p>

    <form method="post">
        {{ form.as_p }}
        <input type="submit" value="Send e-mail">
        {% csrf_token %}
    </form>
{% endblock  %}
```
现在，在同一目录中创建另一个文档，并将其命名为**password_reset_email**。 嗯。向其添加以下代码：
```python
Someone asked for password reset for email {{ email }}. Follow the link below:

{{ protocol }}://{{ domain }}{% url "password_reset_confirm" uidb64=uid token=token %}

Your username, in case you've forgotten: {{ user.get_username }}
```
password_reset_email.html模板将用于呈现发送给用户以重置其密码的电子邮件。它包括由视图生成的重置令牌。

在同一目录中创建另一个文档，并将其命名为**password_reset_done.html**。 向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}
    Reset your password
{% endblock  %}

{% block content %}
    <h1>Reset your password</h1>
    <p>We've emailed you instructions for setting your password.</p>
    <p>If you don't receive an email, please make sure you've entered the address you registered with.</p>
{% endblock  %}
```
在同一目录中创建另一个模板，并将其命名为**password_reset_confirm.html**。向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}
    Reset your Password
{% endblock  %}

{% block content %}
    <h1>Reset Your Password</h1>
    {% if validlink %}
        <p>please enter your new password wtice.</p>
        <form method="post">
            {{ form.as_p }}
            {% csrf_token %}
            <p><input type="submit" value="Change My Password"></p>
        </form>
    {% else %}
        <p>The password reset link was invalid, possibly because it has already been used. Please request a new password reset.</p>
    {% endif %}
{% endblock  %}
```
在此模板中，您可以通过检查有效链接变量来检查重置密码的链接是否有效。视图密码重置确认视图检查 URL 中提供的令牌的有效性，并将有效链接变量传递给模板。如果链接有效，则显示用户密码重置表单。 仅当用户具有有效的重置密码链接时，他们才能设置新密码。

创建另一个模板并将其命名为**password_reset_complete.html**。在其中输入以下代码：
```python
{% extends 'base.html' %}

{% block title %}
    Password reset
{% endblock  %}

{% block content %}
    <h1>Password set</h1>
    <p>Your password has been set. You can
    <a href="{% url "login" %}">log in now</a></p>
{% endblock  %}

```
最后，编辑帐户应用进程的 **registration/login.html** 模板，并在 `<form>` 元素后添加以下代码：
```python
<p><a href="{% url "password_reset"%}">Forgotten your password?</a></p>
```
现在，在浏览器中打开 http://127.0.0.1:8000/account/login/，然后单击 **Forgotten your password?**链接。您应该看到以下页面：
![LoginPage Forgotten Image]()

此时，您需要将简单邮件传输协议（SMTP）配置添加到项目的 settings.py 文档中，以便Django能够发送电子邮件。您在第 2 章 “使用高级功能增强博客”中学习了如何将电子邮件设置添加到项目中。但是，在开发过程中，您可以将Django配置为将电子邮件写入标准输出，而不是通过SMTP服务器发送。Django提供了一个电子邮件后端，用于将电子邮件写入控制台。编辑项目的 settings.py 文档，然后添加以下行：
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
`EMAIL_BACKEND`设置指示用于发送电子邮件的类。
```shell
返回浏览器，输入现有用户的电子邮件地址，然后单击“SEND E-MAIL”按钮。您应该看到以下页面：
[Reset Password done Page image]()

查看运行开发服务器的控制台。您将看到生成的电子邮件，如下所示：
```python
System check identified no issues (0 silenced).
September 19, 2022 - 14:42:24
Django version 4.0.7, using settings 'bookmarks.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
[19/Sep/2022 14:42:26] "GET /account/password_reset/ HTTP/1.1" 200 1077
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Password reset on 127.0.0.1:8000
From: webmaster@localhost
To: admin@admin.com
Date: Mon, 19 Sep 2022 14:42:39 -0000
Message-ID: <166359855906.2745.14501718873517628110@sihairong.localdomain>

Someone asked for password reset for email admin@admin.com. Follow the link below:

http://127.0.0.1:8000/account/reset/MQ/bc0673-62bfb42684ced21f101d0d6f8d459076/

Your username, in case you've forgotten: admin
```

电子邮件将使用您之前创建的**password_reset_email.html**模板呈现。重置密码的URL包括由Django动态生成的令牌。

复制 URL 并在浏览器中打开它。您应该看到以下页面：
![Reset Password Image]()

用于设置新密码的页面使用`password_reset_confirm.html`模板。填写新密码，然后单击**CHANGE MY PASSWORD**按钮。Django创建一个新的哈希密码并将其保存在数据库中。您将看到以下成功页面：
![Reset Password done Image]()

现在，您可以使用新密码重新登录您的帐户。

用于设置新密码的每个令牌只能使用一次。如果再次打开收到的链接，您将收到一条消息，指出令牌无效。

现在，您已经将 Django 身份验证框架的视图集成到您的项目中。这些视图适用于大多数情况。但是，如果需要其他行为，则可以创建自己的视图。

Django还提供了您刚刚创建的身份验证URL模式。您可以注释掉已添加到帐户应用进程的 urls.py 文档中的身份验证 URL 模式，并改为包含 `django.contrib.auth.urls`，如下所示：
```python
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
]
```

您可以在  https://github.com/django/django/blob/stable/4.0.x/django/contrib/auth/urls.py 中看到身份验证 URL 模式。

## 4.3 用户注册和用户配置文档
现有用户现在可以登录、注销、更改其密码和重置其密码。现在，您需要构建一个视图以允许访问者创建用户帐户。

### 4.3.1 用户注册
让我们创建一个简单的视图，以允许用户在您的网站上注册。最初，您必须创建一个表单来让用户输入用户名，其真实姓名和密码。
编辑位于帐户应用进程目录中的 **forms.py** 文档，并向其中添加以下代码：
```python
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']
```
您已经为用户模型创建了一个models form。在form中，仅包含模型的username、first_name和email字段。这些字段将根据其相应的模型字段进行验证。例如，如果用户选择已存在的用户名，则会收到验证错误，因为用户名是用 unique=True 定义的字段。

您添加了两个附加字段（password 和 password2），供用户设置并确认密码。您已经定义了一个 `clean_password2（）` 方法来检查第二个密码与第一个密码，如果密码不匹配，则不让表单验证。当您通过调用表单的 `is_valid（）` 方法验证表单时，将完成此检查。您可以为任何表单域提供`clean_<fieldname>()` 方法，以便清理值或引发特定字段的表单验证错误。表单还包括一个通用的 `clean（）` 方法来验证整个表单，这对于验证相互依赖的字段非常有用。在这种情况下，您可以使用特定于字段的 `clean_password2（）` 验证，而不是重写form的 `clean（）` 方法。这样可以避免覆盖 `ModelForm` 从模型中设置的限制中获取的其他特定于字段的检查（例如，验证用户名是否唯一）。

Django还提供了一个你可以使用的`UserCreationForm`，它驻留在`django.contrib.auth.forms`中，与你创建的表单非常相似。

编辑帐户应用进程的 **views.py** 文档，并向其中添加以下代码：
```python
from .forms import LoginForm, UserRegistrationForm

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()

            return render(request, 'account/register_done.html', {'new_user': new_user})

    else:
        user_form = UserRegistrationForm()
    
    return render(request, 'account/register.html', {'user_form': user_form})
```
创建用户帐户的视图非常简单。出于安全原因，您不是保存用户输入的原始密码，而是使用处理哈希的用户模型的 `set_password（）` 方法。

现在，编辑帐户应用进程的 **urls.py** 文档，并添加以下 URL 模式：
```python
urlpatterns = [
    path('register/', views.register, name='register'),
]
```

最后，在**account/templates**目录中创建一个新模板，将其命名为**register.html**，并使其如下所示：
```python
{% extends 'base.html' %}

{% block title %}
    Register Your Account
{% endblock  %}

{% block content %}
    <h1>Register Your Account</h1>
    <p>please sign up using the following form:</p>

    <form method="post">
        {{ user_form.as_p }}
        {% csrf_token %}
        <p>
            <input type="submit" value="Create my account">
        </p>
    </form>
{% endblock  %}
```

在同一目录中添加模板文档，并将其命名为**register_done.html**。 向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}
    Welcome
{% endblock  %}

{% block content %}
    <h1>Welcome {{ new_user.first_name }}!</h1>
    <p>Your account has been successfully created. Now you can <a href="{% url "login" %}">log in</a>.</p>
{% endblock  %}
```

现在在浏览器中打开 http://127.0.0.1:8000/account/register/。您将看到您创建的注册页面：
![Account RegisterPage image]()

填写新用户的详细信息，然后单击**CREATE MY ACCOUNT**按钮。 如果所有字段都有效，则将创建用户，并且您将收到以下成功消息：
![Account Register succees image]()

单击登录链接并输入您的用户名和密码，以验证您是否可以访问您的帐户。

您还可以在登录模板中添加注册链接。编辑 registration/login.html 模板并找到以下行：
```python
<p>Please, use the following form to log-in. If you don't have an account <a href="{% url "register" %}">register here</a></p>
```

您已使注册页面可从登录页面访问。
### 4.3.2 扩展用户模型
当您必须处理用户帐户时，您会发现Django身份验证框架的用户模型适用于常见情况。但是，用户模型附带了非常基本的字段。您可能希望扩展它以包含其他数据。执行此操作的最佳方法是创建一个配置文档模型，其中包含所有其他字段以及与 Django 用户模型的一对一关系。 一对一关系类似于参数为 unique=True 的外键字段。关系的反面是与相关模型的隐式一对一关系，而不是多个元素的管理器。 从关系的每一端，检索单个相关对象。

编辑帐户应用进程的 models.py 文档，并向其中添加以下代码：
```python
from django.conf import settings
from django.db import models

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='user/%Y/%m/%d/', blank = True)

    def __str__(self):
        return f'profile for user {self.user.username}'
```

> 为了使代码保持通用，请使用 `get_user_model（）` 方法检索用户模型，并使用AUTH_USER_MODEL设置在定义模型与用户模型的关系时引用它，而不是直接引用身份验证用户模型。有关此内容的详细信息，请参阅 https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#django.contrib.auth.get_user_model

用户一对一字段允许您将配置文档与用户相关联。将 CASCADE 用于on_delete参数，以便在删除用户时也删除其相关配置文档。照片字段是图像字段字段。您需要安装Pillow库来处理图像。通过在 shell 中运行以下命令来安装 Pillow：
```shell
pip install pillow
```

要使 Django 能够提供用户通过开发服务器上传的媒体文档，请将以下设置添加到项目的 settings.py 文档中：
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
```
**MEDIA_URL**是用于提供用户上传的媒体文档的基本URL，**MEDIA_ROOT**是用户所在的本地路径。您可以相对于项目路径动态生成路径，以使代码更加通用。

现在，编辑书签项目的主 urls.py 文档并修改代码，如下所示：
```python
from django.conf import settings

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
```
这样，Django开发服务器将负责在开发期间（即当DEBUG设置设置为True时）提供媒体文档。

> static（） 帮助进程函数适用于开发，但不适用于生产用途。Django在提供静态文档方面效率非常低下。永远不要在生产环境中使用 Django 提供静态文档。您将在第 14 章 “上线”中学习如何在生产环境中提供静态文档。
打开 shell 并运行以下命令，为新模型创建数据库迁移,同步数据库：
```shell
python manage.py makemigrations
python manage.py migate
```

编辑帐户应用进程的 **admin.py** 文档，并在管理站点中注册配置文档模型，如下所示：
```python
from django.contrib import admin
from account.models import Profile

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'photo']
```

使用 python manage.py 运行服务器命令运行开发服务器，并在浏览器中打开 http://127.0.0.1:8000/admin/。现在，您应该能够在项目的管理站点中看到配置文档模型，如下所示：
![Backup Profile Edit image]()

接下来，您将允许用户在网站上编辑其个人资料。将以下导入和模型表单添加到帐户应用进程的 forms.py 文档中：
```python
from django.contrib.auth.models import User
from .models import Profile

class UserEditForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileEditForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ('date_of_birth', 'photo')

```

这些forms如下：
    - **UserEditForm**: 这将允许用户编辑他们的**first_name**，**last_name**和**email**，这些是内置Django用户模型的属性。
    - **ProfileEditForm**: 这将允许用户编辑保存在自定义配置文档模型中的配置文档数据。用户将能够编辑他们的**birth date**并上传其个人资料的**photo**。

编辑帐户应用进程的 **views.py** 文档并导入配置文档模型，如下所示：
```python
from .forms import LoginForm, ProfileEditForm, UserEditForm, UserRegistrationForm
from .models import Profile
```
然后，将以下行添加到`new_user.save()` 下方的**register**视图中：
```python
Profile.objects.create(user = new_user)
```
当用户在您的网站上注册时，您将创建一个与他们关联的空个人资料。您应使用管理站点为之前创建的用户手动创建配置文档对象。

现在，您将允许用户编辑其个人资料。将以下代码添加到同一文档中：
```python
@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request, 'account/edit.html', {'user_form':user_form, 'profile_form':profile_form})
```
使用login_required装饰器，因为用户必须经过身份验证才能编辑其配置文档。在这种情况下，您将使用两个模型窗体：用户编辑窗体用于存储内置用户模型的数据，以及“配置文档编辑窗体”用于在自定义配置文档模型中存储其他配置文档数据。若要验证提交的数据，请执行两个窗体的 `is_valid（）` 方法。如果两个表单都包含有效数据，则保存这两个表单，并调用 `save（）` 方法来更新数据库中的相应对象。

将以下 URL 模式添加到帐户应用进程的 urls.py 文档中：
```python
path('edit/', views.edit, name='edit')
```

最后，在**templates/account/**中为此视图创建一个模板，并将其命名为**edit.html**。向其添加以下代码：
```python
{% extends 'base.html' %}

{% block title %}
    Edit your account
{% endblock  %}

{% block content %}
    <h1>Edit your account</h1>
    <p>You can edit your account using the following form:</p>

    <form method="post" enctype="multipart/form-data">
        {{user_form.as_p}}
        {{profile.as_p}}
        {% csrf_token %}
        <p><input type="submit" value="save changes"></p>
    </form>
{% endblock  %}
```

在上面的代码中，您可以在表单中包含 `enctype="multipart/form-data"`以启用文档上传。您可以使用 HTML 表单提交`user_form`和`profile_form`表单。

从 URL http://127.0.0.1:8000/account/register/ 注册新用户并打开 http://127.0.0.1:8000/account/edit/。您应该看到以下页面：
![Account Edit Page]()

您还可以编辑仪表板页面，并包括指向编辑配置文档和更改密码页面的链接。打开 account/dashboard.html 模板并找到以下行：
```python
<p>Welcome to your dashboard.</p>
```
将前面的行替换为以下行：
```python
{% extends 'base.html' %}

{% block title %}Dashboard{% endblock  %}

{% block  content%}
    <h1>welcome to your dashboard</h1>
    <p>Welcome to your dashboard. You can <a href="{% url "edit" %}">edit your profile</a> or <a href="{% url "password_change" %}">change your password</a>.</p>
{% endblock  %}
```
用户现在可以访问表单以从其仪表板编辑其个人资料。在浏览器中打开 http://127.0.0.1:8000/account/ 并测试新链接以编辑用户的个人资料：
![dashboard pages]()

#### 4.3.2.1 使用自定义用户模型
Django还提供了一种用自己的自定义模型替换整个用户模型的方法。您的用户类应继承自 Django 的 `AbstractUser` 类，该类将默认用户的完整实现作为抽象模型提供。您可以在  https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#substituting-a-custom-user-model 自定义用户模型中阅读有关此方法的更多信息。

使用自定义用户模型将为您提供更大的灵活性，但它也可能导致与Django的身份验证用户模型交互的可插入应用进程的集成更加困难。

### 4.3.3 使用消息框架
当用户允许您的平台交互时，在许多情况下，您可能希望通知他们其操作的结果。Django有一个内置的消息框架，允许您向用户显示一次性通知。

消息框架位于 `django.contrib.messages` 中，当您使用 `python manage.py` 启动项目创建新项目时，该框架包含在 **settings.py** 文档的默认`INSTALLED_APPS`列表中。您会注意到，您的设置文档包含一个名为 `django.contrib.messages.middleware.MessageMiddleware`,的中间件。 消息中间件设置中的中间件。

**messages frameword**提供了一种向用户添加messages的简单方法。 默认情况下，消息存储在 Cookie 中（回退到会话存储），并显示在用户的下一个请求中。您可以通过导入消息模块并使用简单的快捷方式添加新消息来在视图中使用消息框架，如下所示：
```python
from django.contrib import messages
messages.error(request, 'Something went wrong')
```

您可以使用 add_message（） 方法或以下任何快捷方法创建新邮件：
    - **success** 操作成功后显示的成功消息
    - **info** 信息性消息
    - **warning** 有些事情还没有失败，但可能很快就会失败
    - **error** 操作不成功或失败
    - **debug** 调试将在生产环境中删除或忽略的消息

让我们向您的平台添加消息。由于 **message frameword** 全局应用于项目，因此您可以在`base templates`中显示用户的消息。 打开帐户应用进程的**base.html**模板，并在具有**header** ID 的 <div> 元素和具有内容 ID 的 <div /> 元素之间添加以下代码：
```python
    {% if messages %}
        <ul class="messages">
            {% for message in messages %}
                <li class="{{ message.tags }}">
                    {{ message | safe}}
                    <a href="#" class="close">x</a>
                </li>
            {% endfor %}
        </ul>
{% endif %}
```

**messages frameword** 包括context处理器 `django.contrib.messages.context_processors.messages`，它将消息变量添加到request context中。您可以在项目的**tempaltes**设置的`context_processors`列表中找到它。您可以使用模板中的 messages 变量向用户显示所有现有消息。

> 上下文处理器是一个 Python 函数，它将请求对象作为参数，并返回添加到请求上下文中的字典。您将在第 7 章 “构建在线商店”中学习如何创建自己的上下文处理器。
让我们修改您的编辑视图以使用消息框架。编辑帐户应用进程的 views.py 文档，导入消息，并使编辑视图如下所示：
```python
from django.contrib import messages

if user_form.is_valid() and profile_form.is_valid():
    user_form.save()
    profile_form.save()
    messages.success(request, 'Profile updated successfully')

else:
    messages.error(request, "Error updating your profile")
```

当用户成功更新其配置文档时，将添加成功消息。如果任何表单包含无效数据，请改为添加错误消息。

在浏览器中打开 http://127.0.0.1:8000/account/edit/ 并编辑您的个人资料。成功更新配置文档后，应看到以下消息：
![Page Message success image]()

当数据无效时，例如，如果出生日期字段的日期格式不正确，则应看到以下消息：
![Page Message error image]()

您可以在以下位置了解有关消息框架的更多信息：https://docs.djangoproject.com/en/4.0/ref/contrib/messages/

## 4.4 构建自定义身份验证后端
Django允许您根据不同的来源进行身份验证。`AUTHENTICATION_BACKENDS`设置包括项目的身份验证后端列表。默认情况下，此设置设置如下：
```python
['django.contrib.auth.backends.ModelBackend']
```

默认的模型后端使用用户模型根据数据库对用户进行身份验证。这将适合您的大多数项目。但是，您可以创建自定义后端，以针对其他源**Lightweight Directory Access Protocol (LDAP)**对用户进行身份验证。

您可以在以下位置阅读有关自定义身份验证的更多信息 https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#other-authentication-sources

每当您使用 `django.contrib.auth` 的 `authenticate（）` 函数时，Django 都会尝试逐个针对 **AUTHENTICATION_BACKENDS** 中定义的每个后端对用户进行身份验证，直到其中一个后端成功对用户进行身份验证。仅当所有后端都无法进行身份验证时，用户才会在站点中进行身份验证。

Django提供了一种简单的方法来定义自己的身份验证后端。身份验证后端是提供以下两种方法的类：
- authenticate() 它将请求对象和用户凭据作为参数。它必须返回与这些凭据匹配的用户对象（如果凭据有效）或“无”。请求参数是 HttpRequest 对象，如果未提供该参数来进行身份验证，则为“无”。
- get_user() 这将采用用户 ID 参数，并且必须返回用户对象。

创建自定义身份验证后端就像编写实现这两种方法的 Python 类一样简单。让我们创建一个身份验证后端，让用户使用其电子邮件地址而不是用户名在您的站点中进行身份验证。

在帐户应用进程目录中创建一个新文档，并将其命名为 **authentication.py**。向其添加以下代码：
```python
from urllib import request
from django.contrib.auth.models import User

class EmailAuthBackend(object):

    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            
            if user.check_password(password):
                return user
            return None
        
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)

        except User.DoesNotExist:
            return None
```

上面的代码是一个简单的身份验证后端。authenticate（） 方法接收请求对象以及用户名和密码可选参数。您可以使用不同的参数，但您可以使用用户名和密码来使您的后端立即使用身份验证框架视图。上述代码的工作原理如下：
- authenticate() 您尝试检索具有给定电子邮件地址的用户，并使用用户模型的内置check_password（） 方法检查密码。此方法处理密码哈希，以将给定的密码与数据库中存储的密码进行比较。
- get_user() 通过user_id参数中提供的 ID 获取用户。Django 使用对用户进行身份验证的后端在用户会话期间检索 User 对象。

编辑项目的 settings.py 文档并添加以下设置：
```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'account.authentication.EmailAuthBackend',
]
```

在前面的设置中，将保留用于使用用户名和密码进行身份验证的默认 ModelBackend，并包括您自己的基于电子邮件的身份验证后端。

现在，在浏览器中打开 http://127.0.0.1:8000/account/login/。请记住，Django将尝试针对每个后端对用户进行身份验证，因此现在您应该能够使用您的用户名或电子邮件帐户无缝登录。 将使用 ModelBack 端身份验证后端检查用户凭据，如果未返回任何用户，将使用自定义 EmailAuthBackend 后端检查凭据。

> AUTHENTICATION_BACKENDS设置中列出的后端的顺序很重要。如果相同的凭据对多个后端有效，Django 将在第一个成功对用户进行身份验证的后端停止。

## 4.5 向网站添加社交身份验证
您可能还希望使用 Facebook、Twitter 或 Google 等服务向您的网站添加社交身份验证。Python Social Auth 是一个Python模块，可简化向网站添加社交身份验证的过程。使用此模块，您可以让用户使用其他服务中的帐户登录您的网站。

社交身份验证是一项广泛使用的功能，它使用户的身份验证过程更加容易。您可以在 https://github.com/python-social-auth 中找到此模块的代码。

该模块带有用于不同 Python 框架（包括 Django）的身份验证后端。要通过 pip 安装 Django 包，请打开控制台并运行以下命令：
```shell
pip install social-auth-app-django
```

然后将social_django添加到项目 settings.py 文档中的INSTALLED_APPS设置中：
```python
INSTALLED_APPS = [
    #...
    'social_django',
]
```
这是将Python社交身份验证添加到Django项目的默认应用进程。现在运行以下命令以将 Python 社交身份验证模型与数据库同步
```shell
python manage.py migrate
```

Python社交身份验证包括多个服务的后端。您可以在以下位置查看所有后端的列表 https://python-social-auth.readthedocs.io/en/latest/backends/index.html#supported-backends

让我们包括 Facebook、Twitter和 Google 身份验证后端。

您需要将社交登录 URL 模式添加到项目中。打开主网址。 书签项目的 urls.py 文档，并包含social_django URL 模式，如下所示：
```python
path('social-auth/', include('social_django.urls', namespace='social')),
```

一些 social 服务不允许在身份验证成功后将用户重定向到127.0.0.1或localhost;他们想要一个域名。为了使社交身份验证正常工作，您将需要一个域。要在 Linux 或 macOS 上解决此问题，请编辑您的 /etc/hosts 文档并向其添加以下行：
```txt
127.0.0.1 mysite.test
```

要验证您的主机名关联是否有效，请使用`python manage.py runserver` 启动开发服务器，然后在浏览器中打开 http://mysite.com:8000/account/login/。您将看到以下错误：
![](ALLOWED_HOSTS error image)

Django 使用“ALLOWED_HOSTS”设置控制能够为您的应用进程提供服务的主机。这是一项安全措施，可防止 HTTP 主机标头攻击。 Django将只允许此列表中包含的主机为应用进程提供服务。您可以在  https://docs.djangoproject.com/en/4.0/ref/settings/#allowed-hosts 了解有关ALLOWED_HOSTS设置的更多信息.
```python
ALLOWED_HOSTS = ['mysite.com', 'localhost', '127.0.0.1']
```

### 4.5.1 通过 HTTPS 运行开发服务器
您将要使用的某些社交身份验证方法需要 HTTPS 连接。传输层安全性 （TLS） 协议是通过安全连接为网站提供服务的标准。TLS 前身是安全套接字层 （SSL）。

尽管 SSL 现已弃用，但在多个库和联机文档中，您可以找到对术语 TLS 和 SSL 的引用。Django开发服务器无法通过HTTPS为您的网站提供服务，因为这不是它的预期用途。为了测试通过HTTPS为您的网站提供服务的社交身份验证功能，您将使用Django扩展包的运行服务器Plus扩展。Django扩展是Django的自定义扩展的第三方集合。请注意，这绝不是您应该在真实环境中为您的网站提供服务的方法;这是一个开发服务器。

使用以下命令安装 Django 扩展：
```shell

```

现在，您需要安装 Werkzeug，其中包含运行服务器增强扩展所需的调试器层。使用以下命令进行安装：
```shell
pip install werkzeug
```

最后，使用以下命令安装 pyOpenSSL，这是使用运行服务器增强版的 SSL/TLS 功能所必需的：
```shell
pip install pyOpenSSL
```

编辑项目的 settings.py 文档，并将 Django 扩展名添加到INSTALLED_APPS设置中，如下所示：
```python
INSTALLED_APPS = [
    # ...
    'django_extensions',
]
```

使用 Django 扩展提供的管理命令runserver_plus运行开发服务器，如下所示：
```shell
python manage.py runserver_plus --cert-file cert.crt
```

为 SSL/TLS 证书的runserver_plus命令提供文档名。Django扩展将自动生成密钥和证书。

在浏览器中打开 https://mysite.com:8000/account/login/。现在，您正在通过 HTTPS 访问您的网站。您的浏览器可能会显示安全警告，因为您使用的是自行生成的证书。如果是这种情况，请访问浏览器显示的高级信息并接受自签名证书，以便浏览器信任该证书。

现在，您可以在开发期间通过HTTPS为您的网站提供服务，以便使用脸书，推特和谷歌测试社交身份验证。
### 4.5.2 使用FACEBOOL进行身份验证

### 4.5.3 使用推特进行身份验证

### 4.5.4 使用谷歌进行身份验证


## 4.6 概述
以上社交登陆功能未完成（ssl配置出错），先暂时停止开发；

# Chapter 5 在您的网站上分享内容

## 5.1 创建图像书签网站
在本章中，您将学习如何允许用户为在其他网站和您的网站上找到的图像添加书签和共享这些图像。为此，您需要执行以下任务：
1. 定义用于存储图像及其信息的模型
2. 创建表单和视图以处理图像上传
3. 为用户构建一个系统，以便能够发布他们在外部网站上找到的图像

首先，使用以下命令在您的书签项目目录中创建一个新应用进程：
```shell
django-admin startapp images
```

将新应用进程添加到 settings.py 文档中的 INSTALLED_APPS 设置中，如下所示：
```python
INSTALLED_APPS = [
    #
    'images.apps.ImagesConfig'
]
```

您已在项目中激活图像应用进程。

### 5.1.1 构建**Images**模型
编辑图像应用进程的 models.py 文档，并向其中添加以下代码：
```python
from django.conf import settings
from django.db import models

class Images(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='images_created', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    sulg = models.SlugField(max_length=200, blank=True)
    url = models.URLField()
    images = models.ImageField(upload_to='images/%Y/%m/%d/')
    description = models.TextField(blank=True)
    created = models.DateField(auto_now_add=True, db_index=True)


    def __str__(self):
        return self.title
```

这是您将用于存储从不同站点检索到的图像的模型。让我们看一下此模型的字段：
- **user** 这表示为此图像添加书签的 User 对象。这是一个外键字段，因为它指定了一对多关系：用户可以发布多个图像，但每个图像由单个用户发布。对on_delete参数使用 CASCADE，以便在删除用户时也删除相关图像。

- **title** 图像的标题。

- **slug** 一个简短的标签，仅包含字母，数字，下划线或连字符，用于构建漂亮的SEO友好URL。

- **url** 此图像的原始 URL。

- **images** 图像文档。

- **description** 图像的可选说明。

- **created** 指示在数据库中创建对象的日期和时间。由于您使用的auto_now_add，因此在创建对象时会自动设置此日期时间。您可以使用db_index=True，以便 Django 在数据库中为此字段创建一个索引。

您将覆盖 Image 模型的 save（） 方法，以根据标题字段的值自动生成辅助信息区字段。导入 slugify（） 函数并将 save（） 方法添加到图像模型中，如下所示：
```python
from django.utils.text import slugify

def save(self, *args, **kwargs):
    if not self.sulg:
        self.sulg = slugify(self.title)
    super().save(*args, **kwargs)
```
在上面的代码中，您可以使用 Django 提供的 slugify（） 函数在未提供 slug 时自动生成给定标题的图像数据域。然后，保存该对象。通过自动生成辅助信息块，用户不必为每个图像手动输入数据块。

### 5.1.2 创建多对多关系
接下来，您将向 Image 模型添加另一个字段，以存储喜欢图像的用户。在这种情况下，您将需要多对多关系，因为用户可能喜欢多个图像，并且每个图像可以被多个用户喜欢。

将以下字段添加到图像模型：
```python
users_link = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='images_linkd', blank=True)
```
当您定义**ManyToManyFiled**，Django使用两个模型的主键创建一个中间连接表。**ManyToManyField**可以在两个相关模型中的任何一个中定义。

与外键字段一样，**ManyToManyField**的*related_name*属性允许您将关系从相关对象命名回此对象。**ManyToManyField**字段提供了一个Many-To-Many manager，允许您检索相关对象（如 image.users_like.all（），或从用户对象（如 user.images_liked.all（）） 中获取它们。

您可以在以下位置了解有many-to-many关系的更多信息:[https://docs.djangoproject.com/en/4.0/topics/db/examples/many_to_many/][1]

打开命令行并运行以下命令以创建初始迁移：
```shell
python manage.py makemigrations images
```

现在运行以下命令以应用迁移：
```shell
python manage.py migrate images
```

### 5.1.3 在管理站点中注册映像模型
编辑*Images*应用进程的 admin.py 文档，并将*Images*模型注册到管理站点，如下所示：
```python
from django.contrib import admin

from .models import Images

# Register your models here.
@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ['title', 'sulg', 'images', 'created']
    list_filter = ['created']

```

使用以下命令启动开发服务器：
```shell
python manage.py runserver
```

在浏览器中打开 https://127.0.0.1:8000/admin/，您将在管理站点中看到图像模型。

## 5.2 从其他网站发布内容
您将允许用户为来自外部网站的图像添加书签。用户将提供图像的 URL、标题和可选说明。应用进程将下载Images并在数据库中创建新的 Image 对象。

让我们首先构建一个表单来提交新图像。在 Images 应用进程目录中创建一个新的 forms.py 文档，并向其中添加以下代码：
```python
from django import forms
from .models import Images

class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Images
        fields = ('title', 'url', 'description')
        widgets = {
            'url':forms.HiddenInput,
        }
```

正如您将在前面的代码中注意到的那样，此窗体是从图像模型构建的 ModelForm 窗体，仅包括标题、URL 和描述字段。用户不会直接在表单中输入图像 URL。相反，您将为他们提供一个JavaScript工具，以从外部站点中选择图像，并且您的表单将接收其URL作为参数。您可以覆盖 url 字段的默认构件以使用 `HiddenInput` 构件。此小部件呈现为具有 type=“hidden” 属性的 HTML 输入元素。之所以使用此微件，是因为您不希望此字段对用户可见。

### 5.2.1 清理表单域
为了验证提供的图像 URL 是否有效，您将检查文档名是否以 .jpg 或.jpeg扩展名结尾，以仅允许 JPEG 文档。正如你在上一章中看到的，Django 允许你定义表单方法来使用 clean_<fieldname>（） 约定来清理特定字段。当您在窗体实例上调用 is_valid（） 时，将针对每个字段（如果存在）执行此方法。在 clean 方法中，您可以根据需要更改字段的值或引发此特定字段的任何验证错误。将以下方法添加 ImageCreateForm：
```python
def clean_url(self):
    url = self.cleaned_data['url']
    valid_extensions = ['jpg', 'jpeg']
    extensions = url.rsplit('.', 1)[1].lower()
    if extensions not in valid_extensions:
        raise forms.ValidationError('The given URL does not match valid image extensions.')

    return url
```
在上面的代码中，定义了一个 clean_url（） 方法来清理 url 字段。代码的工作原理如下：
- 您可以通过访问表单实例的cleaned_data字典来获取 url 字段的值。
- 拆分URL以获取文档扩展名，并检查它是否是有效的扩展名之一。如果扩展无效，则引发 ValidationError，并且不会验证表单实例。在这里，您正在执行一个非常简单的验证。您可以使用更高级的方法来检查给定的 URL 是否提供了有效的图像文档。

除了验证给定的 URL 外，您还需要下载图像文档并保存。例如，您可以使用处理表单的视图下载图像文档。相反，让我们采用更通用的方法，重写模型窗体的 save（） 方法，以便在每次保存窗体时执行此任务。

### 5.2.2 重写**ModelForm**的 `save（）` 方法
如您所知，ModelForm 提供了一个 save（） 方法来将当前模型实例保存到数据库并返回对象。此方法接收Boolean提交参数，该参数允许您指定是否必须将对象持久保存到数据库中。save（） 方法将返回一个模型实例，但不会将其保存到数据库中。您将覆盖表单的 save（） 方法，以便检索给定的图像并保存它。

将以下 save（） 方法添加到 ImageCreateForm form中：
```python
    def save(self, force_insert=False, force_update=False, commit=True):
        image = super().save(commit=False)
        image_url = self.cleaned_data['url']
        name = slugify(image.title)
        exentsions = image_url.rsplit('.', 1)[1].lower()
        image_name = f'{name}.{exentsions}'

        response = request.urlopen(image_url)
        image.image.save(image_name, ContentFile(response.read()), commit=False)

        if commit:
            image.save()
        return image
```

您可以覆盖 save（） 方法，保留 ModelForm 所需的参数。 上述代码可以解释如下：
- 通过使用 **commit=False** 调用表单的 `save（）` 方法来创建新的图像实例。
- 您可以从表单的**cleaned_data**字典中获取 URL。
- 通过将图像标题辅助信息域与原始文档扩展名组合在一起来生成图像名称。
- 您可以使用 Python urllib 模块下载图像，然后调用图像字段的 save（） 方法，向其传递一个 ContentFile 对象，该对象使用下载的文档内容进行实例化。通过这种方式，您可以将文档保存到项目的媒体目录中。传递 save=False 参数以避免将对象保存到数据库。
- 为了保持与重写的 save（） 方法相同的行为，仅当 commit 参数为 True 时，才将表单保存到数据库中。

为了使用 [**urllib**][2] 从通过 HTTPS 提供的 URL 中检索图像，您需要安装 **Certifi** Python 包。Certifi 是根证书的集合，用于验证 SSL/TLS 证书的可信度。

使用以下命令安装**certifi**：
```shell
pip install --upgrade certifi
```

您将需要一个视图来处理表单。编辑图像应用进程的 views.py 文档，并向其中添加以下代码：
```python
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .forms import ImageCreateForm
from django.contrib import messages

# Create your views here.
@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # form data is valid
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            # assign current user to the item
            new_item.user = request.user
            new_item.save()
            messages.success(request, 'Image added successfully')
            # redirect to new created item detail view
            return redirect(new_item.get_absolute_url())

    else:
        # build form with data provided by the bookmarklet via GET
        form = ImageCreateForm(data=request.GET)

    return render(request, 'images/image/create.html', {'section':'images', 'form':form})

```

在上面的代码中，您将**image_create**视图使用**login_required修饰器**来防止未经身份验证的用户访问。这是此视图的工作方式：
1. 您希望通过GET获得初始数据，以便创建表单的实例。此数据将包括来自外部网站的图像的 url 和标题属性，并将通过您稍后创建的 JavaScript 工具通过 GET 提供。现在，您只是假设这些数据最初将存在。
2. 如果表单已提交，请检查它是否有效。如果表单数据有效，则可以创建新的 Image 实例，但通过将 commit=False 传递给表单的 save（） 方法来阻止将对象保存到数据库中。
3. 将当前用户分配给新的图像对象。通过这种方式，您可以知道谁上传了每张图片。
4. 将图像对象保存到数据库中。
5. 最后，使用 Django 消息传递框架创建一条成功消息，并将用户重定向到新映像的规范 URL。您尚未实现图像模型的 get_absolute_url（） 方法;你稍后会这样做。

在图像应用进程中创建一个新的 urls.py 文档，并向其添加以下代码：
```python
from django.urls import path
from . import views
app_name = 'images'

urlpatterns = [
    path('create/', views.image_create, name='create')
]
```

编辑书签项目的主 urls.py 文档以包含图像应用进程的模式，如下所示：
```python
path('images/', include('images.urls', namespace='images'))
```

您需要创建一个模板来呈现表单。在图像应用进程目录中创建以下目录结构：
+ templates/
    + images/
        + image/
            + create.html

编辑新的 create.html 模板，并向其添加以下代码：
```html

```
使用 runserver_plus 运行开发服务器并打开 https://127.0.0.1:8000/images/create/?title=...&url=...，包括标题和网址 GET 参数，在后者中提供现有的 JPEG 图像网址。例如，您可以使用以下 URL：https://127.0.0.1:8000/images/create/?title=%20Django%20and%20Duke&url=https://upload.wikimedia.org/wikipedia/commons/8/85/Django_Reinhardt_and_Duke_Ellington_%28Gottlieb%29.jpg.

您将看到带有图像预览的表单，如下所示：
![ImageCreateForm images]()

添加描述并单击BOOKMARK IT! 按钮。一个新的图像对象将保存在您的数据库中。但是，您将收到一个错误，指示映像模型没有 get_absolute_url（） 方法。

暂时不要担心此错误;稍后将向 Image 模型添加 get_absolute_url 方法。

### 5.2.3 使用 jQuery 构建书签
书签是存储在 Web 浏览器中的书签，其中包含用于扩展浏览器功能的 JavaScript 代码。当您单击书签时，JavaScript代码将在浏览器中显示的网站上执行。这对于构建与其他网站交互的工具非常有用。书签是存储在 Web 浏览器中的书签，其中包含用于扩展浏览器功能的 JavaScript 代码。当您单击书签时，JavaScript代码将在浏览器中显示的网站上执行。这对于构建与其他网站交互的工具非常有用。

一些在线服务，如Pinterest，实现了自己的书签，让用户将其他网站的内容分享到他们的平台上。让我们以类似的方式为您的网站创建一个书签，使用 jQuery 构建您的书签。jQuery是一个流行的JavaScript库，它允许你更快地开发客户端功能。您可以在其官方网站上阅读有关jQuery的更多信息：https://jquery.com/。

以下是您的用户将书签添加到其浏览器并使用它的方式：
1. 用户将链接从您的网站拖动到其浏览器的书签。该链接在其 href 属性中包含 JavaScript 代码。此代码将存储在书签中。
2. 用户导航到任何网站并单击书签。执行书签的 JavaScript 代码。

由于 JavaScript 代码将存储为书签，因此您以后将无法更新它。这是一个重要的缺点，您可以通过实现启动器脚本从 URL 加载实际的 JavaScript 书签来解决。您的用户将此启动器脚本另存为书签，并且您可以随时更新书签的代码。这是您将采用的构建书签的方法。让我们开始吧！

在*images/templates/*下创建一个新模板，并将其命名为`bookmarklet_launcher.js`。这将是启动器脚本。将以下 JavaScript 代码添加到此文档：
```js
(function(){
    if(window.myBookmarklet !== undefined){
        myBookmarklet();
    }
    else{
        document.body.appendChild(document.createElement('script')).src='https://127.0.0.1:8000/static/js/bookmarklet.js?r='+Math.floor(Math.random()*99999999999999999999);
    }
})();
```

前面的脚本通过检查是否定义了 myBookmarklet 变量来发现书签是否已加载。通过这样做，您可以避免在用户反复单击书签时再次加载它。如果未定义 myBookmarklet，则可以通过向文档添加 <script> 元素来加载另一个 JavaScript 文档。脚本标记使用随机数作为参数加载书签.js脚本，以防止从浏览器的缓存加载文档。实际的书签代码驻留在bookmarklet.js静态文档中。这允许您更新书签代码，而无需用户更新他们之前添加到浏览器中的书签。
让我们将书签启动器添加到仪表板页面，以便您的用户可以将其复制到其书签中。编辑帐户应用进程的 account/dashboard.html 模板，使其如下所示：

```python
{% extends 'base.html' %}

{% block title %}Dashboard{% endblock  %}

{% block  content%}
    <h1>welcome to your dashboard</h1>

    {% with total_images_created=request.user.images_created.count %}
        <p>
            Wecome to your dashboard. You have bookmraked {{total_images_created}} image{{ total_images_created | pluralize}}.
        </p>
    {% endwith %}
    <p>
        Drag the following button to your bookmarks toolbar to bookmark images from other websites → <a href="javascript:{% include "bookmarklet_launcher.js" %}" class="button">Bookmark it</a>
    </p>
    <p>
        You can also <a href="{% url "edit" %}">edit your profile</a> or <a href="{% url "password_change" %}">change your password</a>.
    </p>
{% endblock  %}
```
确保没有模板标签拆分为多行;Django 不支持多行标签。
仪表板现在显示用户添加书签的图像总数。 您可以使用 {% with %} 模板标记来设置一个变量，其中包含当前用户添加书签的图像总数。您可以包含一个带有 href 属性的链接，该属性包含书签启动器脚本。您将包含来自bookmarklet_launcher.js模板的此 JavaScript 代码。
在浏览器中打开 https://127.0.0.1:8000/account/ 进行测试页面是否正常访问。

现在在图像应用进程目录中创建以下目录和文档：
- static/
    - js/
        - bookmarklet.js

编辑*bookmarklet.js*静态文档，并向其添加以下 JavaScript 代码：
```js
(function(){
    var jquery_version = '3.4.1';
    var site_url = 'https://127.0.0.1:8000';
    var static_url = site_url + 'static/'
    var min_width = 100;
    var min_height = 100;

    function bookmarklet(msg) {
        // Here goes our bookmarklet code
    }

    // Check if jQuery is loaded
    if (typeof window.jQuery != 'undefined') {
        bookmarklet()
    }else {
        // check for conflice
        var conflicts = typeof window.$ != 'undefined';
        // Create the script and point to Google API
        var script = document.createElement('script');
        script.src = '//ajax.googleapis.com/ajax/libs/jquery/' + jquery_version + '/jquery.min.js';
        // Add the script to the 'head' for processing
        document.head.appendChild(script);
        // Create a way to wait until script loading
        var attempts = 15;
        (function(){
            // Check again if jQuery is undefined
            if(typeof window.jQuery == 'undefined') {
            if(--attempts > 0) {
            // Calls himself in a few milliseconds
            window.setTimeout(arguments.callee, 250)
            } else {
            // Too much attempts to load, send error
            alert('An error occurred while loading jQuery')
            }
            } else {
            bookmarklet();
            }
        })();
    }
})()
```

这是主要的jQuery加载器脚本。如果 jQuery 已经加载到当前网站上，它会负责使用 jQuery。如果未加载jQuery，脚本将从Google的内容交付网络（CDN）加载jQuery，该网络托管流行的JavaScript框架。当 jQuery 被加载时，它会执行 bookmarklet（） 函数，该函数将包含你的书签代码。另外，在文档顶部设置一些变量：
- **jQuery** 要加载的 jQuery 版本
- **site_url and static_url** 网站的基本网址和静态文档的基本网址
- **min_width and min_height** 您的书签将尝试在网站上找到的图像的最小宽度和高度（以像素为单位）

现在让我们实现书签函数。编辑 bookmarklet（） 函数使其看起来像这样：
```js
// load CSS
var css = jQuery('<link>');
css.attr({
    rel: 'stylesheet',
    type: 'text/css',
    href: static_url + 'css/bookmarklet.css?r=' + Math.floor(Math.random()*99999999999999999999)
});
jQuery('head').append(css);
// load HTML
box_html = '<div id="bookmarklet"><a href="#" id="close">&times;</a><h1>Select an image to bookmark:</h1><div class="images"></div></div>';
jQuery('body').append(box_html);
// close event
jQuery('#bookmarklet #close').click(function(){
    jQuery('#bookmarklet').remove();
});
```

上述代码的工作原理如下：
- 您可以使用随机数作为参数加载`bookmarklet.css`样式表，以防止浏览器返回缓存文档。
- 将自定义 HTML 添加到当前网站的文档`<body>`元素。它由一个 `<div>` 元素组成，该元素将包含在当前网站上找到的图像
- 您可以添加一个事件，当用户单击 HTML 块的关闭链接时，该事件会从文档中删除您的 HTML。您可以使用#bookmarklet #close选择器查找 ID 名为 close 的 HTML 元素，该元素具有 ID 名为 bookmarklet 的父元素。jQuery选择器允许你查找HTML元素。jQuery 选择器返回给定 CSS 选择器找到的所有元素。你可以在 https:// api.jquery.com/category/selectors/ 找到jQuery选择器的列表。

加载书签的CSS样式和HTML代码后，您需要在网站上找到图像。在 bookmarklet（） 函数的底部添加以下 JavaScript 代码：
```js
// find images and display them
jQuery.each(jQuery('img[src$="jpg"]'), function(index, image) {
    if (jQuery(image).width() >= min_width && jQuery(image).height() >= min_height)
    {
        image_url = jQuery(image).attr('src');
        jQuery('#bookmarklet .images').append('<a href="#"><img src="'+ image_url +'" /></a>');
    }
});
```

前面的代码使用 img[src$=“jpg”] 选择器来查找所有 <img> HTML 元素，其 src 属性以 jpg 字符串结束。这意味着您将搜索当前网站上显示的所有 JPEG 图像。您可以使用 jQuery 的 each（） 方法迭代结果。将大小大于使用 min_width 和 min_height 变量指定的图像添加到 <div class=“images”> HTML 容器中。

出于安全原因，您的浏览器将阻止您在通过HTTPS提供的站点上通过HTTP运行书签。您需要能够在任何站点上加载书签，包括通过HTTPS保护的站点。要使用自动生成的 SSL/TLS 证书运行开发服务器，您将使用您在上一章中安装的 Django 扩展中的 RunServerPlus。

HTML 容器包含可添加书签的图像。您希望用户单击所需的图像并将其添加为书签。编辑 js/bookmarklet.js 静态文档，并在 bookmarklet（） 函数的底部添加以下代码：
```js
// when an image is selected open URL with it
jQuery('#bookmarklet .images a').click(function(e){
    selected_image = jQuery(this).children('img').attr('src');
    // hide bookmarklet
    jQuery('#bookmarklet').hide();
    // open new window to submit the image
    window.open(site_url +'images/create/?url='+ encodeURIComponent(selected_image) + '&title=' + encodeURIComponent(jQuery('title').text()), '_blank');
});
```

上述代码的工作原理如下：
1. 将 click（） 事件附加到每个图像的链接元素。
2. 当用户单击图像时，您可以设置一个名为selected_image的新变量，其中包含所选图像的 URL。
3. 您可以隐藏书签，并打开一个新的浏览器窗口，其中包含用于为网站上的新图像添加书签的 URL。您将网站的`<title>`元素的内容和选定的图像 URL 作为 GET 参数传递。

使用浏览器打开一个新 URL，然后再次单击书签以显示图像选择框。如果单击图像，您将被重定向到图像创建页面，将网站的标题和所选图像的URL作为GET参数传递：
![create bookmark images]()
祝贺！这是你的第一个 JavaScript 书签，它完全集成到你的 Django 项目中。

## 5.3 为图像创建详细信息视图
现在，让我们创建一个简单的详细信息视图来显示已保存到站点中的图像。打开图像应用进程的 views.py 文档，并向其中添加以下代码：
```python
from django.shortcuts import get_object_or_404
def image_detail(requset, id, slug):
    """image detail function"""
    image = get_object_or_404(Image, id=id, slug=slug)
    return render(requset, 'images/image/detail.html', {'image':image, 'section' : 'images'})
```
这是显示图像的简单视图。编辑图像应用进程的 urls.py 文档并添加以下 URL 模式：
```python
path('detail/<int:id>/<slug:slug>/', views.image_detail, name='detail')
```

编辑图像应用进程的 models.py 文档，并将 get_absolute_url（） 方法添加到图像模型中，如下所示：
```python
from django.urls import reverse

def get_absolute_url(self):
    """images detail absolute route"""
    return reverse("images:detail", args=[self.id, self.slug])
```

请记住，为对象提供规范 URL 的常见模式是在模型中定义 get_absolute_url（） 方法。

最后，在图像应用进程的 /images/image/ template目录中创建一个模板，并将其命名为 detail.html。向其添加以下代码：
```html
{% extends 'base.html' %}
{% block title %} {{image.title}} {% endblock  %}

{% block content %}
    <h1> {{ image.title}} </h1>
    <img src="{{ image.image.url }}" alt="{{ image.title}}" class="image-detail">
    {% with total_likes as image.users_like.count  %}
        <div class="image-info">
            <div>
                <span class="count">
                    {{total_likes}} like {{total_likes | pluralize}}
                </span>
            </div>
            {{ image.description }}

        </div>

        <div class="image-links">
            {% for user in image.users_like.all %}
                <div>
                    <img src="{{ user.profile.photo.url }}" alt="{{ user.first_name }}">
                    <p>{{ user.first_name }}</p>
                </div>
            {% empty %}
                Nobody likes this image yet.
            {% endfor %}
        </div>
    {% endwith %}
{% endblock  %}
```

这是用于显示已添加书签的图像的详细信息视图的模板。您可以使用 {% with %} 标记来存储 QuerySet 的结果，在名为 total_likes 的新变量中计算所有用户喜欢。通过这样做，可以避免两次评估同一 QuerySet。您还可以包括映像说明并循环访问映像。 users_like.all 以显示所有喜欢此图像的用户。

> 每当需要在模板中重复查询时，请使用 {% with %} 模板标记以避免其他数据库查询。

## 5.4 使用[**easy-thumbnails**][3]创建图像缩略图
您在详情页面上显示的是原始图片，但不同图片的尺寸可能会有很大差异。此外，某些图像的原始文档可能很大，加载它们可能需要很长时间。以统一方式显示优化图像的最佳方法是生成缩略图。为此，让我们使用一个名为easy-thumbnails的Django应用进程。每当需要在模板中重复查询时，请使用 {% with %} 模板标记以避免其他数据库查询。

使用以下命令打开终端并安装[easy-thumbnails][3]：
```shell

```
编辑书签项目的 settings.py 文档，将 easy_thumbnails 添加到 INSTALLED_APPS 设置中，如下：
```python

```

然后，运行以下命令将应用进程与数据库同步：
```shell
python manage.py migrate
```

easy-thumbnails 应用进程为您提供了定义图像缩略图的不同方法。如果您想在模型中定义缩略图，应用进程提供 {% thumbnail %} 模板标签以在模板中生成缩略图和自定义 ImageField。使用模板标记方法,编辑 *images/image/detail.html* 模板并查找以下行：
```shell
<img src="{{ image.image.url }}" class="image-detail">
```
以下行应替换前一行：
```python

```
定义具有 300 像素固定宽度和灵活高度的缩略图，以使用值 0 保持纵横比。用户首次加载此页面时，将创建一个缩略图。缩略图存储在原始文档的同一目录中。该位置由 MEDIA_ROOT 设置和 Image 模型的 image 字段的 upload_toattribute 定义。

他生成的缩略图在以下请求中提供。启动开发服务器并访问现有映像的映像详细信息页面。缩略图将生成并显示在网站上。如果您检查生成图像的 URL，您将看到原始文档名后面是用于创建缩略图的设置的其他详细信息；例如 *filename.jpg.300x0_q85.jpg.85*。

您可以使用质量参数使用不同的质量值。要设置最高 JPEG 质量，您可以使用值 100，例如 {% thumbnail image.image 300x0 quality=100 %}。

简易缩略图应用进程提供了多个选项来自定义缩略图，包括裁剪算法和可以应用的不同效果。如果在生成缩略图时遇到任何困难，可以将 `THUMBNAIL_DEBUG = True` 添加到 settings.py 文档中以获取调试信息。您可以在 https://easy-thumbnails.readthedocs.io/ 阅读简易缩略图的完整文档。

## 5.5 使用AJAX 操作查询
现在让我们将 AJAX 操作添加到您的应用进程。 AJAX 来自异步 JavaScript 和 XML，包含一组用于发出异步 HTTP 请求的技术。它包括从服务器异步发送和检索数据，而无需重新加载整个页面。尽管名称如此，但 XML 不是必需的。您可以发送或检索其他格式的数据，例如 JSON、HTML 或纯文本。

您将添加指向图像详细信息页面的链接，以允许用户单击它以喜欢图像。您将使用 AJAX 调用执行此操作，以避免重新加载整个页面。

首先，创建一个视图供用户喜欢/不喜欢图像。编辑图像应用进程的 views.py 文档，并向其中添加以下代码：
```python
@login_required
@require_POST
def image_link(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id & action:
        try:
            image = Image.objects.get(id = image_id)
            if action == "link":
                image.users_like.add(request.user)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status' : 'ok'})
        except:
            pass
    return JsonResponse({'status' : 'error'})
```
在您的视图方法中使用了两个装饰器，login_required 装饰器可防止未登录的用户访问此视图，如果 HTTP 请求不是通过 POST 完成的，*require_POST* 装饰器会返回一个 *HttpResponseNotAllowed* 对象（状态码 405）。这样，您只允许对此视图的 POST 请求。

Django 还提供了一个只允许 GET 请求的require_GET装饰器和一个require_http_methods装饰器，您可以将允许的方法列表作为参数传递给它。
在此视图中，使用两个 POST 参数：
- **image_id** 用户对其执行操作的图像对象的 ID
- **action** 用户想要执行的操作，假定该操作是值相似或相似的字符串

您可以使用 Django 为图像模型的users_like多对多字段提供的管理器，以便使用 add（） 或 remove（） 方法在关系中添加或删除对象。调用 add（），即传递相关对象集中已存在的对象，不会复制它。调用 remove（） 并传递不在相关对象集中的对象不执行任何操作。多对多管理器的另一个有用方法是 clear（），它从相关对象集中删除所有对象。最后，您使用 Django 提供的 JsonResponse 类，该类返回具有应用进程/json 内容类型的 HTTP 响应，将给定的对象转换为 JSON 输出。
编辑图像应用进程的 urls.py 文档，并向其添加以下 URL 模式：
```python
path('link', views.image_link, name='link')
```
### 5.3.1 加载 jQuery
您需要将 AJAX 功能添加到图像详细信息模板。为了在模板中使用jQuery，您将首先将其包含在项目的**base.html**中。编辑帐户应用进程的**base.html**模板，并在结束</body> HTML 标记之前包含以下代码：
```js
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    <script>    
        $(document).ready(function(){
          {% block domready %}
          {% endblock %}
        });
      </script>
```

您从 Google 的 CDN 加载 jQuery 框架。您也可以从 https://jquery.com/ 下载jQuery 并将其添加到应用进程的静态目录中。

您可以添加<script>标记以包含 JavaScript 代码 `$（document）.ready（）` 是一个 jQuery 函数，它采用在完全构造文档对象模型 （DOM） 层次结构时执行的处理进程。DOM 由浏览器在加载网页时创建，并构造为对象树。通过在此函数中包含代码，您将确保要与之交互的所有 HTML 元素都加载到 DOM 中。您的代码只会在 DOM 准备就绪后执行。

在文档就绪处理进程函数中，你包含一个名为`domready`的Django模板块，其中扩展基本模板的模板将能够包含特定的JavaScript。不要被 JavaScript 代码和 Django 模板标签所迷惑。Django 模板语言在服务器端呈现，输出最终的 HTML 文档，JavaScript 在客户端执行。在某些情况下，使用 Django 动态生成 JavaScript 代码很有用，以便能够使用 QuerySet 或服务器端计算的结果来定义 JavaScript 中的变量。

本章中的示例包括 Django 模板中的 JavaScript 代码。包含 JavaScript 代码的首选方法是加载.js文档，这些文档作为静态文档提供，尤其是当它们是大型脚本时。

### 5.3.2 AJAX 请求中的跨站点请求伪造
您在第 2 章 “使用高级功能增强博客”中了解了跨站点请求伪造 （CSRF）。激活 CSRF 保护后，Django 会在所有 POST 请求中检查 CSRF 令牌。提交表单时，可以使用 `{% csrf_token %}` template 标记将令牌与表单一起发送。但是，对于 AJAX 请求来说，在每个 POST 请求中将 CSRF 令牌作为 POST 数据传递有点不方便。因此，Django 允许你在 AJAX 请求中使用 CSRF 令牌的值设置一个自定义的 X-CSRFToken 标头。这使您能够设置 jQuery 或任何其他 JavaScript 库，以在每个请求中自动设置 X-CSRFToken 标头。

为了在所有请求中包含令牌，您需要执行以下步骤：
1. 从 csrftoken cookie 中检索 CSRF 令牌，如果 CSRF 保护处于活动状态则设置
2. 使用 X-CSRFToken 标头在 AJAX 请求中发送令牌

您可以在以下位置找到有关 CSRF 保护和 AJAX 的更多信息:[https://docs.djangoproject.com/en/4.0/ref/csrf/#ajax][4]

编辑您在 base.html 模板中包含的最后一个代码，使其如下所示：
```js
    <script src="https://cdn.jsdelivr.net/npm/js-cookie@2.2.1/src/js.cookie.min.js"></script>
    <script>
        var csrftoken = Cookies.get('csrftoken');
        function csrfSafeMethod(method) {
          // these HTTP methods do not require CSRF protection
          return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
        $.ajaxSetup({
          beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
          }
        });
        ...
      </script>
```

前面的代码如下：
1. 您从公共 CDN 加载 JS Cookie 插件，以便您可以轻松地与 cookie 交互。 JS Cookie 是用于处理 cookie 的轻量级 JavaScript API。您可以在 https://github.com/js-cookie/js-cookie 了解更多信息。
2. 您可以使用 `Cookies.get（）` 读取 csrftoken cookie 的值。
3. 您定义 `csrfSafeMethod()` 函数来检查 HTTP 方法是否安全。安全方法不需要 CSRF 保护——它们是 GET、HEAD、OPTIONS 和 TRACE。
4. 您使用 `$.ajaxSetup()` 设置 jQuery AJAX 请求。在执行每个 AJAX 请求之前，请检查请求方法是否安全，以及当前请求是否跨域。如果请求不安全，则使用从 cookie 获取的值设置 X-CSRFToken 标头。此设置将适用于使用 jQuery 执行的所有 AJAX 请求。

CSRF 令牌将包含在所有使用不安全 HTTP 方法（例如 POST 或 PUT）的 AJAX 请求中。

### 5.3.3 使用 jQuery 执行 AJAX 请求
编辑图像应用进程的 **images/image/detail.html** 模板并考虑以下行：
```python
{% with total_likes=image.users_like.count %}
```

将前一行替换为以下行：
```python
{% with total_likes=image.users_like.count users_like=image.users_like.all %}
```

确保模板代码拆分为多行。
替换定义 for 循环的行：
```python
{% for user in image.users_like.all %}
```
与以下一个：
```python
{% for user in users_like %}
```
然后，修改 <div> 带有 image-info 类的元素，如下所示：
```python
<div class="image-info">  
    <div>    
        <span class="count">
            <span class="total">{{ total_likes }}</span>      
            like{{ total_likes|pluralize }}    
        </span>
            <a href="#" data-id="{{ image.id }}" data-action="{% if request.user in users_like %}un{% endif %}like"class="like button">{% if request.user not in users_like %}Like{% else %}Unlike{% endif %}</a>  
        </div>  
        
        {{ image.description|linebreaks }}
</div>
```
首先，您将另一个变量添加到 `{% with %}` 模板标签，以存储 `image.users_like.all` 查询的结果并避免执行两次。您将变量用于迭代喜欢此图像的用户的 for 循环。

您显示喜欢该图像的用户总数，并包含一个喜欢/不喜欢该图像的链接。根据用户与此图像之间的当前关系，检查用户是否在 `users_like` 的相关对象集中以显示喜欢或不喜欢。您将以下属性添加到 </a> HTML 元素：
- `data-id` 显示的图像的 ID。
- `data-action` 用户单击链接时要运行的操作。这可以是相似的，也可以是不像的。

> 任何 HTML 元素的属性名称以 data- 开头的任何属性都是数据属性。数据属性用于存储应用进程的自定义数据。

您将在 AJAX 请求中将这两个属性的值发送到 image_like view。当用户点击赞/不赞链接时，您将在客户端执行以下操作：
1. 调用 AJAX 视图，向其传递映像 ID 和操作参数
2. 如果AJAX请求成功，则更新<a> 的data-action属性。具有相反动作（喜欢/不喜欢）的 HTML 元素，并相应地修改其显示文本
3. 更新显示的点赞总数

使用以下 JavaScript 代码在 **images/image/detail.html** 模板底部添加 domready 块：
```js
{% block domready %}
  $('a.like').click(function(e){
    e.preventDefault();
    $.post('{% url "images:like" %}',
      {
        id: $(this).data('id'),
        action: $(this).data('action')
      },
      function(data){
        if (data['status'] == 'ok')
        {
          var previous_action = $('a.like').data('action');

          // toggle data-action
          $('a.like').data('action', previous_action == 'like' ?
          'unlike' : 'like');
          // toggle link text
          $('a.like').text(previous_action == 'like' ? 'Unlike' :
          'Like');

          // update total likes
          var previous_likes = parseInt($('span.count .total').text());
          $('span.count .total').text(previous_action == 'like' ?
          previous_likes + 1 : previous_likes - 1);
        }
      }
    );
  });
{% endblock %}
```
上述代码的工作原理如下：
1. 您可以使用 `$（'a.like'）` jQuery 选择器来查找具有 like 类的 HTML 文档的所有 <a> 元素。
2. 您为 click 事件定义一个处理函数。每次用户点击喜欢/不喜欢链接时，都会执行此功能。
3. 在处理进程函数中，使用 `e.preventDefault（）` 来避免 <a> 元素的默认行为。这将阻止链接将您带到任何地方。
4. 您可以使用 `$.post（）` 对服务器执行异步 POST 请求。jQuery还提供了`$.get（）`方法来执行GET请求和低级`$.ajax（）`方法。
5. 您使用 Django 的 {% url %} 模板标签来构建 AJAX 请求的 URL。
6. 构建要在请求中发送的 POST 参数字典。这些参数是 Django 视图所期望的 ID 和action参数。您可以从 <a> 元素的数据 ID 和数据操作属性中检索这些值。
7. 定义在收到 HTTP 响应时执行的回调函数;它采用包含响应内容的数据属性。
8. 您访问接收到的数据的状态属性并检查它是否等于正常。如果返回的数据符合预期，则切换链接及其文本的数据操作属性。这允许用户撤消其操作。
9. 您可以将总赞数增加或减少 1，具体取决于执行的操作。

在浏览器中打开图片详情页面，查看已上传的图片。您应该能够看到以下初始喜欢计数和“赞”按钮;
在对 JavaScript 进行编程时，尤其是在执行 AJAX 请求时，建议您使用工具来调试 JavaScript 和 HTTP 请求。大多数现代浏览器都包含用于调试JavaScript的开发人员工具。通常，您可以右键单击网站上的任意位置，然后单击“检查元素”以访问 Web 开发人员工具。

## 5.6 为视图创建自定义装饰器
让我们限制您的 AJAX 视图，以仅允许通过 AJAX 生成的请求。Django 请求对象提供了一个 is_ajax（） 方法，用于检查请求是否是使用 XMLHttpRequest 发出的，这意味着它是一个 AJAX 请求。此值在 `HTTP_X_REQUESTED_WITH` HTTP 标头中设置，大多数 JavaScript 库都包含在 AJAX 请求中。

接下来，您将创建一个修饰器，用于检查视图中的HTTP_X_REQUESTED_WITH标题。装饰器是一个函数，它采用另一个函数并扩展后者的行为而不显式修改它。如果装饰器的概念对您来说很陌生，您可能需要在继续阅读之前先看看 https://www.python.org/dev/peps/pep-0318/。

由于您的装饰器将是通用的并且可以应用于任何视图，因此您将在项目中创建一个通用的 Python 包。在书签项目目录中创建以下目录和文档：
+ common/
    + __init__.py
    + decorators.py

编辑 decorators.py 文档并向其中添加以下代码：
```python
def ajax_required(f):
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest

        return f(request, *args, **kwargs)
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__

    return wrap
```
前面的代码是自定义ajax_required修饰器。它定义了一个包装函数，如果请求不是 AJAX，则返回 HttpResponseBadRequest 对象（HTTP 400 代码）。否则，它将返回修饰的函数。

现在，您可以编辑图像应用进程的 views.py 文档，并将此修饰器添加到image_like AJAX 视图中，如下所示：
```python
from common.decorators import ajax_required

@ajax_required

from django.http import HttpResponseBadRequest
```
如果您尝试直接使用浏览器访问 https://127.0.0.1:8000/images/like/，您将收到 HTTP 400 响应。

> 如果发现在多个视图中重复相同的检查，请为视图构建自定义修饰器。

## 5.7 将 AJAX 分页添加到列表视图
接下来，您需要列出网站上所有已添加书签的图像。您将使用 AJAX 分页来构建无限滚动功能。无限滚动是通过在用户滚动到页面底部时自动加载下一个结果来实现的。

让我们实现一个图像列表视图，该视图将处理标准浏览器请求和 AJAX 请求，包括分页。当用户最初加载图像列表页时，将显示图像的第一页。当他们滚动到页面底部时，您将通过 AJAX 加载下一页的项目并将其附加到主页的底部。

同一视图将同时处理标准分页和 AJAX 分页。编辑图像应用进程的 views.py 文件并向其添加以下代码：
```python
@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if is_ajax(request=request):
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)

    if is_ajax(request=request):
        return render(request, 'images/image/list_ajax.html', {'section': 'images', 'images': images})
    
    return render(request, 'images/image/list.html', {'section': 'images', 'images': images}) 
```
在此视图中，您将创建一个 QuerySet 以返回数据库中的所有图像。然后，构建一个分页器对象来对结果进行分页，每页检索八个图像。如果请求的页面超出范围，则会收到 EmptyPage 异常。如果是这种情况，并且请求是通过 AJAX 完成的，则返回一个空的 HttpResponse，它将帮助您停止客户端的 AJAX 分页。将结果呈现到两个不同的模板：
- 对于 AJAX 请求，呈现list_ajax.html模板。此模板将仅包含所请求页面的图像。
- 对于标准请求，请呈现list.html模板。此模板将扩展 base.html 模板以显示整个页面，并将包括list_ajax.html模板以包含图像列表

编辑图像应用进程的 urls.py 文档，并向其添加以下 URL 模式：
```python
path('', views.image_list, name='list')
```

最后，您需要创建此处提到的模板。在 *images/image/* 模板目录中，创建一个新模板并将其命名为 *list_ajax.html*。向其添加以下代码：
```html
{% load thumbnail %}

{% for image in images %}
    <div class="image">
        <a href="{{ image.get_absolute_url }}">
            {% thumbnail image.image 300x300 crop="smart" as im %}
            <a href="{{ image.get_absolute_url }}">
                <img src="{{ im.url }}">
            </a>
        </a>

        <div class="info">
            <a href="{{ image.get_absolute_url }}" class="title">
                {{image.title}}
            </a>
        </div>
    </div>
{% endfor %}
```

上述模板显示图像列表。您将使用它来返回 AJAX 请求的结果。在此代码中，循环访问图像并为每个图像生成方形缩略图。将缩略图的大小规范化为 300x300 像素。您还可以使用智能裁剪选项。此选项表示必须通过从熵最少的边缘删除切片来增量裁剪图像到请求的大小

在同一目录中创建另一个模板并将其命名为 `list.html`。向其添加以下代码：
```html
{% extends 'base.html' %}

{% block title %} Images bookmarked {% endblock %}

{% block content %}
    <h1>Images Bookmarked</h1>
    <div id="image-list">
        {% include "images/image/list_ajax.html" %}
    </div>
{% endblock %}
```

列表模板扩展了`base.html`。为避免重复代码，请包含用于显示图像的`list_ajax.html`模板。`list.html模`板将保存 JavaScript 代码，用于在滚动到页面底部时加载其他页面。

将以下代码添加到 list.html模板：
```js
{% block domready %}
  var page = 1;
  var empty_page = false;
  var block_request = false;

  $(window).scroll(function() {
    var margin = $(document).height() - $(window).height() - 200;
    if  ($(window).scrollTop() > margin && empty_page == false &&
    block_request == false) {
     block_request = true;
      page += 1;
      $.get('?page=' + page, function(data) {
       if(data == '') {
          empty_page = true;
        }
        else {
          block_request = false;
          $('#image-list').append(data);
        }
      });
    }
  });
{% endblock %}
```

前面的代码提供了无限滚动功能。您可以在 base.html 模板中定义的 domready 块中包含 JavaScript 代码。 代码如下：
1. 您可以定义以下变量：
    - *page* 存储当前页码。
    - *empty_page* 允许您知道用户是否在最后一页并检索空页。一旦获得空页面，您将停止发送其他 AJAX 请求，因为您将假定没有更多结果。
    - *block_request* 防止在 AJAX 请求正在进行时发送其他请求。

2. 您可以使用 $（window）.scroll（） 来捕获滚动事件，并为其定义一个处理进程函数。
3. 计算边距变量以获取总文档高度与窗口高度之间的差异，因为这是供用户滚动的剩余内容的高度。从结果中减去值 200，以便在用户距离页面底部不到 200 像素时加载下一页
4. 仅当没有执行其他 AJAX 请求（block_request必须为 false）并且用户未到达结果的最后一页（empty_page 也是 false）时，才发送 AJAX 请求。
5. 将 block_request 设置为 true 是为了避免滚动事件触发其他 AJAX 请求的情况，并将页计数器增加 1，以便检索下一页。
6. 使用 $.get（） 执行 AJAX GET 请求，并在名为 data 的变量中接收 HTML 响应。以下是两种方案：
    + 响应没有内容：您到了结果的末尾，并且没有更多要加载的页面。将empty_page设置为 true 可防止其他 AJAX 请求。
    + 响应包含数据：将数据追加到具有图像列表 ID 的 HTML 元素。页面内容垂直展开，当用户接近页面底部时追加结果。

在浏览器中打开 https://127.0.0.1:8000/images/。您将看到到目前为止已添加书签的图像列表。

滚动到页面底部以加载其他页面。确保使用书签为八个以上的图像添加书签，因为这是每页显示的图像数量。请记住，您可以使用Firebug或类似的工具来跟踪AJAX请求并调试JavaScript代码。

最后，编辑帐户应用进程的base.html模板，并添加主菜单的图像项的URL，如下所示：
```python
<li {% if section == 'images' %} class='deshboard' {% endif %}>
    <a href="{% url 'images:list' %}"> IMAGES </a>
</li>
```
现在，您可以从主菜单访问图像列表。

## 概要
在本章中，您创建了具有多对多关系的模型，并学习了如何自定义表单的行为。你使用 jQuery 和 Django 构建了一个 JavaScript 书签，将其他网站的图片分享到你的网站中。本章还介绍了使用简易缩略图库创建图像缩略图。最后，您使用 jQuery 实现了 AJAX 视图，并将 AJAX 分页添加到图像列表视图中。

在下一章中，您将学习如何构建关注系统和活动流。您将使用泛型关系、信号和非规范化。你还将学习如何在Django中使用Redis。

# Chapter 6 跟踪用户操作
在上一章中，您使用 jQuery 在项目中实现了 AJAX 视图，并构建了一个 JavaScript 书签来共享平台上其他网站的内容。
在本章中，您将学习如何构建关注系统和创建用户活动流。您还将发现 Django 信号的工作原理，并将 Redis 的快速 I/O 存储集成到您的项目中以存储项目视图。
本章将介绍以下几点：
- 构建关注系统
- 使用中间模型创建多对多关系
- 创建活动流应用进程
- 向模型添加泛型关系
- 优化相关对象的查询集
- 使用信号对计数进行非规范化
- 在 Redis 中存储项目视图

## 6.1 构建关注系统
让我们在你的项目中构建一个跟随系统。这意味着您的用户将能够相互关注并跟踪其他用户在平台上共享的内容。用户之间的关系是多对多关系：一个用户可以关注多个用户，而他们又可以被多个用户关注。

### 6.1.1 使用中间模型创建多对多关系
在前面的章节中，你通过将 ManyToManyField 添加到其中一个相关模型中并让 Django 为该关系创建数据库表来创建多对多关系。这适用于大多数情况，但有时您可能需要为关系创建中介模型。如果要存储关系的其他信息（例如，创建关系的日期或描述关系性质的字段），则必须创建中间模型。

让我们创建一个中间模型来构建用户之间的关系。使用中间模型有两个原因：
- 您正在使用 Django 提供的用户模型，并且希望避免更改它
- 您希望存储创建关系的时间

编辑帐户应用进程的 models.py 文档，并向其中添加以下代码：
```python
class Contact(models.Model):
    """followers 中间模型"""
    user_from = models.ForeignKey('auth.User', related_name='rel_from_set', on_delete=models.CASCADE)
    user_to = models.ForeignKey('auth.User', related_name='rel_to_set', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    class Meta:
        ordering=('-created',)

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'
```

上面的代码显示了将用于用户关系的联系人模型。它包含以下字段：
 - **user_from** 创建关系的用户的外键
 - **user_to** 被关注的用户的外键
 - **created** 具有 auto_now_add=True 的日期时间字段，用于存储创建关系的时间

将在“外键”字段上自动创建数据库索引。您可以使用 db_index=True 为创建的字段创建数据库索引。这将提高按此字段对查询集进行排序时的查询性能。

使用 ORM，您可以为用户 user1 创建关系，关注另一个用户 user2，如下所示：
```python
user1 = User.objects.get(id=1)
user2 = User.objects.get(id=2)
Contact.objects.create(user_from = user1, user_to = user2)
```

相关经理（rel_from_set和rel_to_set）将返回联系人模型的查询集。为了从用户模型访问关系的端，用户最好包含一个 ManyToManyField，如下所示：
```python
following = models.ManyToManyField('self', through=Contact, related_name='followers', symmetrical=False)
```
在前面的示例中，你告诉 Django 通过将 through=Contact 添加到 ManyToManyField 来使用你的自定义中间模型来处理关系。这是从用户模型到自身的多对多关系;您在 ManyToManyField 字段中引用“self”以创建与同一模型的关系。

编辑帐户应用进程的 models.py 文档并添加以下行：
```python
user_model = get_user_model()
user_model.add_to_class('following', models.ManyToManyField('self', through=Contact, related_name='followers', symmetrical=False))
```

在上面的代码中，使用 Django 提供的泛型函数 `get_user_model（）` 检索用户模型。你使用 Django 模型的 `add_to_class（）` 方法来修补用户模型。请注意，使用 `add_to_class（）` 不是向模型添加字段的推荐方法。但是，在这种情况下，您可以利用它来避免创建自定义用户模型，从而保留 Django 内置用户模型的所有优点。

您还可以简化使用 Django ORM 和 user.followers.all（） 和 user.follow.all（） 检索相关对象的方式。您可以使用中间联系人模型并避免涉及其他数据库联接的复杂查询，就像在自定义配置文档模型中定义关系一样。此多对多关系的表将使用联系人模型创建。因此，动态添加的 ManyToManyField 并不意味着 Django 用户模型的任何数据库更改。

请记住，在大多数情况下，最好将字段添加到您之前创建的配置文档模型，而不是猴子修补用户模型。理想情况下，你不应该改变现有的 Django 用户模型。Django 允许你使用自定义用户模型。如果要使用自定义用户模型，请查看 https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#specifying-a-custom-user-model 中的文档。

请注意，该关系包括`symmetrical=False`。当你在模型中定义一个 ManyToManyField 来创建与自身的关系时，Django 强制该关系是对称的。在本例中，您正在设置 `symmetrical=False` 来定义非对称关系（如果我关注您，并不意味着您会自动关注我）。

> 将中间模型用于多对多关系时，某些相关管理器的方法将被禁用，例如 add（）、create（） 或 remove（）。您需要改为创建或删除中间模型的实例。

运行以下命令以生成帐户应用进程的初始迁移：
```shell
python manage.py makemigrations account
```

现在，运行以下命令以将应用进程与数据库同步：
```shell
python manage.py migrate account
```

联系人模型现在已同步到数据库，您可以在用户之间创建关系。但是，您的网站尚不提供浏览用户或查看特定用户个人资料的方法。让我们为用户模型构建列表和详细信息视图。

### 6.1.2 为用户配置文档创建列表和详细信息视图
打开帐户应用进程的 views.py 文档，并向其中添加以下代码：
```python
@login_required
def user_list(request):
    """this user list"""
    users = User.objects.filter(is_active=True)

    return render(request, 'account/user/list.html', {"section":"people", "users": users})


@login_required
def user_detail(request, username):
    """the user detail page"""
    user = get_object_or_404(User, username=username, is_active=True)

    return render(request, 'account/user/detail.html', {'section': 'people', 'user': user})
```
这些是用户对象的简单列表和详细信息视图。user_list视图获取所有活动用户。Django 用户模型包含一个 is_active 标志，用于指定用户帐户是否被视为活动。按 is_active=True 筛选查询以仅返回活动用户。此视图返回所有结果，但您可以通过添加分页来改进它，方法与image_list视图相同。

user_detail视图使用 get_object_or_404（） 快捷方式检索具有给定用户名的活动用户。如果未找到具有给定用户名的活动用户，则视图将返回 HTTP 404 响应

编辑帐户应用进程的 urls.py 文档，并为每个视图添加 URL 模式，如下所示
```python
path('users/', views.user_list, name='user_list'),
path('users/<username>/', views.user_detail, name='user_detail')
```
您将使用`user_detail URL` 模式为用户生成规范 URL。您已经在模型中定义了一个` get_absolute_url（）` 方法来返回每个对象的规范 URL。指定模型 URL 的另一种方法是将ABSOLUTE_URL_OVERRIDES设置添加到项目中。
```python
from django.urls import reverse_lazy
ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: reverse_lazy('user_detail',  args=[u.username])
}
```

Django 将 `get_absolute_url（）` 方法动态添加到`ABSOLUTE_URL_OVERRIDES`设置中出现的任何模型中。此方法返回设置中指定的给定模型的相应 URL。返回给定用户的user_detail URL。现在，您可以在用户实例上使用 get_absolute_url（） 来检索其相应的 URL。

使用 python manage.py shell 命令打开 Python shell，并运行以下代码进行测试：
```shell
from django.contrib.auth.models import User
user = User.objects.latest('id')
str(user.get_absolute_url())
```
您需要为刚生成的视图创建模板。将以下目录和文档添加到帐户应用进程的templates/account/目录中：
+ /user/
    detail.html/
    list.html/

编辑 `account/user/list.html` 模板并向其添加以下代码：
```html
{% extends 'base.html' %}
{% load thumbnail %}
{% block title %}People{% endblock  %}

{% block content %}
<h1>People</h1>
<div class="people-list">
    {% for user in users %}
        <div class="user">
            <a href="{{user.get_absolute_url}}">
                <img src="{% thumbnail user.profile.photo 180x180 %}" alt="" srcset="">
            </a>

            <div class="info">
                <a href="{{user.get_obsolute_url}}" class="title">
                    {{user.get_full_name}}
                </a>
            </div>
        </div>
    {% endfor %}

</div>
{% endblock  %}
```

上述模板允许您列出网站上的所有活动用户。您循环访问给定的用户，并使用简易缩略图中的 {% thumbnail %} 模板标记来生成个人资料图像缩略图

打开项目的 `base.html` 模板，并在以下菜单项的 href 属性中包含`user_list` URL：
```html
<li {% if section == 'people' %} class='deshboard' {% endif %}>
    <a href="{% url 'user_list' %}"> PEOPLE</a>
</li>
```

请记住，如果在生成缩略图时遇到任何困难，可以将 THUMBNAIL_DEBUG = True 添加到 settings.py 文档中，以便在 shell 中获取调试信息。

编辑帐户应用进程的 **account/user/detail.html** 模板，并向其添加以下代码：
```html
{% extends 'base.html' %}
{% block title %} {{user.get_full_name}} {% endblock  %}
{% load thumbnail %}

{% block content %}
    <h1> {{user.get_full_name}} </h1>

    <div class="profile-info">
        <img src="{% thumbnail user.profile.photo 180x180%}" class="user-detail">
    </div>

    {% with total_followers as user.followers.count %}
    
    <span class="count">
        <span class="tatal">
            {{total_followers}}
        </span>
        followers {{total_followers|pluralize}}
    </span>

    <a href="#" data-id="{{ user.id }}", data-action="{% if request.user in user.followers.all %}un{% endif %}follow" class="follow button">
        {% if request.user not in user.followers.all %}
        follow
        {% else %}
        Unfollow
        {% endif %}
    </a>

    <div class="image-container" id="image-list">
        {% include "images/image/list_ajax.html" with images=user.images_created.all %}
    </div>

    {% endwith %}
{% endblock  %}
```
确保没有模板标签拆分为多行;Django 不支持多行标签。

在详细模板中，显示用户配置文档并使用 {% 缩略图 %}模板标记显示配置文档图像。您显示关注者的总数以及用于关注或取消关注用户的链接。执行 AJAX 请求以关注/取消关注特定用户。您可以向 &lt;a&gt;HTML 元素添加数据 ID 和数据操作属性，包括用户 ID 和单击链接元素时要执行的初始操作 - 关注或取消关注，这取决于请求页面的用户是否是该其他用户的关注者（视情况而定）。显示由用户添加书签的图像，包括 images/image/list_ajax.html 模板。

### 6.1.3 构建 AJAX 视图以关注用户
让我们创建一个简单的视图来关注/取消关注使用 AJAX 的用户。编辑帐户应用进程的 views.py 文档，并向其添加以下代码：
```python
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from common.decorators import ajax_required
from .models import Contact
@ajax_required
@require_POST
@login_required
def user_follow(request):
    """the user folowers"""
    user_id = request.POST.get('id')
    action = request.POST.get('action')

    if user_id and action:
        try:
            user = User.objects.get(id = user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from = request.user, user_to = user)
            else:
                Contact.objects.filter(user_from = request.user, user_to=user).delete()

            return JsonResponse({'status' : 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status' : 'error'})

    return JsonResponse({'status': 'error'})
```
`user_follow`视图与您之前创建的`image_like`视图非常相似。由于您正在为用户的多对多关系使用自定义中介模型，因此 ManyToManyField 自动管理器的默认 add（） 和 remove（） 方法不可用。您可以使用中间联系人模型来创建或删除用户关系。

编辑帐户应用进程的 urls.py 文档，并向其添加以下 URL 模式：
```python
path('users/follow/', views.user_follow, name='user_follow'),
```

确保将上述模式放在 user_detail URL 模式之前。否则，对 /users/follow/ 的任何请求都将与user_detail模式的正则表达式匹配，并且将改为执行该视图。请记住，在每个HTTP请求中，Django都会按照出现的顺序根据每个模式检查请求的URL，并在第一次匹配时停止。

编辑帐户应用进程的 `user/detail.html` 模板，并向其追加以下代码：
```python
{% block domready %}
  $('a.follow').click(function(e){
    e.preventDefault();
    $.post('{% url "user_follow" %}',
      {
        id: $(this).data('id'),
        action: $(this).data('action')
      },
      function(data){
        if (data['status'] == 'ok') {
          var previous_action = $('a.follow').data('action');

          // toggle data-action
          $('a.follow').data('action',
            previous_action == 'follow' ? 'unfollow' : 'follow');
          // toggle link text
          $('a.follow').text(
            previous_action == 'follow' ? 'Unfollow' : 'Follow');

          // update total followers
          var previous_followers = parseInt(
            $('span.count .total').text());
          $('span.count .total').text(previous_action == 'follow' ?
          previous_followers + 1 : previous_followers - 1);
        }
      }
    );
  });
{% endblock %}
```
前面的代码是执行 AJAX 请求以关注或取消关注特定用户以及切换关注/取消关注链接的 JavaScript 代码。您可以使用 jQuery 执行 AJAX 请求，并根据 HTML &lt;a&gt; 元素的先前值设置数据操作属性和文本。执行 AJAX 操作时，您还会更新页面上显示的关注者总数.


## 6.2 构建通用活动流应用进程
许多社交网站向其用户显示活动流，以便他们可以跟踪其他用户在平台上的行为。课程动态是一个用户或一组用户最近执行的活动的列表。例如，Facebook的News Feed是一个活动流。示例操作可以是用户 X 已添加书签的图像 Y，也可以是用户 X 现在正在关注用户 Y。

您将构建一个活动流应用进程，以便每个用户都可以看到他们关注的用户最近的交互。为此，您需要一个模型来保存用户在网站上执行的操作，以及一种向源添加操作的简单方法。



### 6.2.1 使用内容类型框架

### 6.2.2 向模型添加泛型关系

### 6.2.3 避免活动流中的重复操作

### 6.2.4 将用户操作添加到动态

### 6.2.5 显示活动流


### 6.2.6 优化涉及相关对象的查询集

#### 使用 select_related（）

#### 使用 prefetch_related（）

### 6.2.7 为操作创建模板

## 6.3 使用信号对计数进行非规范化

## 6.4 使用 Redis 存储项目视图

## 概述


[1]: https://docs.djangoproject.com/en/4.0/topics/db/examples/many_to_many/ "ManyToManyFiled"
[2]: https://docs.python.org/zh-cn/3/library/urllib.html "urllib 文档"
[3]: https://github.com/SmileyChris/easy-thumbnails "easy-thumbnails Github"
[4]: https://docs.djangoproject.com/en/4.0/ref/csrf/#ajax "django csrf doucmente"
